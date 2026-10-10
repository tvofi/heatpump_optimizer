Fix review: merge f7967b64931c4a2614702f4b1560b04088d03b87

bus-nonce: 9d4d75032b18c0014ec4aff2d5c5ec3d

Reviewed round: R9-CI-1 round 2 (#2123), head f7967b64931c4a2614702f4b1560b04088d03b87
(authored code head 7f40401c7; the head adds only the delivery row). Measured in a
detached worktree at the head; head unchanged at publish (ls-remote re-checked).
Round 2 of this fix; this is its first review.

RESULT lines (finder's-side instruments, run by me at the head tree unless named):

- RESULT entities: ALL 2252 ENTITY CHECKS PASSED at f7967b649 (PYTHONPATH=tests/hastub,
  venv-ci 3.14).
- RESULT mutation-proof: all nine body-named mutants applied one per worktree and each
  reddened exactly the check(s) the body names (mut1 -> the shard-null and empty-pool
  checks; mut2 -> the EXCLUSIVE-tail split; mut3/mut4 -> the refusal-wording check;
  mut5 -> the pin-summary split; mut6/mut7 -> the shard-count check; mut8/mut9 -> the
  budget-wiring check). No mutant passed; the proof is not vacuous.
- RESULT arms-first: entities at 5ae1c1608 (parent 23d354970) fails 9 of 2245 in my
  environment -- the seven R9-CI-1 checks the body names, plus the two "window reader"
  checks, which also fail at the plain main parent 23d354970 with none of this branch's
  code (an offline/API artifact of my harness, not the branch's). The body's "7 of 2245"
  reproduces once that pair is excluded; the 2245 count matches exactly.
- RESULT 43-of-49: reproduced from run 37890872462's own logs (all nine mutation-pins
  job logs downloaded). Eight shards refused "no full-line comment in any file in the
  pool", holding 5+5+5+5+5+5+7+6 = 43 sites; shard 1 measured its 6 ("PIN KILLED: 4
  pinned, 2 left unpinned (2 survived...)"). 43 unmeasured of 49 confirmed.
- RESULT budget-tail: job 113802408312 (run 37925123437, shard 3, base b2b6acd64) prints
  the 357 s env_drift baseline ending 11:47:22, then all shared driver runs green until
  13:55:08 (2 h 07 m 48 s ~= 128 min), then five "NOT RUN ... not started: it would have
  overrun" and "MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out,
  5 not started for --budget-minutes". The sites had run every shared driver green; the
  old wording lied. The fix keeps them measured, not re-labelled only: draft #2080's pin
  job ran the same five-site pool under --budget-minutes 260 and pinned all five
  ("PIN KILLED: 5 pinned, 0 left unpinned", "measure: measured, 4 anchor(s)", "shards
  merged: measured", "AUTOFIX: changed", bot push 61fbb9dd, run 38043679085) in ~94 min
  wall clock -- the 260-minute budget holds on a real head with margin. The ~248-min
  derivation is a model and over-predicts here; its conclusion (260 suffices) is what
  was measured, and a conservative model sizing a wall-clock budget games no metric.
- RESULT null-control (green head): run 38034950357 at a5005008d concluded success,
  mutation success, mutation-pin-plan/mutation-pins/mutation-autofix skipped, no bot
  commit. Reproduced.
- RESULT held-run: at both bot heads the branch-level run query returns exactly four
  workflow_dispatch runs and zero pull_request runs (a9ba0b8874092... and
  6308498975f4...). pr-contract.yml lists only pull_request/merge_group (job
  if: pull_request || merge_group) and budget-raise-gate.yml only
  pull_request/pull_request_review/merge_group -- neither takes workflow_dispatch;
  governance.yml does (line 44) and owns policy-docs/env-matrix/wave-script. The rule
  and job comments this diff corrects were wrong; the correction is measured.
- RESULT dispatch-arm refusal: stated as a measurement and cited to the sibling lane
  (R9-RC-AUTOFIX-GOVERNANCE). Verified independently: ruleset 23698884 has 17 required
  contexts; check-runs at a9ba0b887 are 30 completed, 0 pending, with ABSENT =
  budget-raise-gate, env-matrix, policy-docs, pr-contract, wave-script -- the same five;
  dispatching governance.yml restores exactly the 3 it owns. The sibling lane's own PR
  #2083 carries this measurement in full, so the cost-test refusal is not an assertion.
- RESULT forward-carry: the ci-watch fixture landed where the body names it --
  ci-watch.sh v3 and INSTRUMENTS.md on origin/main carry the 30-completed / 5-of-17
  ABSENT measurement at the two bot heads; #2083's body carries the 3-of-5 dispatch
  pricing. Present, with the control (the v2 watcher printed nothing at either head).
- RESULT locals: STRUCTURE RATCHET PASSED; policy_lint 0 errors, ci-autofix.md
  91/96 lines 1466/1469 tokens; closure selftest ALL 57 PASSED; ci_predict clean;
  claim files and VERSION byte-identical to the merge base; MODE: FULL selected
  (tests.yml changes the gate itself -- expected).

Red checks at this head, seen and dispositioned:

- closures FAILURE at f7967b649 (run started 16:40Z): its log prints
  "INERT READS UNDER-APPROXIMATED", main's own defect from #2109's pre-study land.
  The diff touches nothing closures reads (tests.yml, mutation_table.py, entities.py,
  ci-autofix.md, delivery row). Repair #2125 merged 18:41Z and main's Tests runs after
  it are green, so any recarry clears it. Main's, not this head's authored work.
- pr-contract FAILURE at f7967b649: its single PR-BODY error is "check `closures` is
  red and `## Red checks` does not name it" -- wholly downstream of the same main red,
  which appeared at 16:40Z, after the body's 16:11Z re-take. The body does answer
  pr-contract on the proof drafts and the killed app_push run. Not binding.

Not re-derived (contract step 8, said here rather than reported as confirmed): the
autofix_statuses.sh corpus counts (63 of 97 statuses read, 34 expired, the post-#2049
status splits, the RO-11 20-run window superseded) -- the instrument, its window and
its date are named in the body; I did not re-run the 200-run sweep against the shared
API quota. Every load-bearing figure above was reproduced from primary artifacts.

Verdict: merge. The three adversarial numbers reproduce from the runs' own logs, the
deliberately-unbuilt arm is a cited measurement I re-derived, the mutation proof is
non-vacuous at every named mutant, and the two reds at this head are main's
pre-#2125 closures defect and its downstream pr-contract echo.
