Triage batch 174 rules queue line 270, 2026-11-11. It holds one ruling.

- **P591, ACCEPT, re-pointed: SHIM-COMMENT-GUARD-ONE-CHECKOUT.**
  - `seat_venv.sh --install-shims` bakes one tree's `gh_comment.py` into the shim's comment guard.
  - Three live checkouts run seat tools, so the record posts of all but the last installer are refused. The merge train's #3394 record for #3424 was one of them.
  - The ruling adds a PART 2 ITEM carry to R10-GH-READ-RESIDUE. The guard also accepts any checkout's committed, unmodified `tools/pr/gh_comment.py`, and stays deny-by-default for every other caller.

The diff is one file against the merge base: `dev/programme/triage/s6-batch174.md`, the ruling. No product behaviour changes.

## Head

`1217591a8082f50fbc7d5dd5cf05e369c329472f`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P591 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P592 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat e67b79c9fc...1217591a8082f50fbc7d5dd5cf05e369c329472f`: 1 file, 1 commit.
- The figures come from the installed shim's `gcpy=` line, `ps` argv counts per checkout, the train log and `gh-calls.log`. Each is cited beside its source in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
