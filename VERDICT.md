Fix review: merge b451bde0c45b3218ae4099489ac4c1e71cc06f0e

bus-nonce: c39b48f677d055c027bd633752861e95

## Scope

Round 1 review of #2688 (fix/r10-triage-s6-batch1), a ruling-record PR: `dev/programme/triage/s6-batch1.md` (P42-P44) plus its delivery row. Measured at head `b451bde0c45b3218ae4099489ac4c1e71cc06f0e`, merge base `50af6174f`. I re-read the head with `git ls-remote` before writing this and it has not moved. `dev/governance/roles/` has no diff between the merge base and origin/main, so the contract I applied is the current one.

## Rulings against proposal-triage.md

- P42 DEFER: the benefit is unmeasured (3 BUSY waits, no stale write recorded, and an env override exists). The contract says DEFER, never ACCEPT, for that case. The ruling names the owning group and what would change the answer. Compliant.
- P43 ACCEPT: this is a defect in an instrument (a false park), so under the contract's own carve-out it is not a proposal. It is ruled only to set its route, which is the same shape as s5-batch2 P34. The ruling names its destination group, the carry shape and its controls (#2675 refuses before and passes after; the null control is a body citing a carry in neither main nor the head). Compliant.
- P44 DEFER: no incident is cited, and the cost includes a false-positive surface on the roster lint gate. The ruling names what would change the answer. Compliant.
- Every entry carries Verdict/Source/Instances/Cost/Binding, with commands cited beside each figure.

## Findings

- P43 routes a new carry to R10-FLY-CARRY-DISPOSITION, but it is on neither roster `4c54758d7` nor the current `origin/handoff/audit-r10-roster` `9c7ee1826` (`ev/roster.txt`, carries 0-4 hold no P43 text). `roster_edit.py` reads the ACCEPT from the roster branch or origin/main, and the triage seat may not edit the roster. So the orchestrator still has to append it with `roster_edit.py` once this file lands, citing `triage: dev/programme/triage/s6-batch1.md#P43`, with the two controls stated as preconditions. Carry: R10-FLY-CARRY-DISPOSITION
- P42 says "its carry (c) rewrites the relay's handoff arm". Clause (c) is in R10-FLOW-BODY-ONLY's `brief`, not its `carry[]` (`ev/body_only_brief.txt`). The ruling also says "route the observation to that group's fixer; no new carry", but names no mechanism that delivers it. Carry: dismissed: the DEFER stands on its own re-triage triggers, and the observation is unmeasured (no stale write). finding-propagation.md carries only findings established by measurement with a null control, so no carry is owed. The wording slip does not change the owning group, which really does own the arm (files list cloud_relay.sh).

## Evidence

- INERT: `closure.is_inert` is True and `is_gate_file` is False for both added files, and neither appears in tests/closures.json (`ev/figures.txt`).
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0, tree 96f5a5407 (`ev/merge_tree.txt`). VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff is empty).
- Mutation proof: n/a. There is no code line, so no mutant is drawn. Instead I exercised the consumer: `roster_edit.ruling_verdict` gives P42 DEFER, P43 ACCEPT, P44 DEFER, P45 None. `triage_refusal` refuses a P42 citation ("not an ACCEPT ruling (DEFER)") and admits P43 (`ev/ruling_gate.txt`). The body's null control re-derives.
- P43 figures: `queue_pre_flight.py:196` is `ca.load_dests(self.checkout, "origin/main", ...)`. `carry_audit.load_dests` lists carries with `git ls-tree` at that one ref (l.329-338). The class-size command prints 1 (`ev/figures.txt`).
- P42 figures: `cloud_relay.sh:390` skips on `urc = 75`. `tick_loop.sh:76` reads `HPO_TICK_RELAY`. `update_pr.sh` documents exit 75 on a held lock. Out-of-tree logs (`update-2675.log`, `dispatch-report.txt`, `merge-report.txt`) are on the orchestrator's machine, so I could not re-derive the timestamps, pids or line numbers; they are unverified.
- P44 figures: the planted carry (nonexistent file, symbol and line) gives `TOTAL: 0 error(s)` for both the base and the planted copy (`ev/p44_plant.txt`). The `lintBrief` call passing only `g.brief` is at `brief_lint.mjs:988`, with the guard at 987. Against roster `4c54758d7`, 557 carries in 125 of 171 groups re-derive; origin/main's own roster holds 513. The 4 missing paths re-derive exactly (FAHRENHEIT carry 0, BRIEFS-FOLD 19, CI-LAYOUT 11 and 14) under my own rule: backticked, top-level dir of main, no glob. The "62 backticked repo paths" figure does not re-derive: my rule gives 70, or 66 with an extension required, and the file states no rule. I built that instrument myself (`ev/p44_rederive.txt`). The count does not bear on the verdict.
- CI at head (`ev/ci.txt`): no failures. Five test/governance jobs and one prelude were still in progress when read. No pr-contract run appears in the check-runs listing. The body's `## Red checks: none` matches the state as read.
