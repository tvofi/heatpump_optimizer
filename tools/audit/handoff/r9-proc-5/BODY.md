<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Seats stop appending to `RESUME.md`, read the roster through `jq`, and send mechanical turns to cheaper models (round-9 process review, item 10, adopted by tvofi 2026-10-01T16:51Z). Policy text in `tools/audit/round9/fixplan/standing.md` and `docs/HANDOVER.md`.

## Head

Code head 893022c25756de27a60f10d26342b41d6bd939e4 on `handoff/r9-proc-5`, merge base 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0.

## Mutation proof

n/a: prose-only change to a standing template and a handover; no check or production line.

## Null control

n/a: no cost or gain claim is made. The split itself was checked with `wc -c /mnt/project-files/audit-r9/RESUME*.md`: the current file is under the 10 KB budget it states, and the archive is byte-identical to the old log (`cmp` against the pre-split copy).

## Figures

none

## Red checks

none

## Forward-carry

`tools/audit/round9/fixplan/standing.md` (binds every fixer and reviewer seat). The out-of-tree split lives at `/mnt/project-files/audit-r9/RESUME-CURRENT.md` and `RESUME-ARCHIVE.md`; the plan-branch mirror `handoff/round9/RESUME.md` is not updated here (this seat cannot push that branch) and needs the same split by the orchestrator.

## Friction

none
