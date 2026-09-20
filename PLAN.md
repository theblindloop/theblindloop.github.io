# BlindLoop website plan

First version implemented and locally verified on September 19, 2026.
See `docs/VALIDATION.md` for the completed checks. Publication metadata and
deployment remain separate next steps.

## First version

A question-first academic project page based on the Nerfies website: a clickable
72-image header mosaic surrounding the paper title, followed immediately by the
six-card preview linking to the separate 2,439-world gallery at `questions.html`. The abstract, method, results, and credits follow the bounded preview.
Use its Bulma layout and typography with restrained blue accents. No build
framework or backend is required; the site can be served by GitHub Pages.

The main custom component is a question explorer. Readers can filter by
experiment, discovery profile, and coding-agent configuration, search question
text, inspect an uncropped image, switch between three recorded instances,
choose an answer, reveal the recorded answer, and inspect the image-only solution source.
All eligible worlds are searchable, with continuous gallery loading in batches of 48. Each opens
in a focused quiz dialog with next/previous question navigation; closing it
returns to the gallery without losing the reader's position or filters.
Keep each image, original question, and answer together. Deep links identify a
world and instance. Images can be enlarged without cropping.

## Content and evidence

- Read the current manuscript for the narrative and canonical terminology.
- Import selected replay-verified worlds from the supplied paper export.
- Include all nine discovery profiles and all three discovery experiments.
- Keep exact wording, recorded answers, stable record IDs, and image hashes.
- Selection illustrates the collection; it is not a random sample or a new
  estimate of difficulty, human validity, or prevalence.
- Exclude quarantined samples and the unresolved state-switchyard showcase.
- Distinguish acceptance, replay, model evaluation, and human review.
- Describe support as masking sensitivity; feedback results are descriptive.
- Use the main paired adaptation results; defer unreconciled pooled claims.

## Implementation sequence

1. Initialize an independent Git repository and preserve template attribution.
2. Add a deterministic import script and an explicit selection manifest.
3. Populate the academic page and accessible, responsive explorer.
4. Verify imported hashes, question-answer binding, filters, sample switching,
   answer reveal, deep links, source links, and empty/error states.
5. Inspect desktop and mobile browser renders; document local preview commands.

## Publication details still needed

This is an anonymized submission. Author names, affiliations, and author URLs
are intentionally omitted and must not be added. Remaining details are
submission-safe paper/code/dataset URLs, an anonymous citation if needed, and
release/licensing decisions for research assets. Keep these
in a configuration file and omit unconfigured links instead of inventing URLs.
The first scaffold is local; creating a GitHub remote and deploying are separate
steps. No private export directory, logs, credentials, or bulk archives belong
in the website repository.

## Expanded paper content

Implemented: responsive method and campaign graphics, three cherry-picked
forward/inverse source demonstrations, renderer-swap evidence, source analysis,
all main experimental results, and detailed SFT/benchmark tables. Definitions
precede technical discussion, and detailed studies expand below their summaries.

## Later additions

Consider client-side renderers only after reviewing their dependencies and
checking that browser output matches the recorded images and answers.
