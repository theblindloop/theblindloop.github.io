# Website structure

Agreed September 20, 2026. The homepage carries the complete research story;
dedicated pages preserve detailed examples, tables, and analysis.

## Checkpoint

Before restructuring: commit `fed14d09`, annotated tag
`checkpoint-before-story-restructure-2026-09-20`. The checkpoint contains the
reviewed guitar figure and component descriptions. Both commit and tag use the
anonymous project identity.

## Homepage

- Opening mosaic, introduction, six playable questions, and abstract.
- 01 Motivation: why scene-derived answers alone do not establish pixel recoverability.
- 02 Method: interactive guitar, component definitions, generation loop.
- 03 Programs: a short explanation and three recorded guitar instances;
  link to the full program demonstrations.
- 04 Experiments and results, in manuscript order:
  1. Profile-conditioned collection growth.
  2. Image-support-steered discovery.
  3. Model evaluation.
  4. Model-feedback discovery.
  5. Human review.
  6. SFT and external benchmark transfer together.
- Limitations and available resources.

## Dedicated pages

- `questions.html`: complete searchable quiz gallery.
- `programs.html`: three forward/inverse code demonstrations, renderer-change
  test, 225-world source review, and five inverse-program walkthroughs. The
  separate 250-world audit is explicitly distinguished from the paper review.
- `steering.html`: 3×3 category explanation, masking demonstration, and 18 samples.
- `steering-gallery.html`: 108 measured-category worlds, 12 per category, linking to 324 original instances.
- `results.html`: all original tables, denominators, recipes, and additional
  studies in paper order. No detailed results were discarded.
- `inverse-programs.html`: retained for existing public links; its walkthroughs
  are also incorporated into `programs.html`.

## Content and builds

`content/paper-sections.html` holds homepage content.
`content/detailed-sections.html` holds dedicated-page content.
`build_paper_content.py` expands both from the same extracted table data and
source excerpts; `build_story_pages.py` writes the dedicated page shells.
Regenerate steering afterward to synchronize navigation.

The homepage model-accuracy chart is generated from the exact overall row of
the manuscript table. Original images, question/answer records, and code files
are reused without modification. No research program is executed.

Tests assert homepage result order, source and table identities, chart values,
all program tabs, gallery navigation, method interactions, and responsive layouts.
Old homepage verification/source-analysis anchors route to their new program-page
locations. Training and external-result anchors remain valid on the homepage.
