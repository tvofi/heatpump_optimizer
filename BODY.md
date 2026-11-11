`roster_edit.py`'s `_carry_index` resolved `--match` by substring alone, so a bare pending carry whose whole text sits inside a dismissed "From #N, body item X:" sibling could not be named by any match text, and `roster_queue.py`'s `replay_unsafe` refuses the index form in a queue. It now returns the one carry equal to the match text when exactly one is; otherwise the substring rule and its refusals are unchanged. `mark-carry` and `drop-carry` both gain it. Out of scope as briefed: filtering marked carries out of the hits, and any change to `replay_unsafe`.

Alternatives considered: filtering marked carries from the hits (resolves a subset and changes which entry a substring names; briefed out of scope).

Closes the triage item s6-batch195 P619.

## Head

0ceea2fd3f843a29b155631bd4d2c52a4af654ef (code head; base ee64358be7eeccaec5178a923cb3b83a18a924a0).

## Mutation proof

Deleted the predicate `if len(exact) == 1: return exact[0]` in `_carry_index`, ran `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 280 checks, 2 failed`; failing checks "drop-carry --match equal to a carry inside a sibling is that carry" and "drop-carry --match unique substring still resolves" (the latter fails because it follows the former's state in the same fixture). File restored.

## Null control

At the base, a match equal to carry A that is a substring of sibling B hits both and refuses as ambiguous; that is what the mutated tree above reproduces (the first failing check). The null arms pass on the fix: a match equal to no carry that hits two ("zeta") still refuses as ambiguous, and a unique substring ("body item") still resolves.

## Figures

- Self-test result: `python3 tools/audit/seat/roster_edit.py --self-test` prints `280 checks, 0 failed` at the head.
- Gate: `tools/pr/prepr.sh` run with `PREPR_SKIP_CLOSURES=1` (the interpreter lacks homeassistant, ruled allowed) printed `PRE-PR: 0ceea2fd3f84 ... rc=0`; structure ratchet passed via its `merged structure` step. The mode line read `MODE: SCOPED`.
- Not run locally: `GOLDEN_MODE=drift`, the full scope.run list; the diff touches one file under `tools/audit/seat/`.

## Red checks

none

## Forward-carry

none

## Friction

none
