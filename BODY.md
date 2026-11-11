Triage batch 184 records P602's owner-routed arm (queue line 281), 2026-11-11. It holds one ruling.

- **P606, ACCEPT: CODEQL-PR-PATHS, as the new S group R10-CODEQL-PR-PATHS.** This records the orchestrator's ruling under mandate 6715477401 (scope all), not tvofi in person, on P602's owner-routed arm.
  - Pull-request runs analyse Python with `tests/` and `dev/` path-ignored. Main's push run keeps the full path set.
  - The required context stays required; the non-gating arm is declined.
  - The target is the PR python Analyze job under 15 min, against 2173-3623 s today.

The diff is one file against the merge base: `dev/programme/triage/s6-batch184.md`, the ruling. No product behaviour changes.

## Head

`642155fde72b0d55f53c8a93aee7bbe5d90b2a70`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P606 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P606 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P607 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...642155fde72b0d55f53c8a93aee7bbe5d90b2a70`: 1 file, 1 commit.
- The figures come from `codeql.yml` and `tests/entities.py` at `cbd23f1c8b`, and from the orchestrator's CodeQL durations, as cited in P602.

## Red checks

none

## Forward-carry

none

## Friction

none
