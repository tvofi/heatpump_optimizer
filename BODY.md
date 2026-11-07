R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code. Repair round 4 for the blocked fix review at 09ec9a880383: every surviving reviewer mutant is pinned, --since-tag works on main's real merges, design-only and double-counted stamp credit are fixed, and the duplicate size measure is removed.

Carries built: 0 (live-refs, in-flight, inflow; the size measure was already built at the base), 2 (absorbed is done, advisory), 3 (liveness by evidence incl. design-only without credit, binding chain and CP slack, uncalibrated-sensitivity note), 8 (critical-path groups start past the slots cap, exempt), 9 (stamp cadence 3 by group, comment-only diffs ignored, matched by merge topic branch, credit only for done groups), 10 and 11 (post-closure groups), 12 (tools/audit/seat/gantt_drift.py).
Carries 1 and 7 were moved to R10-BODY-CONTRACT; 4, 5 and 6 are dismissed as duplicates.

Repair of the review's items:

- Item 1, mutation-vacuous: one pin per surviving mutant in replan.py --self-test (overflow slot filter, post-closure propagation and STAMP-ROUND-MAJOR mark, credit lane, check refusals, produced credit, carries, binding-chain walk, arrivals median, parse_live_refs, post-closure in the peak sweep, stamp cut). gantt_drift.py is_named now has a direct word-boundary pin and a word-boundary mutant in its table.
- Item 2, --since-tag: production_groups_since names a group by a merge's topic branch (as topic_evidence does) and git_commits_since_tag diffs against the first parent; pinned with a real-shaped "Merge pull request #N from tvofi/fix/<topic>" subject and with a real throwaway merge repository.
- Item 3: a stage-live group whose only evidence is a design ref is design_only, no live credit.
- Item 4: stamp credit is filtered to done groups; a credited group still open is counted once.
- Item 5: measure_sizes_hours, --sizes-input, --sizes-since and --sizes-until are removed with their fixture null and two mutants. Carry 0 (2) was already built at the base: --measure-sizes runs size_durations.run (p75, earliest of first commit or PR creation). I did not re-run that measurement here (it needs the network edge); durations.json sizes are unchanged.
- Item 7: inflow_groups_per_hour 0.4 stays reported-only, never scheduled; it is a working estimate not measured here, and the hard-coded slot_sensitivity string (27 snapshots, r=0.045) is a labelled "uncalibrated" note, not a figure this PR claims. Both are routed to R10-FLOW-TOOLKIT-MODEL's successor measurement: Carry: R10-FLOW-TOOLKIT-MODEL.

## Head

`c59bd6b7346fb8db47d7a06db1639222854a309a` is this PR's head. origin/main was merged at f2a015142714 and prepr.sh was run at this head.

## Mutation proof

`python3 tools/plan/replan.py --self-test` exits 0. The reviewer's evidence/mut.py run against it: 15 of 16 reviewer mutants killed at once, and the sixteenth (credit-lane, whose anchor my edit moved) is killed as the new stamp-credit-lane mutant in the table; new table mutants: stamp-credit-lane, stamp-credit-done, since-tag-merge-topic, since-tag-first-parent, evidence-design-uncredited (re-anchored). `python3 -I tools/audit/seat/gantt_drift.py --self-test` kills 16 mutants including word-boundary.

## Null control

Each new arm has a null: a plan without the exempt group frees the same slot; a group after nothing post-closure stays in the round; a non-production done group earns no credit; merges with comment-only diffs credit nothing; the unmutated copy of the self-test exits 0.

## Figures

none

## Red checks

At the previous head 09ec9a880383, by exact name over all 68 check runs (one page): gate failed (three runs: 128226496049, 128221323084, 128215588422); codeql / Analyze (python) was cancelled at its timeout (128209941747, 23:13 to 23:58Z), and the code run's gate failed on exactly that cancellation; the other two gate failures were edit-run deferrals to that code run. The cancellation is the CI runner's timeout, not a finding in this diff (no production or python-analysed code changed; Analyze (javascript-typescript) and (actions) passed). Cheaper detector: none exists for an analyser timeout; the standing answer is to re-run it. CI at the new head has not run when this body is written; every red it concludes will be answered by the next repair.

## Carry dispositions

Numbering follows the review packet (1-based); the brief's own index is one lower.

- Carry 1 (brief 0): built. --live-refs, --in-flight, inflow field; --measure-sizes already built at the base.
- Carry 2 (brief 1): moved to R10-BODY-CONTRACT.
- Carry 3 (brief 2): built. Absorbed counts as done; advisory.
- Carry 4 (brief 3): built. Liveness by evidence (design-only uncredited), binding chain, CP slack.
- Carry 5 (brief 4): dismissed, duplicate of carry 2.
- Carry 6 (brief 5): dismissed, duplicate of carry 2.
- Carry 7 (brief 6): dismissed, duplicate of carry 2.
- Carry 8 (brief 7): moved to R10-BODY-CONTRACT.
- Carry 9 (brief 8): built. Critical-path groups start past the slots cap.
- Carry 10 (brief 9): built. Stamp cadence by production group, matched by merge topic.
- Carry 11 (brief 10): built. Post-closure groups.
- Carry 12 (brief 11): built with carry 11 (same seam).
- Carry 13 (brief 12): built. tools/audit/seat/gantt_drift.py.

## Forward-carry

none

## Friction

none
