# Proposal triage, session s14, batch 234

Source: the R10-STANDING-CONTRACTS-P2 lane-A fixer's stop record (handoff-wip/r10-standing-contracts-p2
e6ed6421d3, BLOCKED.md) and the group's unmarked carries on the roster branch. Carry indices are
0-based at the roster's current head; line numbers are at origin/main 2ced371c1a. Rulings are the
orchestrator's under mandate 6715477401 (scope all), made by triage s14-42.

## P707: R10-STANDING-CONTRACTS-P2 carries 7, 10, 11, 17 and 18 are already on main

Verdict: NO-OP
Scope: carries 7, 10, 11 (lane A's stop record) and 17, 18 (lane B's range; its handoff
handoff/r10-standing-contracts-p2-p4 e199f727b4 touches only sweep_template.md and sweep_render.py,
which is carry 15).
Evidence: 1b174e9b3 and 0a98a0173f are ancestors of origin/main.
- Carry 7: dev/governance/roles/orchestrator.md:109 reads "only from the plan page and the ledger's
  digest".
- Carries 10, 11: dev/governance/roles/standing-roster.md is the retired stub naming the
  `roster-drain` row of tools/audit/seat/beatd.jobs.json; the row is in the table.
- Carry 17: tools/audit/seat/beat_jobs.py:21 and :263 write new.txt, :329 writes
  `UNACTIONED <key> sweeps=<n>`; sweep_template.md step (5) reads the digest; standing-tick.md is the
  retired stub naming the `tick-digest` and `owed-check` rows.
- Carry 18: beatd.jobs.json carries every mechanical job the carry lists (roster-drain, plan-beat,
  pulse, cancel-sweep, disk, opener), added at 0a98a0173f; the merge seat is outside its list.
Disposition: mark 7, 10, 11 implemented at 1b174e9b319607e9594bfdd7cb21067ca004d340; mark 17, 18
implemented at 0a98a0173ffa8c3a7c3dcc3362eb3e67372a5501. No new work.

## P708: retire the merge and dispatch seats into beat jobs in round 10 (carries 9, 12, 13, 14)

Verdict: DISMISS
Source: BLOCKED.md's question (build merge and dispatch rows, or leave the carries).
Instances: carry 9 (merge seat into a pitch job), carries 12, 13, 14 (dispatch seat into a dispatch
job). tools/audit/seat/beatd.jobs.json at origin/main has 14 rows, none a merge, train or reviewer
dispatch row (`audit-dispatch` runs review_strength.py, beat_jobs.py:578-603). The seats' recent
load, since session s14 began (2026-11-11T01:02Z):
- 48 merges: `git log --first-parent --merges --since=2026-11-11T01:02Z origin/main | wc -l`.
- 46 reviewer dispatches: `awk -F'\t' '$1=="open" && $3=="reviewer-fire" && $2>="2026-11-11T01:02Z"'
  $HPO_STATE_DIR/events.tsv | wc -l`.
Cost: arm (a) is a new L design outside the approved P2 contract-edit design: designer, design
review, fixer, fix review, then one live cycle of each job beside its seat before the seat stops
(the carries' own acceptance and the owner's 2026-10-24 constraint). It sits on the round's closing
chain, whose plan closure has already slipped to 2026-11-16T11:12Z against a mandate ending
2026-11-16T18:00Z: under 7 h of margin for four seat stages plus two live cycles, and a broken
merge job would stop the 48-merge-a-day train on the critical path.
Benefit: the two seats' tokens for the rest of the round (merge on sonnet, dispatch on haiku),
unmeasured; no correctness gain, since both seats already work outside the orchestrator's turns,
which is what the owner's constraint protects.
Binding: the cost lands on the critical path for an unmeasured token saving; the bar refuses it.
Disposition: dismiss carries 9, 12, 13, 14 with the reason that the merge and dispatch seats stay
standing seats for round 10. This is a recorded refusal, not a deferral: standing-dispatch.md:17-18
already states the hand-over condition ("A beat job takes over once a cycle's log agrees; never
inline") and standing-merge.md stays the live contract. Owner-ordered carries 9 and 12 are dismissed
under the mandate; owner visibility is the orchestrator's call.

## Left open (buildable as contract or instrument edits)

- 15: sweep_template.md steps (2), (3), (4), (6); lane B's handoff e199f727b4 carries it.
- 16: hooks_setup.py --check/--install and the digest's STALE line for hooks (no STALE line on main).
- 21, 22: hooks_setup.py and beatd.py liveness-hook parity (P506, P550).
- 23: tools/audit/seat/pulse.py judge_verdict while a train is live (P554).
- 24: dev/governance/roles/fixer.md, the retired `dev/governance/decisions/` citation against the layout guard.
