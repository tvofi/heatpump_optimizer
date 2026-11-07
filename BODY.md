R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code. Repair round 5 for the blocked fix review at 0ce1f09bd196: --since-tag now credits a multi-PR group's part-branch merges (on main's real history v7.1.0..v7.1.1 it credits 12 of 12 production groups that changed code, was 8; v7.1.2..v7.1.3 credits 9 of 9, was 8), and the squash fallback is pinned.

Carries built: 0 (live-refs, in-flight, inflow; the size measure was already built at the base), 2 (absorbed is done, advisory), 3 (liveness by evidence incl. design-only without credit, binding chain and CP slack, uncalibrated-sensitivity note), 8 (critical-path groups start past the slots cap, exempt), 9 (stamp cadence 3 by group, comment-only diffs ignored, matched by merge topic branch, credit only for done groups), 10 and 11 (post-closure groups), 12 (tools/audit/seat/gantt_drift.py).
Carries 1 and 7 were moved to R10-BODY-CONTRACT; 4, 5 and 6 are dismissed as duplicates.

Repair of the review's items:

- Item 1, mutation-vacuous: one pin per surviving mutant in replan.py --self-test (overflow slot filter, post-closure propagation and STAMP-ROUND-MAJOR mark, credit lane, check refusals, produced credit, carries, binding-chain walk, arrivals median, parse_live_refs, post-closure in the peak sweep, stamp cut). gantt_drift.py is_named now has a direct word-boundary pin and a word-boundary mutant in its table.
- Item 2, --since-tag: production_groups_since names a group by a merge's topic branch (as topic_evidence does) and git_commits_since_tag diffs against the first parent; pinned with a real-shaped "Merge pull request #N from tvofi/fix/<topic>" subject and with a real throwaway merge repository.
- Item 3: a stage-live group whose only evidence is a design ref is design_only, no live credit.
- Item 4: stamp credit is filtered to done groups; a credited group still open is counted once.
- Item 5: measure_sizes_hours, --sizes-input, --sizes-since and --sizes-until are removed with their fixture null and two mutants. Carry 0 (2) was already built at the base: --measure-sizes runs size_durations.run (p75, earliest of first commit or PR creation). I did not re-run that measurement here (it needs the network edge); durations.json sizes are unchanged.
- Round 5, item 1: production_groups_since matches a merge topic to the longest roster topic it equals or extends by `-<suffix>` (word boundary as in gantt_drift.py: `r10-storey` credits nothing, `r10-store-p2` credits R10-STORE, `r10-store-races-p2` credits R10-STORE-RACES), once per group. Pinned with `-p2`/`-p3` merge subjects and a null (an unrelated topic and a non-boundary prefix credit nothing); mutants since-tag-part-branch, -part-boundary and -part-longest are killed.
- Round 5, item 2: the squash fallback is pinned (a subject naming R10-STORE-RACES credits it, not R10-STORE); mutant since-tag-squash-longest (`max` -> `min`) is killed.
- Item 7 (dismissed with a reason): inflow_groups_per_hour 0.4 stays reported-only, never scheduled, and the hard-coded slot_sensitivity string (27 snapshots, r=0.045) stays a labelled "uncalibrated" note; neither is a figure this PR claims. No later open group owns measuring them (R10-PLAN-REAL-DURATIONS and R10-PLAN-ARTIFACT are both done and their briefs mention neither), so they are dismissed, not carried: a measurement would be a new group if an owner asks for one.

## Head

77265a28ebc76b64c512779febb0e6a14c2c0d70 is the code head of this repair. It merges the PR head 0ce1f09bd196 and origin/main at be813ecd4924; prepr.sh was run at this head (rc=0).

## Mutation proof

`python3 tools/plan/replan.py --self-test` exits 0. The reviewer's evidence/mut.py run against it: 15 of 15 reviewer mutants killed, and the sixteenth (credit-lane, whose anchor my edit moved) is killed as the new stamp-credit-lane mutant in the table; new table mutants: stamp-credit-lane, stamp-credit-done, since-tag-merge-topic, since-tag-first-parent, evidence-design-uncredited (re-anchored). `python3 -I tools/audit/seat/gantt_drift.py --self-test` kills 16 mutants including word-boundary.

## Null control

Each new arm has a null: a plan without the exempt group frees the same slot; a group after nothing post-closure stays in the round; a non-production done group earns no credit; merges with comment-only diffs credit nothing; the unmutated copy of the self-test exits 0.

## Figures

none

## Red checks

At the PR head 0ce1f09bd196, by exact name over all check-run pages: `gate` concluded failure four times (128274341527, 128285252987: edit-run deferrals to code run 42329754862; 128289689105 and 128289692210: edit runs 42329758968 and 42333416528, each deferring to the other). `gate` 128278851908 and 10 jobs of code run 42329754862 attempt 1 (including `codeql / Analyze (python)`, `instrument-self-tests`, `closures`, `coverage`) were cancelled at 02:54Z; attempt 2 succeeded, with `gate` 128288954024 passing. None is this diff's code: the cancellations were a runner cancellation re-run to green, and the mutual edit-run deferral (runs 42329758968 and 42333416528 each waiting on the other) is the CI gate instrument tools/ci/gate.py, owned by R10-PROCESS-SLIM (#3245), not this diff. Cheaper detector: none for a cancellation; the deadlock is R10-PROCESS-SLIM's. CI at the new head has not run when this body is written; every red it concludes will be answered by the next repair.

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
