<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Seats stop appending to `RESUME.md`, read the roster through `jq`, and send mechanical turns to cheaper models (round-9 process review, item 10, adopted by tvofi 2026-10-01T16:51Z). Policy text in `tools/audit/round9/fixplan/standing.md` and `docs/HANDOVER.md`.

## Head

Code head 9c619477699fded70a91e518201122a1213748b1 on `handoff/r9-proc-5-v3`, merge base 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0.

## Mutation proof

n/a: prose-only change to a standing template and a handover; no check or production line.

## Null control

n/a: no cost or gain claim is made. The split itself was checked with `wc -c /mnt/project-files/audit-r9/RESUME*.md`: the current file is under the 10 KB budget it states, and the archive is a copy of the old log taken just before the split (not verified byte for byte, and not equal to the plan-branch mirror, which carries later lines).

## Figures

none

## Red checks

none

## Forward-carry

`tools/audit/round9/fixplan/standing.md` (binds every fixer and reviewer seat). The out-of-tree split (a current-state file and a frozen archive beside the old log in the shared audit-r9 folder) is done there; the plan-branch mirror of the log is not updated here, because this seat cannot push that branch, and needs the same split by the orchestrator.

## Friction

none
