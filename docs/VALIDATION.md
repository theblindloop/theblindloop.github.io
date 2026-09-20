# Local validation

Validated September 19, 2026.

- Full collection: 2,439 replay-verified worlds and 7,317 recorded instances, covering three experiments, nine profiles, and five coding-agent configurations. The disputed switchyard world remains excluded.
- Source integrity: all 7,317 original PNGs and 4,878 program files match their export SHA-256 hashes. Every shipped question/answer pair matches its source sample row; selected rows are nonexcluded and use one prompt family per world.
- Regeneration: selection ordering and the 72-world header reproduce byte-for-byte. Website code passes whitespace checks; original research text retains its source whitespace to preserve hashes.
- Catalog integrity: compact summaries match full per-world records and detail hashes. Local HTML links and IDs validate.
- Chromium: representative worlds throughout the collection (including all original featured worlds) exercise three-instance bindings, answer reset, choices, filters, next/previous navigation, deep links, clipboard, keyboard focus, source links, and image enlargement.
- Scale behavior: initial 48 cards and zero per-world detail fetches; additional card batches; whole-catalog search; deep links into the end of the collection; detail-fetch failure and retry; rapid question navigation.
- Responsive checks: no page or dialog overflow at 320, 390, 768, 1024, and 1440 pixels. Desktop header/gallery and mobile quiz screenshots inspected.
- Imported program text scan found no email addresses, GitHub URLs, home-directory paths, or recognizable API-key patterns. Author and affiliation rendering remains absent.

Run `python3 scripts/validate_data.py --export /path/to/BlindLoop_PaperExport` and `python3 tests/browser_smoke.py --url http://127.0.0.1:8766` with the static server running. Screenshots are ignored under `artifacts/`.

The static website occupies approximately 151 MB of file content (excluding Git history and local test artifacts); the searchable catalog is approximately 2.25 MB. Filesystem allocation can be larger because the collection contains many small files. No deployment was performed. These checks establish faithful transport and UI behavior, not independent scientific validity.

## Expanded method and results

- Inspected the paper's two method figures, then adapted their information flow into responsive HTML graphics.
- Exact code excerpts and all three renderer-swap image hashes pass provenance checks; imported programs are not executed.
- Paper tables are generated directly from their labeled manuscript rows. The human-review counts and source-analysis summary are transcribed separately.
- Browser checks verify table/data bindings, keyboard-accessible example tabs, original question text, recorded images, quiz links, and navigation.
- All expandable tables and code examples remain inside the page at 320, 390, 768, 1024, and 1440 pixels. Wide tables scroll independently on phones.
- Desktop method, code, verification, and training graphics and mobile layouts were rendered and inspected.

Run `python3 tests/paper_content.py --url http://127.0.0.1:8767` for these checks.

## Separate collection page

The main page now displays exactly six cards and never appends cards while
scrolling. `questions.html` retains the full catalog, filters, 48-card batches,
quiz navigation, and deep links. Browser checks cover gallery-to-paper navigation,
header quizzes, the preview link, both pages' assets/IDs, and responsive renders.
The earlier single-page full-gallery layout has been replaced at the user's request.

## Typography, method figure, and steering page

- Locally hosted Inter font; larger paper headings/body text; original header composition retained.
- Source-checked 18 question/image/answer examples across nine measured categories.
- Browser-tested all three method instances, all nine category selectors, 64 mask positions, reset behavior, and links into the full quiz gallery.
- Checked positive/negative result-cell classes against their numerical changes.
- All three pages pass local-link/ID checks; method and steering sections pass overflow checks at 320–1440px, including expanded details.
- Desktop and mobile renders of the new figure, category matrix, masking illustration, and colored results were inspected.

Run `python3 tests/design_and_steering.py --paper /path/to/manuscript/iclr2027` against the local preview to include the original category-record checks.

## Editorial layout and connected method figure

The latest pass removes repeated centered section intros and rounded prose
cards from the paper page. Its method illustration now includes actual scene
variables, an SVG enlargement of original bridge pixels, RGB brightness curves,
three-row run counts, and responsive connectors. Exact display pixels are
checked against the unchanged PNGs; original questions/answers remain intact.
The six homepage cards use ordinary layout to prevent offscreen size estimates
from shifting the method section while navigating. Desktop/mobile figures and
numbered section layouts were inspected. Gallery and paper interaction checks
still pass.
