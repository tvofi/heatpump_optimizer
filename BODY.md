Triage batch 70 rules the orchestrator's queue line 17 (2026-10-30T10:12:06Z, plan-opt seat): `tools/plan/replan.py` charges a critical-path group one of the slots, though `orchestrator.md` section 5 starts a ready critical-path group regardless of every cap. It is the next rolling batch under V182, after batch 69. It holds one ruling and one held roster op.

- **P304: ACCEPT narrowed, a carry on R10-ORCH-ROSTER-SCHEMA**, which already owns `replan.py`'s stage predicate (P131).
  - (a) The scheduler starts a ready tier-0 group without a slot or a seat. `check_plan` exempts exactly those groups and keeps every other refusal.
  - The prototype's wholesale filter, which drops every `check_plan` line containing `in flight`, `working` or `peak`, is REJECTED: it would pass an over-cap non-critical plan.
  - (b) "Absorbed as closed" is ACCEPT as already carried, three times on the same group (#2554 absorbed-edge closure, the consolidation-folds carry, P131).
  - Re-measured here, main's `replan.py` against the CP-exempt prototype over four rosters: projected closure moves -4.0 h to -7.0 h.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`7b502385888c7baf1e73ef688a2175a369b6e303`; the file is the whole diff against `b646e8306`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P304 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch70.md#P304`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch70.md#P304 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch70.md is not on the roster branch or origin/main`.

## Figures

- `replan.py` at main and the orchestrator's CP-exempt prototype (out of tree, its plan-opt scratch; it rests on that copy), each run with `--roster-file <scratch>.json --start 2026-10-30T09:58:00Z` and main's `tools/plan/durations.json`, all rc 0. Closure, main then CP exempt:
  - `scratch-base`: 2026-11-04T19:27Z, then 12:27Z.
  - `scratch-comb`: 2026-11-03T23:21Z, then 19:24Z.
  - `scratch-cp`: 2026-11-03T23:21Z, then 17:43Z.
  - `scratch-x`: 2026-11-03T23:21Z, then 17:43Z.
- The orchestrator's saved plan-cp plan (out of tree) reads `2026-11-02T01:57:00Z`, the filing's figure, from its own inputs.
- The prototype against main's `tools/plan/replan.py` (a diff of the two files, read in the orchestrator's scratch): 4 lines added at the scheduling site (473-476), and `main()`'s `check_plan` output filtered by substring.
- `orchestrator.md` lines 100-105 at main: "A ready critical-path group starts regardless of every cap".
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
