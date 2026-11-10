Repairs the stale ruling blocked on this PR: P402 asked for R10-FLY-STAMP-FLUSH-HOLD, which merged as #3280 (`aaaec2128`) before this PR's base. The note is re-derived at origin/main `b8f67a775` and P402 is now REJECT (already landed). Docs only.

## Head

`69ec032a21ebb4a302a0cb01db9ee1a6ee4ec13a`

## Mutation proof

n/a: docs-only diff (`dev/programme/triage/s6-batch131.md`, `dev/programme/delivery/3385.md`), no production line.

## Null control

`roster_edit.ruling_verdict` on the first ruling read `ACCEPT`; on this note it reads `REJECT`, so `triage_refusal` now refuses a carry citing it.

## Figures

- `git merge-base --is-ancestor aaaec2128 origin/main && echo anc` prints `anc`: #3280 is in the base.
- `git grep -c train-hold origin/main -- tools/release/stamp.py` counts the references the first ruling found absent (non-zero here).
- `python3 -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_edit as r; print(r.ruling_verdict(open('dev/programme/triage/s6-batch131.md').read(),'P402'))"` prints `REJECT`.
- `git grep -n "s6-batch131" origin/handoff/audit-r10-roster -- dev/programme/rosters` finds the roster brief that still cites the ruling.

## Red checks

none

## Forward-carry

- dev/programme/rosters/wave-r10-groups.json: the R10-FLY-STAMP-FLUSH-HOLD brief cites this entry, now a REJECT; the group is the merged #3280 and a fixer may not write the roster. Carry: dismissed: the group has landed, nothing in it is left to dispatch

## Friction

- stale-premise: stale: the ruling read origin/main `be813ecd4` and merged after #3280 changed the facts (state d, precondition changed underneath). Carry: dismissed: no countermeasure proposed; the fix review caught it at the one gate that reads current main.
