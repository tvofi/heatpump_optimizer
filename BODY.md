R10-PLAN-ARTIFACT: the round's plan page is built only by tracked instruments. `tools/audit/seat/plan_page.py --plan plan.json --html out.html` draws what the out-of-tree `gen.py` + `tpl.html` drew (reference `7bc61133` on `probe/plan-port-src`, read, not merged), from `tools/plan/replan.py`'s plan.json and the roster through `roster_lib`. It refuses (exit 1, nothing written) a plan whose roster blob is not the roster's blob at its ref now. `replan.py --check` applies the same rule, `replan.stale_reason`; until now it printed PLAN OK on a stale plan.

Design (fixer.md step 17):
- **The owner of the page is a new module beside `plan_table.py`, not an `--html` flag on it.** `plan_table.py` is in `tests/entities.py`'s recorded closure (`state_docs.py` spawns it), and its model is dependency depth over the roster. The page's model is replan's schedule. Folding the page into `plan_table.py` would put two models in one file and widen a recorded closure. `plan_page.py` sits under the INERT `tools/audit/` prefix, the same as every seat instrument.
- **The freshness rule has one owner, `replan.py`, because replan.py writes plan.json.** The page imports it, so `--check` and the page cannot disagree about which plans are current. `load_roster` now takes its blob from `replan.roster_blob`, so the blob is derived in one place.
- **plan.json now records the duration model it was computed with** (`generated.model`: sizes, live fraction, the sizes provenance). The ETA text states the plan's figures, not those of whatever `durations.json` holds at render time. A plan without that record is refused with a replan instruction.
- **What changed from `gen.py`:**
  - Dropped: the dependency-depth table, and "ready · depth N".
  - Every literal count is now filled from plan.json. Examples: the 5-group stamp cadence comes from `caps.stamp_every`, the 0-minute window from `caps.batch_window_minutes`, and the "S above M" sentence from `sizes_provenance`.
  - The axis runs to the last planned stamp. The minor stamp lands `closure_lead_minutes` after closure, so it was never drawn before.
  - The link caption printed the *skipped* count as the drawn count. It now prints the drawn count.
  - The tooltip is built with `textContent`, not `innerHTML`.
  - The round number and the `R<N>-` prefix come from the roster path, not a hard-coded `R10-`.
- **A third PR lookup was added, beyond the brief: the one roster group id a PR title names.** It is the last fallback, after `roster_lib.group_for_branch` and then gen.py's tail match. The live check below shows #2524 and #2528 named by neither branch rule. A title naming two groups maps to neither.

## Head

`e8810a6e7dd0c42bae53a7af801c4dd98854adce`. Merge base and `origin/main` tip at measurement: `6961f06637964001a2ed544e495ea0312eeefa37`, at 2026-10-21T10:45Z. Roster ref `origin/handoff/audit-r10-roster` at `05b3bd68f0f5`, roster blob `8974a63d916c`.

## Mutation proof

Driver: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`. It applies one exact one-occurrence replacement, runs `plan_page.py --self-test`, restores the file byte for byte, and refuses a file with uncommitted edits. Every row printed `verdict=killed`. Each row below gives the mutant, then the red checks:
- `live` (LIVE_STAGES branch → `False`): `live`, `rows carry the live class`, `the summary strip counts live`, `... ready`.
- `blocked` (`elif blk and not part:` → `False`): `blocked: an after target not done`, `rows carry the blocked class`, `the summary strip counts blocked`.
- `partial` (the `R<N>-X:` title match → `False`): `partial: a merged R9-PART: title on an open group`, `rows carry the partial class`.
- `blocked-by-less-done` (done targets kept in `blk`): `blocked-by is the roster's after less the done groups`, `ready: its only after target is done`.
- `pr-by-merge-commit`: `done: the PR is found by merge commit`.
- `pr-by-branch`: `done: the PR is found by branch when no merge commit matches`.
- `pr-sha8-fallback`: `done: no PR found falls back to the commit's sha8`.
- `branch-tail-fallback`: `the open PR maps by the branch-tail fallback`.
- `title-fallback`: `an open PR whose branch names no group maps by its title`.
- `closed-strike`: `a closed issue's chip is struck`.
- `tracking-excluded`: `the open-issue count leaves out the tracking issue`.
- `page-refuses-stale` (`if stale:` → `False` in `main`): `a stale plan is refused, nothing written`.
- `freshness-rule` (`if have != want:` → `False` in `replan.stale_reason`): `a stale plan is refused, nothing written`, `and replan --check refuses the same plan`.
- `stamp-on-axis`: `a planned stamp is drawn`.

`replan.py --self-test`'s own mutation harness has a new `freshness` row with the same deletion. It printed `mutation freshness: 'if have != want:' -> rc=1` and `ok self-test fails when freshness is deleted`.

One survivor in the first pass, disclosed: `pr-by-merge-commit` survived because fixture PR #21 also carried `R9-DONE-SHA:` in its title, so the title fallback answered for it. The fixture now names its group by merge commit alone, and the re-run kills it.

## Null control

- M0, nothing replaced: `RESULT mutant=M0 rc=0 fails=0 verdict=null`.
- **Freshness at the merge base: PLAN OK on a stale plan.** The plan was built at `--roster-ref b5ec0c98` (the roster one commit back, blob `eaf4288a90d0`) and relabelled to the live ref. The base's `replan.py --check` printed `PLAN OK` with rc 0. The head refused it, rc 1: `freshness: plan.json is stale: built from roster blob eaf4288a90d0, but origin/handoff/audit-r10-roster:... is now 8974a63d916c`. The head passes a plan built at the live blob (`PLAN OK`, rc 0). On the stale plan, the page printed `refused, nothing written`, rc 1, and the output file did not exist afterwards.
- **The refusal fired for real once during this work.** A plan built before a fetch moved the roster ref (blob `d5b1fbee4f8d` → `8974a63d916c`) was refused by the page's own fetch-then-check.
- `selftest_wiring.py --check` with `governance.yml` reverted to the base printed `UNWIRED tools/audit/seat/plan_page.py` (`37 wired, 1 unwired`). At the head it printed `38 wired, 0 unwired`.
- **The mermaid `;` needs no fix.** Harness: `node dev/audit/harnesses/r10_mermaid_gantt_title.mjs <dir>` over mermaid 11.4.1 and jsdom 24.1.3 from npm. On `plan_table.gantt()` of its own fixture it printed `RESULT arm=tree parsed=true title="Fix waves; crit = the critical path"`. The 11.4.1 lexer rule is `title\s[^\n]+`, so a title runs to the line's end. The null arm, `; x` appended to the `dateFormat` line (rule `[^#\n;]+`), printed `parsed=false`. So the parser can refuse a `;`; it does not refuse one in the title. `plan_table.py` is unchanged.

## Figures

- `plan_page self-test: 36 checks, 0 failed`: `python3 -I tools/audit/seat/plan_page.py --self-test`. GitHub is never reached: `main` runs with a fetch that fails the test if called.
- `self-test: 0 failed`, including 6 new freshness arms and the `freshness` mutant: `python3 tools/plan/replan.py --self-test`.
- `RESULT survived=0`: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`.
- Live page against the roster at blob `8974a63d916c`: `python3 tools/plan/replan.py --out plan.json` then `python3 tools/audit/seat/plan_page.py --plan plan.json --html round-10-plan.html --github-snapshot snap.json`. This container's `gh` token is refused (`gh auth status`: "The token in GH_TOKEN is invalid"), so the snapshot was assembled as follows:
  - Open PRs and open issues from the GitHub MCP tools (`list_pull_requests state=open`, `list_issues state=OPEN`).
  - Roster issues not open marked CLOSED.
  - Merged PRs from `git log origin/main --first-parent --merges` "Merge pull request #N from <owner>/<branch>" subjects, with merge sha and title. This misses a squash-merged PR. The 2026-10-10 onward non-merge first-parent commits are stamps, nightly-kill records and three `record:` rows, none of them a group's PR.
- What the sanity checks measured on that page, out-of-tree style, each by regex over the written HTML:
  - Group rows: 108, and the roster has 108 groups.
  - Name set equal to the roster's, with the `R10-` prefix stripped.
  - Stages: 50 done rows against 50 roster `done`. 21 live rows against 21 `in-progress`. 14 ready + 23 blocked = 37, against 34 `not-started` + 3 `queued`.
  - Open PRs shown on open rows: 11 of 14 (#2513 #2521 #2524 #2527 #2528 #2529 #2531 #2545 #2547 #2548 #2549). #2529 maps by the tail fallback (`fix/r10-ci-layout-g` → R10-CI-LAYOUT). #2524 and #2528 map by title.
  - The three not shown, each dispositioned: #2550 is a `record:` row, owned by no group. #2544, the dependency bump, names no group by branch or title; R10-DEPENDABOT-AIOHTTP's `resume.branch` is `fix/r10-dependabot-aiohttp`. #2525 maps by title to R10-OPENPR-SILENT, a done group, whose row shows its merged PR #2422 by design.
  - Merged PRs shown on an open row: 0.
  - Done rows whose PR cell is a number: 50 of 50.
  - Machine paths (`/home/`, `/Users/`, `/tmp/`) in the page: 0, by `grep -c`.
- `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`: `python3 -I tools/audit/seat/selftest_wiring.py --check`.
- `tmp_paths: 0 refused`: `python3 -I tools/audit/seat/tmp_paths.py --check`.
- `ref_privacy --check ... 0 refused`: `python3 -I tools/audit/seat/ref_privacy.py --check`.
- Scope: `python3 tests/closure.py select --diff 6961f0663796 --workdir "$D"` printed `MODE: FULL`, reason `tests/closure.py changes the gate itself`. The change there is the INERT comment for `tools/plan/`, which named the out-of-tree renderer. The following were run locally with `PYTHONPATH=tests/hastub` and the seat venv; the rest is CI's:
  - `ALL 2375 ENTITY CHECKS PASSED`: `python3 tests/entities.py`.
  - `ALL 109 HARNESS HEADER CHECKS PASSED`: `python3 tests/harness_headers.py`.
  - `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`.
  - `ALL 124 closure shrink pins PASSED`: `python3 tests/closure.py selftest`.
  - `claims hygiene: origin/main ok`: `python3 tests/env_drift.py --claims-only origin/main`.
  - `layout self-test: ok`: `python3 tests/layout.py`.
- `tests/closures.json` gains one `inert_reads` entry, `tests/harness_headers.py` -> `dev/audit/harnesses/r10_plan_page_mutants.py`. That script discovers harness files by their RESULT headers, and prepr's closure predictor refused the head without the entry (`CI PREDICT: 1 predicted red(s) on closures`). It was written by `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --apply-inert`, which then printed `CI PREDICT: no closures or fast red predicted`. The code is byte-identical to the head the figures above were first taken at (`0a0d5d06`). The three self-test and mutant figures were re-taken at this head.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main`. No file under `custom_components/` changed.

## Red checks

`none` at hand-off. One local red, answered: `tests/harness_headers.py` refused the first copy of `r10_plan_page_mutants.py` (`depth seams: ... parents[3]`). It now uses the canonical `repo_root` walk. The cheaper detector is that script itself, run locally before the push as it was here, so nothing further is owed.

## Unpinned sites

n/a: no production module under `custom_components/` changed. The predicates `plan_page.py` adds are each pinned by a self-test arm, shown killed under `## Mutation proof`.

## Forward-carry

- R10-ORCH-MACHINERY's item (3), "the plan page as a tree instrument sharing one model builder with `plan_table.py`, driven by `state_docs.py` ... failing to an explicit UNAVAILABLE page", is partly landed here, and its premise changed:
  - The page exists as `tools/audit/seat/plan_page.py`.
  - Its model is the schedule replan.py writes, not `plan_table.py`'s dependency-depth waves. The two cannot share one builder without one of them computing a schedule the other does not hold.
  - It refuses a stale or violating plan with exit 1 and writes nothing, rather than writing a page of zeros.
  - What remains for that stage: driving it from `state_docs.py`; an UNAVAILABLE page in place of no page, if the design still wants one; and the five generator-defect fixtures. Before building on this, re-measure with `python3 -I tools/audit/seat/plan_page.py --self-test` at that stage's merge base.

  Carry: R10-ORCH-MACHINERY
- The orchestrator's out-of-tree `gen.py` / `tpl.html` should be retired once this merges, since the page they drew is now this instrument's output. The re-measure is the live sanity run under `## Figures`. Carry: R10-ORCH-MACHINERY

## Friction

`none`

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01C68C1zSdZZ7gKc15C8NY6e
