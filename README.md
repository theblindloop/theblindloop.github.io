# BlindLoop public website

A static academic project page based on the [Nerfies website template](https://github.com/nerfies/nerfies.github.io), with a custom question explorer.

The questions lead: a clickable 72-image header mosaic and six sample cards on
the main paper page. The complete searchable gallery lives on `questions.html`,
with a clear link from the preview. The method and results follow immediately
after the six samples; scrolling the main page never adds gallery cards.

The collection includes 2,439 replay-verified worlds, 7,317 unmodified
recorded images, original question/answer pairs, and generator/inverse source
files for inspection. It covers three discovery experiments, all nine discovery
profiles, and all five coding-agent configurations. It includes every replay-verified world except the explicitly disputed switchyard showcase. Three instances per world illustrate the collection; they are not a random sample or evidence of human validity.

The separate gallery page adds cards in batches of 48 as you scroll, with a Load more fallback. Filters search the entire catalog. Images load lazily, and full quiz records load only when opened, with a bounded cache. The header uses 72 distinct worlds.

## Preview

```sh
cd BlindLoopPublicWebsite
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765>. Use an HTTP server rather than opening `index.html`
directly: the explorer fetches JSON. No npm install or production build is needed.
Google Fonts is optional; all content and interactions work with system fonts
when offline. No analytics or inference requests are included.

## Editing

- `index.html`: paper sections, six sample cards, and in-place quizzes.
- `questions.html`: full gallery, filters, continuous loading, and quizzes.
- `steering.html`: dedicated 3×3 category explainer, recorded examples, and masking illustration.
- `content/steering-page.html`, `scripts/build_steering.py`, and `data/steering-examples.json`: explainer source, deterministic source joins, and sample provenance.
- `static/css/design.css`: typography and semantic result colors.
- `static/css/editorial.css`: numbered paper sections and the connected method illustration.
- `scripts/build_method_pixels.py` and `data/method-pixels.json`: exact original image rows and scene geometry used for the method demonstration; no research programs are executed.
- `static/fonts/`: locally hosted Inter variable font and its OFL license.
- `content/paper-sections.html`: editable method/results prose and section layout.
- `scripts/build_paper_content.py`: builds paper sections from manuscript tables and exact program excerpts; never executes research code.
- `data/paper-tables.json` and `data/paper-content-provenance.json`: table rows, manuscript labels/hashes, and excerpt/image provenance.
- `static/css/paper.css` and `static/js/paper.js`: responsive paper figures, tables, and accessible code-example tabs.
- `static/css/site.css`: base BlindLoop styling; `gallery.css` adds the question-first header, gallery, and quiz. `nerfies.css`/`bulma.min.css` retain the template base.
- `static/js/questions.js`: filters, quiz choices, instance switching, answer reveal, modal navigation, and share links.
- `scripts/build_mosaic.py`: generates the static clickable header from the selected question records; the importer runs it automatically.
- `data/site.json`: anonymous-submission-safe resource URLs and citation, if available. Empty entries are omitted. Author and affiliation rendering is intentionally absent.
- `data/featured.json`: the original 24 featured worlds and their display titles.
- `data/exclusions.json`: explicit disputed-world exclusions.
- `data/selection.json`: generated complete stable selection, with featured worlds first.
- `data/questions.json`: compact searchable catalog; `data/worlds/` holds full per-world records. Do not hand-edit the scientific fields.
- `static/questions/`: copied original images and source files as nonexecuting `.py.txt` documents.
- `PLAN.md`: initial scope and next steps.
- `docs/CONTENT_PROVENANCE.md`: claim sources and publication notes.

This is an anonymized submission site. Do not add project author names,
affiliations, author URLs, or identifying citations/resource links.

The resource configuration schema is:

```json
{
  "links": {"paper": "", "code": "", "data": "", "arxiv": ""},
  "bibtex": ""
}
```

## Import from the supplied research export

```sh
python3 scripts/expand_selection.py --export /path/to/BlindLoop_PaperExport
python3 scripts/import_questions.py --export /path/to/BlindLoop_PaperExport
python3 scripts/validate_data.py --export /path/to/BlindLoop_PaperExport
```

The importer reads the three normalized world/sample catalogues, selects only
replay-verified worlds and nonexcluded sample rows, keeps one prompt family per
world, and copies three file-distinct images. It preserves exact text, answers,
source IDs, and SHA-256 hashes. It checks program hashes against the source
catalogues. The export is never modified and imported programs are never run.

The `.py.txt` generator file is the original exported renderer module; it is
not relabeled as the abstract forward answer function. These are source excerpts
for reading, not complete runnable bundles. Full source releases can be linked
through `data/site.json` later.

## Refresh the paper sections

Edit `content/paper-sections.html`, then rebuild against the read-only manuscript:

```sh
python3 scripts/build_method_pixels.py --export /path/to/BlindLoop_PaperExport
python3 scripts/build_paper_content.py --paper /path/to/manuscript/iclr2027
python3 scripts/build_steering.py --paper /path/to/manuscript/iclr2027
```

The method graphic adapts the paper's two-program explanation. Three selected
worlds show exact forward/inverse excerpts with three recorded instances each.
The renderer-swap images are copied unchanged from the paper. Tables cover
both discovery experiments, evaluator coverage, model-feedback discovery,
human review, generated-world SFT, all 16 external benchmarks, direct training,
and profile exclusion. Detailed results expand in place. Paper navigation does
not trigger further gallery growth.

## Validation

Without the original export:

```sh
python3 scripts/validate_data.py
```

For browser checks, install the optional development tools in your preferred
Python environment, start the preview server, then run:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tests/browser_smoke.py
python3 tests/paper_content.py --url http://127.0.0.1:8765
python3 tests/design_and_steering.py --url http://127.0.0.1:8765
```

Screenshots are saved to ignored `artifacts/`. The data validator checks every shipped instance's image/question/answer binding. Browser checks exercise representative worlds across the collection and the explorer's major interactions.
They do not independently adjudicate scientific validity or reproduce campaigns.

## Deployment

The public repository is https://github.com/theblindloop/theblindloop.github.io.
GitHub Pages serves the root of `main` at https://theblindloop.github.io.
All local URLs are relative and support a project subdirectory. Keep `artifacts/`
and the original bulk export out of the release. Keep commit authorship under
the anonymous project account.

Website-template adaptations use CC BY-SA 4.0. Research asset licensing remains
separate; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Page organization

The homepage follows the paper's six results in order. Detailed examples live
on `programs.html`; complete tables and additional studies live on `results.html`.
The question gallery and image-steering explainer remain separate pages.
See [site structure and checkpoint](docs/SITE_STRUCTURE.md) for the content map,
build sources, and preserved pre-restructure tag.
