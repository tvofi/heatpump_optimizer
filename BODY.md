owed_unactioned: key the tick's verdict levels `MERGE-READY:` and `BLOCKED-UNFIXED:` as owed (triage P277, `dev/programme/triage/s6-batch59.md#P277`).

The tick prints flagged `MERGE-READY: #N <head8>` and `BLOCKED-UNFIXED: #N <head8>` (`orchestrator_tick.py`, the verdict-levels block). `owed_unactioned.py`'s `FAMILY` keyed only `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:`, so no sweep had to acknowledge them: blocked #2933/#2925/#2872 and merge-verdicted #2896/#2939 stood 5-11 h (triage's measurement, not re-taken here).

Change, in `tools/audit/seat/owed_unactioned.py` only (plus its instrument guide line):
- `FAMILY` gains `MERGE-READY:` and `BLOCKED-UNFIXED:`.
- `key_of` keys each on `#<N>` with `<head8>` as its id, matched strictly (`(?:MERGE-READY|BLOCKED-UNFIXED): (#\d+) ([0-9a-f]{8})$`). An ack covers one head; a new head re-raises. A verdict-level line of any other shape falls through to the existing `Unreadable` (exit 2), never a silent skip.
- Keyed on `#<N>`, a level and a `REVIEW OWED: #N` line for the same pull request are one obligation, as the existing `#<pr>` keying already makes them.
- The docstring's family list and `instruments/owed_unactioned.py.md` name both.

Alternatives: keying the levels on their own key (`MERGE-READY #N`) lost — it would make one pull request two obligations needing two acks. Widening `SHA` to 8 characters lost — it would make every 8-hex word in every owed line an id. Out of scope per the brief: `sweep_template.md` (its step 5 already runs this tool; #2935) and `orchestrator_tick.py`.

## Head

f7290d373333fda60139629c481ddd63e92cdc67, cut from origin/main 66974d47312caa46e9817b9aeae7186e9764e560 (merge base; origin/main tip at 2026-10-29, `date -u` at measurement).

## Mutation proof

Each mutant applied with `sed` to `tools/audit/seat/owed_unactioned.py`, then `python3 -I tools/audit/seat/owed_unactioned.py --self-test`, then restored:
- `FAMILY` without `|MERGE-READY:` -> 37 checks, 4 failed: `MERGE-READY: keyed #2896 on its head8, unactioned on the second sweep`, `MERGE-READY: an OWED-ACK on #<N> <head8> covers it`, `MERGE-READY: a new head8 re-raises`, `REVIEW OWED and MERGE-READY on one pull request are one key`.
- `FAMILY` without `|BLOCKED-UNFIXED:` -> 37 checks, 3 failed: the three `BLOCKED-UNFIXED:` arms.
- `key_of`'s level branch `return m.group(1), [m.group(2)]` replaced by `pass` -> all six level arms fail, then the run dies `Unreadable: an owed line names no topic or pull request: -> MERGE-READY: #2896 5f3a5dd6` (rc 1).

Failing test first: the new arms at the merge base's production code -> `37 checks, 7 failed` (the six level arms and the shared-key arm).

## Null control

- The unmodified tree (66974d47) on a board holding only `-> MERGE-READY: #2896 5f3a5dd6`, `-> BLOCKED-UNFIXED: #2933 1a2b3c4d` and a non-owed `-> #2887: mergeable state DIRTY`, two sweeps 10 min apart: `owed: 0 key(s) ... 0 unactioned`, rc 0 both times — the defect. The head on the same two boards: sweep 1 `2 key(s) ... 0 unactioned` rc 0, sweep 2 `2 unactioned` rc 1 with `#2896  sweeps=2` and `#2933  sweeps=2` and a ready `ack: OWED-ACK <UTC> #2896 5f3a5dd6 ttl=1 ...` line.
- Self-test arm `null control: a board without the levels keys as before`: the five-shape board keys exactly `{r10-orch-beatd, triage-s7-batch49, #2896, #2920}` at the head, and the non-owed `-> #2887:` line is still not owed.

## Figures

- `python3 -I tools/audit/seat/owed_unactioned.py --self-test` -> `owed_unactioned self-test: 37 checks, 0 failed` at the head (rule: one count per `check()` call; 30 before this diff, 7 added). The governance workflow's own step greps this line for `0 failed`.
- `python3 tests/closure.py select --diff 66974d47312caa46e9817b9aeae7186e9764e560 --workdir <tmpdir>` -> `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `run_always` lines: `tests/env_drift.py --claims-only 66974d47312caa46e9817b9aeae7186e9764e560` ok; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/layout.py` ok. `tests/harness_headers.py` could not run here (`ModuleNotFoundError: No module named 'voluptuous'` in this container); this diff touches no harness, left to CI.
- `bash tools/pr/prepr.sh <body>` at f7290d37: every step ok or skip except `closures`, REFUSED: "no interpreter that parses the tree was found"; `bash tools/audit/seat/seat_venv.sh` fails in this cloud container with `error: No download found for request: cpython-3.14.7-linux-x86_64-gnu`. Not worked around; `ci predict` in the same run predicts no closures red against 66974d47312c, and both changed files are already classified (`owed_unactioned.py` is in `tests/closures.json`). CI's closures job is the check of record.
- Class seams (step 8): the rule is `grep -n 'flag=True' tools/audit/seat/orchestrator_tick.py` over the tick's flagged prints, each against `FAMILY`. This diff closes the two verdict levels the brief names; I did not disposition every other flagged line the tick prints (e.g. the non-owed `#N: mergeable state DIRTY` the self-test keeps out deliberately) — that census is not done here, and is the orchestrator's to scope if wanted.

## Red checks

none

## Forward-carry

none

## Friction

none
