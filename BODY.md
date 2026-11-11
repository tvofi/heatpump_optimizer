Triage batch 185 rules P607 (queue line 285, the mutation-vacuous countermeasure), 2026-11-11. It holds one ruling.

- **P607, ACCEPT narrowed: MUTVAC-REVERT-ARM, as a carry on R10-MUTANT-RUN-FORKCAP.** The carry adds a report-only `STMT_DEL` operator to `mutant_run.py --diff`.
  - The existing diff operators reach 7 of 23 reviewer-named Python sites. Statement deletion reaches about 14-16.
  - The estimated first-pass gain is about +7-9% relative, below the 20% bar. It is accepted as a one-file, opt-in root-cause countermeasure.
  - A separate revert tool is rejected. The `fixer.md` step 2 mandatory run is policy and is routed to the orchestrator; triage recommends deferring it.

The diff is one file against the merge base: `dev/programme/triage/s6-batch185.md`, the ruling. No product behaviour changes.

## Head

`1c8087c38b64d7c10201f07f83262b7fdd570d93`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P607 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P607 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P608 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...1c8087c38b64d7c10201f07f83262b7fdd570d93`: 1 file, 1 commit.
- The figures come from the mutation-vacuous investigation's `verdicts.tsv`, `heads.tsv`, `sites.tsv` and `verdicts/`, and from `mutant_run.py` at `cbd23f1c8b`, as cited in P607.

## Red checks

none

## Forward-carry

none

## Friction

none
