# R10-README-GRAPHICS: design review, round 1 of 3

Design review: revise e995b815 roster-entry: `files` names a file the design does not edit and omits every file it creates; `hot_files` omits the hot file the note itself names

Seat: cloud probe, read-only. Contract: dev/governance/roles/design-review.md at origin/main.
Note: handoff-body/r10-readme-graphics at e995b8153795e9be0b677c26c1259e294d302ef1.
Tree: ca0a6cfbc2e5538e6e2220793831443719ff6e98 (origin/main). The note measured d99cadb12. The
interval touches none of README.md, docs/img/, tests/doc_claims.py, tests/closure.py or tools/site/
(`git diff --stat d99cadb12 ca0a6cfbc` over those paths is empty).
Upstream: `pip download --no-deps homeassistant==2026.11.0b1 home-assistant-frontend==20261028.1`.
No tracked file changed, no PR opened.

## Revise point (one)

1. **Roster entry, `files` and `hot_files`** (body "## Roster entry").
   - `files` lists `docs/img/readme/render.mjs`. Section 3B says the new generator goes *beside*
     it, following its pattern, so render.mjs is not edited.
   - `files` omits every file the design adds:
     - the generator script;
     - the sidecar manifest;
     - the three diagram PNGs;
     - the finder's harness under `dev/audit/harnesses/`.
   - Section 4 calls `tests/doc_claims.py` a hot file shared with R10-ARCH-DOCS, but `hot_files`
     is `["README.md"]` only.
   - `tests/closure.py` is also in `files` of the not-started R10-MERGE-SUBJECT-CASEARM. Name it
     in `hot_files`, or say why not.
   - Fix wanted: make `files` the design's actual edit set (with the new paths named, or their
     directories), and add `tests/doc_claims.py` (and `tests/closure.py`, or a reason) to
     `hot_files`.
   - brief_lint does not catch this. Re-run on the corrected entry: it was exit 0, 0 errors, and
     the same 6 pre-existing R10-FLY-* warnings.

## Attack (1): the evidence, re-derived

**Limit, stated first.** Executing the shipped `markdown-worker.7ccc00a11f740769.js` in Node was
refused by this session's auto-mode classifier ("Code from External"). I did not work around that.
Each rule below was therefore checked against the **shipped bytes statically**, and then applied
by this seat's own transcription of the predicate. That is no stronger than the note's replica,
so the note's P2 (a real 2026.11 instance or a screenshot) still stands as a carry.

| rule | reproduced? | evidence |
|---|---|---|
| backend fetches README at the version, only `<svg`→`<disabled` | yes | `marketplace/repositories/base.py:1914` raw.githubusercontent `{full_name}/{target_version}/{filename}`, `:1920` replace; target_version = installed_version/commit, else last_version = release `tag_name` (`:1599`) |
| sanitizer blanks bare-relative src/href **before** the rewrite | yes | worker byte ~11800, `safeAttrValue`: keeps only `http://`,`https://`,`mailto:`,`tel:`,`data:image/`,`ftp://`,`./`,`../`,`#`,`/`, else `""`. Bundle 42233 `_render` (~@4332): `renderMarkdown(...)` result → template → `setAttribute(r, e(getAttribute(r)))` over `[["a","href"],["img","src"],["source","src"]]` + `source[srcset]`, i.e. rewrite runs on the sanitized string |
| `""` becomes the bare ref directory | yes | module 73003 export `E`: no early return on an empty URL; `new URL("", base).href` = `https://raw.githubusercontent.com/{full_name}/{ref}/` |
| `./` passes, and resolves to the version | yes | `./` is in the keep-list; `E` resolves with `new URL(s, base)`; `.md`/`.markdown` targets go to `github.com/{full_name}/blob/{ref}/`; ref = `installed && installed_version || available_version || default_branch` |
| README at ca0a6cfbc | yes | 57 link/image targets, 32 blanked (17 unique: 4 images, banner/coffee/card-plan-chart/how-it-works, plus 28 links). This matches the note's 4 + 28 |
| mermaid as plain `<pre>` | yes | 0 of 4938 `frontend_latest/*.js` files contain `mermaid`; allow-list `code:[]`, `pre:[]`, so the `language-mermaid` class is stripped; 3 mermaid fences in README |
| inline SVG stripped; svg only under allowSvg | yes | `svg:["xmlns","height","width"]` appears only in the `r.allowSvg` branch; the Marketplace call passes no `allow-svg`; plus the backend `<disabled` rewrite |
| `<picture>`/`<source>` allowed, srcset all-or-nothing | yes | `picture:[]`, `source:["src","srcset","sizes","media","type"]`; the `onTagAttr` srcset hook returns `""` unless every URL part passes `safeAttrValue` |
| `<img>` attributes | yes | `img:["src","alt","title","width","height","loading"]` |
| `<details open>`/`<summary>` | yes | `details:["open"]`, `summary:[]` |

Not re-run: the Chromium load test, and `prefers-color-scheme` picking the `-dark` source
(execution refused, as above). Both are consistent with the allow-list. The only design choice
they bear on, `<picture>`, is out of scope.

The Marketplace renders no other document: there is no `info.md`, and `hacs.json` has no
`render_readme`. So README.md is the whole sibling set (no `class-open`).

## Attack (2): the design

- **`./` rewrite, GitHub and site.**
  - Sound. GitHub resolves `./x` like `x` in a repository README.
  - `tools/site/build_docs.mjs:92` and `:114` resolve both through
    `path.posix.normalize(path.posix.join(dirname(CUR), …))`, so the product page is unchanged.
  - The alternatives' rejections (tag-pinned absolute URLs violate rule 4; main-pinned ones
    mismatch the installed version and trip S11) hold.
- **PNG over SVG.** Justified: inline SVG is stripped twice. Mermaid's default `foreignObject`
  labels and web fonts do not survive an `<img>` context. Opaque light 2x at about 2300 px fits
  the about 1150 CSS px usable width.
- **Light/dark.** One opaque light PNG reads on both themes. Deferring `<picture>` is honest:
  build_docs passes raw HTML through without path resolution, and that is code-owned. Routed
  below.
- **Drift check.** Sound in shape:
  - It is a tracked arm of `tests/doc_claims.py`, so CI runs it through the scoped gate.
  - It is classified as reads of doc_claims in `tests/closure.py` (the coffee.svg route,
    `closure.py:678`).
  - It is self-tested (red on a one-character block edit, red on a `./` removal, green on the
    null control).
  - It compares sources, not PNG bytes, for the same reason goldens are claimed.
  - The setup-flow identity arm (`doc_claims.py:2569-2578`) matches only the fenced block, so
    closing the `<details>` around it leaves the anchor intact.

## Attack (3): placement

- brief_lint at origin/main on a scratch roster with the entry appended
  (`node tools/policy/brief_lint.mjs <copy>`): exit 0, 0 errors. The 6 warnings are all
  pre-existing R10-FLY-*. The unmodified roster also exits 0.
- `after: []` is valid: R10-MARKETPLACE and R10-ARCH-DOCS-FIRST are both `done`.
- Adding the group to R10-ARCH-DOCS's and R10-CATALOG-PR's `after` is a roster edit to other
  groups. It is carried in `resume.next_step`, and nothing in this entry performs it.
  `decision: orchestrator`.
- `files`/`hot_files`: see the revise point.

## Attack (4): what the release-tag fetch implies

- The fix shows at the **first tag stamped after the merge**, not specifically v10.0.0.
  - Today there is no v10 tag; VERSION is 7.1.0, and the latest tag is v7.1.0.
  - R10-STAMP-ROUND-MAJOR (`done`, #2969) changed the stamping, not the version.
  - Any intermediate stamp carries it, so "before R10-ARCH-DOCS so v10.0.0 carries it" is a
    sufficient ordering, but not the reason the fix ships. Whether to stamp early so the store
    page is fixed sooner is `decision: owner`.
- **Installed users see the README at their installed version.** Both the backend
  (`target_version = installed_version`) and the frontend `E` (`installed && installed_version`)
  pin it, so an installed v7.1.0 user keeps the broken page until they update. Nothing in-tree
  can fix that. The fix note should state it.
- The figures are committed at the tag and the rewriter pins them to the same ref, so a figure
  never mismatches its README.

## Carries (findings for the fixer, not revise points)

- Carry: R10-README-GRAPHICS (item P5). The source hash binds the block text to the manifest, not
  to the PNG. A hand-edited manifest hash passes with a stale figure. Record the PNG's sha256 in
  the manifest too, and have the arm refuse a manifest whose PNG hash differs from the file.
  Self-test that, and show regenerate→green after the planted drift, so "passes when fixed" is
  shown, not only "red on drift".
- Carry: R10-README-GRAPHICS (item P6). The generator needs the tools/site mermaid
  (`package.json` pins 12.2.0, which `npm ci` installs in the Pages workflow only) plus
  Playwright. State in the generator's header how a seat installs it, so a README diagram edit is
  not blocked on an unwritten step.
- Carry: R10-README-GRAPHICS (item P7). On the product page the README's diagrams now appear
  twice: the static light PNG, plus the live mermaid inside a closed `<details>`. Confirm with a
  build_docs run that this reads acceptably, or note it for the owner's `<picture>`/tools/site
  option.
- Carry: R10-README-GRAPHICS (item P8). The fix note should state that only a stamped tag shows
  the fix, and only to users once they install or update to that tag.
- Carry: dismissed: sibling documents unaffected (item P9). The Marketplace fetches README.md
  only: there is no `info.md`, and `hacs.json` has no `render_readme`.

## Routed

- decision: orchestrator. Edit R10-ARCH-DOCS's and R10-CATALOG-PR's `after` to include
  R10-README-GRAPHICS.
- decision: owner. `<picture>` dark sources (needs a code-owned tools/site/ change), and whether
  to stamp as soon as this merges.
