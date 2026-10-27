Triage batch 36 rules V124, the duplicate-seat class: two writers on one role, invisible to the liveness file and unstoppable by the orchestrator. The verdict is **DEFER**: the proposed seat-start claim binds only the seats that implement it, and the writer that motivated the proposal implements nothing, so its benefit is unmeasured against its own target while its costs are immediate. The ruling names what would change the answer and the one element that survives (a launch record written by whoever dispatches a seat, which the orchestrator can adopt in its own dispatch path with no repository change). No product behaviour changes: this seat's diff touches two files — one markdown file under `dev/programme/triage/` and the opener's delivery row.

Two facts kept out of the ruling's body but owed to the reader: the seat brief named V119-V122 as pending after `s6-batch35.md` had already ruled them (merged `c73d8984a`, 2026-10-26T22:24:12Z), which this seat reconciled in its state file rather than re-ruling; and the plain-`HOLD` writer was still emitting its line at 09:38:27Z when this batch was cut.

## Head

`f6cb1a4681eeb6329d1503c5bb5f483c64e43d99` is the repair head: one commit on `b95d3faf8d1ebf1a03d26d39a593ad91e410b891`, changing only `dev/programme/triage/s6-batch36.md`, where the round-3 review's F1, F2, F3 and F6 are answered (each claim now carries the command that prints it, or is gone).

`b95d3faf8d1ebf1a03d26d39a593ad91e410b891` is the round-3 head: it merges the authored code head `35a165fc06f3be19d9f51e95348fc014bac6be9f` and then origin/main `67178dc6a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`35a165fc06f3be19d9f51e95348fc014bac6be9f` is the authored code head, not the PR head; `git cat-file -p 35a165fc0 | head -3` prints its single parent `7c5cb7aeb2cd709327f656bc75a867755157e6eb`, whose own parent is the merge `f92442065832f5ccbe397882b73c79c173ab4dd7` of `6d58fa0bc404485ca96f543b0c894d6ea8e72a59` (the opener's delivery row, `dev/programme/delivery/2877.md` +1) and `996eb1df1bda32611d3f104d611fb321ce30ef8c` (the batch file's P197 correction).

Five commits touch `dev/programme/triage/s6-batch36.md`: `1b84be415` (first, 78 lines), `996eb1df1` (85 lines, +12/−5), `7c5cb7aeb` (89 lines, +12/−8), `35a165fc0` (89 lines, +3/−3) and `f6cb1a468` (98 lines, +32/−23). `524c1896b6943b3da03d6cad61420ced31e14c9c` is the branch's base — `git merge-base 524c1896b f6cb1a468` prints it — and is not a parent at the head.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only consumer, and it reads the verdict. On the committed file:

```
committed verdict: DEFER
committed refusal: dev/programme/triage/s6-batch36.md#P204 is not an ACCEPT ruling (DEFER)
```

Flipping `Verdict: DEFER.` to `Verdict: ACCEPT.` in an out-of-tree copy and re-running the same two calls prints `mutant verdict: ACCEPT` and `mutant refusal: None`: the gate is sensitive to this file's verdict line, so a DEFER cannot be laundered into a carry. The out-of-tree copy is at `/tmp/b36-mutant.md`; the tree is untouched.

## Null control

At the merge base the file does not exist, and the gate prints `the triage ruling dev/programme/triage/s6-batch36.md is not on the roster branch or origin/main`. An entry that does not exist in the committed file (`P999`) resolves to `None`, and is refused the same way.

## Figures

One line per figure, with the command that printed it.

- 18 plain `HOLD (no v7.0.5 tag)` lines at 5:00-5:01 intervals, 08:13:15Z to 09:38:27Z, four of them inside this seat's 21-minute stall (its own last line 08:54:25Z, next 09:15:38Z): `grep -n 'triage s7:' seat-ledger.md`, in the orchestrator state directory.
- the board's alive-age threshold was 660 s and moved to 1800 s after 22 beat gaps, min 1 s, median 57 s, max 1235 s: the orchestrator's measurement and change, recorded in its 09:37Z message and in this seat's state file, not re-derived here.
- `R10-ORCH-BEATD` is `not-started`, size L, with 34 carries: `git show origin/main:dev/programme/rosters/wave-r10-groups.json | python3 -I -c "import json,sys;g=[x for x in json.load(sys.stdin)['groups'] if x['group']=='R10-ORCH-BEATD'][0];print(g['resume']['stage'],g['size'],len(g['carry']))"` prints `not-started L 34`. That file holds no `P197` string: `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c P197` prints `0`. P197 was DEFERred to that group (`s6-batch34.md#P197`), whose carry 13 (index 12) already holds the context-rotation paragraph its substance falls under, so it needs no roster entry.

## Red checks

`none`. At `b95d3faf8d1ebf1a03d26d39a593ad91e410b891`, the head this repair was cut from and the PR head when this body was written, `gh api repos/tvofi/heatpump_optimizer/commits/b95d3faf8d1ebf1a03d26d39a593ad91e410b891/check-runs --paginate` returns 55 check-runs at 16:53Z: 37 success, 17 skipped, 1 cancelled, 0 failed. The cancelled job is `governance / instrument-self-tests` in the `CI code` run at that sha; the `CI edit` run at the same sha completed success. The repair head `f6cb1a4681eeb6329d1503c5bb5f483c64e43d99` was not on origin when this body was written, so it carries no check-runs of its own; its rollup is taken after the push with the same command at that sha. Locally `tools/pr/prepr.sh --body-check` prints `pr-body ok` and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Forward-carry

none

## Friction

`none`.
