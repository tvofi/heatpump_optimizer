Fix review: merge 2a25229f9d07f83c94dbf858c79697ca0d55e5fa

bus-nonce: 776d5cf41256e98b8c13402df64126fb

Round 1. Reviewed head 2a25229f9d07f83c94dbf858c79697ca0d55e5fa (docs-only record: dev/programme/triage/s6-batch61.md and delivery/2970.md).

## Findings

- Rulings P286-P289 use a "Cost and benefit:" paragraph and carry no `Binding:` line or `--budgets` row, which proposal-triage.md lists as the ruling's fields; P286's benefit ("every wrong figure either refuses or allows a dispatch") has no count beside it, which the bar treats as unmeasured. P286 is ACCEPTed as bringing the gate in line with the owner's restated rule rather than as an optimisation, so I do not block. Carry: dismissed: record-only PR; P286 follows the owner's 2026-10-29 rule, P287/P288 are measured, P289 is owner-ruled; the format gap is cosmetic and the roster-edit citation only needs the ACCEPT headings.

## Evidence

- No production code, VERSION, manifest or notes heading touched (three-dot diff: 2 added files). Mutation proof, claim-file drift and budget steps (1-5, 14) do not apply.
- Re-read cited code at the head: pr_cap.py WIP_STAGE/WIP_CAP_DEFAULT=6, wip_groups, dispatch_gate, null control at :290-291; orchestrator_tick.py WIP line :608 and the self-test arm :3688; orchestrator.md section 5 :96-99; cloud_relay.sh review-worktree arm :892-895 and null control :889-890; merge_train.py sweep_bots :1078; roster_lib group_for_branch/critical_path_groups; body_push.sh calls review_packet.py handoff (:56). All match the text. The 15 verdict-ref count, relay-log pass counts and handoff timestamps are on the orchestrator's machine; I could not re-derive them.
- Destinations: R10-FLOW-WIP, R10-FLY-CARRY-DISPOSITION (after R10-FLY-ORPHANS-REWRITTEN), R10-FLOW-BODY-ONLY and R10-TRAIN-OVERLAP-GRADE (carries-open) are live in the roster; R10-FLY-PACKET-RED-PATHS has a handoff ref on origin (not in this tree's roster copy, which lags). R10-FLY-PR-CAP-COUNT and R10-FLY-RELAY-FREEZE-REGISTRY are new fly-ins the ruling asks the orchestrator to append, which is the seat's route. Note: this tree's roster copy shows R10-FLY-ORPHANS-REWRITTEN not-started while the ruling calls it done; the live roster branch is authoritative and was not read.
- carry_audit at the head: 0 finding items, 0 unrouted. figure_lint: 0 refused (6 git commands unverified by design).
- Merge: git merge-tree --write-tree origin/main HEAD exits 0 (origin/main e5ddba1fa, the base). No conflict.
- CI at this head: 7 check runs, arm skipped, prelude/refresh/cancel-superseded queued, none concluded when read. Not a required check I could cite; the train gates on them. No red check, so the red-answer rule (step 11) is not triggered.
