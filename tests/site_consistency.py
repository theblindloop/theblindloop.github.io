"""Cross-page navigation, narrative placement, links, and responsive layout."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PAGES=['index.html','questions.html','programs.html','results.html','steering.html','steering-gallery.html','inverse-programs.html']
BASE='http://127.0.0.1:8767/'
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page()
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    navigation=None
    for route in PAGES:
        page.goto(BASE+route,wait_until='networkidle')
        links=page.locator('.site-nav .nav-links a').evaluate_all('(es)=>es.map(e=>[e.textContent,e.getAttribute("href")])')
        if navigation is None:navigation=links
        assert links==navigation,route
        assert page.locator('.site-nav [aria-current="page"]').count()==1,route
        assert page.locator('h1').count()==1,route
        assert page.locator('link[href="static/css/reading.css"]').count()==1,route
        for width in [320,390,768,1440]:
            page.set_viewport_size({'width':width,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(route,width)
            if width in [390,1440]:
                page.screenshot(path=str(ROOT/f'artifacts/review-{route[:-5]}-{width}.png'),full_page=True)
        for href in page.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
            u=urlsplit(href)
            if u.scheme or u.netloc or not u.path or not u.path.endswith('.html'):continue
            assert (ROOT/unquote(u.path)).exists(),(route,href)
    page.goto(BASE)
    assert page.locator('main>.paper-section').evaluate_all('(es)=>es.map(e=>e.id)')==['motivation','method','results','limitations']
    assert page.locator('#generation #programs img').count()==3
    assert page.locator('#generation #programs .inverse-summary-button').count()==1
    assert page.locator('#generation #programs table').count()==0
    assert page.locator('.accuracy-track').count()==0
    assert 'Project page:' not in page.locator('#abstract').inner_text()
    assert not errors,errors
    browser.close()
print('PASS: seven pages; consistent navigation; narrative placement; responsive layouts; local page links; no JavaScript errors.')
