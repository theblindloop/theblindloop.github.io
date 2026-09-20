#!/usr/bin/env python3
"""Exercise real selection/reveal/navigation behavior in a served static site.

Run `python3 -m http.server 8765 --bind 127.0.0.1` first.
Requires the optional Playwright development dependency.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main(home):
    base = home + "/questions.html"
    worlds = json.loads((ROOT / 'data/questions.json').read_text())['worlds']
    catalogue = worlds
    worlds = [json.loads((ROOT / w['detail']).read_text()) for w in catalogue]
    total = len(worlds)
    output = ROOT / 'artifacts'
    output.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce', permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base, wait_until='networkidle')
        expect(page.locator('#explorer')).to_be_visible()
        expect(page.locator('#filter-count')).to_have_text(f'{total:,} of {total:,} worlds')
        expect(page.locator('.world-card')).to_have_count(48)
        expect(page.locator('#question-dialog')).to_be_hidden()
        page.locator('.world-card').first.click()
        expect(page.locator('#question-dialog')).to_be_visible()
        expect(page.locator('#recorded-answer')).to_be_hidden()
        page.locator('#option-buttons').get_by_role('button', name=worlds[0]['samples'][0]['answer'], exact=True).click()
        page.locator('#reveal-answer').click()
        expect(page.locator('#choice-status')).to_have_text('Your choice matches the recorded answer.')
        expect(page.locator('#answer-text')).to_have_text(worlds[0]['samples'][0]['answer'])
        page.locator('#next-sample').click()
        expect(page.locator('#recorded-answer')).to_be_hidden()
        expect(page.locator('#sample-label')).to_have_text('Instance 2 of 3')
        page.locator('#copy-link').click()
        assert '#world=' in page.evaluate('navigator.clipboard.readText()')
        page.locator('#enlarge-image').click()
        expect(page.locator('#image-dialog')).to_be_visible()
        page.keyboard.press('Escape')
        expect(page.locator('#image-dialog')).to_be_hidden()
        expect(page.locator('#enlarge-image')).to_be_focused()

        # Cross-check representative rendered instance bindings, including answer reset and sources.
        for world in worlds[:24] + worlds[48::137] + worlds[-1:]:
            page.goto(f'{base}#world={world["id"]}&sample=1')
            expect(page.locator('#world-title')).to_have_text(world['title'])
            expect(page.locator('#question-viewer')).to_be_visible()
            for i, sample in enumerate(world['samples']):
                page.get_by_role('button', name=f'Show instance {i + 1}', exact=True).click()
                expect(page.locator('#recorded-answer')).to_be_hidden()
                expect(page.locator('#question-text')).to_have_text(sample['question'])
                expect(page.locator('#question-image')).to_have_attribute('src', sample['image'])
                assert page.locator('#question-image').evaluate('(img) => img.decode().then(() => img.naturalWidth > 0)')
                page.locator('#reveal-answer').click()
                expect(page.locator('#answer-text')).to_have_text(sample['answer'])
            for program in world['programs'].values():
                response = context.request.get(f'{home}/{program["path"]}')
                assert response.ok and response.body()
        page.locator('#close-question').click()
        page.locator('#reset-filters').click()
        page.locator('#experiment-filter').select_option('model-feedback')
        expect(page.locator('#filter-count')).to_have_text(f'{sum(w["experiment"] == "model-feedback" for w in worlds):,} of {total:,} worlds')
        page.locator('#profile-filter').select_option('Tracing')
        expect(page.locator('#no-results')).to_be_visible()
        expect(page.locator('#question-viewer')).to_be_hidden()
        page.locator('#reset-filters').click()
        page.locator('#profile-filter').select_option('Tracing')
        expect(page.locator('#filter-count')).to_have_text(f'{sum(w["profile"] == "Tracing" for w in worlds):,} of {total:,} worlds')
        page.locator('#reset-filters').click()
        page.locator('#question-search').fill('nothing_matches_this_query')
        expect(page.locator('#no-results')).to_be_visible()
        page.locator('#reset-filters').click()
        page.locator('#generator-filter').select_option('Luna')
        assert int(page.locator('#filter-count').inner_text().split()[0].replace(',', '')) == sum(w['generator'] == 'Luna' for w in worlds)
        page.locator('#reset-filters').click()
        expect(page.locator('.world-card')).to_have_count(48)
        page.locator('.world-card').nth(6).click()
        expect(page.locator('#world-title')).to_have_text(worlds[6]['title'])
        page.locator('#next-question').click()
        expect(page.locator('#world-title')).to_have_text(worlds[7]['title'])
        page.locator('#previous-question').click()
        expect(page.locator('#world-title')).to_have_text(worlds[6]['title'])
        page.keyboard.press('Escape')
        expect(page.locator('#question-dialog')).to_be_hidden()
        expect(page.locator('.world-card').nth(6)).to_be_focused()
        page.goto(f'{base}#world={worlds[3]["id"]}&sample=3')
        expect(page.locator('#sample-label')).to_have_text('Instance 3 of 3')
        page.reload()
        expect(page.locator('#sample-label')).to_have_text('Instance 3 of 3')
        page.goto(base, wait_until='networkidle')
        page.evaluate('scrollTo(0,0)')
        page.screenshot(path=str(output / 'desktop-full.png'), full_page=True)
        page.screenshot(path=str(output / 'desktop-hero.png'))
        page.locator('#questions').evaluate('(e) => e.scrollIntoView({block: "start"})')
        page.screenshot(path=str(output / 'desktop-explorer.png'))
        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')

        # Narrow layouts and a long question must remain readable without page overflow.
        mobile = context.new_page()
        mobile.set_viewport_size({'width': 390, 'height': 844})
        mobile.goto(base, wait_until='networkidle')
        mobile.screenshot(path=str(output / 'mobile-full.png'), full_page=True)
        mobile.screenshot(path=str(output / 'mobile-hero.png'))
        mobile.goto(f'{base}#world=profile-linked-ring-panel&sample=2')
        expect(mobile.locator('#world-title')).to_have_text(next(w['title'] for w in worlds if w['id'] == 'profile-linked-ring-panel'))
        mobile.screenshot(path=str(output / 'mobile-long-question.png'))
        for width in [320, 390, 768, 1024]:
            mobile.set_viewport_size({'width': width, 'height': 844})
            assert not mobile.evaluate('document.documentElement.scrollWidth > innerWidth'), width
            assert mobile.locator('#question-dialog').evaluate('(e) => e.scrollWidth <= e.clientWidth'), width
        mobile.locator('#close-question').click()
        for width in [320, 390, 768, 1024]:
            mobile.set_viewport_size({'width': width, 'height': 844})
            assert not mobile.evaluate('document.documentElement.scrollWidth > innerWidth'), width
        # Fetch errors are visible and retry restores the explorer.
        failure = context.new_page()
        failure.route('**/data/questions.json', lambda route: route.fulfill(status=503, body='unavailable'))
        failure.goto(base)
        expect(failure.locator('#explorer-error')).to_be_visible()
        failure.unroute('**/data/questions.json')
        failure.locator('#retry-load').click()
        expect(failure.locator('#explorer')).to_be_visible()
        # The full collection is searchable without downloading full quiz records.
        lazy = context.new_page()
        details = []
        lazy.on('request', lambda request: details.append(request.url) if '/data/worlds/' in request.url else None)
        lazy.goto(base, wait_until='networkidle')
        assert not details
        expect(lazy.locator('.world-card')).to_have_count(48)
        lazy.locator('#load-more').evaluate('(e) => e.click()')
        expect(lazy.locator('.world-card')).to_have_count(96)
        lazy.locator('#question-search').fill(worlds[-1]['title'])
        assert lazy.locator('.world-card').count() > 0
        lazy.locator('#reset-filters').click()
        lazy.route('**/data/worlds/**', lambda route: route.fulfill(status=503, body='unavailable'))
        lazy.goto(f'{base}#world={worlds[-1]["id"]}&sample=3')
        expect(lazy.locator('#quiz-error')).to_be_visible()
        lazy.unroute('**/data/worlds/**')
        lazy.locator('#retry-question').click()
        expect(lazy.locator('#question-viewer')).to_be_visible()
        expect(lazy.locator('#sample-label')).to_have_text('Instance 3 of 3')
        expect(lazy.locator('#question-text')).to_have_text(worlds[-1]['samples'][2]['question'])
        lazy.locator('#next-question').click()
        lazy.locator('#previous-question').click()
        expect(lazy.locator('#question-viewer')).to_be_visible()
        expect(lazy.locator('#world-title')).to_have_text(worlds[-1]['title'])
        preview = context.new_page()
        preview.goto(home, wait_until='networkidle')
        expect(preview.locator('.world-card')).to_have_count(6)
        expect(preview.locator('.mosaic-tile')).to_have_count(72)
        expect(preview.locator('.filter-bar')).to_be_hidden()
        for target in ['#questions', '#abstract', '#method', '#training']:
            preview.locator(target).evaluate('(e)=>e.scrollIntoView()')
            expect(preview.locator('.world-card')).to_have_count(6)
        preview.locator('.gallery-invitation a').click()
        expect(preview).to_have_url(home + '/questions.html')
        expect(preview.locator('.world-card')).to_have_count(48)
        preview.locator('.site-nav .nav-links a[href="index.html"]').click()
        expect(preview.locator('#method')).to_be_visible()
        expect(preview.locator('.world-card')).to_have_count(6)
        preview.goto(home)
        preview.locator('.mosaic-tile').first.click()
        expect(preview.locator('#question-viewer')).to_be_visible()
        preview.locator('#close-question').click()
        preview.locator('#questions').screenshot(path=str(output / 'homepage-preview-desktop.png'))
        preview.set_viewport_size({'width':390,'height':844})
        preview.locator('#questions').screenshot(path=str(output / 'homepage-preview-mobile.png'))
        assert not preview.evaluate('document.documentElement.scrollWidth>innerWidth')
        assert not errors, errors
        browser.close()
    print('PASS: representative instance bindings, reveal reset, filters, all-world gallery, clickable mosaic, quiz options, next/previous question, clipboard, deep links/reload, modal/keyboard, source links, fetch retry, and responsive overflow checks.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    main(parser.parse_args().url.rstrip('/'))
