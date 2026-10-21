R10-PLAN-ARTIFACT: the round's plan page is built only by tracked instruments. `tools/audit/seat/plan_page.py --plan plan.json --html out.html` draws what the out-of-tree `gen.py` + `tpl.html` drew (reference `7bc61133` on `probe/plan-port-src`, read, not merged), from `tools/plan/replan.py`'s plan.json and the roster through `roster_lib`. It refuses (exit 1, nothing written) a plan whose roster blob is not the roster's blob at its ref now. `replan.py --check` applies the same rule, `replan.stale_reason`; until now it printed PLAN OK on a stale plan.

Design (fixer.md step 17):
- **The owner of the page is a new module beside `plan_table.py`, not an `--html` flag on it.** `plan_table.py` is in `tests/entities.py`'s recorded closure (`state_docs.py` spawns it), and its model is dependency depth over the roster. The page's model is replan's schedule. Folding the page into `plan_table.py` would put two models in one file and widen a recorded closure. `plan_page.py` sits under the INERT `tools/audit/` prefix, the same as every seat instrument.
- **The freshness rule has one owner, `replan.py`, because replan.py writes plan.json.** The page imports it, so `--check` and the page cannot disagree about which plans are current. `load_roster` now takes its blob from `replan.roster_blob`, so the blob is derived in one place.
- **plan.json now records the duration model it was computed with** (`generated.model`: sizes, live fraction, the sizes provenance). The ETA text states the plan's figures, not those of whatever `durations.json` holds at render time. A fresh plan without that record is refused with a replan instruction, exit 1, nothing written (self-test arm `a fresh plan recording no duration model is refused, nothing written`).
- **What changed from `gen.py`:**
  - Dropped: the dependency-depth table, and "ready · depth N".
  - Every literal count is now filled from plan.json. Examples: the 5-group stamp cadence comes from `caps.stamp_every`, the 0-minute window from `caps.batch_window_minutes`, and the "S above M" sentence from `sizes_provenance`.
  - The axis runs to the last planned stamp. The minor stamp lands `closure_lead_minutes` after closure, so it was never drawn before.
  - The link caption printed the *skipped* count as the drawn count. It now prints the drawn count.
  - The tooltip is built with `textContent`, not `innerHTML`.
  - The round number and the `R<N>-` prefix come from the roster path, not a hard-coded `R10-`.
- **A third PR lookup was added, beyond the brief: the one roster group id a PR title names.** It is the last fallback, after `roster_lib.group_for_branch` and then gen.py's tail match. The live check below shows #2524 and #2528 named by neither branch rule. A title naming two groups maps to neither.

## Head

`a4a2a653333cf41b73759587e0fa396a7cabaabe`. It is the merge of origin/main `1ebc737e7e187a1d45c62069ae8ab69c465db928` (measured 2026-10-21T21:28Z) into the round-2 code commit, which sits on the PR's reviewed head `59c5b20ef0d7beef377fe2580bd87f9fdb783ff7`. The merge was clean and brought 3 files, none of them this PR's (`dev/programme/delivery/2583.md` among them). Every figure below was re-taken at `a4a2a653333cf41b73759587e0fa396a7cabaabe` unless it says otherwise.

Round 2 answers the fix review at `probe/rev-2558-e98d4b97` (blocked: mutation-survivor plus carry-missing). Production code is unchanged in this round: the diff since `59c5b20e` adds self-test arms to `plan_page.py` and `replan.py` and four rows to `dev/audit/harnesses/r10_plan_page_mutants.py`.

- **B** (`generated.model` refusal): arm `a fresh plan recording no duration model is refused, nothing written`. It runs `main` on a fresh plan with `generated.model` deleted and expects rc 1, no file, and `generated.model` named on stderr. A crash counts as a failed arm, not a refusal.
- **C** (`check_plan` refusal): arm `a fresh plan that check_plan refuses is refused, nothing written`. The plan's `summary.stamps` is raised by one, and the arm expects rc 1, no file, and `summary: stamp count` on stderr. The precondition arm `the violating variant is fresh: only check_plan can refuse it` asserts `stale_reason` is None and `check_plan` is non-empty for that variant.
- **D** (the caption's drawn count): two arms, one each way. In the base fixture the chart draws 0 of 1 critical-path links: `R9-LIVE` and `R9-BLOCK` share a track back to back, so 0 drawn against 1 skipped. In a variant with `R9-BLOCK` in the adjacent lane it draws 1 of 1, so 1 drawn against 0 skipped. Each arm asserts the caption figure and the `critline` count in the page.
- **E** (an explicit ref outranks `generated.roster_ref`): this one is in scope. Two arms in `replan.py --self-test`, after the roster has moved on `main`: `an explicit ref is read instead of generated.roster_ref` (`stale_reason(fresh, repo, "main~1")` is None while `generated.roster_ref` is `main`), and `--check --roster-ref passes the plan at the ref it names` (rc 0).

## Mutation proof

Driver: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`. It applies one exact one-occurrence replacement, runs `plan_page.py --self-test` (plus `replan.py --self-test` for a `replan.py` mutant and for M0), restores the file byte for byte, and refuses a file with uncommitted edits. It counts a mutant that kills only by crashing as CRASHED, never killed. At `a4a2a653333cf41b73759587e0fa396a7cabaabe` it printed `RESULT survived=0`. Each row is applied alone. Rows B to E are new this round and are modelled on the reviewer's `ev/reviewer_mutants_driver.py`, with the same anchors:

| mutant | replacement | rc | FAIL lines (checks that went red) |
|---|---|---|---|
| M0 | none | 0 | none (null) |
| live | LIVE_STAGES branch -> `False` | 1 | `live`, `rows carry the live class`, `the summary strip counts live`, `... ready` (5) |
| blocked | `elif blk and not part:` -> `False` | 1 | `blocked: an after target not done`, `rows carry the blocked class`, ... (5) |
| partial | the `R<N>-X:` title match -> `False` | 1 | `partial: a merged R9-PART: title on an open group`, ... (5) |
| blocked-by-less-done | done targets kept in `blk` | 1 | `blocked-by is the roster's after less the done groups`, ... (6) |
| pr-by-merge-commit | merge-commit match -> `False` | 1 | `done: the PR is found by merge commit` |
| pr-by-branch | `by_group[g] = ...` -> `pass` | 1 | `done: the PR is found by branch when no merge commit matches` |
| pr-sha8-fallback | sha8 label -> folded label | 1 | `done: no PR found falls back to the commit's sha8` |
| branch-tail-fallback | `return None` | 1 | `the open PR maps by the branch-tail fallback` |
| title-fallback | `return None` | 1 | `an open PR whose branch names no group maps by its title` |
| closed-strike | `" closed"` dropped | 1 | `a closed issue's chip is struck` |
| tracking-excluded | tracking issue counted | 1 | `the open-issue count leaves out the tracking issue` |
| page-refuses-stale | `if stale:` -> `if False:` | 1 | `a stale plan is refused, nothing written` |
| freshness-rule | `if have != want:` -> `if False:` (replan.py) | 1 | `a stale plan is refused, nothing written`, `and replan --check refuses the same plan`, replan's `a roster commit after the replan makes the plan stale`, `--check exits 1 on a stale plan`, plus 2 lines from replan's in-suite mutation harness, which loses its anchor (6) |
| stamp-on-axis | axis ends at closure | 1 | `a planned stamp is drawn` |
| **B-model-record-refusal** | `if "model" not in plan["generated"]:` -> `if False:` | 1 | `a fresh plan recording no duration model is refused, nothing written` |
| **C-check_plan-refusal** | `bad = replan.check_plan(plan)` -> `bad = []` | 1 | `a fresh plan that check_plan refuses is refused, nothing written`, `a stale plan is refused, nothing written` (2; the second is a knock-on: the accepted variant leaves the output file behind) |
| **D-caption-drawn-count** | caption `{drawn} of` -> `{max(0, len(chain) - 1) - drawn} of` | 1 | `the caption counts the links drawn (none drawn, one left)`, `the caption counts the links drawn (one drawn, none left)` |
| **E-explicit-ref-wins** | `ref = ref or gen.get("roster_ref") or ""` -> `ref = gen.get("roster_ref") or ref or ""` (replan.py) | 1 | `an explicit ref is read instead of generated.roster_ref`, `--check --roster-ref passes the plan at the ref it names`, plus replan's in-suite null control `the unmutated copy's self-test exits 0` (3) |

Unmutated, at the same head: `plan_page self-test: 41 checks, 0 failed` and `replan.py --self-test`: `self-test: 0 failed`. So each new arm passes unmutated and fails under its own mutant.

Independent cross-check: the reviewer's own driver (`ev/reviewer_mutants_driver.py` from `probe/rev-2558-e98d4b97`) was run unchanged at `a4a2a653333cf41b73759587e0fa396a7cabaabe`. M0 gave rc 0/0 (page/replan). A was killed (rc 0/1). B, C and D were killed (page rc 1). E was killed (rc 0/1).

`replan.py --self-test`'s own mutation harness keeps its `freshness` row: `mutation freshness: 'if have != want:' -> rc=1`.

## Null control

- M0, nothing replaced: `RESULT mutant=M0 rc=0 fails=0 verdict=null`. That run covers both suites.
- D's two fixtures are their own controls. The figure a correct caption prints and the figure the mutant prints differ in both: 0 against 1, then 1 against 0. A constant caption (`0 of` or `1 of`) would fail one of the two.
- C's precondition arm shows that the refusal it pins can only come from `check_plan`, because the variant is fresh by `stale_reason`. Without that arm, C's arm could pass on a freshness refusal.
- E's arm reads `main~1`, which still holds the plan's blob. On the same tree with no override, `main` refuses the plan as stale: that is the existing arm `a roster commit after the replan makes the plan stale`. So the override is what passes it.
- Round 1 (head `e8810a6e`), not re-taken because this round changes no production line: freshness at the merge base printed PLAN OK on a stale plan, and the head refused it; `selftest_wiring` with `governance.yml` reverted printed `UNWIRED tools/audit/seat/plan_page.py`; the mermaid `;` harness (`node dev/audit/harnesses/r10_mermaid_gantt_title.mjs`) printed `parsed=true` on the title and `parsed=false` on the null arm.

## Figures

At `a4a2a653333cf41b73759587e0fa396a7cabaabe`, unless marked:
- `plan_page self-test: 41 checks, 0 failed`: `python3 -I tools/audit/seat/plan_page.py --self-test`. That is 5 checks more than round 1's 36: B, C plus its precondition, and D's two. GitHub is never reached, because `main` runs with a fetch that fails the test if called.
- `self-test: 0 failed`, 41 `ok` lines: `python3 tools/plan/replan.py --self-test` (and `| grep -c '^ok'`).
- `RESULT survived=0` over 19 mutants plus M0: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`.
- `selftest_wiring: 39 self-testing, 39 wired, 0 unwired`: `python3 -I tools/audit/seat/selftest_wiring.py --check`. Round 1 printed 38, before main added one instrument.
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`.
- `ALL 124 closure shrink pins PASSED`: `python3 tests/closure.py selftest`.
- `layout self-test: ok`: `python3 tests/layout.py`.
- `claims hygiene: origin/main ok`: `python3 tests/env_drift.py --claims-only origin/main`.
- `CI PREDICT: no closures or fast red predicted against 1ebc737e7e18`: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main`. No file under `custom_components/` changed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL`, reason `tests/closure.py changes the gate itself`. That is round 1's INERT comment for `tools/plan/`, unchanged here. The rest is CI's.
- `ALL 2382 ENTITY CHECKS PASSED`: `python3 tests/entities.py`, and `ALL 109 HARNESS HEADER CHECKS PASSED`: `python3 tests/harness_headers.py`. Both ran with `PYTHONPATH=tests/hastub` in a scratch python3.13 venv built from `tests/requirements-ci.txt` with `--require-hashes`. This container's `python3` 3.11 cannot import the hastub (`No module named 'voluptuous'`).
- **Live page figures (round 1, at `e8810a6e`, 2026-10-21T10:45Z, roster blob `8974a63d916c`): not re-taken.** These are 108 rows, the stage counts, and 11 of 14 open PRs. They depend on the roster and on a GitHub snapshot assembled by hand that is not committed. This round changes no line `render`, `build_rows` or `swimlanes` executes, so the page these figures describe is the same function of its inputs. The roster has since grown, so the counts themselves would differ today. The reviewer could not re-derive them either.
- `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`, rc 0: `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>`, roster at `4cae0b9dab15`. Null control: with the self-carry written `(item B-E)` and the Friction line unrouted, the same command printed `1 unrouted, 1 bad destination(s)`, rc 1 (see `## Forward-carry` (`python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>`).

## Red checks

At the PR's reviewed head `59c5b20ef0d7beef377fe2580bd87f9fdb783ff7` (check-runs read at about 21:30Z), the one red is `nightly-status` (job 119485352084). Every other concluded check is green or skipped. `fast (3.14)`, `coverage` and `Analyze (python)` were still in progress. This round's head `a4a2a653333cf41b73759587e0fa396a7cabaabe` has not been pushed through CI yet.

- **`nightly-status` (job 119485352084 at `59c5b20e`): main's red, not this diff's.** It grades `main`'s scheduled `tests.yml` run 39563978649 (`NIGHTLY FAILED: mutation-nightly, slow`), head `c77f89d`, which is an ancestor of this branch's base. This diff does not change `tests.yml` or `tests/nightly_status.py`. Its one `governance.yml` step runs the page's self-test, which that reporter does not read. Owned on `main` by the orchestrator, per `defect-root-cause.md`. No cheaper detector is owed by this diff.
- Round-1 reds, already answered and now green: `closures` at `2b1ba538` was repaired by `closures-autofix` in `43b1307`. The cheaper detector, `ci_predict.py`'s `inert_siblings`, missed it because of its 3-sibling threshold; that root cause belongs to its own seat, not this fix. `pr-contract` at `43b1307` was `BAD-DEST R10-ORCH-MACHINERY`, because the group was not yet in the head's tree roster. It is green at `59c5b20e` (jobs 119485351325 and 119485887676), after the orchestrator's main merge.
- **`closures` at the merged head (predicted, not yet run).** Merging origin/main into `a4a2a653` and running `ci_predict.py` predicts `closures` red: `tools/audit/seat/plan_page.py` is a new file beside 6 siblings that `tests/entities.py` lists as INERT. `closures-autofix` repairs exactly this shape (`ci-autofix.md`: wait for the bot commit, do not duplicate), and the round-1 occurrence was repaired the same way in `43b1307`. No code change is made here.
- Local, not CI: `tests/entities.py` and `tests/harness_headers.py` need the CI requirements (`voluptuous`, `aiohttp`), which this container's `python3` lacks. They were run in a scratch venv built from `tests/requirements-ci.txt` with `--require-hashes` (result under `## Figures`).

## Unpinned sites

n/a: no production module under `custom_components/` changed. Every predicate `plan_page.py` adds is now pinned by a self-test arm and shown killed in the table under `## Mutation proof`. That includes the round-1 survivors B (`generated.model` refusal), C (`check_plan` refusal) and D (caption drawn count), and E in `replan.stale_reason`. The table has 19 rows, every one `killed`, with `RESULT survived=0`.

## Forward-carry

- R10-ORCH-MACHINERY's item (3), "the plan page as a tree instrument sharing one model builder with `plan_table.py`, driven by `state_docs.py` ... failing to an explicit UNAVAILABLE page", is partly landed here, and its premise changed:
  - The page exists as `tools/audit/seat/plan_page.py`.
  - Its model is the schedule `replan.py` writes, not `plan_table.py`'s dependency-depth waves. The page cannot share one model builder with `plan_table.py` without one of them computing a schedule the other does not hold.
  - It refuses a stale, violating or model-less plan with exit 1 and writes nothing, rather than writing a page of zeros. Each refusal is pinned (see `## Mutation proof`).
  - What remains for that stage: driving it from `state_docs.py`; an UNAVAILABLE page in place of no page, if the design still wants one; and the five generator-defect fixtures.
  - Precondition (the control): before building on this, that stage re-measures `python3 -I tools/audit/seat/plan_page.py --self-test` at its own merge base and expects 0 failed.
  - Roster: the orchestrator landed this carry, and this seat did not edit the roster. It is on `origin/handoff/audit-r10-roster` at `7213e761ea5a47f6aa9bace1b03620e650b1cd3c` (`roster_edit append-carry R10-ORCH-MACHINERY`, 2026-10-21T21:35:40Z). It is still present at the tip I re-fetched, `4cae0b9dab15fa20f0f25d31724349cbe00ed0f6`. The carry entry reads "From #2558 (R10-PLAN-ARTIFACT; verdict at origin/probe/rev-2558-e98d4b97): item (3)'s premise changed. ... Also retire the out-of-tree gen.py/tpl.html. Control: plan_page.py --self-test re-measured at that stage's merge base, as a precondition." The group's `brief` text for (3) is unchanged, so the carry is what records the change.
  - The STUDY K17 carry at `8162c672d99d15d7cb5e11e8a6d2ba51ddc30138` agrees with it. Its item (6) reads "if R10-PLAN-ARTIFACT (#2558) merges first, part (3) extracts plan_model() from its code rather than building a second page".

  Carry: R10-ORCH-MACHINERY (item 3)
- The orchestrator's out-of-tree `gen.py` / `tpl.html` are retired once this merges, since the page they drew is now this instrument's output. Same precondition: `plan_page.py --self-test` re-measured at that stage's merge base. Carry: R10-ORCH-MACHINERY (item 3)
- The fix review's survivors B to E are closed in this PR (above). Carry: R10-PLAN-ARTIFACT

## Friction

none

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01C68C1zSdZZ7gKc15C8NY6e
https://claude.ai/code/session_01S25pjzsWGC2U7zMp9yJg5U
https://claude.ai/code/session_019sdA2ZdyXWX1knTTxVxfSH
