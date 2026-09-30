# Design of record: the product page (R9-WEB-1, R9-WEB-2)

tvofi, 2026-09-30:
- "Design a full product web page, based on the user facing documentation in the repo, in the same design language as
  the showcase page, then make a rev 4.2 of the plan where implementation of this page and pining it to the master
  documentation is added."
- Pinning: "test-pinned + linked". Hosting: "GitHub Pages via workflow".

`index.html` is the page. It is built only from the reader documents at origin/main `5dfa6684`, and every sentence of
fact on it is quoted from one of them. It passes again at `aac8fb77` (#1794), which touched no reader document. Other files:
- `check_site.py`: the pin prototype that R9-WEB-1 ports into `tests/doc_claims.py`.
- `controls.py`: its planted-error controls. `SITE-CHECKS.txt` is their output: baseline green, 15 controls red.
- `contrast.py`: measures every colour pair. `CONTRAST.json` is the result: 32 pairs, all passing in both themes.
- `shots.mjs`: renders `shots/page-{light,dark}-{1280,390}.png` and checks there is no horizontal overflow, no page
  error, and that the theme toggle and the gallery tabs work.

## Decisions taken in the design

- **S1. The page sits at `docs/index.html`.** Page-owned assets go in `docs/site/`. Relative image paths such as
  `img/card-plan-chart.png` and `setup/01-first-screen.png` then resolve identically in the tree and on Pages, so the
  pin checks the same paths a reader loads.
- **S2. Every claim is quoted, not paraphrased.** A product page is where the round-6 stale-prose class would live
  longest: nothing reads it, and it is written to persuade. So the page makes no claim the README or the docs do not
  make in the same words (see "Claim rules").
- **S3. No savings percentage.** The only percentages in the docs (`docs/how-it-works.md`, comfort-weight table) are "a
  one-off measurement on the author's house, not a test-pinned guarantee", and `DISCLAIMER.md` says every saving is a
  model estimate. The page quotes that disclaimer instead. If tvofi wants the figure, it goes in a note labelled as that
  one-off measurement, pinned like any other claim.
- **S4. No third-party request.** Outfit (600, 700) and Source Sans 3 (400, 600) are self-hosted: the latin subset as
  woff2, about 60 KB in all, with their OFL texts, taken from the `@fontsource` packages. There are no analytics, no
  cookies and no CDN. `localStorage` holds only the theme choice, and every access is in try/catch.
- **S5. The page states no version** (CLAUDE.md rule 4). Deploying on release tags keeps it matched to what HACS
  installs (S6).
- **S6. Deploy on release, not on every merge.** `release.yml` runs on `push: tags v*`, and the stamp pushes that tag
  over the deploy key, so a Pages workflow on the same trigger fires. It publishes the page as of the release HACS
  users install, and `workflow_dispatch` covers a re-deploy.

## Anatomy

The showcase's system throughout:
- tokens frost `#f3f8fc` / ink `#0f2233` / slate `#4d5d6c` / fjord `#026aa8` / ember `#b4501a` (text) and `#d2601f`
  (mark), with the dark set under `prefers-color-scheme` and a `data-theme` toggle;
- Outfit for display, Source Sans 3 for body;
- the dusk mark as an inline symbol;
- 12 px surfaces, eyebrow labels, a 74 rem column.

| # | section | content | source |
|---|---|---|---|
| 1 | top bar | mark, wordmark, section links (hidden under 860 px), theme toggle, GitHub | none |
| 2 | hero | h1 "As warm as you asked, bought in better hours." (ember on the second phrase); the lede; CTAs; the plan chart on a stage (a 375 px render under 600 px, dark renders in dark); its caption | README intro |
| 3 | tiles | 24 h, 30 min, 20 h, EN·SV, in the card's stat-tile style | key-phrase claims |
| 4 | features | nine cards, h3 = the README bold lead verbatim | README "What it does" |
| 5 | how it works | the lane-UI figure (light and dark); three steps quoted from the README's sequence diagram | README "How it works" |
| 6 | the card | README paragraph; YAML; a tabbed gallery (Advisor, Hot water by weekday, Weekday options) | README "Dashboard card", `docs/dashboard-card.md`, `docs/configuration.md` |
| 7 | works with | prices, weather, sensors; the control-path table (cards under 640 px) | README "Requirements", "Supported heat pumps and controls" |
| 8 | get started | the HACS steps; requirements; "Immediately"; setup screenshots 01, 03, 04, 08 | README "HACS", "Requirements", "Your first week"; `docs/setup.md` |
| 9 | limits | six limits; the savings disclaimer | README "Known limitations"; `DISCLAIMER.md` |
| 10 | written with AI | a quote and two sentences | README "Written with AI" |
| 11 | documentation | one card per row of the README Documentation table | README "Documentation" |
| 12 | footer | links; acknowledgement; disclaimer line | README "Acknowledgement"; `DISCLAIMER.md` |

Interaction:
- The gallery is an ARIA tablist with arrow-key navigation.
- The theme toggle rewrites the `<source media>` of each picture, so an explicit theme also swaps the renders.
- Tab targets are at least 40 px tall, and the buttons 46 px.

## Claim rules (what the pin enforces)

- **A claim** is an element with `data-src="<reader doc>#<GitHub heading slug>"`. The section runs from that heading
  to the next heading of level ≤ max(own, 2), so the title's section is the intro.
- **Verbatim mode** (the default): every text node inside the element, split on "…", must appear in the section's
  reader text. Reader text is the markdown with emphasis, code ticks, link syntax and HTML tags dropped, image alt text
  kept, whitespace and quote marks normalised, and case ignored.
- **Key-phrase mode** (`data-q`): for tiles, whose short labels are page copy. `data-q` must appear in the section, and
  every number in the element must be a number the section states.
- **`data-copy`** marks page copy that states no fact: panel labels, the YAML line, the "Every sentence…" line, link
  lines. The arm counts these and reports the count.
- **Refused:**
  - a digit in visible text outside any claim or `data-copy`;
  - a `data-repo` image not in the tree, or an image without alt text;
  - a link into `github.com/tvofi/heatpump_optimizer/blob/main/` whose path or heading slug does not resolve;
  - any third-party script, stylesheet, CSS `url()` or `@import`, or image;
  - the stamped `VERSION`, or a `vX.Y.Z` literal.
- **Two-sided:**
  - every README "What it does" bold lead is a `data-feature` heading on the page, and nothing else is;
  - the page's `data-doc` set equals the README Documentation table's link targets.
  - So a later PR that adds a feature paragraph or a docs row to the README is forced to add it here, and one that
    removes it is forced to remove it.
- **Anchor:** no page, zero claims, zero features or zero docs rows is red.

Measured on the design (`SITE-CHECKS.txt`):
- 47 claims, 108 verbatim fragments, 3 key-phrase numbers, 9 features, 9 docs rows, 11 images, 14 repository links.
- Red on each of: a wrong number, a reworded quote, a dead slug, a dropped feature, an extra or missing docs row, a
  number outside a claim, a version literal, a missing image, an external script, a third-party stylesheet or font URL,
  a README sentence changed under an unchanged page, and both anchors.

## Implementation map (R9-WEB-1)

| design | repository |
|---|---|
| `index.html` | `docs/index.html`: image `src` becomes the `data-repo` path relative to `docs/`; the `a/` folder and the design note go; `data-repo` stays as the pin's handle |
| `fonts/*.woff2`, `fonts/OFL-*.txt` | `docs/site/fonts/` |
| hero render | `docs/img/card-plan-chart.png`, the README hero path, regenerated by R9-UI-4's hero mode (a 375 px render only if UI-3's page-screenshot mode produces one; otherwise one `<img>`) |
| how-it-works figure | the `docs/img/readme/` files R9-UI-2 lands (the design's `PENDING` map names them; the port carries no such map) |
| `check_site.py` | one new function in `tests/doc_claims.py` with its anchor, reading `docs/index.html` from the working tree and the corpus from the working tree (never a git ref); its docstring entry names the arm |
| `controls.py` | the PR body's planted-error table, run at the head |

Other changes in the same PR:
- The README gains a "Product page" row in its Documentation table (a link to `docs/index.html` until WEB-2 serves
  it) and one line under the badges.
- `tests/closure.py`: `docs/index.html` and `docs/site/` go on `INERT_EXCEPT`, since the arm reads the page and
  `docs/site/fonts` only by path existence.
- `tests/layout.json` gets one category glob for `docs/index.html` and `docs/site/**`.
- The `doc_claims.py` closure is re-recorded by the autofix bot, not by hand.

## Hosting (R9-WEB-2)

`.github/workflows/pages.yml`:
- `on: push: tags: ["v*"]` and `workflow_dispatch`;
- `permissions: contents: read, pages: write, id-token: write`;
- `concurrency: pages`.

One job checks out the tag and stages `_site/` with shell only:
- `docs/index.html`;
- `docs/site/**`;
- every `*.png` and `*.svg` under `docs/`, keeping its path;
- never a `.md`.

Then it runs the upload and deploy actions, pinned by the repository's convention.

Rules for the workflow:
- It runs no repository script, so `codeowners_gap.py`'s enforcement surface does not grow; the harness is re-run to
  show that.
- Because it stages by pattern, the moves R9-RO-3 makes need no workflow edit.
- The served URL replaces the file link in the README row.
- tvofi sets Settings → Pages → Source: "GitHub Actions" once, before the first dispatch.

## Gallery slots (filled by later groups, in the same PR as their screenshots)

The pin forces these only indirectly: a slot's caption must be quoted from the page's documented section. U5 (rev 4.1)
makes each card PR regenerate its screenshots, and rev 4.2 adds the gallery slot to the same PR.

| slot | group | image (UI-3's page-screenshot mode) | caption source |
|---|---|---|---|
| Plan | R9-UI-4 (already the hero) | the hero | README "Dashboard card" |
| Why now, why not | R9-UX-1 | Plan tab with the idle tooltip | `docs/dashboard-card.md`, the UX-1 section |
| Advisor inbox | R9-UX-2 | replaces today's Advisor slot | that page's section |
| Health | R9-UX-3, R9-UX-7 | Health tab | that page's section |
| Savings and replay | R9-UX-6 | Savings tab | "The savings page" |

## Must keep working

- The README's HACS rules in `tests/entities.py`:
  - mermaid only inside details blocks;
  - no relative `<img>`;
  - the hero line pinned to `docs/img/card-plan-chart.png`;
  - the HA floor matching `hacs.json`;
  - the counts.
- `tests/md_tables.mjs` on the README row.
- Every existing `tests/doc_claims.py` arm.
- `tests/README.md` is not edited: it is code-owned and in the F11.4/F11.5 lane. If `entities.py` demands a line
  there, the PR stops and the orchestrator orders it after F11.5.

## Documentation sub-pages (rev 4.3, R9-WEB-3)

tvofi, 2026-09-30: "The docs should also be adopted to sub pages, if that is not unfeasible."

It is feasible and cheap:
- **What the docs use.** The reader docs use a small markdown subset: tables, fenced code, eight mermaid diagrams, one
  `[!IMPORTANT]` callout, three `<details>` blocks, images and relative links. There is no maths and no footnotes.
- **The parser is already in the repository.** It vendors markdown-it 14.1.0 at `.claude/workflows/vendor/`, used by
  `render_md.mjs` and `tests/md_tables.mjs`, so rendering needs no new dependency.

Files:
- `docs_build.mjs`: the generator prototype.
- `docs.css`: the sub-page design.
- `docs_controls.py` and `DOCS-CHECKS.txt`: the planted-error controls and their output.
- `docs_shots.mjs` and `docs_shots/`: the renders.

The artifact serves the product page with all nine sub-pages beside it.

### Decisions

- **S7. Built at deploy, never committed.** The Pages workflow renders the pages from the release tag's markdown. No
  generated HTML is tracked, so no doc-touching PR owes a regeneration: there are about a dozen such PRs left in
  round 9. A page cannot drift from its source, because it is re-made from it. The PR-time guard is the build itself,
  run by one new `tests/doc_claims.py` arm into a temporary directory; every FAIL line it prints fails the arm.
- **S8. GitHub's heading slugs.**
  - Every existing anchor, in the docs, in the README and on the product page, keeps working.
  - A link to another published doc becomes its page. A link to any other tracked file becomes a GitHub link. A link
    to nothing is an error.
- **S9. Which documents.** The set is derived, not listed:
  - the README, as "Overview (README)", because it holds the entity and service reference;
  - every row of the README Documentation table, except `EXCLUDE`, which today holds only `docs/backlog.md` (an
    archive that R9-RO-4 archives; the product page links it on GitHub).

  This is two-sided. A new row is built. A row whose file is missing fails. An `EXCLUDE` entry that is no longer a
  row fails.
- **S10. Mermaid.**
  - It is one self-hosted UMD file (`mermaid.min.js`), installed at deploy by `npm ci` from a lockfile beside the
    generator: the `tests/pwlane` precedent, #1548.
  - It loads only on the four pages that draw a diagram, and redraws in the other theme on toggle.
  - It is never tracked, and there is no CDN.
- **S11. No third-party request.** README badges render as their words in a chip, and external links stay links.

### Anatomy

Every page has the same parts:
- the top bar: Overview, Documentation, Get started, the theme toggle and GitHub;
- a docs rail on the left, ordered as the README table orders the docs, with the current page marked;
- one reading column of about 76ch;
- "On this page" on the right, listing the h2s, from 1180 px on pages with three or more.

Under 900 px the rail folds into a "Documentation" menu above the text. Each page ends with previous and next links
and "Rendered from docs/x.md, which is the source of truth". Rendered markdown takes styled parts only from the
generator:
- tables in a scroll box;
- callouts with an ember rule and label;
- single-image paragraphs as white figures;
- `<details>` as surfaces;
- code in the well colour;
- heading anchors that appear on hover.

### Measured on the docs at `aac8fb77`

- 9 pages built, `docs/backlog.md` excluded.
- 51 links between pages, 39 anchors verified, 20 GitHub links, 20 images, 4 badges rendered as text, 8 diagrams.
- `docs_shots.mjs`: every page at 1280 and 390 px, light and dark, with no overflow, no page error, every image
  loading and every diagram drawn.
- `DOCS-CHECKS.txt`: the baseline is green, and each of these turns it red:
  - an anchor to a missing heading, on the same page or across pages;
  - a missing image;
  - a link to an untracked file;
  - a README row whose file does not exist;
  - a stale `EXCLUDE` entry;
  - a heading renamed under an inbound link;
  - a README without its Documentation table.
- The product page's documentation cards now link to the sub-pages. `check_site.py` refuses a link to a sub-page the
  build would not produce (control added to `SITE-CHECKS.txt`).

### Implementation map (R9-WEB-3)

| design | repository |
|---|---|
| `docs_build.mjs` | `tools/site/build_docs.mjs`, which requires the vendored parser by the path `render_md.mjs` uses. R9-RO-6, which moves the vendor folder to `tools/policy/vendor/`, re-points it, and the arm refuses a missing parser. |
| `docs.css` | `docs/site/docs.css` (fonts first, from `docs/site/fonts/`); the product page may share its tokens from it |
| mermaid | `tools/site/package.json` and `package-lock.json` pinning mermaid; `npm ci` runs only in the Pages workflow, never in tests |
| `docs_controls.py` | the PR body's planted-error table, run at the head |
| the build check | one new arm in `tests/doc_claims.py`: run the build over the working tree into a temp dir with the tracked-file list, fail on every FAIL line, and anchor on zero pages |
| product page links | the documentation cards, the card and setup links, and the footer point at the sub-pages; `check_site.py`'s sub-page rule joins the WEB-1 arm |

Classification:
- `tools/site/` needs one `tests/layout.json` glob.
- The arm makes it part of `doc_claims.py`'s closure, which the autofix records.
- `.github/CODEOWNERS` gains `/tools/site/ @tvofi` in this PR. The Pages workflow will execute the generator, which
  puts it on the required-check enforcement surface, and owning it first means R9-WEB-2 need not edit
  `.github/CODEOWNERS`.

### Hosting change (R9-WEB-2, amended)

The workflow now does four things:
- runs `npm ci` in `tools/site/`;
- runs the generator into `_site/` beside the product page;
- copies `mermaid.min.js` to `site/mermaid/`;
- stages the images by pattern, as before.

Because it executes one repository script, it changes what `codeowners_gap.py` reports:
- The body shows that the surface grew by exactly the generator (and anything the harness says it imports), and that
  all of it is owned.
- If the harness reports a path that is not yet owned, WEB-2 stops. The orchestrator then orders it before R9-RO-2,
  which also edits `.github/CODEOWNERS`. That placement is at depth 8 with zero slack, and the programme gets no
  longer.
