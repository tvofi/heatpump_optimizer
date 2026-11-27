Main is red on required `tests / mutation` at 43ec8e327349 (run 46027145718, job 140601839109). #3931 deleted the `return_temp` guard in `FlowCurveBias.observe_temps`; the ledger entry pinning that BOOLOP site (04143c3f, from the D3 pin batch 34867f4987) stayed, so the table refuses: "disposition names no site the inventory generates". This drops the stale entry.

## Head

78021d06c97e3b3913863344483b5bd2c460f2bf

## Mutation proof

Restoring the entry reproduces the main refusal quoted above; with it removed, `tests/mutation_table.py --scope changed --base origin/main` reports "the ledger agrees with the deterministic inventory" and PASSED, and a `--base origin/main~1` run exits 0.

## Null control

Unmodified origin/main: MUTATION TABLE REFUSED (log line above).

## Figures

none

## Red checks

`tests / mutation` on main 43ec8e327349: merge-skew between #3931 (deleted the site) and the D3 pin batch (pinned it); cause is a stale pin. A ledger-vs-inventory check at merge would catch it; the PR-head job only sees its own base. Fixed here.

## Forward-carry

none

## Friction

none
