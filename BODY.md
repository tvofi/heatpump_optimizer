Part 2 of R10-ROSTER-WRITE-SWEEP (part 1 merged as #3253). Builds the carries part 1 did not deliver in `roster_edit.py`, `roster_queue.py` and `postmerge.py`; the rest are verified at the merge base and listed below. Part of #201.

## Head

6bc631f2a2f9bdc768881efa4aa9d237ce737b36 (merge base 73365699a135fb813a43380096b6776d57f8ff4c; `origin/main` had not moved when this was written, and per the owner ruling of 2026-11-07 the merge train re-proves the head, so no second prepr run).

## Mutation proof

Each mutant was applied to the production line, the owning self-test run, and the line restored.

- Carry 19: dropping `action="extend"` from `--add` fails `set-files --add a --add b parses to ['a', 'b']` and `set-files --add a b --add c parses to ['a', 'b', 'c']` (2 failed of 249).
- Carry 17: returning `False` before the fetch in `_on_origin` fails `P409: a stale tracking ref (a rival's push) passes after the one fetch`.
- Carry 20: `new = list(errs)` (an empty base set) fails `lint gate: an unrelated write passes beside a pre-existing error, warning it` and `lint gate: the same write adding a bad citation is refused, naming it`.
- Carry 18: catching `ZeroDivisionError` in place of `(SystemExit, re_.Refuse)` in `_run_batch` fails `run --batch: a malformed line is named and refused, the rest still batch (no fallback)`.

## Null control

- Carry 19: one `--add a` parses to `['a']` (row present, passes).
- Carry 17: a real unpushed commit in the worktree still reports "not on origin" (`P409: a real unpushed commit still refuses`).
- Carry 20: a clean roster writes with `TOTAL: 0` and no WARN; no base text (the old gate) refuses every error.
- Carry 18: `refusal_tail` of non-gate output is its last three lines, and the existing lost-race fallback row still passes (its expectations moved by one line: the new `roster: batch failed <Type>: <reason>` line precedes the fallback line).

## Figures

- Self-tests at this head: `python3 tools/audit/seat/roster_edit.py --self-test` (254 checks, 0 failed), `python3 -I tools/audit/seat/roster_queue.py --self-test` (55 checks, 0 failed), `python3 -I tools/audit/seat/postmerge.py --self-test` (18 checks, 0 failed).
- Diff size: `git diff --stat origin/main...HEAD` is three files, about 200 added lines (well under the 400-line split bound).
- Carry audit at the merge base (commands: `git merge-base --is-ancestor 28482eceeb6b9809e44b12d80fc994282cc21645 HEAD`, then reading the symbol and its self-test row):
  - Carry 0: covered by 28482ece, `triage gate: a lettered label citing no ruling is refused` (and the ACCEPT and null rows).
  - Carry 1: M4/M5/M6 do not exist in `r10_roster_ops_mutants.py` (plant ids A, C, P, D, T, S, K, L, Y, R, H, Z, W1 to W8, Q). The reviewer's three fail-closed plants are unrecoverable from #2513's text, so no tightening is invented here: waits on a ruling or the original plants.
  - Carry 2: covered by 28482ece, `set-stage done clears a note naming owed work and says so (carry 2)`.
  - Carry 3: covered by 28482ece, `append-carry to an absorbed group names absorbed_into` and the WARN row.
  - Carry 4: code covered by 28482ece (`set-resume --field pr round-trips an integer`). Data not done: R10-FLOW-RECORD-PITCH has `resume.pr` null. Owed as roster-data ops (`set-resume R10-FLOW-RECORD-PITCH 2836 --field pr`, then each done group lacking a pr) for the roster seat, because this seat pushes no roster branch.
  - Carry 5: covered by 28482ece, `append-group overlapping a not-started group refuses, naming both (carry 5)`. `group_for_branch` resolves `-pN` phase branches in `roster_lib`; no dedicated row was found for it here.
  - Carry 6: covered by 28482ece, `append-group @file lands (carry 6)`.
  - Carry 7: covered by 28482ece in `write_roster`'s in-process `privacy_refusal` (`<op> naming a host path is refused with the scrub hint (carry 7)`); it runs beside the lint gate, not inside `lint_gate`.
  - Carry 8: framing only; its sub-items are carries 9 to 14.
  - Carry 9: not delivered. The phrase "handoff_push" still occurs in 91 of 342 groups of `wave-r10-groups.json` (67 briefs, 14 carries, 1 files list). Owed as one `edit-brief` op per live group, for the roster seat.
  - Carries 10, 11, 12, 14, 15: covered by 28482ece (`parse_line`, `run --mark`, `loop`/`release-held`/`unwired`, `lane_refusal`).
  - Carry 13: (1) docstring and (3) comment parsing covered; (4) `run --batch` covered; (2) refers to `roster_drain.py`, which does not exist in the tree, so there is nothing to fix.
  - Carry 16: code covered by 28482ece (`set-stage absorbed --into`). Data not done: the ten named groups are still `done`. Owed as ten `set-stage G absorbed --into H` ops for the roster seat; the host for each is a ruling for the orchestrator.
- Carries built here: 17 (`_on_origin`, `update-ref` after the push), 18 (`_run_batch` names the failure and isolates a malformed line), 19 (`--add` is `action="extend"`; it is the only repeatable flag in `build_parser`), 20 (`lint_gate(..., base_text)`, `refusal_tail` in `roster_queue.py`, `refusal_detail` in `postmerge.py`).
- Mutant run: `MUTANT_CMD='<the three self-tests chained with &&>' python3 -I tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --max-mutants 25 --report-only`: wall 430 s, 11 SURVIVED, 0 KILLED. Zero kills in 11 is suspect (the same guards die under my hand mutants above), so the runner's result is not trusted as a measurement; I have not diagnosed why.
- prepr.sh at this head: every step ok or skip except `closures`, which REFUSEd because `tests/entities.py` cannot import `homeassistant` in this container (environment, not the diff); `ci predict` reports no red predicted. Left to CI.

## Unpinned sites

The 11 survivors above (postmerge.py `refusal_detail` guard/constants; roster_edit.py `_on_origin` `if held()` guard, fetch `capture_output`, base-dir `rmtree` flags) are undispositioned beyond the hand mutants in `## Mutation proof`; the `if held()` short-circuit is behaviourally equivalent (the fetch then re-asks), the rest are display bounds or cleanup flags. `tools/` sites are outside the `custom_components/` mutation lane. Each added predicate is pinned by an in-tree self-test row and the mutant listed under `## Mutation proof`; the postmerge `refusal_detail` truncation length is a display bound with no semantic pin.

## Red checks

none

## Forward-carry

- Carries 4, 9 and 16 data ops: `Carry: R10-ROSTER-WRITE-SWEEP` (roster seat applies them through `roster_queue.py`; this seat does not push the roster branch).
- Carry 1 (M4 to M6 plants): waits on the original plants or an owner ruling; `Carry: R10-ROSTER-WRITE-SWEEP`.

## Friction

none
