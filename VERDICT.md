Fix review: merge 18b972526f16ea16b9522faf11d1a6781ea28966
bus-nonce: 32a469aef91eac548b0f310a80862f4b

Round 3 -- the R1 rework's resolution delta (round-1 blocked 648f22d7a on the unanswered
instrument-self-tests red; round-2 merged abf7dc7f9 once the schema repair landed). Measured
at detached worktree /Users/timmalmstrom/hpo-seats/r9rev-2132/wt, head
18b972526f16ea16b9522faf11d1a6781ea28966; branch head verified equal at publish time.

- RESULT the resolution keeps every C1/C2 property inside R1's structures: rec() itself still
  carries the COMPOSED_CONSUMED skip and the HPO_CI_METRICS emission, and rec_special() routes
  the cheap-argv scripts through rec on both the --single and the new --scripts-from lane path,
  so a scoped re-derive consumes composed records and emits metrics exactly as the full arm;
  the lane runner is loud (dead lane -> exit 1, missing recording -> exit 1, never silent).
  The workflow's C2 consume step, the composed fetch/verify steps and the three HPO_CI_* envs
  are byte-identical to the tree my round-2 verdict named; only the scoped step's loop became
  one --scripts-from run.
- RESULT re-measured at this exact sha, my own runs: selftest ALL 93 PINS PASSED (my 74 C1/C2
  pins + R1's 19 lane-plan pins, both selftest families running); entities.py rc=0, ALL 2259
  ENTITY CHECKS PASSED; STRUCTURE RATCHET PASSED; budget_raise_gate --self-test 219 checks,
  0 failed.
- RESULT the four C2 refusal arms re-driven at this sha: other-tree rc=1, corrupt recording
  rc=1, roster missing a selectable script rc=1, empty artifact rc=1; only a full-roster
  artifact naming this tree consumes (rc=0, 33 scripts). Fail-closed survives the rework.
- RESULT all five mutants re-killed, each exactly its named arm: proof_consume tree-guard,
  composed_verify rc-guard, ci_ratchet compare -> if False: (1 of 2259 entities), SCHEMA entry
  deleted (3 fails), archscore.* MAX->FREE (2 fails). Tree clean after every restore.
- RESULT check-runs at the head (commit API): instrument-self-tests completed success,
  pr-contract completed success; budget-raise-gate failure x2 is the disclosed owner-gated
  initial record (the owner's approval, unchanged); heavy lanes in progress are the merge's
  own required contexts.
- Round-1/2 findings that still stand and are still owed downstream, none a block: the Linux
  composed-proof byte-identity run (C1's authority) must complete green before reliance, and
  the 53->52 headroom tightening's roster carry at the first post-merge batch.

Round 9, review round 3.
