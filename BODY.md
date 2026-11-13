R10-HOTFIX-SELFTEST-SCOPE-TABLE. Clears main's `governance / instrument-self-tests` red (step `drift`, "Refuse a self-test read set the committed table misses"). Round 2, after `Fix review: blocked eb07df9be8 under-scoped`.

The first cut committed CI's `selftest-closures` artifact (run 43448248435, measured at 154dbb4c61) as the table. That replaced the table with what one run in one environment had measured, and it narrowed entries a Linux strace record still measures: app-push and throwaway-git-helper `objects` True to False (a Linux record at the head refuses both), tick-loop `index` and `objects` True to False, and beatd `index` True to False. Those narrowings came from the first cut. They are not refusals CI printed: CI's refusals contain no flag line.

This cut:

- `tools/ci/selftest_closures.json` is main's table (which contains the merge base's) unioned with that artifact, then with a Linux strace `record` taken at this head, per step: lists unioned, flags OR'd, run_sha from the measurement. It is written by the instrument's own writer (`write_table(TABLE, union_entries(committed, measured))`), not by a hand script. This is `b06e830153`'s method.
- Finding (a): `check --write` now writes that union (`union_entries`), so the uploaded artifact is the table to commit and never drops a read another environment measured. The docstring states the union.
- Finding (b): `drift()` excused a probe only under a directory the table lists, while `write_table`'s `compact_probes` drops a probe under a directory the run listed. Drift over the compacted artifact therefore refused one line fewer than the live check did (33 against 34). `drift()` now also excuses a probe under a directory the run listed. Such a probe is still refused once, as that step's `dirs` miss, whenever the table lacks the directory. So the set of refused steps does not change, and drift over the live measurement and over the compacted one refuse the same lines.
- Main moved under the branch and conflicted on the table (80efc75a32 re-recorded update-pr). The conflict was resolved by merge, using the same writer.

The Linux record at this head added 8 reads to the table that main's 85 commits since 154dbb4c61 brought in (the `tests/mutation_ledger/killed_by/duty_legs.py` ledger directory for three steps, `tests/throwaway_git.py` and the `tests`/`tools` listings for bare-array-expansion) plus the seat-only `dev/programme/delivery/5.md` probes. CI's next push run would otherwise have refused the 6 non-seat ones.

## Head

92d5782bb5823d437125cd00c97ba8ebec5cdf43, measured over origin/main e23124ff6e45bac1d48b4a775dad555a37965355, date -u 2026-11-13. Merge base with main: e23124ff6e.

## Mutation proof

`sh tools/ci/selftest_scope_mutants.sh --self-test` has 4 new mutants, and the self-test refuses each one:
- `check --write writes the bare measurement` (union reverted to the old `write_table(write, measured, root)`): FAIL `check --write: a planted committed read and flag the run did not measure survive the write`
- `the union drops a committed list entry`: FAIL `union_entries keeps a committed read and flag ...` and the `check --write` arm
- `the union drops a committed flag`: the same two FAILs
- `drift refuses a probe the run's own listed dir answers` (fix (b) reverted): FAIL `drift: a probe under a directory the run listed is refused once, as the dirs miss, live and compacted alike`

The script ends `SELFTEST-SCOPE MUTANTS: every mutant refused`.

For the table, reverting it to the PR's first-cut table (the artifact) brings back the reviewer's objects refusals under this seat's Linux traces. Under the drift replay below, the artifact as table refuses 13 lines over the Linux record, including `app-push: it read the objects, the table says not` and `throwaway-git-helper: it read the objects, the table says not`. The table at the head refuses 0 lines.

## Null control

Each table against each measurement, using the instrument's own `drift()` at this head's workflow:

| table | vs CI artifact (run 43448248435) | vs Linux strace record at head |
|---|---|---|
| merge base 154dbb4c61 | 33 (CI's own red; old code printed 34, see finding b) | 36 |
| main e23124ff6e | 33 | 36 |
| first cut eb07df9be8 (artifact) | 0 | 13, two of them objects flags |
| this head | 0 | 0 |

`covers_check` (every read an old table answers, does the new table answer it) gives 0 lost reads at the head for each of base, main, artifact and Linux record. Its control is base against the artifact: 2359 lost reads, the first cut's narrowing.

## Figures

- Drift replay, one line per cell above: `python3 -I -c "import sys;sys.path.insert(0,'tools/ci');import selftest_scope as s;from pathlib import Path as P;r=s.drift(s.load_table(P(sys.argv[1])),s.load_table(P(sys.argv[2]))['steps'],s.workflow_steps())[0];print(len(r))" TABLE MEASURED`. TABLE is `git show <sha>:tools/ci/selftest_closures.json`. MEASURED is `git show eb07df9be8:tools/ci/selftest_closures.json` (the CI artifact; the first-cut body says it is byte for byte the artifact) or the Linux record's `--out` file.
- Linux record: `python3 -I tools/ci/selftest_scope.py record --out FILE` at the head, with trace deletion disabled by the reviewer's driver (the record-keep-traces driver in review/3557's evidence at 53603571bd; it wraps `record` and only disables its trace deletion): `recorded 114 step(s) ...; 0 failed [], 0 broken trace(s)`. Then `python3 -I tools/ci/selftest_scope.py check --traces DIR` over those traces gave `114 gated step(s), 8 refusal(s)` before the union commit (all 8 are reads, no flag) and `114 gated step(s), 0 refusal(s)` after it.
- `python3 -I tools/ci/selftest_scope.py static`: `114 gated step(s), 0 problem(s)`.
- `python3 -I tools/ci/selftest_scope.py --self-test`: `120 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (the table is a gate file), so CI runs everything. The hotfix used `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`.

<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=92d5782bb5823d437125cd00c97ba8ebec5cdf43 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none of the branch's own. Main's red is `governance / instrument-self-tests`, step `drift`. Cause: merged PRs added reads that no one re-measured into the table, and the first cut's remedy (commit the artifact) would have dropped reads only another environment measures. Cheaper detector: none below the push run. Catching drift at PR time would need strace on every step of every PR, which is exactly the cost the scoping removed; the push-time re-measure is the designed detector (CLAUDE.md rule 1). This PR makes the detector's own remedy safe: `check --write` writes the union, so committing the artifact no longer narrows the table.

## Forward-carry

none

## Friction

none
