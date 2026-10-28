Root-cause seat for #2883's red-check trigger (R10-FLOW-BOARD). This PR runs beside the fix and never inside it (`dev/governance/roles/root-cause.md`). The full analysis is `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md`, and it is registered in `dev/audit/config/bugclasses.json` `_rca`.

**Defect.** `tests / closures` went red twice on #2883. Both times it was `INERT READS UNDER-APPROXIMATED` for `tests/entities.py`:

- run 40548660478 at `8f05b74d4`, on `tools/audit/merge_throughput.py`;
- check-run 122599859589 at `71987ff1e`, on `dev/programme/rosters/critical-path.json` and `wave-r9-groups.json`. That run was FULL scope and took 35 min 10 s, `closures-autofix` answered `skip-manual-repair-owed`, and the round-3 review blocked on it.

`tools/pr/ci_predict.py` was quiet on both heads.

**Cause.** `tests/entities.py` runs the self-tests of `state_docs.py` and `roster_lib.py`. `closure._exec_record` records what those runs read, including every argv token that names a repo file:

- in round 1, `state_docs.py` spawns `merge_throughput.py`, so the read was real;
- in round 3, `roster_lib.blob_at`'s self-test passes two roster paths to `git ls-tree` in a temp repo, so the read was an over-approximation.

The predictor's unit is the static top-level import edge, so it cannot see any read a run makes.

**Process state: (c).** Step 6d ran and passed on both heads, but its unit does not reach a run-time read. The cheaper detector that existed was `--single`, at 868 s to 913 s, and the heavy-scripts rule keeps it out of every local path.

**Countermeasure.** `ci_predict.py` gains the arm SELF-TEST READS, turned on by `--record-self-tests`. `prepr.sh` step 6d passes the flag through `predict_line`'s fifth argument. `body_push.sh` and every other caller stay static. For each changed file that carries `--self-test`, and each host script whose table lists that file and whose source runs its self-test:

1. It records `<file> --self-test` with CI's recorder, `closure._exec_record`, with a 180 s timeout. A timeout prints a `NOTE` and never a red.
2. It grades that record as the host's with CI's own `closure.check(partial=True)`.
3. Each pair `check` names prints as `PREDICT tests / closures SELF-TEST READS ...`. The repair line names INERT_EXCEPT plus `--single`, the route #2883 took.

**Cost test** (`dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` section 5):

- One recurrence costs about 85 min: a 35 min red run, a 15 min `--single` and a 35 min review round.
- In 300 R10 PR merges over 7 days, 4 reds had this shape and 2 are demonstrated catchable.
- The standing cost is 0.5 s to 29 s for each changed hosted file. Measured over the same 300 PRs, it was 63.4 s in total, spread across the 15 PRs that touched one.

Verdict: build it.

No policy text changes, no budget changes, and no claim file, `VERSION`, manifest or `RELEASE_NOTES.md` is touched. The new file `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` is classified: `closure.is_inert` returns True, which is the `dev/audit/` prefix.

## Head

`c68b62203f5e22cb881d8b4dd9ca810d0a11b8bf` merges origin/main `6d86acc909f7fc465e5736771daf8fa45c1373a4` into `80cf79c2cc7cc8d10a31e11cccd599eefd289173`. It is an automatic merge: main's delta touches none of the four files. The figures below were measured at `80cf79c2c` or at this head, three-dot over `6d86acc909f7fc465e5736771daf8fa45c1373a4...c68b62203f5e22cb881d8b4dd9ca810d0a11b8bf`.

## Mutation proof

Each mutant replaces one predicate of `self_test_reads` or `self_test_hosts`. The seat's driver asserts its replacement matched once, runs `self_test_reads_self_test` and restores the file, and `cmp` with a pre-run copy is identical afterwards. **5 of 5 are killed:**

- M1, the host rule is always true: 2 FAIL (`an INERT read the host's inert_reads omit is predicted, for the host that runs it only`, and the UNDER-SCOPED arm).
- M2, a failing `check` is skipped (`if True: continue`): 2 FAIL, the same two arms.
- M3, a recorder failure is graded anyway: 1 FAIL (`a self-test the recorder cannot finish is a note, never a red`).
- M4, the INERT header is never parsed: 1 FAIL (the INERT arm).
- M5, an unchanged file is recorded too: 1 FAIL (`null control: a file the diff does not change is never recorded`).

The unmutated run exits 0.

**The detector shown on the defect.** Head `ci_predict.py` was copied into detached worktrees of #2883's heads and run with `--base 00ab2e97b^1`:

- At `8f05b74d4` (instance 1): rc 1, `PREDICT tests / closures SELF-TEST READS INERT tests/entities.py: tools/audit/merge_throughput.py (its run of tools/audit/seat/state_docs.py's self-test ...)`. Without the flag: rc 0, quiet.
- At `71987ff1e` (instance 2): rc 1, `SELF-TEST READS INERT tests/entities.py: dev/programme/rosters/critical-path.json` and `.../wave-r9-groups.json`, the pair CI named. Without the flag: rc 0, quiet.
- At the repaired head `7b071dbd7`: rc 0, `... (a data-file read is not seen unless a changed file's own self-test makes it)`.

## Null control

**The sweep.** At `6349205b6`, the seat recorded every tracked `.py` that carries `--self-test` and is listed by a host (32 files, 38 file-host pairs), and graded each record as its host's.

- The 8 pairs the host rule keeps grade rc 0. Each is a host whose source names the file within 12 lines of a self-test mention: `ci_ratchet.py`, `archscore/gate.py`, `record_row.py`, `roster_lib.py`, `state_docs.py`, `tools/ci/gate.py`, `ledger_merge.py` and `stamp.py`.
- The 11 rc-1 pairs on that green main are all hosts that list a file as text and never run it, such as `harness_headers.py`, `doc_claims.py` and `arch_score.py`. That is why the host rule exists.

**This branch.** `ci_predict.py --base origin/main --record-self-tests` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 6d86acc909f7 (a data-file read is not seen unless a changed file's own self-test makes it)`, rc 0, in 19.4 s.

**The self-test's own null arms.** `null control: a record inside the host's closure is not` and `null control: a file the diff does not change is never recorded` both pass.

## Figures

- the gate, `PRE-PR: c68b62203f5e22cb881d8b4dd9ca810d0a11b8bf 00000000000000000000000000`, `clean no refusal`, rc 0: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`
- `ci_predict.py --self-test` at this head prints 32 `ok` lines and 5 FAIL lines, and `ci_predict self-test: 5 failed`. At the base `6349205b6` it prints 27 `ok` lines and the same 5 FAIL lines, all in the AGREEMENT arm (`a grammar registered only in the head's copy is predicted red`, and four more). The 5 extra `ok` lines are this PR's arms, so the diff adds no failure: `python3 -I tools/pr/ci_predict.py --self-test`
- three-dot diffstat, 4 files changed, 423 insertions(+), 17 deletions(-): `git diff --stat 6d86acc909f7fc465e5736771daf8fa45c1373a4...c68b62203f5e22cb881d8b4dd9ca810d0a11b8bf`
- scoped-gate mode line, `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`: `python3 tests/closure.py select --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4`
- the arm's self-test, 5 `ok` lines and rc 0: `python3 -I -c "import sys; sys.path.insert(0, 'tools/pr'); import ci_predict as c; from pathlib import Path; sys.exit(c.self_test_reads_self_test(Path('.').resolve()))"`
- the new file is INERT, `True`: `python3 -c "import sys; sys.path.insert(0, 'tests'); import closure; print(closure.is_inert('dev/audit/rca/R10-RCA-CLOSURE-ARGV.md'))"`
- the cost-test and class-search figures are each named with their command in `dev/audit/rca/R10-RCA-CLOSURE-ARGV.md` sections 4 and 5

## Red checks

none

## Forward-carry

none

## Friction

none
