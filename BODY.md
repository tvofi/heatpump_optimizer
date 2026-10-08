A root-cause PR for `tools/pr/prepr.sh --self-test`, which went red on healthy trees three times in one hour: the train's recarry of #2062 (211/1), #2010's body push (14 failures in 6d) and #2058's stall. The analysis is `dev/audit/rca/R9-RCA-prepr-tmp.md`.

Five serial runs on a loaded box (load average 59 to 77) separated three causes:

- **Disk.** The volume reached 100%, and every 6d/7d fixture then failed with `No space left on device`. Killed self-test runs leak their fixture clones, about 109 MB each. `$TMPDIR` held 492 directories, 7.1 GB.
- **`printf | grep -q` under `pipefail`.** `grep -q` exits on its first match, so the writer can take SIGPIPE, and the pipeline reads 141, which counts as no match. That is the hazard the `pinned_unrun` note already names. It applied in two self-test rows and in `stamp_paths`, CLAUDE.md rule 4's predicate. Behind 2 MB of diff, `stamp_paths` named a version edit 0 of 5 times.
- **One `star-matcher` row** that failed once in 5 runs and did not reproduce in 18 more.

Linked worktrees are refuted as the cause: the fixtures already run under `throwaway_git_env`, and runs 1 and 2 passed 212/0 from a linked worktree.

This PR changes only `tools/pr/prepr.sh`:

1. `selftest_tmp_root`: every temporary path lives under one `$TMPDIR/prepr-st.*` root, which one `EXIT` trap removes. `HUP`, `INT` and `TERM` become exits so the trap runs.
2. `tmp_floor_check`: below twice the measured peak (223,124 KB, so a floor of 446,248 KB), the self-test exits 3 with one `ENVIRONMENT:` line. If `df` cannot measure, it runs anyway.
3. The four `grep -q` readers now read all of their input.
4. The `star-matcher` row prints its output when it fails, so the next occurrence can be read.

## Head

`d8c34eebc26c018f7f9dcd385cf329e562509cad`. Every local figure below was measured at this head unless it names another commit.

## Mutation proof

- Rows first, code second. At `6468b6f0` (the new rows, no code), `bash tools/pr/prepr.sh --self-test` reports `211 passed, 10 failed`, and all ten failures are the new rows: the two 2 MB `stamp_paths` rows, the three temp-root rows, the three floor rows, and the entry-wiring row.
- `stamp_paths` alone, extracted and driven over a manifest `version` line plus 2 MB of filler, five times each: the head's form named the edit 5 of 5. Changing the predicate back to `grep -qE` named it 0 of 5.
- `selftest_tmp_root` driven alone: a run that makes a clone directory and a `mktemp -d`, then kills itself with `TERM`, leaves no `prepr-st.*` directory behind.
- `tmp_floor_check` driven alone: at a floor of 446,248 KB on 14.8 GB free it returns 0. At a floor of 999,999,999,999 KB it returns 3 and prints `ENVIRONMENT: ...`.

## Null control

- `stamp_paths` over 2 MB with no version line and no heading names nothing in either form (0 bytes).
- `a temp dir with room passes the floor` and `an unmeasurable temp dir runs anyway, never refuses` are rows in the self-test.
- A full self-test run with these helpers (before the hooks-output change and with a floor of 2 KB, `SELFTEST_PEAK_KB=1`) left 0 entries in its `$TMPDIR` and passed every new row: `220 passed, 1 failed`. The one failure was the unreproduced `star-matcher` row, which this PR makes diagnosable rather than fixed.

## Figures

- Self-test, 211/10 before the code and 220/1 with it: `bash tools/pr/prepr.sh --self-test`. Under the owner's heavy-scripts rule, the result at this head is CI's `instrument-self-tests` run, cited once it settles.
- 223,124 KB peak: `du -sk` on the run's temp root once a second over a full `bash tools/pr/prepr.sh --self-test`.
- `tests/layout.py` `GUARD: 0 refusal(s)`: `python3 tests/layout.py`.
- Policy corpus `TOTAL: 0 error(s)`: `node tools/policy/policy_lint.mjs`.
- Scoped gate `MODE: SCOPED -- 0 script(s) run`: `python3 tests/closure.py select --files <the diff's paths>`.
- Five serial runs, the leaked directories, and the `stamp_paths` and `star-matcher` repeats: `dev/audit/rca/R9-RCA-prepr-tmp.md`, section 6.

## Red checks

none yet. This body was written before CI ran at this head. Any red will be named and answered in a re-take of this section.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
