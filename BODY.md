# R10-README-GRAPHICS: pre-study, round 2 of 3 (revises e995b815 per design review fe1d5b7f)

Round 2 changes only "## Roster entry" and adds the reviewer's carries to the fixer notes. Everything else is round 1, unchanged.

Seat: cloud probe, read-only. Tree: `d99cadb1235a5e40e250466e656c41c7ce88e641` (= origin/main, v7.1.0).
Roster read: `origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`.
Upstream measured: `homeassistant==2026.11.0b1` wheel (core `marketplace` integration) and the
`home-assistant-frontend==20261028.1` wheel it pins, plus upstream frontend sources at tag `20261028.1`.
No tracked file changed; no PR opened.

## Summary

The owner's report is right, and the main cause is not mermaid. **Every repository-relative image
and link in README.md is blanked by the Marketplace's sanitizer before the URL rewriter runs.**
That means the banner, the coffee button, the card chart and the how-it-works figure, and every
relative doc link. The fix is mechanical: prefix each relative target with `./`. GitHub renders
`./docs/...` exactly like `docs/...`, and the Marketplace sanitizer lets `./` through.
The mermaid diagrams are the second cause. They render as raw text in a `<pre>`. The fix is a
committed PNG for each diagram plus a source-hash drift check.
Recommended: a new M group, lane PR, ordered before R10-ARCH-DOCS so v10.0.0 carries it. The
Marketplace fetches the README **at the release tag**, so nothing shows until a release ships.

## 1. Inventory: README.md at d99cadb12

GitHub rendering is "yes" for all of them today.

| line | kind | target | size |
|---|---|---|---|
| 1 | md image, relative | docs/img/readme/banner.png | 2560x640 PNG, 69 KB (SVG source beside it) |
| 11-14 | md image, absolute | img.shields.io badges | external SVG |
| 16 | md image, relative | docs/img/brand/coffee.svg | 816 B SVG |
| 22 | md image, relative | docs/img/card/card-plan-chart.png | 1864x1700 PNG, 237 KB |
| 120-169 | `<details open>` + mermaid `flowchart LR` | "How the pieces fit" | inline |
| 320 | md image, absolute | my.home-assistant.io HACS badge | external SVG |
| 402-428 | `<details open>` + mermaid `flowchart TD` | setup flow; pinned identical to configuration.md and setup.md by tests/doc_claims.py around line 2574 | inline |
| 805 | md image, relative | docs/img/readme/how-it-works.png | 2400x880 PNG, 173 KB; a `-dark.png` variant exists but is unused |
| 807-838 | `<details open>` + mermaid `sequenceDiagram` | "One optimization interval" | inline |

The README has no `<picture>`, no inline `<svg>` and no GIF. It also has 28 relative markdown
links (`docs/*.md`, `NOTICE`, ...), and they fail the same way as the images.
The existing renderer is docs/img/readme/make_readme_figures.py (fontTools) with
docs/img/readme/render.mjs (Playwright PNG).

## 2. What the Marketplace renders, with evidence

The pipeline:

1. **Backend fetch.** `homeassistant/components/marketplace/repositories/base.py`:
   - :720 `additional_info = await async_get_readme_contents()`.
   - :1884-1930 `get_documentation` fetches
     `raw.githubusercontent.com/{full_name}/{target_version}/README.md`. `target_version` is the
     installed version, else `last_version` (the release `tag_name`, :1599), else the commit.
   - The only transform is `<svg` to `<disabled`. Nothing is rewritten.
2. **Frontend renderer.** `ha-marketplace-repository-dashboard` (bundle `42233.4256c55c2225a8eb.js`,
   around byte 32840) renders
   `<ha-markdown .content=${readme} .rewriteUrl=${readmeUrl} lazy-images>`.
   `allow-svg` and `breaks` are not set.
3. **Pre-step.** Module 73003 export `t` protects code, HTML and links, and autolinks `#N`.
   It does not rewrite URLs.
4. **Markdown and sanitizer.** `src/resources/markdown-worker.ts` uses `marked`
   (`gfm: true`, `ha-markdown-element.ts:97`). Each token then goes through js-xss `filterXSS`,
   with the default allow-list extended at :55-74 by `picture`, `source[src,srcset,sizes,media,type]`
   and others.
5. **URL rewrite, after sanitizing.** `src/common/dom/rewrite-html-urls.ts:29-56` rewrites
   `a[href]`, `img[src]`, `source[src|srcset]` with module 73003 export `E` (bundle byte ~47331).
   - Absolute, `#` and `//` targets are untouched.
   - Anything else resolves against
     `raw.githubusercontent.com/{full_name}/{installed_version || available_version || default_branch}/`,
     or `github.com/.../blob/...` for `.md` targets.

The rules, with evidence:

| question | answer | evidence |
|---|---|---|
| **relative paths** | **Broken for bare `docs/...`; working for `./docs/...` and `/docs/...`** | js-xss `safeAttrValue` keeps `src`/`href` only when it starts with `http://`, `https://`, `mailto:`, `tel:`, `data:image/`, `ftp://`, `./`, `../`, `#` or `/`, else `""`. Shipped worker `markdown-worker.7ccc00a11f740769.js` byte 11805; same in xss `lib/default.js:176-194`. The rewriter then turns `""` into the bare ref directory, which is not an image. Replica run below. |
| mermaid | Not supported: shows as plain code text | No mermaid in `frontend_latest/*.js` (grep: none). marked emits `<pre><code class="language-mermaid">`; the allow-list has `code:[]`, so the class is stripped. Replica: 3 of 3 blocks are plain `<pre><code>`. |
| SVG | Inline `<svg>` stripped. SVG **as `<img>` works** | Backend `<svg` to `<disabled`; no `svg` in the normal allow-list (`markdown-worker.ts:78-90`, svg only under `allowSvg`). raw.githubusercontent serves `.svg` as `image/svg+xml` with `CSP: sandbox`, which does not stop `<img>` rendering. Chromium loaded `coffee.svg` at naturalWidth 178 through `./`. |
| `<picture>` / dark sources | Allowed and working, given `./` paths | `picture: []` and `source[...media, srcset]` at :55-74. `srcset` parts must each pass `safeAttrValue` (:21-43), so bare relative paths drop the whole `srcset`. Chromium with `colorScheme: dark` picked `how-it-works-dark.png`, and `light` picked the light one. Follows the OS/browser `prefers-color-scheme`, not HA's own theme picker. GitHub's `#gh-dark-mode-only` fragment is not honoured: both images would show. |
| `<details>`/`<summary>` | Allowed (`details[open]`, `summary`) | js-xss default allow-list (bundle bytes ~8482-9250). |
| `<img>` attributes | `src, alt, title, width, height, loading` only | Same allow-list: no `class`, `style`, `align`, `srcset` on `<img>`. |
| max width | Page `.content{max-width:1200px}` with `--ha-space-4` padding; `img{max-width:100%}` inside `ha-card` | Bundle 42233 byte ~40396; `ha-markdown.ts:75-79`. About 1150 CSS px usable, so 2x PNGs near 2300 px wide are right. |

**Replica run.** This is not the shipped bundle: marked 15 + xss 1 + jsdom, using the worker's
allow-list and export `E` as transcribed, with ref `v7.1.0`. Rendered in Chromium 1280x1400.

| case | images that loaded | relative `href`s | mermaid |
|---|---|---|---|
| current README | none of `banner`, `coffee`, `card-plan-chart`, `how-it-works`; every `src` is the bare ref directory | all 28 become the bare ref directory | plain text |
| README with `./` prefixes (sed only) | banner 2560, coffee 178, card chart 1864, how-it-works 2400 | resolve | unchanged |

Shields and my.home-assistant badges stayed 0 because this sandbox's proxy refuses those hosts
(CONNECT 403). That is an environment limit, not a Marketplace rule.

The harness lives in this seat's scratchpad and is not tracked. The fixer rebuilds it as the
finder's harness (see section 5).

## 3. Design

**A. Relative targets (the main fix).** Rewrite every repository-relative markdown link and image
target in README.md from `path` to `./path`.

- GitHub resolves both forms the same way.
- tools/site/build_docs.mjs resolves through `path.posix.join(dirname(CUR), ...)`, which normalizes
  `./`. So the product-page build is unchanged.
- The Marketplace rewriter pins each target to the installed or available version, so images
  always match the README's version.

Alternatives that lost:

- **Absolute raw URLs pinned to a tag.** Each release needs an edit, and that edit would have to
  happen after the stamp (CLAUDE.md rule 4 keeps versions out of branches). It drifts by
  construction.
- **Absolute URLs on `main`.** The images stop matching the installed version. Also,
  tools/site/build_docs.mjs turns an absolute image into a text badge and flags absolute raw HTML
  sources as third-party (S11). The product page would lose its figures.
- **Leading `/`.** It passes the sanitizer too, but GitHub's README view and build_docs.mjs treat
  it differently from a relative path.

**B. Mermaid.** For each of the three mermaid blocks:

1. Commit a pre-rendered PNG (2x, opaque, light theme, matching the docs/img/readme/ house style).
2. Insert it as a markdown image (`./` path) directly above the block.
3. Change the block's `<details open>` to `<details>`, with a summary naming it as the diagram
   source.

Result: GitHub shows the figure with the live mermaid one click away. The Marketplace shows the
figure with the raw code folded away. The setup-flow block stays byte-identical in all three docs,
so doc_claims' identity anchor is untouched. The README remains the single source.

- **Rendering.** Use the pinned mermaid in tools/site (package.json, Dependabot-watched) inside
  Chromium, following docs/img/readme/render.mjs. A new generator script goes beside it. No
  mermaid-cli/puppeteer dependency is added.
- **Drift check (the regeneration guard).** Byte-comparing PNGs cannot reproduce across machines
  (fonts and rasteriser, the same reason value-bearing goldens are claimed). So the check compares
  **sources**:
  - The generator writes a sidecar manifest mapping each figure to the sha256 of its README mermaid
    block text.
  - A new arm in tests/doc_claims.py re-extracts each block and refuses on any of: a hash mismatch,
    a missing PNG, a block with no figure directly above it, or a manifest entry with no block.
  - The arm also refuses any bare-relative `src`/`href`/`srcset` target in README.md, using the
    js-xss predicate transcribed with its upstream citation. This makes finding A a barrier, not a
    one-off.
  - Both checks are self-tested in the arm's style:
    - a planted one-character block edit goes red;
    - a planted `./` removal goes red;
    - the null control (unchanged tree) stays green.
- **Light/dark.** The opaque light-background PNGs read correctly on both GitHub and HA themes, and
  that is the recommended default.
  `<picture>` with a `prefers-color-scheme: dark` source is measured to work on both sites. It is
  left out of this group because build_docs.mjs passes raw HTML through without path resolution:
  a relative `srcset` inside `<picture>` would break on the product page (it is served from docs/).
  Enabling it means editing tools/site/, which is code-owned. Carry it as an owner option, not
  scope.

Alternatives for B that lost:

- **Replace mermaid with images only.** The setup-flow identity arm would need a second source of
  truth outside README. The product page would also lose its live, theme-switching diagrams
  (build_docs.mjs renders `pre.mermaid` with its own theme toggle).
- **Inline SVG.** The backend and the sanitizer both strip it.
- **SVG figure via `<img>`.** It renders, but mermaid SVG relies on `foreignObject` HTML labels and
  web fonts that an `<img>` context cannot load. Text would fall back or clip.

**Policy notes.**

- **D5/D6.** No claim text changes. The new figures depict existing diagrams, which R10-ARCH-DOCS
  already owns verifying (its P40 fold: committed figures compared to what they depict).
- README.md is outside writing-for-agents.md, which rules only the development record.
- **Closures.** The docs/ prefix stays INERT. The manifest and the new PNGs become reads of
  tests/doc_claims.py, so they join that script's explicit list in tests/closure.py (the route
  coffee.svg and how-it-works.png took). tests/entities.py then stays green with no INERT edit.
- No `*_budgets.json` raise is expected: the change adds no production code.

## 4. Programme placement

- **Fold or new?**
  - R10-CATALOG-PR is an owner-step with no files and an owner gate (tvofi personal account), so it
    cannot carry code.
  - R10-ARCH-DOCS is L, the last stage, after-gated on most of the round, and docs-verification
    in scope. Folding this in would delay a user-visible Marketplace defect to the round's end and
    widen an L.
  - R10-MARKETPLACE is done (#2973).
  - **Verdict: a new group, M, lane PR** (the Marketplace lane).
- **Ordering.**
  - after: none. Its predecessors R10-MARKETPLACE and R10-ARCH-DOCS-FIRST have both merged.
  - **Add it to R10-ARCH-DOCS's `after`**, so the closeout verifies the figures and v10.0.0 is cut
    with it.
  - **Add it to R10-CATALOG-PR's `after`**, so the catalog PR is not opened on a README the store
    renders broken.
- **Hot files.** README.md, shared with R10-ARCH-DOCS (not started) and tests/doc_claims.py.
- **Size: M.** A mechanical link pass, a generator, three figures, one doc_claims arm with its
  controls, and closure entries. Not L, so designer.md does not require a design seat; this note
  stands as its architect note.

### Notes for the fixer

- Carry: R10-README-GRAPHICS (item P1). The finder's harness is a replica of the HA
  2026.11.0b1/frontend 20261028.1 pipeline: marked gfm, the worker allow-list, the rewrite rule.
  Rebuild it under dev/audit/harnesses/ and cite the upstream lines above. Show it red at the base
  (no repository image resolves) and green at the head. The null control is an absolute-URL image,
  which passes at both ends.
- Carry: R10-README-GRAPHICS (item P2). Verify with a real 2026.11 instance if one is reachable:
  the replica transcribes but is not the bundle. A screenshot of the Marketplace repository page at
  a pre-release tag is the strongest evidence.
- Carry: R10-ARCH-DOCS (item P3). The new mermaid figures are committed figures that the P40 check
  compares to what they depict.
- Carry: dismissed: product page unaffected by dot prefixes (item P4). build_docs.mjs normalizes
  `./` (resolveHref and the image rule both use `path.posix.join`). Re-run its doc_claims arm
  anyway.

- Carry: R10-README-GRAPHICS (item P2, reviewer's restatement). The design review could not execute the shipped markdown worker (session classifier refused), so every rule was checked statically only. The fixer must obtain a real HA 2026.11 instance or a screenshot of the Marketplace repository page at a pre-release tag; a replica alone is not enough.
- Carry: R10-README-GRAPHICS (item P5). The source hash binds the block text to the manifest, not to the PNG. Record each PNG's sha256 in the manifest too and have the arm refuse a manifest whose PNG hash differs from the file. Self-test it, and show regenerate -> green after the planted drift, so "passes when fixed" is shown, not only "red on drift".
- Carry: R10-README-GRAPHICS (item P6). The generator needs the tools/site mermaid (package.json pins 12.2.0, installed by `npm ci --prefix tools/site`, run in pages.yml only) plus Playwright. State in the generator's header how a seat installs both.
- Carry: R10-README-GRAPHICS (item P7). On the product page the README diagrams appear twice: the static light PNG, plus live mermaid inside a closed `<details>`. Confirm with a build_docs run that this reads acceptably, or note it for the owner's `<picture>`/tools/site option.
- Carry: R10-README-GRAPHICS (item P8). The fix note must state that only a stamped tag shows the fix (any stamp after the merge, not specifically v10.0.0), and only to users who install or update to it; an installed v7.1.0 keeps the broken page.
- Carry: dismissed: sibling documents unaffected (item P9). The Marketplace fetches README.md only: no info.md, and hacs.json has no render_readme.
- Routed: decision orchestrator: add this group to R10-ARCH-DOCS's and R10-CATALOG-PR's `after`. Decision owner: `<picture>` dark sources (code-owned tools/site/ change), and whether to stamp as soon as this merges.

Probe-seat process note: a session-local inline-search guard (frugal plugin) refused two inline
searches. The seat did not work around it: it delegated those reads to a read-only sub-seat, as
the guard's own message directs.

## Roster entry

`files` is the design's actual edit set. render.mjs is not edited (the new generator goes beside it), so it is dropped. New paths are named exactly; the three PNG names are the fixer's to rename within docs/img/readme/. No workflow file is edited: the drift arm lives in tests/doc_claims.py, which tests.yml already runs through the scoped gate, so the CI wiring is the tests/closure.py classification (reads of doc_claims.py, the coffee.svg route) and nothing else. `hot_files` adds tests/doc_claims.py (shared with R10-ARCH-DOCS) and tests/closure.py (also in `files` of the not-started R10-MERGE-SUBJECT-CASEARM).

Linted by appending this entry to a scratch copy of the roster at origin/handoff/audit-r10-roster and running `node tools/policy/brief_lint.mjs <copy>`: exit 0, 0 errors, 6 warnings, all pre-existing R10-FLY-* groups, none for this group.

```json
{
 "group": "R10-README-GRAPHICS",
 "lane": "PR",
 "kind": "production",
 "class": "docs",
 "severity": "medium",
 "size": "M",
 "issues": [],
 "fixes": [],
 "findings": [],
 "hot_files": [
  "README.md",
  "tests/doc_claims.py",
  "tests/closure.py"
 ],
 "fixture": false,
 "owner_gate": null,
 "rca": [],
 "architect_note": "handoff-body/r10-readme-graphics",
 "effort": "medium",
 "model": {
  "fixer": "sonnet",
  "reviewer": "opus",
  "rca": null,
  "runner": "haiku",
  "record": "sonnet"
 },
 "fixerModel": "sonnet",
 "reviewerModel": "opus",
 "after": [],
 "files": [
  "README.md",
  "docs/img/readme/render_mermaid.mjs",
  "docs/img/readme/mermaid_figures.json",
  "docs/img/readme/mermaid-how-the-pieces-fit.png",
  "docs/img/readme/mermaid-setup-flow.png",
  "docs/img/readme/mermaid-one-interval.png",
  "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",
  "tests/doc_claims.py",
  "tests/closure.py"
 ],
 "carry": [],
 "resume": {
  "stage": "not-started",
  "branch": null,
  "commit": null,
  "last_step": null,
  "next_step": "dispatch fixer; add this group to the after lists of R10-ARCH-DOCS and R10-CATALOG-PR",
  "note": "2026-10-30 owner request (tvofi): README graphics in the HA Marketplace; pre-study at handoff-body/r10-readme-graphics"
 },
 "brief": "Owner request, 2026-10-30 (tvofi): the Home Assistant Marketplace repository page does not show the front-page README graphics. Pre-study at handoff-body/r10-readme-graphics, measured against homeassistant 2026.11.0b1 and home-assistant-frontend 20261028.1. Its core finding: the Marketplace sanitizer (js-xss safeAttrValue in the frontend markdown worker) blanks every src and href that is not absolute and does not start with ./ or ../ or /, before its URL rewriter runs. So every repository-relative image and link in README.md renders broken, and mermaid fences show as plain code. (1) Prefix every repository-relative link and image target in README.md with ./ so GitHub, tools/site/build_docs.mjs and the Marketplace all resolve it. (2) For each mermaid block in README.md, commit a pre-rendered PNG (2x, opaque, light) rendered with the mermaid pinned in tools/site through Chromium on the pattern of docs/img/readme/render.mjs. Place it as a ./ markdown image directly above the block, and close that block's details element. The setup-flow block stays identical to docs/configuration.md and docs/setup.md. (3) Add an arm to tests/doc_claims.py that refuses a bare-relative src, href or srcset in README.md, and refuses a mermaid block whose figure is missing or whose recorded source hash (a sidecar manifest the generator writes) differs from the block. Show a planted one-character block edit red, a planted prefix removal red, and the unchanged tree green. (4) Classify the new manifest and figures as reads of tests/doc_claims.py in tests/closure.py, the route docs/img/brand/coffee.svg took. Finder's harness: a replica of the Marketplace markdown pipeline under dev/audit/harnesses/, red at the base and green at the head, with an absolute-URL image as the null control. Out of scope: picture elements with dark sources (needs a code-owned tools/site/ change), docs other than README.md, VERSION and release notes. Must merge before R10-ARCH-DOCS and R10-CATALOG-PR: the Marketplace fetches README.md at the release tag, so only a stamped release shows the fix."
}
```
