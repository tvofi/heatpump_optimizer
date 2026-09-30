# Prompt (rev 4.2): the round-9 fixing orchestrator adopts lane WEB (the product page) into the live roster

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting. Nothing below loosens them.

**The mandate** of 2026-09-29 stands, with rev 4.1's exception: it does **not** pre-confirm structure-budget raises for lane UX (U4), and the same holds for lane WEB. None is expected, because no structure metric measures `docs/` or `tests/`.

What remains for tvofi's hands, and you request it; you never wait on it silently:
- approving reviews at the head for WEB-1 (`tests/closure.py`, `tests/layout.json`) and WEB-2 (`.github/workflows`);
- a one-time repository setting before WEB-2's first dispatch: Settings → Pages → Source: "GitHub Actions";
- decision S3 below, only if tvofi wants a savings figure on the page.

## Background

- Rev 4.1 (lane UX, Part of #1795) is applied on `handoff/audit-r9-fixplan`. The live roster was at `9e63d2a3` when this revision was written; origin/main was at `aac8fb77` (after #1794).
- tvofi asked on 2026-09-30: "Design a full product web page, based on the user facing documentation in the repo, in the same design language as the showcase page, then make a rev 4.2 of the plan where implementation of this page and pining it to the master documentation is added." The decisions:
  - W1: pinning is test-pinned and linked. Every claim on the page carries a source anchor into the README or a reader doc, a test refuses drift, and the README links the page.
  - W2: the page is served by GitHub Pages through a workflow.
  - S3 (a design decision, open to tvofi): no savings percentage, because the docs call the only one a one-off measurement on the author's house.
- Everything is on branch `handoff/audit-r9-alt`:
  - `handoff/round9/state/alt/design/site/` (commit `2b5031bf`): `DESIGN-SITE.md`, the page `index.html`, the pin prototype `check_site.py`, `controls.py` and `SITE-CHECKS.txt`, `CONTRAST.json`, the shots;
  - `handoff/round9/state/ALT-ENDGAME-PLAN.md`, section R6 (rev 4.2);
  - `handoff/round9/state/ALT-ROSTER.json`: roster rev 4.2, 99 groups, acyclic, `brief_lint` `TOTAL: 0 error(s)`;
  - `handoff/round9/state/alt/build_roster_rev42.py`, which rebuilds it from the live file.

Before step 1, read plan section R6 and `DESIGN-SITE.md`.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `aac8fb77` and every commit on `handoff/audit-r9-fixplan` since `9e63d2a3`, and truth each group's stage.
   - If a merge touched `README.md`, `DISCLAIMER.md`, a reader doc under `docs/`, `docs/img/` or `docs/setup/`, re-run the pin prototype at your origin/main: `HPO_REPO=<checkout> python3 handoff/round9/state/alt/design/site/check_site.py handoff/round9/state/alt/design/site/index.html --ref origin/main`.
   - A red line there is a quote the docs no longer make. Record it in WEB-1's resume note as a page fix WEB-1 owes. Never weaken the rule.

2. **Apply rev 4.2** to the live roster on `handoff/audit-r9-fixplan`.
   - Run `python3 handoff/round9/state/alt/build_roster_rev42.py <live wave-r9-groups.json> <out> 2b5031bf`.
     - It refuses a file without R9-UX-1, a file that already has R9-WEB-1, a dangling edge, a cycle, and any result that lengthens the longest open chain or EG-A4's.
     - It prints the depths: WEB-1 6 and WEB-2 7 at `9e63d2a3`.
   - Fetch `handoff/audit-r9-alt`, `handoff/silent-windows-plan` and `handoff/repo-reorg-plan`. Then lint with origin/main's `.claude/workflows/brief_lint.mjs`; it must print `TOTAL: 0 error(s)`.
   - Diff the output against the live file. Only these may differ:
     - the two new groups;
     - RO-2's and RO-3's `after`;
     - appended carries on the briefs of RO-3, RO-4, RO-9, UX-1, UX-2, UX-3, UX-5, UX-6 and UX-7;
     - one `_comment`.
   - Re-run the coverage (`alt/gen_coverage_rev31.py`) on the live open-issue list. #1793 is the one issue that is uncovered on purpose.
   - Commit the result as the live roster.

3. **File one feature issue for lane WEB**, with W1, W2 and S3, `DESIGN-SITE.md` at `2b5031bf`, the two groups and their order, and the gallery-slot carries into lane UX.
   - Read it back.
   - Write its number into WEB-1's and WEB-2's `issues`. WEB-1 is Part of it; WEB-2 Fixes it.

4. **Post one #201 comment** with `gh_comment.py` and read it back. It covers:
   - rev 4.2 adopted, with the roster commit;
   - W1, W2 and S3;
   - the new WEB issue;
   - the chain arithmetic (unchanged at 12 and 11; WEB-1 at depth 6 and WEB-2 at 7, both with slack);
   - tvofi's two reviews and the Pages setting.

5. **Dispatch.**
   - WEB-1 when UI-2, UI-4 and F10.4 have merged.
   - WEB-2 when WEB-1 has merged. Ask tvofi for the Pages setting when you dispatch it, not later.
   - Everything else continues per rev 4.1, one merge at a time.

## Rules specific to rev 4.2

- **Pinned, not paraphrased.** Every sentence of fact on the page is quoted from a documented section. The arm refuses:
  - a quote the section no longer makes;
  - a number the section does not state;
  - a digit outside a claim;
  - a missing README feature lead or Documentation row, or an extra one;
  - a dead image or repository link;
  - a version literal;
  - any third-party request.

  A reviewer returns blocked on a claim element without `data-src` that states a fact, and on `data-copy` used to
  exempt one.
- **The arm reads the working tree.** It is one new function in `tests/doc_claims.py` with its own anchor, named in the module docstring. It is not a new test script, so `tests/run.sh` is untouched. The closure is re-recorded by CI's autofix, not by hand.
- **No `tests/README.md` edit in WEB-1.** It is code-owned and in the F11.4/F11.5 lane. If `tests/entities.py` demands a line there, order WEB-1 after F11.5 (depth 8, still under RO-2's 9).
- **The workflow publishes images and the page, never a `.md`,** and runs no repository script. WEB-2's body shows `codeowners_gap.py`'s surface count unchanged, and after its dispatch shows a `.md` path returning 404.
- **Deploys follow releases.** The trigger is the `v*` tag the stamp pushes, plus `workflow_dispatch`, so the served page matches what HACS installs.
- **Later groups keep the page true.**
  - RO-3 moves the page's image references with the images.
  - RO-4 drops the backlog row from the page when it archives `docs/backlog.md`.
  - The UX card groups add their gallery slots in the same PR as their screenshots.
- **Rev 4.1's rules stand.** That includes U4 budgets, U5 screenshots and the must-keep-working lists.
- **No `VERSION` edit.**

## Stop and tell tvofi (not ask) when

- `brief_lint` is non-zero after re-basing, and the only fix would weaken a citation;
- the build script refuses because a chain would grow;
- the diff in step 2 shows anything outside the listed entries;
- a page quote cannot be satisfied without changing what the docs say: the docs change is its own PR, never folded into WEB-1;
- the Pages deploy would publish a `.md`, or needs a repository script.
