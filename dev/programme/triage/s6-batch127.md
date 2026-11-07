# Proposal triage, session s12, batch 127 (P393 to P398)

The rolling batch after batch 126. It rules on the six queue lines that followed it, in the orchestrator's numbering for P393 and in queue order for the
rest. Facts were read at origin/main `41aa9050f`, at the roster branch `cdab8348b`, in the verdict and review refs, and in the seat events log. Every figure
that is not a single read comes from `dev/audit/harnesses/r10_triage_p393.py` at `3a45ec251`:

    python3 -I dev/audit/harnesses/r10_triage_p393.py stale  <events.tsv>      # P393
    python3 -I dev/audit/harnesses/r10_triage_p393.py bodies <merged.json>     # P396

The `stale` arm reads the seat events log, which is host-local. The `bodies` arm reads a dump of `gh pr list --state merged --limit 400 --json number,body,mergedAt`, taken 2026-11-07T01:10Z.

## P393: queue-stale-round-verdict, the train admits a superseded merge verdict

Verdict: ACCEPT narrowed. This is an instrument defect: the train takes the newest `verdict/<pr>` tip and so admits a PR over a live blocked finding. It keeps its route as a fix and is not taken on the >10 % exemption. Destination R10-TRAIN-MERGE-LOOP-2 (not-started), with the carry text under Binding. The rule is the queue line's nonce-ordered shape; the cheaper "any earlier blocked at this head" form is refused by the null figures below.

Source: the orchestrator's queue line for batch 127 (incident #3232, 2026-11-06), with its enumerator `scan-stale-verdict.sh`.

Instances (the `stale` arm, 644 verdict refs, 59 instances: the enumerator's own count):
- **STALE, 1:** PR 3232 at `bba5b4d4`. The merge verdict's nonce `2a9f4501` was dispatched at 2026-11-06T20:50:26Z, the blocked verdict's `cc3bfb99` at 22:13:28Z. The rule refuses it. It was not merged: the merge seat killed the train.
- **LATER, 21:** the merge verdict's nonce was dispatched after the blocked one's: a later round's legitimate approval. The rule admits all 21. The cheaper form would refuse all 21.
- **SAME, 4:** one nonce posted both verdicts, so one reviewer revised its own verdict. The rule admits all 4.
- **UNKNOWN, 33:** a dispatch time is missing. All 33 were dispatched before the events log began (2026-10-28). Every open PR's dispatches are in the log, so the rule meets none of them live.
- **Result:** one true refusal and no false refusal among the 26 resolvable instances. No PR was merged over a live finding in the log's window. The incident's cost was one planned train, killed by hand before its batch.

Cost:
- About 30 lines in `tools/audit/seat/merge_train.py` (7871 lines) on the admit path, reading `bus-nonce` from the VERDICT.md of each verdict's `bus-confirmed` review SHA and the dispatch time from the events log. Self-test arms for STALE refused, LATER admitted, SAME admitted and a missing dispatch time refused with a reason, plus a mutant that drops the comparison.
- One git read per verdict commit at admit time. No API call and no standing CPU.
- No capped file: `tests/structure_budgets.json` has no row under `tools/`, and the file is not policy, so it has no `policy_lint.mjs --budgets` row. Six live groups name `merge_train.py`, so the fixer rebases over them.

Binding:
- Carry text: `Carry 8 (triage: dev/programme/triage/s6-batch127.md#P393 at <roster sha>): merge_train.py admit refuses a merge verdict at <head> when a blocked verdict at the same head carries a different bus-nonce that was dispatched later (events log reviewer-fire), and refuses with a reason when either dispatch time is missing; same-nonce and later-dispatch merges are admitted. Self-test: STALE refused, LATER and SAME admitted, missing time refused; a mutant drops the comparison. Re-run dev/audit/harnesses/r10_triage_p393.py stale at your base: 1 stale, 21 later, 4 same.`
- The figures above are the fixer's control. Re-derive them at the fixer's own base; do not carry them.

## P394: replan prices len(carry), so marked carries still cost a part

Verdict: DEFER. The 23.4 h and the byte-identical plan measure the plan's forecast. They do not measure CI time, completion time, right-first-time or tokens (owner bar, 2026-11-05). This changes when a dispatch or critical-path choice the mispricing altered is measured. The owning group is R10-FLOW-TOOLKIT-MODEL (in progress, PR 3264).

Source: queue line `s12-replan-carry-pricing`. Instances: `tools/plan/replan.py` `held_open` at `41aa9050f`, lines 403 to 413, counts `held_open_carries` plus carries appended since, and reads no carry mark. Cost: not taken. Binding: none.

## P395: R10-BUFFER-STORE carry 1, the DHW tank seed, is unrouted

Verdict: ACCEPT (route only). This is a finding's fix, not a proposal. It keeps its route, and this entry rules on form only. A done group is not a destination (`finding-propagation.md`). The recommended destination is a new size-S production fly-in owning the `dhw_temp_trajectory` seed (`custom_components/heatpump_optimizer/coordinator.py`, the plan's tank seed). R10-COMBI-TANK (in progress, L, files `[]`) can take it instead if its design note claims the tank-state seam. The orchestrator chooses.

Source: queue line `s12-buffer-store-carry1`, with the independent verifier of 2026-11-06. Instances: one carry, R10-BUFFER-STORE carry 1, at roster `cdab8348b`. Cost: production fix cost, priced by its group. Binding: the carry text quotes carry 1 verbatim and cites `triage: dev/programme/triage/s6-batch127.md#P395`. It blocks closing issue 2499.

## P396: one refused append aborts every roster_sync write

Verdict: REJECT. The benefit is measured, and it is marginal against a new pre-filter, a new OWED line kind and a second detector.

Source: queue line `s12-roster-sync-refused-append-blocks-all` (incident PR 3248, 2026-11-06).

Instances:
- **Recurrence:** the `bodies` arm over 400 merged pull requests (2026-10-24T21:57Z to 2026-11-07T01:03Z) finds 1 body, PR 3060, whose Forward-carry holds an uncited proposal-sourced `Carry:` line. PR 3242's body before its cure held 5 such lines, read from the orchestrator's before-copy with the same regexes. So there are 2 bodies in 400, 0.5 %, and 1 incident.
- **Incident cost:** four seat turns and one orchestrator ruling (the queue line). A `roster_sync.py` dry run at `41aa9050f` against roster `cdab8348b` today derives no change and refuses nothing.
- **Defect triggers:** neither applies (`defect-root-cause.md`). The incident reached no release, and it turned no pull-request check red. So this is a proposal, not a countermeasure.

Cost: a pre-filter in `carry_plan`, a new OWED kind, a self-test, a mutant, and a second detector in `pr-contract` or `carry_audit`. Two live groups name `roster_sync.py` (R10-ROSTER-READ-SWEEP, R10-TICK-LEVELS).

Binding: the binding cost is that 0.5 % of merged bodies is under the 10 % bar for a new mechanism. The cure that exists, editing the merged body to add the cite, cost one ruling. This changes if a second incident lands inside 400 merges. Re-run the `bodies` arm.

## P397: the mutation lane draws no augmented-assignment deletion

Verdict: DEFER. The queue line names the first step and does not take it. The count of augmented assignments in `custom_components/` that no operator reaches, and the survivors among them, are unmeasured. The instance found in PR 3232 was fixed there by hand. The owning group is the live mutation-tooling owner, R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT (in progress, S), or a new size-S group: the orchestrator chooses.

Source: queue line `s12-mutation-augassign-operator-gap`. Instances, cost, binding: none taken (P392, binding 1).

## P398: cloud_dispatch.py renders the subagent discovery line

Verdict: ACCEPT. This is an owner directive (tvofi, 2026-11-06, quoted in the queue line: "Drop the frugal change. Instead, have the seats use subagents as required"). It keeps its route, and this entry rules on form only. The form is sound: one rendered line for every role, a self-test arm per role and a mutant that drops it. Destination R10-POLICY-ROLE-PACK (carries-open, PR 3256), which owns the role text `cloud_dispatch.py` renders. A size-S fly-in is the alternative if that group is closing.

Source: queue line `s12-cloud-dispatch-subagent-discovery-line`. Instances: three BLOCKED.md files named in the line (handoff-wip `571144c1`, `9f8c8d57`, `d84b16b0`). Cost: one function and one self-test in `tools/audit/seat/cloud_dispatch.py`, which is not capped and not policy. Binding: the carry text holds the queue line's verbatim sentence and cites `triage: dev/programme/triage/s6-batch127.md#P398`.
