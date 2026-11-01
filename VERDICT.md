Fix review: blocked 72ea40aa3a30dbd5b59fc16354f55f136367ece3 root-cause-unrecorded: governance / instrument-self-tests is red at this head and the body's Red checks does not name it; pr-contract run 124811159508, started after it concluded, refuses on exactly that

bus-nonce: f15070140438840a4bd4b25ca0d7a330

## Round

This is round 3, a delta on round 2's block at 26f2a6df6a8b (root-cause-detectable). I measured head 72ea40aa3a30dbd5b59fc16354f55f136367ece3 from a detached worktree at that SHA. At 09:43Z `git ls-remote` and the PR API both still gave that head (`ev/head-reread.txt`). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract I read is the one in force.

## Block

- `governance / instrument-self-tests` (check run 124803472179) concluded `failure` at 09:30:04Z. It is an input to `gate`, which is red (runs 124810880905 and 124811291440).
  - The failing step is `bash tools/audit/seat/update_pr.sh --self-test`, with the same two rows failing in the open_pr and pr_args steps: `pr_args self-test: 158 checks, 2 failed`.
  - The rows are `FAIL open_pr: the null control -- an unrelated sleeper survives` and `FAIL null control: a normal successful update_pr leaves nothing behind and stops nothing it did not start`.
  - The cause shows just before them: `Security violation: Requested utility 'unrelated-sleep' does not match executable name: /usr/lib/cargo/bin/coreutils/sleep` (`ev/instrument-self-tests-red-lines.txt`, full log `ev/instrument-self-tests.log`).
- pr-contract run 124811159508 started at 09:39:39Z, after that red concluded. It refuses: `` check `governance / instrument-self-tests` is red and `## Red checks` does not name it ``. `merge_train.py classify` gives `RED ... red: gate`, rc 1 (`ev/ci-classify.txt`).
- The red is not caused by this diff, but it still needs an answer:
  - This run landed on runner image `ubuntu-26.04` (20261025.179.1). Main's green run of the same job at 92588d58 (124783717352) and this PR's green run at 26f2a6df (124707514974) ran on `ubuntu-24.04` (`ev/main-instrument-self-tests.txt`, `.log`). The workflow says `runs-on: ubuntu-latest`.
  - On 26.04, coreutils is uutils' multicall binary, which refuses the symlinked name. The symlink is `tools/audit/seat/pr_args.sh:625`, `ln -s /bin/sleep "$REAP_DIR/unrelated-sleep"`.
  - None of the 15 files in the three-dot diff (`ev/three-dot-files.txt`) is pr_args.sh, update_pr.sh or open_pr.sh.
  - The nightly/delivery-status exception does not cover this check, so fix-review step 11 still requires the body to answer it.
- Class: no cheaper detector in the tree could have shown this before the handoff. A local run uses GNU coreutils 9.4 and passes. The check itself is the cheapest detector, so the class is `root-cause-unrecorded`.
- Repair owed: name `governance / instrument-self-tests` in `## Red checks` with this cause and the finding that no cheaper detector exists. A rerun that lands on a 24.04 runner may come back green, but it does not answer the trigger, and it does not settle the instrument finding below.
- Everything else this round owed is settled at this head (Evidence). A repair that changes only the body leaves that evidence standing.

## Findings

- `tools/audit/seat/pr_args.sh:625` starts its unrelated-sleeper null control through a symlink named `unrelated-sleep` to `/bin/sleep`. uutils coreutils (ubuntu-26.04, which `ubuntu-latest` now resolves to on some runners) refuses that name. So `instrument-self-tests` goes red, independent of the diff, for every PR and for main once a run lands on a 26.04 runner. Carry: dismissed: an instrument defect off this diff with no live roster destination I could verify. The orchestrator routes it, and this PR only owes the Red-checks answer that the Block forces.
- The body's round-3 `## Red checks` defers building the round-2 countermeasure to a separate root-cause seat: a `ci_predict` arm that runs `harness_headers.inline_scan()`, about 1 s, for a diff adding a `.py` under `dev/audit/`. It gives the cause, process state (c) and a cost test, which is what step 11 checks. The arm itself is still unbuilt. Carry: dismissed: root-cause.md assigns the countermeasure to its own seat beside the fix, never inside it. The body records that trigger as answered, and the orchestrator dispatches that seat.

## Evidence

- Delta since round 2. `git log --first-parent` shows 26f2a6df6 -> 52a89253d (merges e0a1227bb) -> 72ea40aa3 (merges origin/main df66556f2).
  - `review_carry.py` prints FRESH-REVIEW: e0a1227bb is a branch-only commit carrying code (`ev/review-carry.txt`), so this is a re-review, not a carry.
  - e0a1227bb changes only `dev/audit/harnesses/r10_prepr_cap_lease_mutants.py`. It replaces `ROOT = Path(__file__).resolve().parents[3]` with an inlined `repo_root`, which `diff` shows is byte-identical to `tools/audit/repo_root.py`'s.
  - I compared the PR's net diff per file, round-2 merge base against round-3 merge base. Only that file moved. Main's own edits to `r10_carry_parser_mutants.py` and `tests/closures.json` leave the PR's hunks unchanged.
- Round 2's block is fixed.
  - `harness_headers.inline_scan()` at the head prints nothing, rc 0 (`ev/inline-scan-head.txt`).
  - My mutant puts `parents[3]` back in the worktree and gives `FAIL depth seams: ...r10_prepr_cap_lease_mutants.py:54`, rc 1 (`ev/inline-scan-mutant-depthroot.txt`). Killed.
  - CI's `tests / fast (3.14)` at this head is `success` (`ev/check-runs.txt`).
- (1) The finder's `runsh_edge.sh` (sha1 d5ca4926aa3d2d130a90fca6aca9a42afec33a38, from probe/rev-3051-a1539223 ev/). I ran it on `git archive` copies of `tests/` with stress.py and harness_headers.py recorded at 3 s (`ev/runsh-edge-all.txt`):
  - Round-1 head eeb947e5: `flock-wrap refused, seat holds no lease: lease held by w, not seat`, `>>> FAILED ... tests/harness_headers.py`, manifest `main-002 1`. The defect reproduces.
  - Control, eeb947e5 plus `_mark_held` after the release in the RenewRefused arm: `main-001 0 #skip tests/stress.py` and `main-002 0 #skip tests/harness_headers.py`.
  - This head: the same two `#skip` rows. Both are named unrun.
  - The head with the re-mark line deleted: `main-002 1`, refused again. The finder's harness sees the mutant.
  - The head with the `if [ -e "$one.waited" ]` block deleted (nomap): `>>> FAILED ... tests/stress.py`.
  - Class enumeration: `flock_wrap` (lines 910-941) has two `release(` calls, 924 and 933. Each is followed by `_mark_held` (`ev/class-enum.txt`), so the two arms behave alike. The unbounded path is unchanged: with `wait_bound=None`, `take` returns only on success, which re-marks anyway.
- (2) `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` at the head prints `ALL 41 gate lock acceptance checks PASSED`, rc 0, with `ok a bounded give-up on re-queue keeps the witness; the next wrap queues again` (`ev/gate_lock-accept.txt`). My own drop-re-mark mutant gives `FAIL ... [first=76 witness_kept=False second=1 ran=False]`, `1 of 41 ... FAILED`, rc 1. Killed (`ev/gate_lock-accept-mutant-remark.txt`).
- (3) and (4) The finder's `runsh_harness.sh` (sha1 593da3b86d10cf1fb75d2fa8857e17b117d6aa95) (`ev/runsh-harness-all.txt`):
  - Round 1, JOBS=2: console `ok`.
  - Head, JOBS=2: console `SKIP`. The manifest is `main-001 0 #skip tests/stress.py` at both ends.
  - Nomap mutant, JOBS=1 and JOBS=2: `main-001 76 ... tests/stress.py`, `FAILED`.
  - The fixer's lease-mutant harness at the head: `M0 clean`, `M-remark killed`, `M-nomap killed`, `M-word killed`, `mutants=3 survived=0` (`ev/lease-mutants.txt`). That is the fixer's instrument, and it agrees with mine.
- (5) and (6) Round 1's finding 3 is dismissed in the body with round 1's reason, and round 2 confirmed that. The body cites no roster SHA, and `## Forward-carry` says none.
  - The P206 and P211 mechanisms are present: `WAIT_BOUND_RC = 76`, `WaitBoundExceeded`, the lapse arm and the witness.
  - The P309 fold is present: `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md`, `OWED_CARRY` at `tools/audit/carry_audit.py:133`, and the prepr.sh process-state (c) WHY at line 992.
  - `carry_audit.py --self-test`: 211 checks, 0 failed.
  - `r10_carry_parser_mutants.py`: `RESULT sites=167 unmapped=0 mutants=241 survived=0`.
  - `field_coverage.mjs`: `FIELD COVERAGE ok`.
  - The body states M2 (P310) and P311 as out of scope.
- Gate and structure:
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0. This tree has no `summary` subcommand (`ev/structure.txt`).
  - `closure.py select --diff df66556f2`: `MODE: FULL -- every test script runs, nothing is scoped out.` (`ev/closure-select.txt`).
  - `rules_sync.mjs --check`: `RULES-SYNC ok`. `policy_lint.mjs --budgets`: rc 0.
  - Both claim files, VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff (`ev/untouched.txt`).
  - The delivery row `dev/programme/delivery/3051.md` is in the three-dot diff.
- `git merge-tree --write-tree origin/main 72ea40aa3`, with origin/main at 92588d581, gives rc 0 and no conflict (`ev/merge-tree.txt`).
- Figures I did not re-derive: the body's prepr `rc=0` at e0a1227bb8 and at 9787f68e15. I did not re-run prepr, because step 11 says to cite CI's heavy runs. Its local `13 of 112 HARNESS HEADER CHECKS FAILED` is machine-measuring, and CI's `tests / fast (3.14)` is green at this head.
- CI at this head, from the whole check-run set: 55 runs, from the paginated commit `check-runs` API (`ev/check-runs.txt`).
  - Red: `governance / instrument-self-tests` (Block), `pr-contract / pr-contract` twice (both refuse the body on that check), and `gate` twice (the aggregate).
  - Everything else is success, skipped or neutral. `CodeQL` is neutral, and that is not a required red.
