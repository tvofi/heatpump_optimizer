Root-cause record for the red `tests / ci-ratchet` on `main` from `d5dc3e26a`: `tests/ci_ratchet.py` keyed push runs on `.name == "CI"`, which `ci.yml`'s `run-name:` rewrites. Process state (d); the cost test refuses a new countermeasure. Docs only: `dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md`.

## Head

776d37392cd4a40fa75dd592e64290952e9d478b

## Mutation proof

n/a: one document, no code or check changed.

## Null control

n/a: no check proposed. The refused candidate (the job classifies its own run) was costed, not built.

## Figures

- 6.0 h of red `main` (02:36 to 08:35Z), 5 red push runs: `gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main`
- 113 `ci.yml` runs in 24 h: `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?created=2026-10-23T06:00:00Z..2026-10-24T06:00:00Z&per_page=1' --jq .total_count`

## Red checks

`none`

## Forward-carry

none

## Friction

none
