Adds the report-only convergence scorecard as a beat row (R10-MACH-SCORECARD): `tools/audit/seat/scorecard.py` computes A_gate, A_run, Y_rev, M_first, Y_train, H, S, E, C and K by the study's section-7 rules; the `scorecard` row of `beatd.jobs.json` runs it daily into `S/beatd/scorecard.txt`. No gate, exit code or digest wake changes: the digest hears only `scorecard: UNREADABLE` when the instrument fails. Inputs: the row reads the overlay's `train_log` (and optional `sweep_record`, declared in `sweep_template.md`) and `S/scorecard/{runs.json,jobs/,verdicts.json,merges.tsv,roster.json}`; M_first reads the class-word family map as a literal from `S/study/work/yield.py` (never executed). An input it cannot read prints `unread` on that line, never a number. H has no null control: the study gives it none (a branch-token naming measure) and the line says so. C and K share one row. The study branch is not copied into the tree; the rules live in the code and in `instruments/scorecard.py.md`.

## Head

c77c5a836b396b67beddad333234fe5f7071494c

## Mutation proof

One mutant per predicate of `scorecard.py` (window sizes, the gate-versus-run split, the job named `gate`, first-verdict kind and its ordering by `t`, which verdict is kept as first, machinery family membership, SKIP and PARK, the train-named filter including `MERGED`, hotfix token and class filter, each escape arm, the cancelled streak, the seat filter of K, the sweep record handed to K, the ratchet's exit code, the ratio and the unreadable count) is planted in a temp copy by `python3 -I tools/audit/seat/scorecard.py --self-test`, and each must be killed by the named case; plus three row mutants in `python3 -I tools/audit/seat/beat_jobs.py --self-test`.

Review verdict c766208d, the six survivors, each now `KILLED` by `mutant_run.py --spec` over `scorecard.py --self-test --no-mutants` (the unedited tree is `SURVIVED NULL`, as it must):
- gate_name_any: the planted `jobs_5.json` lists a failed `governance / instrument-self-tests` job after `gate`; case "report: A_gate reads the job named gate".
- report_record_dropped: case "report: K reads the sweep record it is given".
- first_by_input_not_t: `line_review` now sorts the verdicts by `t` before taking the first per pull request, so "first verdict" is the earliest whatever the file order (the ordering point of the verdict; documented in the docstring and `instruments/scorecard.py.md`); cases "Y_rev unordered" and "Y_rev unordered window" on shuffled verdicts.
- named_regex_no_merged: case "Y_train named", a pull request named only on a `MERGED` line.
- ratchet_rc_ignored: case "S: a ratchet that exits non-zero is unread even when it printed JSON"; the guard is kept and pinned rather than called equivalent.
- dedup_dropped: the de-duplication on (pr, head, kind, cls) could not change any first verdict, so it is deleted rather than excused; the first verdict per pull request is `setdefault` over the `t`-sorted list, and its last-wins mutant is killed by "Y_rev first verdict".

Diff arm: `mutant_run.py --diff <merge-base>...HEAD`, run with the scorecard self-test for `scorecard.py` and `scorecard_selftest.py`, and with the `beat_jobs.py` self-test for `beat_jobs.py` (`--path`). Further survivors, listed and not chased (outside the verdict):
- `beat_jobs.py:647` CALL_DEL: dropping the final `write_job(ctx, "scorecard", [])` on success.
- `scorecard.py`: 92 (`family_of` unmapped return), 99 (`load_family` split index), 104/105 (no concluded run guard), 119/120 (no verdict guard), 138 (PARK takes the first `#nnnn`), 183-186 (`sh_out` timeout and OSError return), 217 and 228 (`rd`/`load` unreadable returns), 263-276 (argparse and `main`).
- `scorecard_selftest.py`: the constants of the planted fixtures and the mutant-runner loop (lines 68-73, 118-129, 193-218), which the `--no-mutants` command cannot reach.

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
