Triage batch 134 rules on queue lines 96 and 97 and on three items batch 133 left with the orchestrator: five rulings, P419 to P423.

- **P419, ACCEPT changed: the owner rulings reach a group-dispatched seat only through a scratch wrapper.** The fix is a new S group, R10-FLY-DISPATCH-RULINGS. It adds a `--preamble FILE` flag to `cloud_dispatch.py`, on the `--group` path too, and takes over R10-TICK-LEVELS carry 17. Carry 17 is needed because the tracked fixer prompt (line 247) still orders a re-merge whenever main moves. That contradicts `fixer.md` lines 93 to 95 and the owner's ruling. A tracked rulings file is rejected, because each ruling already has a policy home.
- **P420, ACCEPT changed (an owner directive, ruled on form): outside work first.** The mechanism is one roster field, `"source": "outside"`. Three orderers read it: replan `dispatch_tier`, the opener's `default_class` and `order`, and the train's drain key. The order becomes main, hotfix, outside, then today's order. It is a new M group, R10-OUTSIDE-FIRST. The three-valued enumeration and the `orchestrator.md` sentence are rejected: no policy file states the order today. The orchestrator sets the field on the four outside groups.
- **P421, DEFER: move the roster drain onto the beat row (P410).** The move waits for R10-ROSTER-WRITE-SWEEP's P409 carry. The beat row never retries a refusal, and it does not fetch before each op, so it would lose P409's stale-ref ops. Of the 621 sweep-runner marks, 35 are mispaired. All 35 read back as applied at roster `badbae55a`, so no re-queue is owed.
- **P422, ACCEPT: the #3252 codescan_wait fail-closed (P406 cause C).** The code run was cancelled and then re-run. The sweep re-runs only `gate`, so the edit run's `pr-contract` red stood for 3 h 10 min. It is a carry to R10-HOTFIX-GATE-BUSY-DEFER, measured first.
- **P423, ACCEPT changed: P415's measurement.** Its RCA owner is done. It becomes the coverage term of R10-FIXER-MD-SPELLING-CORPUS carry 0's measure-first, the owner's mutant ruling.

The diff is one file against the merge base: `dev/programme/triage/s6-batch134.md`, the ruling. No product behaviour changes.

## Head

`6f0c4422d5649eb47f283c490b23db56e644a8d0`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads ACCEPT for P419, P420, P422 and P423, and DEFER for P421.
- Each of the 5 brief and carry texts in the rulings' `Binding:` passes `triage_refusal`.
- With P422's verdict flipped to REJECT, its carry is refused as "not an ACCEPT ruling (REJECT)".
- A citation of P421 is refused as DEFER.
- The roster at `badbae55a` with both new groups, both carries, the carry-17 move and the files edit applied lints `TOTAL: 0 error(s)` under `node tools/policy/brief_lint.mjs` at `53273de4d`. Before the second commit, it printed 2 path errors (`PROMPT.md` and `open-priority.txt`), and that commit removed them.

## Null control

P424 reads `None`. With the file absent, a carry citing P423 is refused as "not on the roster branch or origin/main". The unmodified roster lints `TOTAL: 0 error(s)`.

## Figures

- `git diff --stat 53273de4d...6f0c4422d5649eb47f283c490b23db56e644a8d0`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.
- No capped file is touched. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and `tests/closure.py select --files dev/programme/triage/s6-batch134.md` prints `MODE: SCOPED -- 0 script(s) run`.

## Red checks

`none`. The merge base is main `53273de4d`, whose 70 check-runs include no failure. This head's checks run after its push.

## Forward-carry

none

## Friction

none
