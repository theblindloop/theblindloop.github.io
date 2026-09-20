# Content provenance and publication notes

This version uses the supplied September 19, 2026 manuscript for the narrative. The manuscript
and export are read-only inputs. The page abstract is extracted verbatim from the manuscript, with LaTeX macros and punctuation rendered for HTML. `data/paper-abstract.json` records its source hash and exact text.

| Website content | Manuscript source |
| --- | --- |
| Title and method | Main title; `sec:worlds`, `sec:loop` |
| 1,301 / 1,331 replay outcome, 45 campaigns, 4.95/hour | `sec:profile-discovery`; `app:profile-replay`, `app:profile-yield` |
| 835 / 874 replay-verified request matches; broader 918 / 981 episode matches | `sec:support-steering-results`; `app:support-fidelity` |
| 21 / 252 panel-hard worlds, complete-panel definition | `sec:model-feedback-results`; `tab:model-feedback-summary` |
| Three base/SFT accuracy pairs and changes | `tab:sft-generated-transfer` |
| Human review 733 / 800 under current classification | `tab:human-review-outcomes`; `app:human-review-outcomes` |
| Verification and interpretation limits | `sec:worlds`; `sec:discussion` |

These figures are transcribed from the manuscript. Website data validation does
not independently reproduce campaign-level outcomes or resolve the manuscript's
remaining evidence requests. The adaptation changes are computed from unrounded
underlying scores, so subtraction of the displayed one-decimal accuracies may
differ by 0.1 points.

## Question selection

`data/selection.json` records all 2,439 eligible replay-verified worlds. One disputed switchyard world is excluded through `data/exclusions.json`. The original 24 illustrative worlds retain their friendly titles and lead the collection; remaining worlds are interleaved across experiments, profiles, and coding-agent configurations. Ordering is not random and must not support prevalence claims. Model-feedback worlds have no discovery profile assigned by this website.

Images are newly selected **recorded instances of those worlds**, not necessarily
the exact scene shown in the main-paper gallery. Their answers are joined from
their own sample rows, never copied from manuscript gallery captions. The
question explorer preserves verbatim exported questions, including their answer
formatting. Source filenames, paths relative to the export, sample IDs, and
SHA-256 hashes remain in `data/worlds/*.json` for traceability.

All shipped worlds have `replay_status=verified`; row-level exclusions are
omitted. Human admission is not inferred. The unresolved
`state_switchyard_replay` world is excluded from the showcase.

The source files contain generated research programs supplied for inspection.
The website never executes them and does not implement live world generation.

## Before publication

- Preserve submission anonymity: omit project authors and affiliations; use only submission-safe resource URLs.
- Supply research-asset release terms and an anonymous citation only if appropriate.
- Reconcile any changed paper counts against the owning semantic sections above.
- Retain the qualifications on support matching and classified human reviews.
- Do not add the disputed switchyard answer until adjudicated.
- Do not substitute the conditional/multisplit external score summaries for
  full-denominator single-checkpoint results.
- Review public names/versions of coding and evaluation models.

## Expanded paper sections

The paper source is read-only. `data/paper-tables.json` records manuscript source
files and semantic table labels. The builder extracts numerical rows directly,
expands model display macros, and produces accessible HTML tables. Prose and the
human-review table are transcribed from their owning sections. Source hashes,
exact excerpt line ranges, and copied figure hashes are recorded in
`data/paper-content-provenance.json`.

| Website section | Evidence owner |
| --- | --- |
| Two-program graphic and campaign flow | `sec:worlds`, `sec:loop`; Figures 1 and 2 |
| Three program demonstrations | Original exported `analytic_gold` and inverse functions for guitar string count, marked articulation search, and breach-relevel depth |
| Renderer-swap images and 45-trial findings | `app:inverse-mutation`; `fig:inverse-mutation-example` |
| 225-world code inspection | `app:inverse-anatomy`, `app:inverse-boundary`, `app:inverse-pipeline` |
| Generation counts by configuration | `tab:discovery-generation` |
| Steering fidelity and equal-count comparison | `sec:support-steering-results`, `app:support-fidelity`, `app:support-coverage` |
| Generation-model × evaluator scores | `tab:discovery-generator-evaluation-preview` |
| Scored response denominators | `tab:discovery-evaluator-detail` |
| Feedback outcomes and both evaluator groups | `tab:model-feedback-summary` |
| Human review and exclusion sensitivity | `tab:human-review-outcomes`, `app:human-review-outcomes` |
| Main SFT recipe and transfer | `app:sft-paired`, `tab:sft-generated-transfer` |
| Four-split external changes | `tab:sft-multisplit` |
| Single-checkpoint external scores | `tab:sft-external-full` |
| Additional training studies | `tab:sft-indistribution`, `tab:sft-direct`, `tab:downstream-profile-holdout` |

Four-split and single-checkpoint evidence remains separate; the conditional V*
denominator and DocVQA's ANLS metric are explicitly disclosed. Profile-exclusion
results retain the archived-membership caveat. No pending experiment is reported
as complete. Human-review outcomes retain the 19-label exclusion and its
sensitivity. Code demonstrations are illustrative source readings, not new
program executions or human validity judgments.

The retired growth-and-steering visual has not been restored. The page uses
numerical steering findings, responsive method graphics, and the paper's
existing renderer-swap images.

## Dedicated steering explainer and visual redesign

`steering.html` uses `app:support-protocol` and
`tables/support-fidelity-populations.tex` for definitions, thresholds, and
population counts. Category examples are joined by exact record ID between
`support_audit_replay.csv`, `support_replay_join.csv`, and the shipped world
records. Each category contributes two replay-verified worlds with complete,
stable measurements and matching requests. Selection favors higher category
stability and shorter original questions, then record ID. It is illustrative.
`data/steering-examples.json` records both source hashes and exact image hashes,
questions, answers, measured/requested categories, and scene counts.

The 3×3 grid contains schematic glyphs, not empirical support maps. Its labels
are world-level aggregates; the recorded displayed instance is not asserted to
have that individual scene category. The 8×8 masking widget is explicitly a
display-only illustration. No inverse program is run and no selected-probe
response is invented. Full-category measurement rules remain separate from
verification and acceptance.

The redesigned two-program figure switches among the original three guitar
instances and their recorded counts (6, 7, 8). Its enlarged bridge view references the original PNG. Brightness traces and run markers now use exact pixels from three editorially selected bridge rows. Scene computation is orange; pixel computation is
blue. Accuracy changes use green for positive values and red for negative
values, with signs/values retained. No scientific result was changed by styling.

## Pixel-level method illustration

`data/method-pixels.json` stores the recorded scene variables and RGB values
from three adjacent bridge rows in each of the original three guitar images.
The extraction script reads the source manifest and original images without
running the generated programs. The chosen crop/row coordinates use the recorded
scene geometry solely for the explanatory display; the actual inverse locates
the bridge independently from pixels. The website states this distinction.
The curve plots the mean of the three color channels along the central row;
the dashed threshold is 105, as in the source code. Contiguous dark runs are
counted on each of the three selected rows and match the recorded answers.
These display checks are not new campaign-level verification outcomes.

## Inverse-program walkthroughs

`inverse-programs.html` explains five selected original programs and reuses their shipped images and source files. Pseudocode is explanatory, not executable source. `data/inverse-examples.json` records image, program, and archived analysis hashes. The 250-world Sol (max) audit is separate from the paper’s 225-world review. Taxonomy counts group heuristic primary labels; they are not estimates for the entire collection. No candidate programs were executed.

## Method teaser and category gallery

`data/method-examples.json` binds three additional teaser worlds to original images, answers, source hashes, and AST-extracted forward functions. The browser switches saved records; it does not execute research programs. `data/steering-gallery.json` records 108 worlds, twelve per measured category, using the same completeness, stability, and request-match criteria as the steering explainer. Thumbnails are original question images, not measured support maps.

## Pixel measurements in the method teaser

`build_inverse_measurements.py` reads original PNG pixels and explicitly computes
source-informed display measurements: frame/color segmentation and four-connected
components for rings, band/marker row measurements at six checkpoint columns, and
least-squares circle fitting with marker centroids. It never imports or executes
candidate programs. All nine computed decisions are asserted against recorded
answers. `data/method-examples.json` stores measurements with image hashes. These
illustrations are not a new held-out verification result. Original images remain
unchanged; SVG masks and overlays visualize the extracted evidence.
