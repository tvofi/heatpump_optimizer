R11-HOTFIX: record the selftest reads the round-11 audit tree and currency.py triage directory added

main's required `governance / instrument-self-tests` has failed its drift step, *Refuse a self-test read set the committed table misses* (`selftest_scope.py check`), on every push since 5bc69f9b94 (last green 107988b792). Two merges added directories the committed `tools/ci/selftest_closures.json` did not list: #3724 (5bc69f9b94) added `tests/mutation_ledger/survivor_triage/currency.py/` (4 refusals), and #3723 (8fa10e00ce) added `dev/audit/rounds/round11/**` (a fifth, and 197 more paths in three steps). Neither is a behaviour change: both are new data directories that tree-walking steps list. So this is a table re-record, not a revert.

The table committed here is main's own `selftest-closures` artifact from run 44451107719 at 7ae05284d5: the committed table unioned with that run's measurement, which is the remedy `selftest_scope.py` names. The diff is additions only: 197 dirs each for `prepr` and `dependency-graph-census`, 196 probes for `policy-lint-mutants`, and one entry each for `temp-or-machine-path` and `self-tests-outside-seat`. No run_sha or step set changes, so the table stays fresh and selection stays SCOPED.

Overlap: #3801 (open) adds the four currency.py entries only. This head adds the same entries and also covers #3723's directories. Merging #3801 alone leaves main red on the `dev/audit/rounds/round11` misses.

Closes: none

## Head

27cfce6f1dc83b12f94200612dc50297e2dc2c4d

## Mutation proof

The hotfix is data, so the drift function is replayed against both tables (`drift_emulate.py` in the seat scratch: `selftest_scope.drift(table, measured, workflow_steps)` with measured = the CI artifact's steps). origin/main's table gives `emulated check: 127 gated step(s), 5 refusal(s)`, the same five UNDER-SCOPED lines as job 135315282758. This head's table gives `127 gated step(s), 0 refusal(s)`.

## Null control

`selftest_scope.py select --change M:docs/x.md` at this head prints `MODE: SCOPED -- 22 step(s) run`, so the table is not stale (FULL would mean a run_sha or step-set mismatch). `select --change A:dev/audit/rounds/round11/D0/s1/findings/n.md` selects the same five steps with either table: selection was already covered, and only the drift check's exactness was red.

## Figures

- `selftest_scope check` emulated (instrument): 5 refusals on origin/main's table, 0 at this head.

## Red checks

`governance / instrument-self-tests` is red on main (job 135315282758); this head is its fix.

## Forward-carry

none

## Friction

none
