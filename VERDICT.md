Fix review: merge 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b

bus-nonce: 56de8255aecb7dcf032842f1d886a3d1

## Scope

Round: this is the third review of #3350's resolution-delta series (ab236e01 merge, 9f4a1a41 blocked, now 3377b5f0). Under the owner's 2026-11-09 ruling I reviewed only `git diff 9f4a1a41078ab70510afe7e2413ac603e0ffdd56 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b`. `review_carry.py 9f4a1a410 3377b5f06` prints `FRESH-REVIEW`.

The delta contains the selftest_scope repair (bb84b1bd2), a merge of origin/main 2f6d699e5 with one textual conflict (855003fbf), four follow-up commits (7f505becb, f86004e5c, 9dca46ba9, c0ad3ad51) and one production-code commit (f95b593a5, `translations/de.json`).

I compared the branch's own diff at each end per file: `f365ce7..9f4a1a4` against `2f6d699..3377b5f` (`ev/interdiff-files.txt`). These files differ:
- `governance.yml`
- `de.json`
- `selftest_closures.json`
- `tests/closures.json`
- `replan.py`
- `plan_page.py`
- the two harnesses

Every other file is byte-identical in its added and removed lines and stands on the earlier verdicts.

The only production delta is the five German strings. They are text only and change no code path, so the review is not widened. `tests/closures.json` differs only because main already lists `tools/audit/seat/pr_cap.py`, which the branch had added before. Nothing is lost or duplicated.

## Previous verdict's finding: resolved

The previous verdict was `blocked 9f4a1a41 resolution-ungated-step`.

At this head, the step `Show the bottleneck alert ...` has `id: bottleneck-alert` and `if: steps.scope.outputs.bottleneck-alert == 'true'`, and `tools/ci/selftest_closures.json` has a `bottleneck-alert` row.

- `python3 -I tools/ci/selftest_scope.py --self-test` prints `ok   the live job parses (116 steps) and its gating is consistent` and `selftest_scope self-test: 90 checks, 0 failed`, rc 0 (`ev/selftest-scope-selftest-head.txt`). At 9f4a1a41 the previous verdict measured `1 failed`.
- **The table row is live.** In a scratch commit on a detached worktree, a one-line append to `tools/audit/seat/bottleneck_check.py` gives `MODE: SCOPED -- 20 step(s) run`, naming `run bottleneck-alert`, with no stale-table refusal (`ev/selftest-scope-select-probe.txt`).
- **Null control.** The same append to `tools/plan/replan.py` gives `MODE: SCOPED -- 25 step(s) run` without `bottleneck-alert` (`ev/selftest-scope-select-null.txt`).
- CI: the required-adjacent lane `governance / instrument-self-tests` (job 129352818254) concluded `success` at this head.

## Evidence

- Head reviewed: 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b (`ev/HEAD.txt`). Re-read before writing: `refs/pull/3350/head` is still 3377b5f0, and origin/main is 2f6d699e5 (`ev/head-recheck.txt`).
- The PR body's `## Head` names 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b.
- **Merge check.** `git merge-tree --write-tree origin/main 3377b5f0660d421e6c8eb01a5f50c9ef114a6c4b` exits rc 0 with tree 1e662c3e3364f61ebdf65f2c87f45cbb88a15d9a, so there is no conflict (`ev/merge-tree.txt`). The head contains main.
- **Conflict resolution in `replan.py`** (855003fbf; `ev/old-replan.py.patch`, `ev/new-replan.py.patch`). `dependency_graph(G, legacy)` keeps the discharged-as-done read beside main's `roster_lib.gates(G[a])` edge release. `build_plan` computes `held_behind_deferred(live)` over the roster less its discharged groups, so a discharged group is neither held nor holds. `python3 tools/plan/replan.py --self-test` prints `self-test: 0 failed`, rc 0, including the new 3d pair and its null.
- **Semantic resolution in `plan_page.py`** (7f505becb). The blocked list is `if a in G and a not in discharged and roster_lib.gates(G[a])`. `python3 -I tools/audit/seat/plan_page.py --self-test` prints `plan_page self-test: 76 checks, 0 failed`. `roster_lib.py --self-test` prints `81 checks, 0 failed`, and `bottleneck_check.py --self-test` prints `ok`.
- **My own mutants** (step 1). Each was applied by hand in a detached worktree at the head and then restored (`ev/mut-*.txt`):
  - `held = roster_lib.held_behind_deferred(live)` -> `(G)`, on the production line only: rc 1, `FAIL discharged behind deferred: closed and not held; its dependent released`.
  - `discharged = {...}` -> `set()`: rc 1, 2 behaviour FAILs (the discharged pair).
  - `dependency_graph(G, legacy)` -> `dependency_graph(G)`: rc 1, `FAIL discharged: a legacy carry is not owed (the cut-over is read)`.
  - plan_page drop of `a not in discharged and`: rc 1, `FAIL discharged: rendered merged, naming the record step it owes`.
  - plan_page drop of `and roster_lib.gates(G[a])`: rc 1, 3 FAILs (`ready: its only after target is done`, `defect 2: ...`, `blocked-by is the roster's after less the done groups`).

  All five are killed.
- **Group harnesses on the resolution rows**:
  - `python3 -I dev/audit/harnesses/r10_outside_intake_p2_mutants.py M0 page-discharged-edge replan-discharged-arm replan-legacy-dropped` prints M0 `verdict=null`, each row `verdict=killed`, `RESULT survived=0`.
  - `python3 -I dev/audit/harnesses/r10_plan_page_mutants.py M0 stamp-on-axis blocked-by-less-done defect-2-scratch-graph` prints M0 `verdict=null`, each row `verdict=killed`, `RESULT survived=0`.

  Both are in `ev/harness-*-rows.txt`. Full runs of both harnesses hit my own 230 s per-command timeout locally and were restored by `mutant_guard` (`ev/head-r10_*_mutants.py.txt`). I did not re-derive the body's figure `RESULT survived=0` for all rows; only the rows above are verified.
- **`de.json`** (f95b593a5):
  - **Key parity.** At main 2f6d699e5, en.json has 5 keys that de.json lacks (`flow_min_lift_k` and `flow_heat_c` label and description, and `space_setpoint_unit` option `return`). At the head there are 0 missing either way, and strings.json shows 0 missing from de (`ev/de-parity.txt`).
  - **Claims check.** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` prints `claims_false=0` at the head (`ev/d6-claims-head.txt`). With main's de.json swapped in it prints `claims_false=1`, `FALSE C112` (null control, `ev/d6-claims-main-dejson.txt`). This matches the body.
- **CI at this head.** `merge_train.py classify 3377b5f0... --pr 3350` exited 1 at 2026-11-09T19:22:06Z with `RED ... pending: none red: gate` (`ev/classify-log.txt`).
  - The code run's `gate` (job 129379586278, run 42674500178) prints exactly one failure: `FAIL tests / fast (3.14): failure (this run)`.
  - `tests / fast (3.14)` (job 129353236613) ends with `2 CARD CHECK(S) FAILED`, `>>> FAILED: node tests/card.mjs`, `1 TEST SCRIPT(S) FAILED` (`ev/ci-fast-log-tail1000.txt`).
  - The edit-run gates (129353418962, 129380106371) are deferrals to that code run.
  - Every other required context in `merge_train.py owed-reds` (`ev/owed-reds.txt`) concluded success or skipped, including `pr-contract / pr-contract` (job 129379016787), `tests / closures`, `tests / coverage`, `tests / mutation` and `codeql / Analyze (python)`.
- **The `card.mjs` red is inherited from main**, so under the CI SETTLE ruling it does not block. After `tests/plan_view.py`, `node tests/card.mjs` fails identically at the head and at the merge base 2f6d699e5 = origin/main (`ev/card-head.txt`, `ev/card-main.txt`). Both runs show the same two FAILs, `every card language is key-for-key with en and keeps en's placeholders` and `de: missing savings.below_meter_floor; de: missing savings.meter_floor_note`, plus the null-control companion. The branch's diff touches no card file. Both keys came from main's #3360 (R10-SAV-METER-FLOOR) after #3331 shipped the German card dictionary.
- **Not affected.** `VERSION`, the manifest, `RELEASE_NOTES.md`, the claim files and the `*_budgets.json` files are not in the delta. The review packet's carry_audit at the head reports 2 items routed, 0 unrouted (`ev/review-packet.md`).

## Findings

- Out of scope: main itself is red on `tests / fast (3.14)` through `node tests/card.mjs`. The German card dictionary lacks `savings.below_meter_floor` and `savings.meter_floor_note`, which #3360 added after #3331. The failure reproduces at origin/main 2f6d699e5 and gates every pull request's `gate` until it is repaired on main. Carry: dismissed: main's own red, inherited at merge base 2f6d699e5 and not this PR's diff, so the repair belongs to the orchestrator's main-red duty, not a stage of this group
