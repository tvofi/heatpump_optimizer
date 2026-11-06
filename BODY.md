Roster-reader predicates for R10-ROSTER-READ-SWEEP, carries 1-4: `absorbed` is a closed stage for the open set and after-edges, a destination check that names `absorbed_into`, a `gate_kind` classifier the tick calls, and one shared REFUSED line for a missing roster ref. Carries 5-8 are not landed here (see Forward-carry); #2733 and #2505 stay open for the remaining carries (review-packet numbering: Carry 5, Carry 6, Carry 7, Carry 8 and Carry 9, the brief's carries 5-8 plus its Carry 0 fold note, none landed here), which stay owed by this group and unchanged in its roster brief; this diff produced no new finding for a later stage. Carry: R10-ROSTER-READ-SWEEP


Design: `DONE_STAGES` keeps meaning "merged" (flow_metrics, merge_throughput, size_durations key on it); the new `CLOSED_STAGES` is the open-set boundary and `CARRY_CLOSED` is the same object, so the write-time and review-time stage sets are one definition. `absorbed` stays a disposition, so `roster_sync` still never rewrites it. `replan.is_done` now calls `roster_lib.is_open`, because carry 1's control needs the schedule to drop the groups.

## Head

Measured at `0287fe05d6618396fb1d9caecedbc636102d59a1`, on `origin/main` `7e8939d38cedb2976acc80a4ad7875cb545bd588` (unmoved since the cut, so no second prepr run is owed).

## Mutation proof

Each mutant applied to one predicate, its self-test run, then reverted; the unmutated self-test is the control (rc 0).
- `roster_lib.is_open` reading `DONE_STAGES` instead of `CLOSED_STAGES`: `roster_lib.py --self-test` fails "absorbed is closed: not open, and an after-edge on it clears" and "an absorbed group is not in the open set or the dependency depth"; `replan.py --self-test` fails "an absorbed group is closed work, not scheduled".
- `gate_kind` final `return "covered"` made `"owner"`: `roster_lib.py` fails "gate_kind: every gate shape on the roster is covered"; `orchestrator_tick.py` fails the covered-gate rows.
- `gate_kind` owner branch made `"covered"`: `roster_lib.py` fails "a pending decision is owner"; `orchestrator_tick.py` fails "an owner gate is flagged blocked on owner".
- `carry_audit.py` dropping the `absorbed_into` text: fails "an absorbed destination is refused naming absorbed_into".
- `run_refusing("<tool>", main)` replaced by `main()` in each of `plan_table.py`, `resume_doc.py`, `handover_prompt.py`: each self-test fails "a missing roster ref is one REFUSED line, rc 2, no traceback" with `(1, 0, True)`. A first placement of that row after the summary line survived the mutant; moved before it in `0287fe05d`.

## Null control

- Carry 1: the open set read `DONE_STAGES` only; a group at `absorbed` counted open and held its dependants' after-edges.
- Carry 4: at the base, `resume_doc.py`, `handover_prompt.py` and `plan_table.py` with `--roster-ref origin/no-such-ref-xyz` each exit rc 1 with a Traceback; at the head each exits rc 2 with one `REFUSED` line.
- Output against the live ref (`--roster-ref origin/main`) is not byte-identical, by design: `plan_table.py` and `handover_prompt.py` no longer list `absorbed` groups as open. `resume_doc.py`'s difference was not read.
- Carry 3: a group with no gate is in neither the covered nor the owner line (self-test row).
- Carry 2: an open destination passes (the existing live-group rows).

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`; `scope.run` is `tests/entities.py`, which passes, as do the `run_always` lines (`tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`).
- `python3 tests/structure.py` passes (STRUCTURE RATCHET PASSED); no budget moved.
- Self-tests green at the head: `roster_lib.py`, `carry_audit.py`, `plan_table.py`, `resume_doc.py`, `handover_prompt.py`, `roster_edit.py`, `roster_sync.py`, `orchestrator_tick.py`, `replan.py`.

## Red checks

none

## Forward-carry

none

## Friction

- brief-citations: stale: carry 2 asked for a review-time check that `carry_audit.Dests.live` already performed through `CARRY_CLOSED`; only the `absorbed_into` naming was missing. Carry: dismissed: landed in this PR
