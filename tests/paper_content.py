#!/usr/bin/env python3
"""Validate source excerpts, table bindings, navigation and responsive paper sections."""
import argparse
import hashlib
import json
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
        page.goto(base+'/#method',wait_until='networkidle')
        expect(page.locator('#method')).to_be_visible()
        assert page.locator('.world-card').count()==6
        page.locator('#method').screenshot(path=str(ROOT/'artifacts/paper-method-desktop.png'))
        for key in ['transfer','heldout','direct','external','excluded','coverage']:
            actual=page.locator('#table-'+key+' tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.children].map(c=>c.textContent))')
            assert actual==tables[key]['rows'],key
        assert page.locator('#table-external tbody tr').count()==17
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
        expect(page.locator('#program-example-0')).to_be_visible()
        page.locator('#programs').screenshot(path=str(ROOT/'artifacts/paper-programs-desktop.png'))
        page.locator('#program-example-0 .instance-strip a').first.click()
        expect(page.locator('#question-dialog')).to_be_visible()
        expect(page.locator('#question-viewer')).to_be_visible()
        page.locator('#close-question').click()
        expect(page.locator('#program-example-0 .instance-strip a').first).to_be_focused()
        page.wait_for_url('**/#programs')
        page.locator('#verification').screenshot(path=str(ROOT/'artifacts/paper-verification-desktop.png'))
        page.locator('#training').screenshot(path=str(ROOT/'artifacts/paper-training-desktop.png'))
        page.locator('#external').screenshot(path=str(ROOT/'artifacts/paper-external-desktop.png'))
        for width in [320,390,768,1024,1440]:
            page.set_viewport_size({'width':width,'height':844})
            page.evaluate('document.querySelectorAll(".paper-details").forEach(d=>d.open=true)')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),width
            for i in range(3):
                page.locator(f'#program-tab-{i}').click()
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,i)
            page.evaluate('document.querySelectorAll(".paper-details").forEach(d=>d.open=false)')
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#method').screenshot(path=str(ROOT/'artifacts/paper-method-mobile.png'))
        page.locator('#programs').screenshot(path=str(ROOT/'artifacts/paper-programs-mobile.png'))
        page.locator('#training').screenshot(path=str(ROOT/'artifacts/paper-training-mobile.png'))
        page.locator('#external').screenshot(path=str(ROOT/'artifacts/paper-external-mobile.png'))
        assert not errors,errors
        browser.close()
    print('PASS: exact code excerpts and hashes; table bindings; three accessible program tabs; quiz links; paper navigation; all expandable tables and code panels fit 320–1440px.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8767');main(parser.parse_args().url.rstrip('/'))
