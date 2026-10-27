Triage batch 36 rules V124, the duplicate-seat class: two writers on one role, invisible to the liveness file and unstoppable by the orchestrator. The verdict is **DEFER**: the proposed seat-start claim binds only the seats that implement it, and the writer that motivated the proposal implements nothing, so its benefit is unmeasured against its own target while its costs are immediate. The ruling names what would change the answer and the one element that survives (a launch record written by whoever dispatches a seat, which the orchestrator can adopt in its own dispatch path with no repository change). No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

Two facts kept out of the ruling's body but owed to the reader: the seat brief named V119-V122 as pending after `s6-batch35.md` had already ruled them (merged `c73d8984a`, 2026-10-26T22:24:12Z), which this seat reconciled in its state file rather than re-ruling; and the second writer was still emitting its plain HOLD line at 09:38:27Z when this batch was cut.

## Head

`1b84be415587523f0e26ebbbf274b2e871ef2334`; the file is the whole diff against `524c1896b6943b3da03d6cad61420ced31e14c9c`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only consumer, and it reads the verdict. On the committed file, with `PYTHONPATH=tools/audit/seat`:

```
P204 verdict: DEFER
refusal on committed file: dev/programme/triage/s6-batch36.md#P204 is not an ACCEPT ruling (DEFER)
```

Flipping `Verdict: DEFER.` to `Verdict: ACCEPT.` in an out-of-tree copy and re-running the same two calls prints `mutant verdict: ACCEPT` and `mutant refusal: None`: the gate is sensitive to this file's verdict line, so a DEFER cannot be laundered into a carry. The out-of-tree copy is at `/tmp/b36-mutant.md`; the tree is untouched.

## Null control

At the merge base the file does not exist, and the gate prints `the triage ruling dev/programme/triage/s6-batch36.md is not on the roster branch or origin/main`. An entry that does not exist in the committed file (`P999`) resolves to `None`, and is refused the same way.

## Figures

One line per figure, with the command that printed it.

- 18 plain `HOLD (no v7.0.5 tag)` lines at 5:00-5:01 intervals, 08:13:15Z to 09:38:27Z, four of them inside this seat's 21-minute stall (its own last line 08:54:25Z, next 09:15:38Z): `grep -n 'triage s7:' seat-ledger.md`, in the orchestrator state directory.
- the board's alive-age threshold was 660 s and moved to 1800 s after 22 beat gaps, min 1 s, median 57 s, max 1235 s: the orchestrator's measurement and change, recorded in its 09:37Z message and in this seat's state file, not re-derived here.
- `R10-ORCH-BEATD` is `not-started`, size L, and already carries P197: `git show origin/main:dev/programme/rosters/wave-r10-groups.json`, filtered to that group.

## Red checks

`none`. A ref with no pull request has no checks; locally `tools/pr/prepr.sh` passes with the gate step printing `ok gate mode MODE: SCOPED` (a markdown file under `dev/programme/` is in no test's measured closure; the mode line is the fact, not a script count) and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Forward-carry

none

## Friction

`none`.
