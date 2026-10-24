# tests / closures red on B1 #2656 and B2 #2657 (coordinator, 2026-10-23 ~09:45Z)

The step that fails is "Fail if tests/closures.json under-approximates": it reports INERT READS UNDER-APPROXIMATED, the new
dev/audit/harnesses/r10_ci_layout_* files read by tests/harness_headers.py. closures-autofix would normally repair that,
but it reports skip-failed-recording, because tests/harness_headers.py exited 1 WHILE being recorded under strace.
From the closure-recordings artifacts (harness_headers.py.out):
  FAIL dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound [cpu=309.8s against 240s]
frontier CPU under strace recording (closures job):
  B1 1st 268.3 | B2 1st 260.1 | B1 2nd 309.8 | B2 2nd 309.0  (AFTER, umbrella callee)
  twin #2654 179.1 | P2b-pre #2658 143.9                     (standalone tests.yml)
Without strace (fast): B1 163.6 vs twin 120.8. Locally (macOS) 85.4 on both trees.
The files read by the slow numeric scripts are identical between the trees (only tests/run.sh differs, and it is only read).
Packages and runner image are identical. The whole lane is slower on AFTER: boost_drift_replay 388 s vs 219 s, features 777 vs 428.
Not yet established: runner variance or a systematic cause. Discriminator: B1's closures job re-run at 09:44:50Z (ci_probe rerun-job).

## Runner class (main's ask 1)
jobs API, closures job of each run:
  B1 120328855195  runner "GitHub Actions 1000160258"  group "GitHub Actions"  labels ubuntu-latest
  B2 120329272270  runner "GitHub Actions 1000160276"  group "GitHub Actions"  labels ubuntu-latest
  twin 120328615169 runner "GitHub Actions 1000160220" group "GitHub Actions"  labels ubuntu-latest
  #2658 120337154528 runner "GitHub Actions 1000160389" group "GitHub Actions" labels ubuntu-latest
Set up job (both): Hosted Compute Agent 20261012.601, Azure, image ubuntu-24.04 20261012.334.1, runner 2.338.0.
The callee and the standalone job use the same runs-on label (ubuntu-latest, from the same job definition) and the same hosted pool and group.
Neither step prints nproc or the CPU model, so the machine class is not readable from these logs.

## The discriminator (re-run of B1's closures job, 09:44:50Z -> job 120349266562)
At the same head d0ff8268 and with the same job, harness_headers exited 0. The frontier cost 166.4 CPU-s under strace, and the lane was fast again
(boost_drift_replay done in about 3.5 min). So the 260-310 s readings are RUNNER VARIANCE, not caused by P2b: the same tree and job measured
166 vs 310. The 240 s headroom (50% of 480) is crossed under strace on a slow runner. The fast lane, without strace, measured 120.8-163.6.
The re-run's closures still failed, on the second, real defect, now visible because the recording completed:
  closures-autofix 120356230438: skip-merge-failed -- "files on the INERT list are actually read by tests":
  dev/audit/harnesses/r10_ci_layout_u5/run_part.py, .../unitcheck.py (entities _u5_load), tools/pr/codeql_scope.py (U3's pins).
  P2b defect, fixed on the assembly at 9f7f443cc (INERT_EXCEPT). The same Linux recordings (artifact 12493224545) now
  merge and check clean locally. closures.json is left to the bot commit. closure.py selftest 112/112.
