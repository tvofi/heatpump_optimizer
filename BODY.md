Triage batch 175 rules queue line 271, 2026-11-11. It holds one ruling.

- **P592, ACCEPT, narrowed: DESIGN-REVIEW-ROUND-CONTEXT.**
  - The design-reviewer render names only the design tip. 25 of the 51 design verdicts on record are later rounds, and each needed its round context pasted by hand.
  - The ruling adds a carry to R10-REVIEW-DISPATCH-RESIDUE. When `design-verdict/<group>` exists, the render states the round, the last verdict's sha, and the design diff range since that verdict.
  - No `--brief` flag is added. A routed owner decision goes into the group brief through `edit-brief`.

The diff is one file against the merge base: `dev/programme/triage/s6-batch175.md`, the ruling. No product behaviour changes.

## Head

`fce42c15c363666e8bbed7fe0f829b5784413f8b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P592 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P593 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 45a8b828a4...fce42c15c363666e8bbed7fe0f829b5784413f8b`: 1 file, 1 commit.
- The figures come from `git ls-remote` of `design-verdict/*` and each ref's `verdict.md` history. Each is cited beside its source in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
