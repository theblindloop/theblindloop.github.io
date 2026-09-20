#!/usr/bin/env python3
"""Check source-bound results, program navigation, and paper-ordered site structure."""
import argparse, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
def main(base):
    manifest=json.loads((ROOT/'data/paper-content-provenance.json').read_text())
    for item in manifest['excerptsAndImages']:
        p=ROOT/item['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
        if 'text' in item: assert '\n'.join(p.read_text().splitlines()[item['startLine']-1:item['endLine']])==item['text']
    tables=json.loads((ROOT/'data/paper-tables.json').read_text())
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base+'/',wait_until='networkidle')
        assert page.locator('.world-card').count()==6
        assert page.locator('#results > .container > article').evaluate_all('(els)=>els.map(e=>e.id)')==['generation','steering','evaluation','feedback','human-review','training']
        assert page.locator('#training #external').count()==1
        assert page.locator('#generation #programs').count()==1
        assert page.locator('.accuracy-track').count()==0
        assert page.locator('#table-evaluation-summary tbody tr td:nth-child(3)').all_text_contents()==tables['evaluation']['rows'][5][2:]
        assert page.locator('#table-evaluation-summary tbody tr td:nth-child(4)').all_text_contents()==tables['evaluation']['rows'][11][2:]
        assert page.locator('main > .paper-section').evaluate_all('(els)=>els.map(e=>e.id)')==['motivation','method','results','limitations']
        for i in range(3):
            page.locator(f'[data-method-sample="{i}"]').click()
            assert page.locator('[data-method-count]').all_text_contents()==[str(6+i)]*3
            assert page.locator('[data-comparison-count]').all_text_contents()==[str(6+i)]*2
        page.goto(base+'/results.html',wait_until='networkidle')
        for key in ['transfer','heldout','direct','external','excluded','coverage']:
            actual=page.locator('#table-'+key+' tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.children].map(c=>c.textContent))')
            assert actual==tables[key]['rows'],key
        assert page.locator('#table-external tbody tr').count()==17
        page.goto(base+'/programs.html',wait_until='networkidle')
        for i in range(3):
            page.locator(f'#program-tab-{i}').click()
            expect(page.locator(f'#program-example-{i}')).to_be_visible()
            assert page.locator('.program-example:visible').count()==1
            panel=page.locator(f'#program-example-{i}')
            for img in panel.locator('img').all(): assert img.evaluate('(img)=>img.decode().then(()=>img.naturalWidth>0)')
            id=['profile-guitar-string-count','steered-marked-articulation-search','feedback-breach-relevel-depth'][i]
            world=json.loads((ROOT/'data/worlds'/f'{id}.json').read_text())
            expect(panel.locator('blockquote p')).to_have_text(world['samples'][0]['question'])
            code='\n\n'.join(panel.locator('pre code').all_text_contents())
            for item in manifest['excerptsAndImages']:
                if item.get('world')==id: assert item['text'] in code
        page.locator('#program-tab-2').focus();page.keyboard.press('ArrowRight')
        expect(page.locator('#program-tab-0')).to_be_focused()
        page.locator('#program-example-0 .instance-strip a').first.click()
        page.wait_for_url('**/questions.html#world=*')
        expect(page.locator('#question-dialog')).to_be_visible()
        page.goto(base+'/programs.html')
        assert page.locator('.inverse-example').count()==5
        for route in ['/', '/programs.html', '/results.html']:
            page.goto(base+route,wait_until='networkidle')
            for width in [320,390,768,1024,1440]:
                page.set_viewport_size({'width':width,'height':844})
                page.evaluate('document.querySelectorAll(".paper-details").forEach(d=>d.open=true)')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(route,width)
                if route=='/programs.html':
                    for i in range(3):
                        page.locator(f'#program-tab-{i}').click()
                        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(route,width,i)
                page.evaluate('document.querySelectorAll(".paper-details").forEach(d=>d.open=false)')
            for width in [1440,390]:
                page.set_viewport_size({'width':width,'height':1000})
                page.screenshot(path=str(ROOT/f'artifacts/story-{route.strip("/").replace(".html", "") or "home"}-{width}.png'),full_page=True)
        assert not errors,errors
        browser.close()
    print('PASS: paper order; live method instances; exact source/table bindings; all program tabs and gallery links; five inverse walkthroughs; 320–1440px layouts; no JS errors.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8767');main(parser.parse_args().url.rstrip('/'))
