Fix review: blocked ebbc01eaa62d73c639ffb883f5f2211bd3b11fb8 claim-false: P228's gate rule reads only FAIL-prefixed lines, but gate.py:295 prints reasons 2..n with no prefix; the instance's own gate log names validate-hacs on an unprefixed line 4373, so the stamp-shape fixture and the absent-job null control as written are not the instance's shape
bus-nonce: 7abe72998cf607311b72ce4f498ab67b

# Fix review -- PR #2900, triage s7 batch 45: rule P227-P231 (V141-V145)

Round 2. Reviewed head: ebbc01eaa62d73c639ffb883f5f2211bd3b11fb8, in a detached worktree at that
head, against origin/main b9e286254. `dev/governance/roles/` has no diff between the merge base and
origin/main.

## Results

- Since the round-1 head `75cfbce6f`, the only authored change is P228 in `s6-batch45.md`. Every
  other file in `75cfbce6f..HEAD` came in with the main merges. P227, P229, P230 and P231 are
  byte-identical to the text round 1 verified. `tools/` has no diff between `e8cb7e683` and
  origin/main, so their citations still hold. I spot-checked them again at this head:
  `merge_train.py` has 5,831 lines, `main_green` is at 2422 and `gh pr merge` at 1110, and
  `bus.sh:467` and `open_pr.sh:37,:55` read as cited (`ev/claims.txt`).
- Round-1 F1 is answered in substance. The new rule exempts the aggregating `gate` job and judges it
  by the jobs it names. On the instance, run 40596083060 attempt 1, the failed jobs are
  validate-hacs at 22:37:27Z, env-matrix at 22:43:03Z and gate at 23:10:21Z. Re-read from the API,
  the gate log holds none of the three strings, and both jobs it names are failed jobs of the run
  that match. So the stamp is re-run under the new rule.
- Round-1 F2 is answered. The red lasted 2 h 30 min, from 22:37:27Z to 01:07:45Z. The 2 h 07 min
  figure is 23:10:21Z to 01:17:17Z. The re-run time is 23:43:03Z, which is env-matrix plus 3600 s.
  That is 1 h 24 min 42 s before the hand re-run, and the ruling's "about 1 h 25 min" matches.
  Attempt 2 ran from 01:07:45Z to 01:17:17Z and succeeded (API).
- Null controls are now stated: another failure is not re-run, a `gate` naming a non-infra job is
  not re-run, a `gate` naming an absent job is not re-run, attempt 2 is not re-run, a run before the
  reset is not re-run, and a mutant accepting any match is caught.
- `git merge-tree --write-tree origin/main <head>` exits 0 (`ev/merge-tree.txt`). The live checks
  at the head (`ev/check-runs.txt`) show no failure. The packet refuses nothing, and
  `carry_audit` routes 0 items.

## Findings

- F1 (blocking, claim-false): P228's rule and its carry text read the gate's verdict as "its log's
  `FAIL <job>: ... (this run)` lines". `tools/ci/gate.py:224` prefixes only the first reason
  (`f"FAIL {why[0]}"`). Line 295 prints the rest with no prefix
  (`print("\n".join([outcome] + why[1:]))`). The instance's own gate log, job 122526090837
  (`ev/gate-122526090837.log`), shows this. Line 4372 reads
  `FAIL governance / env-matrix: failure (this run)`. Line 4373 reads
  `validate / validate-hacs: failure (this run)`, with no `FAIL`.
  Three parts of the ruling are therefore false against its own instance.
  1. The Instances line says gate failed "on `FAIL governance / env-matrix: failure (this run)`".
     The log names two jobs.
  2. The control fixture is "of the stamp's shape" with a single FAIL line. That is not the stamp's
     shape.
  3. A fixer following the text parses only `FAIL`-prefixed lines. Then the null control "a `gate`
     red naming a job absent from the run's failed jobs is not re-run" holds only when that job is
     the first reason. A required context that is SKIPPED, ABSENT or red in another run, listed
     second, is not a failed job of this run. The every-failed-job test does not cover it, and the
     gate would qualify anyway.

  Repair: state that the gate's reasons are the first line after `FAIL ` plus each following
  unprefixed `<name>: <state> (...)` line, up to the step's end. Change the stamp fixture to the
  two-reason log, and add the null control with the non-qualifying job as the second reason. Then
  re-take the head. Carry: dismissed: blocking; this PR's re-cut owes the repair
- F2 (non-blocking): I did not re-read the gate job's start time, 23:09:58Z. Its completion,
  23:10:21Z, and its FAIL line at 23:10:18Z are verified. Carry: dismissed: no ruling turns on it
