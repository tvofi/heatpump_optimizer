Hotfix for a main breakage. Since main 31255c3289 (#3635's merge), `tools/audit/seat/orchestrator_tick.py` raises `NameError: name 'SEAT_WINDOW_MIN' is not defined` at `outside_chain_idle` (line 1730) on every run, both the live tick and `--self-test`. No board has been written since then.

Cause: two merges collided semantically.
- d0f225c602 (#3651, merged 07:41Z as 1f7c59ebc4) "owed_watch: the cp-owed beat row, and the tick's fired-ledger, seat-on and FIRE-OWED reads moved into it" moved `SEAT_WINDOW_MIN` into `tools/audit/seat/owed_watch.py:55` and removed the tick's module-level name.
- d1ee130c48 (#3635, merged 07:51Z as 31255c3289) "tick: OUTSIDE-CHAIN-IDLE walks after-edges for outside-sourced groups (carry 0)" added a use of the old module-level name. #3635's head did not contain d0f225c602, so its CI ran against a tree where the name still existed.

Fix: `outside_chain_idle` reads `owatch.SEAT_WINDOW_MIN`, the same way the tick's other owed_watch reads go through `owatch` (`_module("owed_watch_tick", ...)`). The constant is not redefined, so it keeps one owner. The docstring names the owner. Two lines change.

## Head

58d6b0ff03b526c6072e6d540bf21a9821a6fe77, one commit on origin/main b94425b94f.

## Mutation proof

- `python3 tools/audit/seat/mutant_run.py --diff origin/main...HEAD --cmd "python3 tools/audit/seat/orchestrator_tick.py --self-test"`: rc 0, one mutant (`orchestrator_tick.py:1730 STMT_DEL pass`, per `--list`), killed, 0 survived.
- The failing test came first: the self-test's existing `OUTSIDE-CHAIN-IDLE` block (`cboard`, which calls `t.outside_chain_idle`) and `t.plan()` already drive this line. At origin/main b94425b94f, `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` exits 1 with `NameError: name 'SEAT_WINDOW_MIN' is not defined` (orchestrator_tick.py:1730, reached via `plan` at line 3483). At this head it prints `orchestrator_tick self-test: 368 checks, 0 failed`, rc 0. Its `null control: a path ending in a seat ref inside the window prints nothing` row (a 0.5 h old seat ref) pins the window's value too. Pointing it at `owatch.FIRE_GRACE_MIN` (15 min) would flag that ref.

## Null control

The unmodified tree (origin/main b94425b94f) crashes on every tick. `orchestrator_tick.py --self-test` stops at the NameError above, rc 1, and the live tick has written no board since 31255c3289. At this head, against the orchestrator's live `HPO_STATE_DIR`, `python3 tools/audit/seat/orchestrator_tick.py` (the call `tick_loop.sh` makes) exits 0 with no traceback. Its first line is `BOARD measured from origin/main at b94425b94f0d, 2026-11-16T08:11:56.582680+00:00`, and the arm prints two `OUTSIDE-CHAIN-IDLE` lines.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `orchestrator_tick self-test: 368 checks, 0 failed` at this head. At origin/main: NameError, rc 1.
- `uvx ruff check --select F821` on origin/main's `orchestrator_tick.py`: `Found 1 error` (line 1730). On this head's file: `All checks passed!`.
- `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: `PRE-PR: 58d6b0ff03b5 ... rc=0` (hotfix scope).

<!-- figure-block: scope-line mb=b94425b94f0d25a02576e98fa10a8ff324974a0c head=58d6b0ff03b526c6072e6d540bf21a9821a6fe77 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Root cause

Trigger: main breaks a required check. The forced-full push runs since 31255c3289 reach `governance / instrument-self-tests`, which runs `orchestrator_tick.py --self-test`, and that self-test exits 1 at that tree (reproduced locally). Those runs (43826727614, 43828769147) had not concluded when this was cut. A cheaper detector could have caught it.

- Cause: a merge-time semantic collision that neither PR's CI could see. Each head was green alone. #3651 removed a name. #3635 added a use of it, and its CI measured a merge with a main that did not yet contain #3651. The textual merge was clean, so nothing re-ran on the combined tree before it landed.
- Process state: (d), the process was sound and its precondition changed underneath it. A PR's CI result stands for the merge with the main it was measured against. Main moved, 10 minutes apart, and the merge did not notice that the result was stale for the files it touched.
- Cheaper detector: two exist, both run on the merge of the PR head with the current origin/main at merge time. (1) A static undefined-name check (`ruff --select F821`) over the touched Python files finds this in under one second; at main it reports exactly this line. (2) The `--self-test` of each instrument the diff touches takes about 8 s here (7.9 s real for this one). Standing cost: about 1 s per merge for (1), or the closure-reached self-tests (seconds to minutes) for (2). Defect cost: the orchestrator's tick board was unreadable from 07:51Z until this merges, plus one hotfix seat.
- P(recurrence): no measured class frequency exists. Estimate: low but non-zero. Round 11 lands several instrument PRs a day that move names between `tools/audit/seat/` modules (this one came from the R11-PRE-STANDING-SCRIPTS move), so recurrence comes with each such move.
- Countermeasure: not built in this hotfix. The tooling freeze admits only the main-red repair, so detector (1), run on the merged tree at merge time, goes to the round-end proposal triage, where the cost test above is decided.

## Red checks

none. At this head no required check has gone red on a commit of this branch. Any `instrument-self-tests` red belongs to main's push runs since 31255c3289, and this diff repairs it.

## Forward-carry

- The merge-time undefined-name detector, lands in the round-end proposal set (`tools/audit/seat/merge_train.py`'s merge step is its candidate site), for the round-end proposal triage. Carry: R11-CLOSEOUT-CLEANUP

## Friction

none
