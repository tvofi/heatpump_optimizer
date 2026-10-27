Triage batch 36 rules V124, the duplicate-seat class: two writers on one role, invisible to the liveness file and unstoppable by the orchestrator. The verdict is **DEFER**: the proposed seat-start claim binds only the seats that implement it, and the writer that motivated the proposal implements nothing, so its benefit is unmeasured against its own target while its costs are immediate. The ruling names what would change the answer and the one element that survives (a launch record written by whoever dispatches a seat, which the orchestrator can adopt in its own dispatch path with no repository change). No product behaviour changes: this seat's diff is one markdown file under `dev/programme/triage/`, and the branch's only other commits are the opener's delivery row and this review-repair commit.

Two facts kept out of the ruling's body but owed to the reader: the seat brief named V119-V122 as pending after `s6-batch35.md` had already ruled them (merged `c73d8984a`, 2026-10-26T22:24:12Z), which this seat reconciled in its state file rather than re-ruling; and the second writer was still emitting its plain HOLD line at 09:38:27Z when this batch was cut.

## Head

`996eb1df1bda32611d3f104d611fb321ce30ef8c`; against `524c1896b6943b3da03d6cad61420ced31e14c9c` the diff is `1b84be41` (the batch file), `6d58fa0bc` (the opener's delivery row) and this review-repair commit (the two corrected claims below; no ruling text changed).

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
- `R10-ORCH-BEATD` is `not-started`, size L, and P197 is **deferred** into its carry 13 (index 12), the context-rotation paragraph, per `dev/programme/triage/s6-batch34.md`; the roster holds no `P197` string: `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c P197` prints `0`.

## Red checks

`none` at the reviewed head `6d58fa0bc404485ca96f543b0c894d6ea8e72a59`: every check-run there was `success` or `skipped` (the r1 review's R8). The repaired head's checks had not run when this body was pushed; locally `tools/pr/prepr.sh` passes with the gate step printing `ok gate mode MODE: SCOPED` (a markdown file under `dev/programme/` is in no test's measured closure; the mode line is the fact, not a script count) and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Forward-carry

none

## Friction

`none`.
