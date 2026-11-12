Adds the report-only convergence scorecard as a beat row (R10-MACH-SCORECARD): `tools/audit/seat/scorecard.py` computes A_gate, A_run, Y_rev, M_first, Y_train, H, S, E, C and K by the study's section-7 rules; the `scorecard` row of `beatd.jobs.json` runs it daily into `S/beatd/scorecard.txt`. No gate, exit code or digest wake changes: the digest hears only `scorecard: UNREADABLE` when the instrument fails. Inputs: the row reads the overlay's `train_log` (and optional `sweep_record`, declared in `sweep_template.md`) and `S/scorecard/{runs.json,jobs/,verdicts.json,merges.tsv,roster.json}`; M_first reads the class-word family map as a literal from `S/study/work/yield.py` (never executed). An input it cannot read prints `unread` on that line, never a number. H has no null control: the study gives it none (a branch-token naming measure) and the line says so. C and K share one row. The study branch is not copied into the tree; the rules live in the code and in `instruments/scorecard.py.md`.

## Head

c766208d486edd8f80323d615af802c08aa5c3ce

## Mutation proof

One mutant per predicate of `scorecard.py` (window sizes, the gate-versus-run split, first-verdict kind, machinery family membership, SKIP and PARK, the train-named filter, hotfix token and class filter, each escape arm, the cancelled streak, the seat filter of K, the ratio and the unreadable count) is planted in a temp copy by `python3 -I tools/audit/seat/scorecard.py --self-test`, and each must be killed by the named case; plus three row mutants (rc check, sweep_record hand-on, the scorecard.txt write) in `python3 -I tools/audit/seat/beat_jobs.py --self-test`. Both end `ok`/`0 failed` only when every mutant is killed. The first-verdict de-duplication key is not mutated: it cannot change a first verdict.

## Null control

Each line has one in the self-test, run on the unmodified tree: a failure only outside the `gate` job counts green in A_gate and red in A_run; a bus of merge verdicts prints 100% Y_rev and 0% M_first; a log with no SKIP or PARK prints 100% Y_train; no cancelled run and no recycle line print C 0 and K 0; no escape adds none; frozen machinery and product keep S's ratio. H has none, by the study's own text.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

scorecard: stale: the refresh scripts of the study (`runs_refresh.py`, `verdicts_dump.py`, `merges.py`), the FAMILY map (`yield.py`) and the sweep record that K counts are not in the tree, so the row reads `unread` until the orchestrator provisions `S/scorecard/`, `S/study/work/yield.py` and the overlay's `sweep_record`. Carry: dismissed: out-of-tree session inputs, named in instruments/scorecard.py.md
