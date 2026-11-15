# R10-RCA-FAMILY-FLAKY-SELFTEST: timing-dependent self-test arms read as an introduced red

Round-end family analysis (loop card L8) of the family `flaky-selftest` and proposal
PC-1113-21. Measured at `origin/main` `a39627da59` on 2026-11-15. Lands no code.

## 1. Instances

- `bus.sh` self-test, "two concurrent confirms produce one verdict commit and one post (P354)":
  #3564 at `d6a7b00b` (run 43557083740, 2026-11-14T04:43Z; the same head passed in run
  43549224360); #3566 at `3487296c` twice (run 43609476185 and job 132606865401, 22:31Z), where
  the repair fixer measured 0 failed at the head, the merge base and head plus main, and 8 of 8
  concurrent runs locally (sweep lines 2479, 2485).
- `beatd.py` self-test case (9), "a running instance defers the restart to the next pass": #3576
  at `8317d9e1` (run 43566574065, job 132363359731; line 2104).
- intake carry 167: `tests/entities.py`'s redaction check reds with the wall clock (a
  `dt_util.utcnow` at `...:59.312345` reds it, `...:58.312345` does not).

Four timing-arm reds on three pull requests, plus one clock-dependent test. HANDOVER counted the
family at 3 including the `gh_transient` census row; that row's cause is SIGPIPE and is counted
in `R10-RCA-FAMILY-PIPEFAIL-SIGPIPE.md`, not here.

Required check: `instrument-self-tests` is not in the required set, but `merge_train.py
classify --pr` reads a red at the head and not at the merge base as INTRODUCED, which blocks the
review dispatch and the merge (`fix-review.md` step 11). It blocked #3564, a
`custom_components/` strings pull request, and held #3566 to round 11.

## 2. Named cause

Two arms assert an ordering between concurrent processes (two `confirm` calls racing a lock;
a running instance seen before a restart) with no barrier, so on a loaded hosted runner the
other interleaving occurs; the attribution compares one run at the head with one at the base, so
a nondeterministic arm that fails once at the head reads as introduced by the diff.

## 3. Process state: (c)

The introduced-red rule was followed and is right for deterministic checks; for a racing arm it
attributes noise to the diff. The arms themselves were reviewed and merged as passing; their
nondeterminism shows only under load.

## 4. Class reach

Any self-test arm that sleeps, polls or races a lock. PC-1113-12 (strace `PTRACE_LISTEN` after a
clean exit) is an infrastructure flake of the same job, one instance, deferred.

## 5. Cost test

- cost(defect): each instance costs a job re-run (the job runs 10-25 min) and a seat turn to
  answer it in the body; #3564 waited about an hour (line 2112); #3566 slipped a round.
- P(recurrence): four in two days.
- cost(countermeasure, recurring): zero standing seconds for a deterministic arm (a barrier
  replaces a race); a clock pin in one test.

Passes.

## 6. Countermeasure

Make the arms deterministic, not retried: a barrier before the lock in the P354 arm, an explicit
"running" handshake in beatd case (9), and a pinned clock in the redaction check. Group
R11-HOTFIX-SELFTEST-FLAKE-ARMS (triage `dev/programme/triage/r10-round-end.md#P782`); admissible
under the freeze because it blocked a production pull request. Demonstration owed: each arm run
50 times under `stress`-level load on the fixer's host, failures before, none after; null
control, the arm still fails when the behaviour it pins is mutated. Refused: a blanket "re-run a
red self-test once before calling it introduced" (it would hide a real intermittent defect and
costs a job per red).
