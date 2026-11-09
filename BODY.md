state_docs.py read the state ref's tip once, generated ~30 s, pushed once with no re-read; a second writer landing in that window refused the push (train postmerge `OWED docs: rc 2`). Process state (d): the push assumed one writer. Fix in roster_edit.py's R10-ROSTER-PUSH-RACE shape: the tip is fetched when read (also cures "failed to unpack tree object"); a refused push whose tip moved regenerates on the new tip, at most `PUSH_ATTEMPTS` (3), then refuses loudly rc 2; a refusal at an unmoved tip refuses at once as not a race; never forced. Alternative rejected: retrying the push alone, which would push a regeneration stale against the rival's tip.

## Head

6ae023651d5d59be12425ce7d8d391a00f3ccc51

## Mutation proof

Mutants of tools/audit/seat/state_docs.py, each run with `python3 tools/audit/seat/state_docs.py --self-test`, all killed: (M1) retry bound made always-true -> 2 checks red (one rival -> rc 0; bounded at PUSH_ATTEMPTS rivals); (M2) moved-tip predicate inverted -> 4 red; (M3) predicate always "raced" -> "non-race refusal: rc 2 at once, named not a race" red; (M4) tip fetch removed -> 4 red. Predicate and retry loop mutated, not a tail.

## Null control

The new self-test arms (rival pushed from a second clone inside generate()) were run at the merge base (origin/main's state_docs.py plus the same arms): 4 checks red, e.g. "race: one rival inside generation -> rc 0" got rc 2 non-fast-forward and "failed to unpack tree object". At the head: all checks passed. No-rival null control ("race null control") gives rc 0 and no race said at both ends.

## Figures

- `python3 tools/audit/seat/state_docs.py --self-test`: head all checks passed; baseline 4 failed (above).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none
