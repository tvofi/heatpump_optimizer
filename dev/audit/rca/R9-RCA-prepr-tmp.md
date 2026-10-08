# RCA-prepr-tmp: `prepr.sh --self-test` failed on healthy trees on a loaded, full box

The root-cause seat for the self-test reds the merge train and two seats hit
within one hour on 2026-10-08 (`dev/governance/roles/root-cause.md`). Base
measured: `origin/main` at `4dbe5aac`.

## 1. The reds (what triggered it)

- The train's recarry of #2062 (main merged into `5964b583`): 211 passed, 1 failed. The PR head alone passed 212.
- #2010's body push: 14 failures in step 6d, one of them with an empty rc.
- #2058: the push stalled for more than 25 minutes.

**Trigger.** The red-check trigger. Each red stopped a pull request at a gate
that a cheaper and earlier detector could have stopped before it ran.

## 2. Reproduction and cause

The self-test ran five times in series on a fresh merge of `origin/main` into
#2062's head, with load averages of 59 to 77 recorded at each start and end.

| run | result | failures |
|---|---|---|
| 1, 2 | 212 / 0 | none |
| 3 | 211 / 1 | `star-matcher passes (null control)` |
| 4, 5 | 198 / 14 | every 6d/7d row: `fatal: Unable to create '.../index.lock': No space left on device`, then `cannot create temp file for here document` |

Three causes, in order of cost:

1. **The disk ran out, because killed runs leak about 109 MB each.** Every
   fixture `mktemp -d`s its own directory and `rm -rf`s it at its own end.
   No trap covers a run that is killed between the two. Measured on the box:
   `$TMPDIR` held 492 `tmp.*` directories, 7.1 GB, with the volume at 100%
   and 203 MiB free. A git error in a fixture exits 128, and a failed
   here-document leaves an empty capture (the empty `got ,` rows). That is
   the shape #2010 and the train saw. One run's measured peak is 223,124 KB,
   taken with `du -sk` on its temp root every second; it builds two clones
   at once.
2. **`printf | grep -q` under `pipefail`.** `grep -q` exits on its first
   match, the writer takes SIGPIPE, and the pipeline reads 141, so a match
   is reported as no match. The note above `pinned_unrun` already names this
   hazard (27 of 200 runs). Four call sites were still written that way:
   - the two self-test rows `the pr-body step calls body_line` and `... copies_line`. One measurement run on the loaded box failed the first of these with rc 141.
   - the two `stamp_paths` predicates. These are CLAUDE.md rule 4's check, the one `pr-contract` runs through `--version-edit`. Driven with a manifest `version` line followed by 2 MB of diff, the `grep -q` form named the edit **0 of 5** times and the drained form **5 of 5**. A real manifest diff is far under the 64 KB pipe buffer, so this has not misfired in CI. It is still a fail-open in a refusing check.
3. **`star-matcher` (run 3) did not reproduce.** It failed in 1 of 5 serial
   runs, and 0 of 18 later standalone runs of the same `--hooks` call
   failed. Its output was sent to `/dev/null`, so nothing could be read
   afterwards. It is not fixed here. It is made diagnosable: the row now
   prints the check's output when it fails.

Linked worktrees are refuted as the cause. The self-test already calls
`throwaway_git_env`, which unsets `GIT_DIR`, `GIT_INDEX_FILE`,
`GIT_COMMON_DIR` and `GIT_WORK_TREE`, and every fixture clones into its own
temporary directory. Runs 1 and 2 passed 212/0 from a linked worktree.

## 3. Process state: **(d)** for cause 1, **(a)** for cause 2

- **Cause 1 is (d).** The fixtures' own cleanup is sound when a run finishes.
  Its precondition changed underneath it: many seats on one box, runs killed
  by timeouts and `TaskStop`, and a disk shared by all of them. Following
  `defect-root-cause.md`, the countermeasure makes the process notice its
  precondition (a free-space floor) and survive the kill (one root, one
  trap). It is not a new rule.
- **Cause 2 is (a).** The `pinned_unrun` note binds the code below it and
  nothing else in the file. No check finds a `| grep -q` under `pipefail`
  anywhere else.

## 4. Countermeasures (in this pull request, `tools/pr/prepr.sh`)

1. **`selftest_tmp_root`**: one root, `$TMPDIR/prepr-st.XXXXXXXX`. It sets
   `TMPDIR` for child processes and wraps `mktemp`, because macOS `mktemp`
   with no template ignores `TMPDIR`. One `EXIT` trap removes the root, and
   `HUP`, `INT` and `TERM` become exits so the trap runs. A `KILL` cannot be
   trapped; it now leaves one root instead of one directory per fixture.
2. **`tmp_floor_check`**: below twice the measured peak (446,248 KB), the
   self-test exits 3 with one `ENVIRONMENT:` line and builds nothing. Step
   3h's caller prints the last line, so the refusal reads as a box fault and
   not as a list of broken checks. If `df` cannot measure, the self-test runs
   anyway. `PREPR_SELFTEST_FLOOR_KB` overrides the floor.
3. The four `grep -q` readers now drain their input: `grep ... >/dev/null`,
   or `case` on a variable.

Each is pinned by a self-test row written first. At `6468b6f0` (rows without
code) the run was `211 passed, 10 failed`, and all ten failures were the new
rows.

## 5. Cost test

- **Defect cost.** Three gate reds in one hour, each needing a re-run or a
  seat: the train's recarry of #2062 (one round, and an RCA seat), #2010's
  body push, and #2058's stall. One train round plus a seat turn is about 30
  to 60 minutes of wall clock, so roughly 1.5 to 3 hours in the hour
  measured. Load and disk pressure persist while round 9 runs about 15
  seats on one machine, so P(recurrence) is high.
- **Standing cost.** One `df` and one `mkdir` per self-test, under 0.1 s.
  The self-test itself runs in about 3 minutes.
- **Verdict.** Build it. The floor refuses only a box that cannot finish
  one run, so a seat that can run is never refused.

## 6. Figures

- **Five serial runs, load and failures.** `bash tools/pr/prepr.sh --self-test`, five times on a merge of `4dbe5aac` into `5964b583`, with `sysctl -n vm.loadavg` before and after each run.
- **492 directories, 7.1 GB.** `ls -d $TMPDIR/tmp.* | wc -l`; `du -sh $TMPDIR`.
- **223,124 KB peak.** `du -sk` on the self-test's temp root once a second over a full run.
- **0 of 5 against 5 of 5.** `stamp_paths` extracted and driven over a `version` line plus 2 MB of filler, in the `grep -q` form and in the drained form.
- **star-matcher, 0 of 18.** `node tools/policy/policy_lint.mjs --hooks tools/policy/fixtures/policy-rot/hooks/star-matcher.json`, repeated.
