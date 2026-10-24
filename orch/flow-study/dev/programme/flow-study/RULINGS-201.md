Owner rulings, round-10 flow plan (tvofi, 2026-10-21), under mandate 6175172275 (scope all, to 2026-10-28T18:14Z). Basis: the Lean flow study pack, FUTURE-STATE.md section 8; its figures are re-derived by the enumerators in STUDY.md section 0, never carried.

R1 Demand: one full programme round in at most 100 h, previous stamp to this stamp. Merges run on an hourly pitch: one batch train per hour.

R2 Work in progress: lane caps A 4 (critical chain and coordinator.py), B 4 (other product), C 3 (process), F 2 (fly-ins), 13 in total, replacing HPO_WIP_CAP 6 and the coordinator cap of 2. Lane A stays at 2 until R10-FLOW-RECHAIN merges.

R3 Record pull requests merge inside the pitch (train with --bot-prs). Rows stay one per merge (HANDOVER trap 15); only the merge time is batched.

R4 Main is absorbed into an open head only when the head is DIRTY or git merge-tree --write-tree reports a conflict. A clean head stays frozen; the batch proof tests the combined result.

R5 Classes of service. Expedite (red main, Actions quota exhaustion, outage, security, owner-flagged) bypasses the caps, one at a time. A fly-in is size S, registered before dispatch with roster_edit.py append-group as R10-FLY-<topic>, lane F. Scope freezes at the register: anything larger found mid-round goes to the next round's register.

R6 Serial chains order groups whose owning seams overlap, not groups that share a file. R10-FLOW-RECHAIN decides each coordinator.py edge from the two owning seams; orchestrator.md section 5 gains the rule through R10-FLOW-PULL.

R7 Decision 0012: running an existing checker earlier (carry_audit.py check in prepr.sh, the check pr-contract already runs) is not a new lint class. R10-FLOW-JIDOKA may proceed.

R8 The merge-queue probe is authorised on a throwaway branch under a throwaway ruleset only (merge method merge, decision 0010). main-protect-checks is not touched; adoption is a later owner decision on the probe's report.

R9 fix-review step 11 stands on a green pr-contract run that started after the head's last workflow concluded. The reviewer still runs the step-1 mutation proof, the finder's harness at both ends and the class attack.

Unchanged: identities (decision 0011), budget raises, VERSION and notes, --allow-red, and the 0012 moratorium on new policy files and rules. A move in any quality guardrail (red push runs on main, a revert, a reopened issue, fewer real-catch blocked verdicts per PR) stops the flow plan pending the owner.
