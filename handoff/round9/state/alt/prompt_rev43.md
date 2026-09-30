# Prompt (rev 4.3): the round-9 fixing orchestrator adopts lane WEB (the product page and its documentation sub-pages) into the live roster

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting. Nothing below loosens them.

This prompt adopts rev 4.2 (the product page) and rev 4.3 (the docs as sub-pages) together. If you already applied rev 4.2, skip its script in step 2 and apply only rev 4.3.

**The mandate** of 2026-09-29 stands, with rev 4.1's exception: it does **not** pre-confirm structure-budget raises for lane UX (U4), and the same holds for lane WEB. None is expected, because no structure metric measures `docs/`, `tests/` or `tools/`.

What remains for tvofi's hands, and you request it; you never wait on it silently:
- approving reviews at the head for:
  - WEB-1 (`tests/closure.py`, `tests/layout.json`);
  - WEB-3 (the same two files plus `.github/CODEOWNERS`);
  - WEB-2 (`.github/workflows`);
- a one-time repository setting before WEB-2's first dispatch: Settings → Pages → Source: "GitHub Actions";
- decision S3 below, only if tvofi wants a savings figure on the page.

## Background

- Rev 4.1 (lane UX, Part of #1795) is applied on `handoff/audit-r9-fixplan`. The live roster was at `9e63d2a3` when this revision was written; origin/main was at `aac8fb77` (after #1794).
- tvofi on 2026-09-30:
  - "Design a full product web page, based on the user facing documentation in the repo, in the same design language as the showcase page, then make a rev 4.2 of the plan where implementation of this page and pining it to the master documentation is added."
  - Then: "The docs should also be adopted to sub pages, if that is not unfeasible."
- The decisions:
  - W1: pinning is test-pinned and linked. Every claim on the page carries a source anchor into the README or a reader doc, a test refuses drift, and the README links the page.
  - W2: the site is served by GitHub Pages through a workflow.
  - S3 (a design decision, open to tvofi): no savings percentage on the page, because the docs call the only one a one-off measurement on the author's house.
  - S7–S11 (design, rev 4.3):
    - the docs are rendered at deploy and never committed;
    - GitHub heading slugs;
    - the page set is derived from the README Documentation table, two-sided;
    - mermaid is self-hosted from a lockfile;
    - no third-party request.
- Everything is on branch `handoff/audit-r9-alt`:
  - `handoff/round9/state/alt/design/site/`:
    - `DESIGN-SITE.md`;
    - the page `index.html`;
    - the pin prototype `check_site.py`, with `controls.py` and `SITE-CHECKS.txt`;
    - the docs generator prototype `docs_build.mjs` and `docs.css`, with `docs_controls.py` and `DOCS-CHECKS.txt`;
    - the renders.

    The page was designed at `2b5031bf`, and the sub-pages and page links at `6c539ee3`.
  - `handoff/round9/state/ALT-ENDGAME-PLAN.md`, sections R6 (rev 4.2) and R7 (rev 4.3);
  - `handoff/round9/state/ALT-ROSTER.json`: roster rev 4.3, 100 groups, acyclic, `brief_lint` `TOTAL: 0 error(s)`;
  - `handoff/round9/state/alt/build_roster_rev42.py` and `build_roster_rev43.py`, which rebuild it from the live file.

Before step 1, read plan sections R6 and R7 and `DESIGN-SITE.md`.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `aac8fb77` and every commit on `handoff/audit-r9-fixplan` since `9e63d2a3`, and truth each group's stage.
   - If a merge touched `README.md`, `DISCLAIMER.md`, a reader doc under `docs/`, `docs/img/` or `docs/setup/`, re-run both prototypes at your origin/main:
     - `HPO_REPO=<checkout> python3 handoff/round9/state/alt/design/site/check_site.py handoff/round9/state/alt/design/site/index.html --ref origin/main`;
     - `docs_build.mjs` over a `git archive` of origin/main's README, DISCLAIMER and `docs/`, with `git ls-tree -r --name-only origin/main` as its tree list.
   - A red line is a claim or a link the docs no longer support. Record it in WEB-1's or WEB-3's resume note as a fix that PR owes. Never weaken a rule.

2. **Apply rev 4.2, then rev 4.3,** to the live roster on `handoff/audit-r9-fixplan`.
   - Run these in order:
     - `python3 handoff/round9/state/alt/build_roster_rev42.py <live> <tmp> 2b5031bf`
     - `python3 handoff/round9/state/alt/build_roster_rev43.py <tmp> <out> 6c539ee3`
   - Each refuses its own second run, a missing predecessor revision, a dangling edge, a cycle, and any result that lengthens the longest open chain or EG-A4's. At `9e63d2a3` they print WEB-1 depth 6, WEB-3 7 and WEB-2 8.
   - Fetch `handoff/audit-r9-alt`, `handoff/silent-windows-plan` and `handoff/repo-reorg-plan`. Then lint with origin/main's `.claude/workflows/brief_lint.mjs`; it must print `TOTAL: 0 error(s)`.
   - Diff the output against the live file. Only these may differ:
     - the three new groups WEB-1, WEB-2 and WEB-3;
     - RO-2's `after` (WEB-1, WEB-3) and RO-3's (WEB-2);
     - appended carries on the briefs of RO-3, RO-4, RO-6, RO-9, UX-1, UX-2, UX-3, UX-5, UX-6 and UX-7;
     - two `_comment` lines.
   - Re-run the coverage (`alt/gen_coverage_rev31.py`) on the live open-issue list. #1793 is the one issue that is uncovered on purpose.
   - Commit the result as the live roster.

3. **File one feature issue for lane WEB**, with W1, W2, S3 and S7–S11, `DESIGN-SITE.md` at `6c539ee3`, the three groups and their order (WEB-1 → WEB-3 → WEB-2), and the carries into lanes UX and RO.
   - Read it back.
   - Write its number into the three groups' `issues`. WEB-1 and WEB-3 are Part of it; WEB-2, the last, Fixes it.

4. **Post one #201 comment** with `gh_comment.py` and read it back. It covers:
   - revs 4.2 and 4.3 adopted, with the roster commit;
   - the decisions;
   - the new WEB issue;
   - the chain arithmetic (unchanged at 12 and 11; WEB-1 at depth 6, WEB-3 at 7 and WEB-2 at 8, each with one step of slack);
   - tvofi's three reviews and the Pages setting.

5. **Dispatch.**
   - WEB-1 when UI-2, UI-4 and F10.4 have merged.
   - WEB-3 when WEB-1 has merged.
   - WEB-2 when WEB-3 has merged. Ask tvofi for the Pages setting when you dispatch it, not later.
   - Everything else continues per rev 4.1, one merge at a time.

## Rules specific to lane WEB

- **Pinned, not paraphrased.** Every sentence of fact on the product page is quoted from a documented section. The page arm refuses:
  - a quote the section no longer makes;
  - a number the section does not state;
  - a digit outside a claim;
  - a missing or extra README feature lead or Documentation row;
  - a dead image or link, or a link to a sub-page the docs build does not produce;
  - a version literal;
  - any third-party request.

  A reviewer returns blocked on a fact without `data-src`, and on `data-copy` used to exempt one.
- **The sub-pages are the docs, rendered.**
  - Nothing is written per document, and no generated HTML is committed (S7).
  - The docs-build arm fails on a dead anchor, a missing image, a link to an untracked file, a README row without a file, and a stale `EXCLUDE` entry.
  - A dead anchor already on main is a doc defect that WEB-3 fixes in the doc, named in its body. It is never excluded.
- **Both arms live in `tests/doc_claims.py`** and read the working tree. There is no new test script, `tests/run.sh` is untouched, and closures are re-recorded by CI's autofix. Neither PR edits `tests/README.md`; if `tests/entities.py` demands a line there, order that PR after F11.5 (still under RO-2's depth 9).
- **The parser is the vendored one.** WEB-3 requires `.claude/workflows/vendor/markdown-it.min.js` by the path `render_md.mjs` uses and adds no parser. RO-6 re-points the import when it moves the vendor directory.
- **The deploy publishes the page, the sub-pages and images, never a `.md`.**
  - It runs on the `v*` tag the stamp pushes, plus `workflow_dispatch`, so the site matches what HACS installs.
  - It runs `npm ci` and the generator in the site folder under `tools/`. WEB-3 owns that folder in `.github/CODEOWNERS`.
  - WEB-2's body shows `codeowners_gap.py`'s surface grew by exactly the owned generator (and its imports). After the dispatch it shows a `.md` path returning 404, one diagram drawn and one cross-page anchor landing.
- **Later groups keep the site true.**
  - RO-3 moves the page's image references with the images; the sub-pages follow the markdown by themselves.
  - RO-4 drops the backlog row from the page and from `EXCLUDE` when it archives `docs/backlog.md`.
  - The UX card groups add their gallery slots in the same PR as their screenshots.
- **Rev 4.1's rules stand.** That includes U4 budgets, U5 screenshots and the must-keep-working lists.
- **No `VERSION` edit.**

## Stop and tell tvofi (not ask) when

- `brief_lint` is non-zero after re-basing, and the only fix would weaken a citation;
- a build script refuses because a chain would grow;
- the diff in step 2 shows anything outside the listed entries;
- a page quote cannot be satisfied without changing what the docs say: the docs change is its own PR, never folded into WEB-1;
- the Pages deploy would publish a `.md`, or `codeowners_gap.py` reports an unowned path after WEB-3's owner line. In that case order WEB-2 before RO-2 (depth 8, zero slack, no chain growth) and say so.
