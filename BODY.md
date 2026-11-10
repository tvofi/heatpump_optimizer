Main-red hotfix: `governance / instrument-self-tests` red on main at 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb (run 42780661829, job 129709886308), `UNDER-SCOPED step prepr: files misses ['docs/img/card/advisor-light.png', ...] (+4974 more)`.

**Cause: a racily clean git index, not a tree walk in prepr's code.** A fresh checkout leaves every file it wrote in the index's own mtime second "racily clean". Those are the alphabetical tail of the checkout, because git writes files in index order. The first index-refreshing git command (`git status`) run in the real checkout opens and hashes each racy file. Under strace those opens fold into whichever traced step ran that command first. In prepr's self-test, that command is `WIRE_PORC=$(git status --porcelain)` in the real checkout, in the red-check-arm wiring block of `tools/pr/prepr.sh`. The arm's later `git status` calls read nothing, because the first call rewrote the index. CI's measured `files` for prepr start at `docs/img/card/advisor-light.png` and run through `tools/**`: exactly a checkout tail. The read set therefore moves with scheduling (prepr runs as a background step beside the inline steps) and with the checkout's timing, not with the tree. It is not deterministic. The one commit between the last green re-record (#3409) and this red, #3413, only bumps `tests/pwlane`.

**Fix: `selftest_scope.py settle`.** It waits until the clock is past the newest tracked file's mtime second, then runs `git update-index -q --really-refresh --force-write-index`, so no entry is racy when tracing starts. It verifies the result with `racy_entries`, retries up to three times with a 1.1 s margin past the newest second, and refuses (rc 1) if any entry is still left, or if a file is stamped in the future. It runs untraced in CI's `strace` step, before `launch` starts the background self-tests, and as `record`'s first act. The table is not re-recorded: the committed prepr entry is CI's own measurement and holds the step's real reads, and the cloud-dispatcher over-scope note is left alone with it (informational; there is no re-record to prune it in).

Alternatives that lost:
- **Re-record prepr from run 42780661829's `selftest-closures` artifact.** That widens prepr to `tests/**`, `tools/**` and `docs/**`, so prepr would run on nearly every diff. It also bakes in one run's timing: the next run's racy tail starts elsewhere (four local baseline records gave four different sets, listed under Figures).
- **Scope the `WIRE_PORC` arm to its fixture directory (`git status -- "$DABS"`).** That weakens a guard meant to cover the whole worktree, and it only moves the first index refresh to another step's `git status`. That is the same moving read set, in another entry.
- **Drop opens by `git status` in `fold_trace`.** That hides a real content read in a dirty tree, and `git diff` pays the same racy reads.

Same class as R10-RCA-MAIN-SELFTESTS-RED shape 2 (a read set that moves between runs of one tree).

## Head

9679946bc090063bea1d24e74cdaad0675290459 (two commits on origin/main 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb). The fix-head records below ran at its first commit, 143a53d41. The second commit only adds `settle`'s wait margin and retry (see Figures).

## Mutation proof

Pinned in-tree by `tools/ci/selftest_scope_mutants.sh` (it runs in CI's traced step):
- `settle never rewrites the index`: the `update-index` argv is replaced by `["true"]`. Self-test rc 1, `FAIL settle: no index entry is left racily clean (rc=1)` and `FAIL record: it settles a racy index before tracing (racy before, none after)`.

Run locally, not in the harness: deleting `record`'s `if settle_index(root): return 1` gives self-test rc 1, `FAIL record: it settles a racy index before tracing (racy before, none after)`. That arm needs strace and runs only untraced, and CI's mutant step is traced, so that mutant would survive there. It is left out of the harness rather than letting the harness turn the job red. Both mutants: `sh tools/ci/selftest_scope_mutants.sh --self-test` with the second line restored. The harness ends `SELFTEST-SCOPE MUTANTS: every mutant refused`.

## Null control

At 5d09dedf6 (no `settle`), `python3 -I tools/ci/selftest_scope.py record --step prepr --out <f>` in a worktree gave a different prepr entry on each of four runs, against 86 committed:
- 253 entries (`docs/**`, `tests/**`, `tools/**`, `dev/audit/rounds/round9/...` onward);
- 84 entries, on a worktree whose index an earlier run had already refreshed;
- 21 entries (`docs/**`, `hacs.json`, `tests/**`, `tools/**`);
- 282 entries.

In the two kept traces, one `git status` process in the real checkout made the tree-wide opens: 9811 tracked-file opens in one, 3862 in the other.

The self-test's racy fixture is the in-tree control: over files stamped in the index's own second, `racy_entries` names all three, and a traced `git status` opens all three. After `settle` it opens none.

## Figures

- Baseline record entries, 253 / 84 / 21 / 282 (prepr `files`, 86 committed): `python3 -I tools/ci/selftest_scope.py record --step prepr --out <f>` at 5d09dedf6, then `len(json.load(open(f))['steps']['prepr']['files'])`. Rule: one entry per file or collapsed `D/**`, as `write_table` writes them.
- Fix-head record entries, 84 and 84, identical to each other: the same command at 143a53d41, two fresh worktrees recorded in parallel. Each started with 8228 racy entries (`racy_entries`), which `record`'s `settle` cleared. Against the committed entry, the only differences are environment reads that the baseline's settled run shows identically: `tools/policy/fixtures/required-contexts.json` is read only when the live ruleset requires `gate` (`merge_train.gating_names`), and `.gitattributes`, `tests/env_drift.py` and `tools/merge/ledger_merge.py` are merge-driver reads.
- 9811 and 3862 tracked-file opens by one `git status` pid in the real checkout: a scratch fold of the two kept baseline traces with `selftest_scope.trace_events`, grouped by the git subcommand each pid exec'd. That probe is not in the tree; the self-test's traced racy-index arm is its in-tree reproduction.
- `settle` flake and its repair: 2 of 60 self-test runs failed at 143a53d41 (`settle left 5 racily clean index entr(ies)` and `settle left 3 ...`, with five concurrent loops of `python3 -I tools/ci/selftest_scope.py --self-test`), and 0 of 40 at 9679946bc under the same loops. Rule: a run counts as failed when its last line is not `... 0 failed`.
- `settle` cost, 0.82 s on a fresh worktree with 5234 racy entries and 0.08 s with none: `python3 -I tools/ci/selftest_scope.py settle`, timed through `settle_index`.
- Self-test, 109 checks, 0 failed, at 9679946bc: `python3 -I tools/ci/selftest_scope.py --self-test`, untraced with strace on PATH. CI runs it traced, which skips the strace arms.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (`tools/ci/selftest_scope.py` changes the gate itself).

## Red checks

none

## Forward-carry

- Class R10-RCA-MAIN-SELFTESTS-RED shape 2 (a read set that moves between runs of one tree): here the moving part was the index state the checkout left, and this PR builds that countermeasure (`settle`). The one environment-dependent read seen beside it, `tools/policy/fixtures/required-contexts.json`, was measured only locally, and the committed CI entry does not hold it. Carry: dismissed: R10-RCA-MAIN-SELFTESTS-RED is resume.stage done, and the countermeasure lands in this PR

## Friction

none
