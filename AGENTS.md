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
