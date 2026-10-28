# R10-RCA-CLOSURE-ARGV: `tests / closures` red twice on #2883, on reads only a run makes

This is the root-cause seat for the red-check trigger on #2883 (R10-FLOW-BOARD). It follows
`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`. It ran
beside the fix, never inside it, from a worktree cut at `origin/main` `6349205b6`. The fix
merged as #2883 (`00ab2e97b`) while this seat ran. The seat posted nothing and filed no
issue. Evidence is in the seat's scratch `ev/` and is named per claim below.

## 1. The defect, reproduced

`tests / closures` went red on two heads of #2883. Both times the static predictor, which
`prepr.sh` step 6d and `body_push.sh` run, was quiet.

| head | CI | what it named | repair |
|---|---|---|---|
| `8f05b74d4` (round 1) | run 40548660478 | `INERT READS UNDER-APPROXIMATED: tests/entities.py: tools/audit/merge_throughput.py` | `d218ef378`: INERT_EXCEPT plus `--single` |
| `71987ff1e` (round 3) | check-run 122599859589, `SCOPE_CASE: full`, 02:45:06 to 03:20:16Z (35 min 10 s) | `tests/entities.py: dev/programme/rosters/critical-path.json`, `.../wave-r9-groups.json` | `28b0fa0f3`: INERT_EXCEPT plus a 913 s `--single` |

At `71987ff1e`, `closures-autofix` printed `skip-manual-repair-owed`. The round-3 fix review
blocked on that red (`rev-fr10/2883/verdict.md`). The fixer's
`ci_predict.py` run at that head printed `no closures ... red predicted ... (a data-file read
is not seen)` (`fix-2883-s8c/ev/ci_predict-71987ff.txt`).

**The seat's own reproduction** is `ev/proto.py`. It records one file's `--self-test` with
`closure._exec_record`, writes the record as the host script's, and grades it with
`closure.check(partial=True)`:

- `roster_lib.py` at `71987ff1e` took 4.7 s. Its `inert_reads` were the two roster paths, and
  `check` printed CI's own `INERT READS UNDER-APPROXIMATED` lines for `tests/entities.py`,
  rc 1. At `7b071dbd7` it took 4.9 s, and `check` passed with rc 0.
- `state_docs.py` at `8f05b74d4` took 41.0 s on a loaded machine. Its `inert_reads` were
  `tools/audit/merge_throughput.py`, and `check` printed CI's line for `tests/entities.py`,
  rc 1.

## 2. Cause

There are two halves, and the defect is where they meet.

1. **The recorder counts a run's argv as reads.** `closure._exec_record`
   (`tests/closure.py`, the "Any repo path that showed up on a subprocess command line" loop)
   files every argv token that names an existing repo file as an open. So does
   `strace -f` on Linux, through the child's own opens. In round 1 the token was real:
   `state_docs.py` spawns `merge_throughput.py flow`. In round 3 it was an
   over-approximation. `roster_lib.blob_at`'s self-test runs
   `git ls-tree -z --full-tree <ref> -- <path>` against a temp repo, and the path
   resolves against the recorder's cwd, the checkout. Over-scope is the safe direction, so
   the recorder is not wrong.
2. **The predictor's unit is the static import edge.** `ci_predict.py` models what a script
   imports at top level. It cannot see what a gate script *runs*. `tests/entities.py` runs
   roster_lib's and state_docs' self-tests in-process, and those self-tests read files and
   spawn processes. The docstring names that blind spot: "a data file a script opens by
   name". So every read that a changed file's self-test makes reached CI unpredicted.

**Which side moved.** Neither recorder rule changed in #2883. `tests/closure.py` and
`tests/closures.json` are unchanged between `3bd284f74` and `71987ff1e` (round-3 review).
The diff added code to self-tests that a gate script runs: the `blob_at` arms
(`70928ca4e`) and the state-doc generator (`c35a4e313`). Each new read was the diff's.

## 3. Process state: (c)

Step 6d is the process that predicts a `closures` red before the push. The fixer ran it on
both heads, and it passed (`ci_predict-71987ff.txt`). It did not produce the intended
result, because its unit, the import edge, does not reach a read made at run time. The
process existed, so this is not (a). It was obeyed, so it is not (b). Its precondition did
not change, so it is not (d): the predictor never modelled run-time reads.

A cheaper detector did exist. It was `derive_closures.sh --single tests/entities.py`, at
868 s on CI's last recording and 913 s on the fixer's Darwin seat (`single.txt`). It is in
no local path, because the owner's heavy-scripts rule leaves recordings to CI, and
`PREPR_SKIP_CLOSURES=1` is sanctioned. That matches `CLAUDE.md`'s (c) example: a check that
existed in CI but in no local path.

The countermeasure changes the unit. It records one changed file's own self-test, which
takes seconds, instead of the host script, which takes 15 minutes.

**Class.** Class I2 ("a measured closure diverges from the real dependency graph") is
barriered, and its barrier held here: CI's `check` caught both reads. What failed is how
early the red was found, not whether it escaped. So this is registered as an
instance-or-process RCA with `class: null`, as `R10-RCA-INERT-PREDICT` was.

## 4. How far the class reaches

**The sweep.** `ev/nullsweep.py` over `6349205b6` covered every tracked `.py` that carries
`--self-test` and is listed in some committed closure or `inert_reads`
(`ev/nullsweep-main.txt`, 9 min 25 s):

- 95 tracked files carry `--self-test`. 32 of them are listed in some script's `closures`
  entry, which makes 38 (file, host) pairs. The sweep built its host set from `closures`
  alone.
- Recording each file and grading it as every listing host's record gives 11 rc-1 pairs on a
  green main. Each is a host that lists the file as text without running it, such as
  `harness_headers.py`'s header scan, `doc_claims.py` and `arch_score.py`. Two timed out at
  180 s: `tests/entities.py` and `merge_train.py`.
- **So a host counts only when its source runs the file's self-test.** The rule is that the
  host names the file within 12 lines of a `self-test` or `self_test` mention. That keeps 8
  pairs: `ci_ratchet.py`, `archscore/gate.py`, `record_row.py`, `roster_lib.py`,
  `state_docs.py`, `tools/ci/gate.py`, `ledger_merge.py` and `stamp.py`, each with
  `tests/entities.py` or `tests/arch_score.py` as host. **All 8 grade rc 0 on main**, which
  is the null control. Both #2883 pairs, roster_lib and state_docs, are among the 8.
- **Round 2 (#2910 review 1).**
  - The code shipped in round 1 did not match this sweep. `self_test_hosts` also counted a
    script that lists the file under `inert_reads` alone, which gave 10 pairs, not 8. The
    two extra were `budget_raise_gate.py` and `selftest_wiring.py`, both hosted by
    `tests/entities.py`, which reads both files as text. On a green tree each predicted a
    red that is false.
  - Four PRs merged in the window touched one of those two files, so each would have taken
    a false 6d refusal. That is 4 false reds against 2 true catches.
  - The rule now reads `closures` alone and never takes a file as its own host.
  - Re-run over the shipped code (`ev/nullsweep-r2.txt`, `ev/nullsweep2.py`), the head's own
    `self_test_hosts` and `self_test_reads`, at merge base `6d86acc90`, give the figures
    listed under `## Null control` in the PR body.

**The argv shape is wider than #2883.** On main, `roster_edit.py`'s and `roster_sync.py`'s
self-tests also put `dev/programme/rosters/wave-r9-groups.json` on a git command line, and
`check` reads them as INERT reads. `tests/entities.py` does not run those self-tests today.
A gate script that starts running them will go red the same way, and this arm predicts it
when it does.

**Past instances, from main's record** (`git log origin/main` since 2026-10-21, 300 PR merges):

- 22 hand-written closure repairs name a CI closures red. 7 more are bot re-records.
- Four were reds of the shape "a gate script runs a changed tool, and the reads it makes are
  unseen":
  - `243df21db`: state_docs, then roster_sync, roster_edit and carry_audit (run 119202770035).
  - `ea464fe68`: merge_train, then ledger.py and proof_watch.py (CI at `f3bd78c35`).
  - #2883's two.
- This arm is demonstrated on #2883's two. `243df21db`'s host pair (state_docs and
  entities) is one the arm records, but this seat did not replay it. `ea464fe68`'s file
  (`merge_train.py`) is outside the rule and timed out, so the arm would not have caught it.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **cost(defect), measured on instance 2:**
  - a red FULL closures run: 35 min 10 s;
  - the `--single` repair: 913 s;
  - one blocked review round: round 4 ran from 05:55 to 06:30Z, 35 min.
  - That is about 85 min of wall time on the critical path. Instance 1 cost a red run and a
    review round as well; this seat did not time it.
- **P(recurrence):** 4 reds of the shape in 300 PR merges over 7 days. 2 are demonstrated
  catchable and 1 is plausible.
- **cost(countermeasure, recurring), measured on the same 300 PRs:**
  - 15 of the 300 changed one of the 8 hosted files.
  - Recording those files costs 0.5 s to 29.0 s per PR (`state_docs.py` is the 29 s; the
    others are 0.5 s to 4.6 s). That totals 63.4 s over the 15 PRs, or 0.21 s per PR when
    averaged over all 300.
  - A diff that changes none of the 8 pays one source scan per changed self-testing file.
  - Even at 5 prepr runs a PR, that is about 5.3 min in 7 days.
- **False reds** are a standing cost too. Round 1's rule would have charged 4 false 6d
  refusals in the window, and each sends a fixer to a 15 min `--single` for nothing. With
  the closures-only rule, the 8 pairs grade rc 0 on a green tree. The 15 PRs and 63.4 s
  above were computed over exactly those 8 files.
- **Verdict.** About 5 min of standing cost and no false red, against 2 demonstrated reds
  at about 85 min each, which is 170 min in the same window. **Build it.** Under round 1's
  rule the same window costs 4 false reds, at least 60 min of `--single` plus the
  refusals, against 170 min: positive, but not the figure round 1 claimed.

## 6. Countermeasure, on this branch

It addresses state (c) by changing the predictor's unit from "an import edge" to "an import
edge, plus the reads a changed file's own self-test makes in the gate script that runs it".

1. `tools/pr/ci_predict.py` gains the arm `self-test-reads` (SELF-TEST READS). For each
   changed `.py` that carries `--self-test`, and each host whose `closures` entry lists the
   file (never `inert_reads` alone, never the file itself) and whose source runs its
   self-test:
   - It records `<file> --self-test` with CI's recorder, `closure._exec_record`, in a child
     with a 180 s timeout.
   - It writes the record as the host's and grades it with CI's own
     `closure.check(partial=True)`.
   - Each line `check` names becomes `PREDICT tests / closures SELF-TEST READS INERT|UNDER-SCOPED
     <host>: <file>`.
   - A recording that does not finish is a `NOTE` and never a red.
   - The repair line names INERT_EXCEPT plus `--single`, the route #2883 took. It does not
     name `--apply-inert`: the host really records the file, so an `inert_reads` entry
     cannot clear it, and the `--single` merge refuses that pair.
2. The arm is opt-in through `--record-self-tests`, because it runs code. `prepr.sh` step 6d
   passes it through `predict_line`'s fifth argument. `body_push.sh` and every other caller
   stay static.
3. `ci_predict.py --self-test` adds five arms (`self_test_reads_self_test`), driven by a
   planted recorder over a scratch table and graded by the real `closure.check`:
   - an INERT read is predicted, for the running host only;
   - a plain read is UNDER-SCOPED;
   - null control: a record inside the closure is not predicted;
   - a recorder failure is a note;
   - null control: an unchanged file is never recorded.

**Shown to detect** (`ev/demo.txt`). Head `ci_predict.py` was copied into detached
worktrees of #2883's heads and run against the PR's base:

| head | without the flag | with `--record-self-tests` |
|---|---|---|
| `8f05b74d4`, instance 1 | rc 0, quiet | rc 1, `SELF-TEST READS INERT tests/entities.py: tools/audit/merge_throughput.py` (its run of state_docs.py's self-test) |
| `71987ff1e`, instance 2 | rc 0, quiet | rc 1, `SELF-TEST READS INERT tests/entities.py: dev/programme/rosters/critical-path.json` and `.../wave-r9-groups.json` |
| `7b071dbd7`, repaired | rc 0 | rc 0, quiet: "unless a changed file's own self-test makes it" |

The pairs predicted are the ones CI named. The machine's load average was 137 to 170
during the demo. Its wall times are upper bounds, not the standing cost: 61 s, 179 s and
340 s with the flag, against 16 s, 96 s and 187 s without it. The standing cost is the
quieter sweep's per-file figures in section 5. The `SELF-TEST READS INERT` repair line in
`repairs()` was added after these runs. It adds output only and changes no rc; the
self-test arms ran on the final text.

**It does not go green by skipping.** The quiet line says the arm ran ("unless a changed
file's own self-test makes it"). The 8-pair null sweep and the self-test's null arms show
it does not fire on a healthy tree.

**Mutation proof, round 2** (`ev/mutants-r2.txt`): 8 of 8 killed by the arm's self-test.
These include the three that survived review 1.

- R2, window 0: 4 FAIL.
- R3, round 1's closures-or-inert_reads rule: 3 FAIL.
- R6, a file as its own host: 2 FAIL.
- M1, the host rule always true: 2 FAIL.
- M2, a failing `check` skipped: 2 FAIL.
- M3, a recorder failure graded: 1 FAIL.
- M4, the INERT header unparsed: 1 FAIL.
- M5, unchanged files recorded: 1 FAIL.

The plant's host names the file on one line and its `--self-test` on the next, which is
what kills R2. A null host names it one line past the window. A third host lists the file
under `inert_reads` alone. The file is also a key of its own.

The unmutated arm passes with rc 0, and `ci_predict.py` was byte-identical afterwards.

`prepr.sh --self-test` pins the wiring: 6d passes `record`, and `predict_line` maps its
fifth argument to `--record-self-tests`. Each pin's predicate was driven over a copy with
that line removed: `6d-record=1`, and `predict_line-maps=1` (`ev/pin6d.sh`).

**Considered and not built.** Narrowing `_exec_record`'s argv rule to resolve a relative
token against the child's cwd would remove instance 2's false read. It would not touch
instance 1, whose read is real. It would also make a closure.py change that forces the FULL
suite and moves the recordings in the dangerous direction: a child that changes directory
would drop real reads. The arm above catches both instances without moving the recorder.

No policy text changes. No budget is raised.
