# r10-process-slim repair 3: superseded handoff, return refs not pushed

A concurrent run of this fixer seat pushed handoff/r10-process-slim at 343a05219ecf1ab6974755863e9405b26713dd87 and handoff-body/r10-process-slim at 22306c98b (2026-11-06 18:34Z), which is the return signal. This run therefore pushed neither return ref: the handoff freezes the branch, and moving it after the signal would move a head under review.

What this run adds, on handoff-wip/r10-process-slim at a302cc5ea34cd92f2f9f3462fbd5edec8d98c5a3 (343a05219 plus one commit, harness only):
- body_push-5 and body_push-6 in dev/audit/harnesses/r10_seat_selftests_mutants.py, both graded by ref_privacy's self-test (STEP_OF). This is the brief's "add a mutant showing the arm still reds when the author guard is removed". The handed-off body does not name such a mutant.
  - body_push-5 drops the identity guard: KILLED, `ref_privacy self-test: 109 checks, 1 failed`.
  - body_push-6 re-plants the reviewed head's order, a `## Head` check before the guard: KILLED, 109 checks, 1 failed. RESULT survivors=0.
- Measured at a302cc5ea:
  - ref_privacy --self-test prints 109 checks, 0 failed; at the reviewed head 6289321a it prints 109, 1 failed (the null control).
  - All 100 instrument-self-tests steps, run as CI runs them: 0 red (M0: 66 seat steps; the other 34 by the same run_step).
  - ci_predict-5 KILLED; prepr.sh rc=0 against main 4b7e1770b; structure passed; entities 2614 passed; archscore dS +0.0000 NULL; MODE: FULL.
- PR-BODY.md beside this note is a full body for a302cc5ea that passes `prepr.sh --body-check` and carry_audit.
- origin/main has since moved to 57958d6a4 (#3258), which is not merged here.

Question for the orchestrator: carry a302cc5ea, a harness-only delta that is an ancestor-extension of the handed-off head, with the two mutants, or leave it. If it is carried, merge origin/main and rerun prepr first.
