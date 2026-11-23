# R11-OWNER-STEP-KICK: blocked at handoff -- a second seat holds handoff/r11-owner-step-kick

Question: two fixer seats built this group. handoff/r11-owner-step-kick is 58a605d3a67db81908e060f1af49cd899ab5f8ec (another seat, ten commits from e6873a7fb1, last pushed 2026-11-22T21:14:38Z), and handoff-wip/r11-owner-step-kick-body carries that seat's refused bodies (c19dff3bd2, 2026-11-22T23:55Z). This seat's head, f67fb20bae167d86f0e6fa68ac012a3e0bcbdbc6 (the parent of this commit), passed tools/pr/prepr.sh rc=0 with its body. Which head goes forward: (a) 58a605d3, this seat's work dropped; (b) f67fb20b, replacing handoff/r11-owner-step-kick (a non-fast-forward move this seat may not make); or (c) another seat ports what one head has and the other lacks?

Measured 2026-11-23, origin/main 9276ddf6b1:
- `git push origin HEAD:refs/heads/handoff/r11-owner-step-kick` was refused non-fast-forward; `git merge-base --is-ancestor 58a605d3 f67fb20b` returned non-zero. Nothing was pushed to handoff/ or handoff-body/, and body_push.sh was not run.
- Control: `git merge-base --is-ancestor f67fb20b~1 f67fb20b` returns zero.
- `git merge-tree --write-tree origin/main f67fb20b` reports conflicts in pump_arbiter.py, docs/architecture.md and dev/audit/rounds/round4/D6/claims.{py,json,md} against 9276ddf6b1 (main moved since e3cb5c01); f67fb20b was not merged, because the head choice comes first.

What f67fb20b holds, for (c): flow_anchor.py (Served, note, settled_inlet_c; the inlet keys moved, no re-export); _map_inputs maps min(today's floor, the settled floor); desired reads the record on a flow unit only; module_excess_loc 21779 -> 21761 and unloaded_package_imports 14 -> 12 recorded; dev/audit/harnesses/r11_owner_step_kick.py (classes, leg R replay, leg S soak, H1; 19 EXPECTED lines from its synthetic self-test); the heated-gate flow cells pinned against the written swap command plus a cell that the masked episode now books; 22 closures re-recorded green on Linux; 21 named mutants each killed by a named check, and prepr's one survivor (desired's feedback guard) killed by 8 R10-WATER-SETPOINT-FEEDBACK checks. Its body is the BODY.md the prepr run passed (not pushed).

Carry: R11-OWNER-STEP-KICK (pending orchestrator ruling on which head goes forward)
