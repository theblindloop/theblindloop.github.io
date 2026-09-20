"""Build dedicated reading pages from shared, source-bound paper content."""
import re

def build_story_pages(root, detailed):
    pieces=re.split(r'(?=<section class="section paper-section)',detailed)
    sections={re.search(r'id="([^"]+)"',p).group(1):p for p in pieces if p.strip()}
    index=(root/'index.html').read_text()
    head=index[:index.index('</head>')]
    head=re.sub(r'<script[^>]*src="static/js/(questions|site)\.js"[^>]*></script>','',head)
    # Program links open the existing gallery; dedicated pages do not need a second quiz UI.
    nav='''<nav class="site-nav" aria-label="Main navigation"><a class="wordmark" href="index.html">BlindLoop</a><div class="nav-links"><a href="index.html#method">Overview</a><a href="questions.html">Questions</a><a href="programs.html">Programs</a><a href="steering.html">Steering</a><a href="results.html">Detailed results</a></div></nav>'''
    def write(name,title,lead,body,extra=''):
        h=re.sub(r'<title>.*?</title>',f'<title>{title} · BlindLoop</title>',head,flags=re.S)
        body=re.sub(r'href="#world=', 'href="questions.html#world=',body)
        body=body.replace('href="#method"','href="index.html#method"')
        (root/name).write_text(h+extra+'</head><body class="reading-page"><a class="skip-link" href="#main">Skip to content</a>'+nav+f'<main id="main"><header class="reading-page-intro container site-width"><a href="index.html">← Project overview</a><h1>{title}</h1><p>{lead}</p></header>'+body+'</main><footer class="reading-footer"><a href="index.html">Project overview</a> · <a href="THIRD_PARTY_NOTICES.md">Third-party notices</a></footer></body></html>')
    results=''.join(sections[k] for k in ['results','human-review','training','external'])
    write('results.html','Detailed experiments and results','Full tables, denominators, and additional analyses, in the same order as the paper.',results)
    inverse=(root/'inverse-programs.html').read_text()
    inverse=inverse[inverse.index('<div class="inverse-pipeline"'):inverse.index('<footer class="inverse-foot"')]
    program=sections['programs']+sections['verification']+sections['source-analysis']
    program=program.replace('href="inverse-programs.html"','href="#inverse-walkthroughs"')
    program+='<section class="section" id="inverse-walkthroughs"><div class="container site-width inverse-wrap"><h2>Five inverse programs, step by step</h2>'+inverse+'</div></section>'
    write('programs.html','Programs behind the questions','Inspect the two answer programs, test the role of pixels, and follow five inverse computations from image to decision.',program,'<link rel="stylesheet" href="static/css/inverse.css">')
