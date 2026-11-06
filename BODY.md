Roster-reader predicates for R10-ROSTER-READ-SWEEP: `absorbed` is a closed stage for the open set and after-edges, a destination check that names `absorbed_into`, a `gate_kind` classifier the tick calls, and one shared REFUSED line for a missing roster ref (roster carries 1-5). Repair round 2 (fix-review round 1 blocked, instrument-broken): the rewrite of `CARRY_CLOSED` in `roster_lib.py` broke two mutant plants that anchored on its old spelling, and left one changed line in `handover_prompt.in_flight` with no pin. This round re-anchors both plants, pins that line, and corrects the body's carry map. #2733 and #2505 stay open.

Design: `DONE_STAGES` keeps meaning "merged" (flow_metrics, merge_throughput, size_durations key on it); the new `CLOSED_STAGES` is the open-set boundary and `CARRY_CLOSED` is the same object, so the write-time and review-time stage sets are one definition. `absorbed` stays a disposition, so `roster_sync` still never rewrites it.

Carry map (roster entry `R10-ROSTER-READ-SWEEP`, `carry` list, 1-based index):
- Carry 1 (absorbed counted as open): landed in this diff (`roster_lib.is_open`, depth and after-edge readers). Deviation, stated: carry 1's text routes "tools/plan/replan.py's side of the absorbed stage" to R10-FLOW-TOOLKIT-MODEL, yet this diff changes `replan.is_done` to call `roster_lib.is_open`. I did it here because carry 2's control (replan must drop exactly the absorbed groups from the schedule) cannot read true otherwise, and the change is one call into the roster library's own predicate, not a second definition. R10-FLOW-TOOLKIT-MODEL keeps whatever else replan.py owes; it no longer owes this line.
- Carry 2 (absorbed terminal, refuse a Carry: to it): landed (`CLOSED_STAGES`, `carry_audit` reading it). Departure from its text, "treat absorbed as terminal in DONE_STAGES": `DONE_STAGES` stays "merged" and `CLOSED_STAGES` carries the terminal set, because the flow readers keyed on `DONE_STAGES` must not count a fold as a merge.
- Carry 3 (review-time destination check names `absorbed_into`): landed.
- Carry 4 (`gate_kind` classifier the tick calls): landed.
- Carry 5 (the RosterNotFound traceback in plan_table, resume_doc, handover_prompt): landed in this diff, via the shared `roster_lib.run_refusing`. The first body listed it as out of the diff; that was wrong.
- Carry 6 (the routing audit's disposed-key mechanism): not landed; it stays on the open roster entry.
- Carry 7 (#2875 unowned): not landed; routed to R10-ORCH-ROSTER-SCHEMA by its own text.
- Carry 8 (#2855's key): not landed; routed to R10-ORCH-ROSTER-SCHEMA by its own text.
- Carry 9 (the invariant-3 tick line and the issue-arm dispositions): not landed; it stays on the open roster entry.

## Head

Measured at the final handoff code `2f1a93ea74df7b9d43b5e0f15088ad01041ba94f`. `origin/main` was `33e60b5b71b67610bd02fdea238b882e9a97007b` when I merged it into the PR head `99cf3c2537c0199d966aff7b1c5fd86bcc8f663c` and ran `tools/pr/prepr.sh` (stamped `date -u` 2026-11-06). Main has moved since the last review, so the prepr run is the second one, not skipped.

## Mutation proof

Each mutant applied to one predicate, its self-test run, then reverted; the unmutated self-test is the control.
- Round 1, carried unchanged and re-run by the reviewer: `roster_lib.is_open` reading `DONE_STAGES` (roster_lib 2 fails, replan 2 fails); `gate_kind` final `covered` to `owner` (roster_lib 1, tick 2); `gate_kind` owner branch to `covered` (roster_lib 1, tick 1); `carry_audit` dropping the `absorbed_into` text (1); `run_refusing(...)` replaced by `main()` in each of plan_table, resume_doc, handover_prompt (each 1 fail).
- New this round, the surviving mutant: `handover_prompt.in_flight` reading `roster_lib.DONE_STAGES` (the base spelling) is plant `S09b` in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Before the new check it left `handover_prompt.py --self-test` at `16 checks, 0 failed` (the reviewer's measurement, probe mutant `handover-in_flight-DONE`). The new check "absorbed group is not in flight and has no pickup" (fixture group `R9-D` at stage `absorbed`) turns it red: `S09b handover_prompt.py: KILLED rc=1`.
- Re-anchored plants: `S09` (same harness, anchor now `if stage not in roster_lib.CLOSED_STAGES and stage != NOT_STARTED:`) is `KILLED rc=1`; `L4` (`tools/audit/seat/r10_roster_ops_mutants.py`, anchor now `CARRY_CLOSED = CLOSED_STAGES`, mutated to `CARRY_CLOSED = DONE_STAGES`) prints `RESULT mutant=L4 rc=1 fails=2` in the full plant run. The `S09` and `S09b` run prints `RESULT survivors=0`.

## Null control

- Anchors at the unrepaired PR head: `roster_lib.py` had 0 occurrences of the old L4 anchor (1 at the base), and `r10_roster_ops_mutants.py --self-test` printed `231 checks, 1 failed` (`FAIL L4: anchor occurs once in tools/audit/seat/roster_lib.py`), the full plant run stopped at L4 with rc 2; S09's old anchor had 0 occurrences at the PR head (1 at the base), `NOT RUN`. At this head each re-anchored plant's anchor occurs once (Figures).
- The new handover_prompt check on the unmutated tree: `handover_prompt self-test: 17 checks, 0 failed` (16 before, 17 now: one added).
- Carry 4 at the base: `resume_doc.py`, `handover_prompt.py` and `plan_table.py` with `--roster-ref origin/no-such-ref-xyz` each exit rc 1 with a Traceback; at the head each exits rc 2 with one `REFUSED` line.
- Carry 1: the open set read `DONE_STAGES` only; a group at `absorbed` counted open and held its dependants' after-edges. The reviewer's replan over roster a631ce6ec2c0 scheduled 69 groups (13 absorbed) at the base and 56 at the head, dropping exactly the 13.
- Carry 3 and 2: a group with no gate is in neither the covered nor the owner line; an open destination passes.
- Output against the live ref is not byte-identical, by design: `plan_table.py` and `handover_prompt.py` no longer list `absorbed` groups as open.

## Figures

- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py` (full plant run at head): `plants: 75, without a FAIL line: ['C6']`, rc 1 from that line, and no plant printed `NOT RUN` (`grep -c "NOT RUN"` on its output printed 0); the base run printed the same 75 and the same `['C6']` (reviewer's ev/ops-harness-base-tail.txt), so C6 is inherited, not new.
- `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test`: `231 checks, 0 failed` (the base prints the same 231).
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S09 S09b`: both KILLED, `RESULT survivors=0`.
- `grep -c 'CARRY_CLOSED = CLOSED_STAGES' tools/audit/seat/roster_lib.py` prints 1; `grep -c 'if stage not in roster_lib.CLOSED_STAGES and stage != NOT_STARTED:' tools/audit/seat/handover_prompt.py` prints 1.
- Self-tests at the head, each `--self-test`: roster_lib 64, plan_table 26, resume_doc 15, handover_prompt 17, orchestrator_tick 275, roster_edit 191, roster_sync 95, r10_roster_ops_mutants 231, carry_audit 365 checks, all 0 failed; `tools/plan/replan.py --self-test` prints `self-test: 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; `scope.run` is `tests/entities.py`, which prints `ALL 2637 ENTITY CHECKS PASSED` (run with `PYTHONPATH=tests/hastub`). The `run_always` lines pass: `tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget file is in the diff.
- Class enumeration (fixer step 8, the plant anchors a rewrite can strand): the instrument is `r10_roster_ops_mutants.py` and `r10_seat_selftests_mutants.py` themselves, each of which refuses or prints `NOT RUN` on a missing anchor; both ran clean at this head, so the two stranded anchors the review found are the only ones.

## Red checks

At the PR head `99cf3c2537c0199d966aff7b1c5fd86bcc8f663c`, read across the one check-run page (55 runs, `total_count` 55), four concluded red:
- `governance / instrument-self-tests` (job 127919930623): this PR's own instrument break (the stranded L4 anchor, `r10_roster_ops_mutants.py --self-test` 1 failed). Class: a change to a constant whose spelling an in-tree instrument anchors on, found by CI. Cheaper detector: `prepr.sh` does not run the instrument self-tests; the fix review found it by running that self-test. Repaired here (0 failed). Standing cost of a detector: running the self-test of every instrument that names a changed file; I did not build one, and record that none exists today for plants anchored on production text.
- `gate` (jobs 127920529181 and 127931993971): the `FAIL run(s) ... are still being judged; their gate decides` deferral, which the sweep re-runs; it was red because of the instrument-self-tests run above, so it follows it.
- `pr-contract / pr-contract` (job 127931123955): the body's `## Red checks` read `none` while the runs above were red (`red-unanswered`). Answered here.
- The first `gate` (job 127920529181) was the earlier deferral at the first run of the same head.

## Forward-carry

`none`. Carries 6-9 are already on the open roster entry in `dev/programme/rosters/wave-r10-groups.json`; this round found nothing new that changes how a later stage works.

## Friction

- brief-citations: stale: carry 2 asked for a review-time check that `carry_audit.Dests.live` already performed through `CARRY_CLOSED`; only the `absorbed_into` naming was missing. Carry: dismissed: landed in this PR
