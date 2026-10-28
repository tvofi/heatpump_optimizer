Fix review: blocked fb2f3de8624bbdcff8d1f801ada3d7c161f1af33 carry-missing: not carried to R10-FLOW-BOARD

bus-nonce: c3bdf81ffd6ef6deb474489e972c566e
round: 1 (fresh dispatch; PR marked ready by this seat on the orchestrator's instruction)
measured-head: fb2f3de8624bbdcff8d1f801ada3d7c161f1af33 (re-read at post: unchanged)
base: edd7e0e14e08279d0ddc53ec4fcc983570edf12a

RESULT triage gate (roster_edit.triage_refusal / ruling_verdict, driven at the head):
  committed  -> verdict DEFER, refusal "dev/programme/triage/s6-batch47.md#P235 is not an ACCEPT ruling (DEFER)"
  mutant DEFER->ACCEPT -> refusal None (carry would land) -- mutation proof reproduces
  mutant DEFER->REJECT -> refused (REJECT); wrong pid P236 -> refused (no such entry)
  null (file absent, base) -> "the triage ruling ... is not on the roster branch or origin/main" -- reproduces
RESULT route exists: R10-FLOW-BOARD is in wave-r10-groups.json (origin/main and handoff/audit-r10-roster 05c60458a), resume.stage in-progress, resume.pr 2883; #2883 OPEN; its body's ## Red checks answers root-cause-detectable: tests/closures with the 3.9 s cheaper detector and process state (c), and states the RCA "belong[s] to a separate root-cause seat" (owed: orchestrator to-main ledger "SEAT-OWED root-cause R10-FLOW-BOARD #2883"; no root-cause seat or dev/audit/rca file exists yet)
RESULT V149 quote: matches proposals.md V149 ("the 2nd instance in one PR"); P235 unused elsewhere on origin/main
RESULT figures: closure.py:1221-1225 "for argv in spawned" OK; ci_predict.py:795 "a data-file read is not seen" OK; prepr.sh:672-675 PREPR_RECORD_CLOSURES OK; 2b84db687 "leave the closures step to CI off Linux" OK; 28b0fa0f3 on refs/pull/2883/head OK; argv/command-line subjects 0 OK
RESULT figure NOT re-derived: "311 commits" -- the enumerator prints 310 at edd7e0e14 now (UTC, CET and PT alike) and 314 with --since=2026-10-01T00:00:00Z; git approxidate fills the current time of day into a bare date, so the command's output moves with the clock. Non-binding to the DEFER, but the figure should name a fixed instant
RESULT live check-runs at head: 45, 0 failed, 2 pending (gate, prelude)

BLOCK (fix-review.md step 10; finding-propagation.md Enforcement): the body's ## Forward-carry ends "Carry: R10-FLOW-BOARD" and the ruling binds that stage's root-cause seat (its cost test decides; a no-countermeasure result plus a further instance on another PR returns the item to triage). It narrows what that later seat does, so it must be in the group's brief before merge. At handoff/audit-r10-roster 05c60458a the R10-FLOW-BOARD brief (1279 chars) names none of P235, V149, #2883, argv, ci_predict or root-cause, the group has no carries, and the body cites no roster SHA. To clear: land a roster carry on R10-FLOW-BOARD (via the roster seat; it must not cite "triage P235" as a proposal source, since the gate refuses a DEFER citation -- phrase it as the root-cause obligation with its control: record the changed self-test under closure._exec_record, expected the two INERT_EXCEPT paths, null = 3bd284f74 recording files none), cite the roster SHA in the body, and re-dispatch. Also re-state the 311 figure against a fixed instant. Carry: R10-FLOW-BOARD
