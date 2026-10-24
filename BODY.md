Root-cause record for the red `tests / ci-ratchet` on `main` from `d5dc3e26a`: `tests/ci_ratchet.py` keyed push runs on `.name == "CI"`, which `ci.yml`'s `run-name:` rewrites. Process state (d); the cost test refuses a new countermeasure. Docs and register only (the class id is also in finding.schema.json's class_guess enum and the finder's generated block, via fold_ledger.py sync, so the agreement lane's finding-class-id readers agree; `node tools/policy/agreement.mjs` after `python3 -I tools/policy/agreement_py.py --run` prints AGREEMENT ok): `dev/audit/rca/R10-RCA-CI-RATCHET-RUN-NAME.md` and a `dev/audit/config/bugclasses.json` row for the P2b assembly class (total 0, 4 non_round_instances, barrier null; triage P52 rejected a barrier).

## Head

f5b2f4624994807939b717533dc6d8f0a0b3fb6d

## Mutation proof

n/a: one document and one register row, no code or check changed. `python3 tools/audit/fold_ledger.py check` printed UNKNOWN-RCA and DRIFT before the row's _rca entry and refresh, and 0 violations after.

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
