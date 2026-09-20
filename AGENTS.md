# BlindLoop public website

Keep the Nerfies academic-paper layout requested by the author. Maintain
attribution and third-party notices. Do not add analytics by default.

Questions remain prominent: keep the clickable header mosaic and six sample
cards on the main page, followed by a clear link to `questions.html`. The full
searchable collection lives on that separate page. Do not add infinite gallery
scrolling to the main page; method and results must stay easy to reach. The
quiz dialog keeps original images, questions, choices, and answers together.

The sibling research manuscript's PAPER_STRUCTURE.md defines scientific
terminology and evidence boundaries. Never change the manuscript or export
while working on this website. Never use internal campaign numbering in
reader-facing content. Keep verbatim questions and original image pixels.

Use `scripts/import_questions.py` to regenerate selected website assets.
Use `scripts/expand_selection.py` to rebuild the complete selection; edit featured titles and exclusions through `data/featured.json` and `data/exclusions.json`. Retain source record IDs and
SHA-256 hashes. Exclude quarantined examples and unresolved disputed showcases.
Do not execute imported research programs; they are text for inspection.

Before delivery, run the data validator and browser checks, and inspect desktop
and mobile screenshots. Never infer human approval from automated verification.
Configure publication details in `data/site.json`; do not invent author lists,
publication status, URLs, citations, or research licenses.

This is an anonymized submission website. Do not include project author names,
affiliations, author URLs, or identifying publication metadata. Author omission
is intentional, not a missing task. Only add submission-safe resource links.

## Website narrative and presentation

Use conventional main headings: Introduction, Method, Experiments and Results,
and Limitations. Follow the paper’s six-experiment order within Results.
The inverse-program analysis belongs under Collection Growth, not in its own
numbered homepage section. Its homepage summary contains three recorded guitar
images, what the inverse program does, the principal findings, and one button
to the dedicated analysis. Keep the detailed tables and walkthroughs there.
Use the manuscript abstract without its redundant project-page sentence.
Use plain academic English and define technical terms before relying on them.
Keep the 225-world paper analysis distinct from the supplementary 250-world audit.
Show model accuracy as a table, not progress-style bars. Preserve the
side-by-side forward/image/inverse comparison on phones.
Shared navigation is maintained by scripts/sync_navigation.py; reading.css
loads last and provides common reading styles across all seven pages.
Run tests/site_consistency.py after cross-page changes.
