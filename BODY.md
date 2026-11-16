Hotfix for a red main: push run 43774717279 at 921214bf (merge of #3626), job governance / instrument-self-tests, step "Refuse a self-test read set the committed table misses" (selftest_scope check, 16 UNDER-SCOPED refusals). Newer merges added reads of dev/programme/RULINGS.md, tools/audit/seat/finder_overlap.py, tools/audit/seat/plant_recall.py, tools/audit/seat/pr_args.sh and tests/mutation_ledger/killed_by/running_signal.py. This re-records tools/ci/selftest_closures.json with `selftest_scope.py record` on Linux with strace (119 steps, 0 failed, 0 broken traces); the diff is 42 added lines, no removals, and runs under the union rule.

## Head

82e301585d2af0ae0a3c5d3ae9ff2fa753198e49

## Mutation proof

n/a: data-file re-record; the instrument's own self-test is the proof and is untouched.

## Null control

Unmodified main's committed table lacks those reads, which is the red above.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
