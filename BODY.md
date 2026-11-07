R10-FLOW-TOOLKIT-MODEL: plan-model correctness in tools/plan/replan.py, plus the tracked Gantt-drift instrument (carry 12). Measures the roster/plan semantics only; no production code. Merge-resolution on top of repair round 5 for the blocked fix review at 0ce1f09bd196: --since-tag now credits a multi-PR group's part-branch merges (on main's real history v7.1.0..v7.1.1 it credits 12 of 12 production groups that changed code, was 8; v7.1.2..v7.1.3 credits 9 of 9, was 8), and the squash fallback is pinned.

Merge resolution (PR was DIRTY; only the merge was done, no other edit): `git merge origin/main` conflicted in two files, each resolved by union.

- tools/plan/replan.py, `is_done` hunk. Main contributed: `is_done` delegates to `roster_lib.is_open` (the one owner of closed stages, absorbed included) and a selftest arm "an absorbed group is closed work, not scheduled". Branch contributed: the `DONE_STAGES`/`ABSORBED_RE` block, `absorbers()` (the absorbed advisory) and `post_closure_groups()`. Kept: main's `is_done` body, `ABSORBED_RE`, `absorbers`, `post_closure_groups`, main's selftest arm. The branch's local `DONE_STAGES` tuple duplicated `roster_lib.CLOSED_STAGES` and nothing else read it once `is_done` delegated, so only that constant went; its comment was kept as the doc of `is_done`, and its mutant `absorbed-done` was re-anchored from the tuple to main's `return not roster_lib.is_open(group)` (mutated to the old two-stage test) and is killed by main's absorbed arm.
- tools/audit/seat/plan_page.py, two selftest hunks (bar present for every open group; ETA reason for every open group). Main contributed the shared `scheduled(g)` helper (not plan-done). Branch contributed the `rows[g]["st"] != "done"` test. Kept both conditions in each: `rows[g]["st"] != "done" and scheduled(g)`.
- Auto-merged without conflict and read back: tests/closures.json (ledger merge driver), main's selftest additions in replan.py. Claim files byte-identical to origin/main.

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

0542969c33313f54db611ca0609fade7c1b14989 is the PR head: the merge of origin/main into the code head 28ec0da039a094fd5093adb34e6c6a328f982f86 (the earlier merge of ec3b2460156219519962589fdaed1d382e1e41ab and origin/main 630bf533d838). Measured at 0542969c3, in a worktree of it: `python3 tools/plan/replan.py --self-test` 0 failed; `python3 -I tools/audit/seat/gantt_drift.py --self-test` 45 checks, 0 failed; `python3 tools/audit/seat/plan_page.py --self-test` 67 checks, 0 failed; `python3 tests/structure.py` PASSED with no budget change; `python3 tools/audit/seat/selftest_wiring.py --check` 119 self-testing, 119 wired, 0 unwired. origin/main has moved since this head (now 4b5d771bdf8f); the PR head is deliberately not moved by this body re-take, so no second prepr code run applies.

## Mutation proof

`python3 tools/plan/replan.py --self-test` exits 0. The reviewer's evidence/mut.py run against it: 15 of 15 reviewer mutants killed, and the sixteenth (credit-lane, whose anchor my edit moved) is killed as the new stamp-credit-lane mutant in the table; new table mutants: stamp-credit-lane, stamp-credit-done, since-tag-merge-topic, since-tag-first-parent, evidence-design-uncredited (re-anchored). `python3 -I tools/audit/seat/gantt_drift.py --self-test` kills 16 mutants including word-boundary.

## Null control

Each new arm has a null: a plan without the exempt group frees the same slot; a group after nothing post-closure stays in the round; a non-production done group earns no credit; merges with comment-only diffs credit nothing; the unmutated copy of the self-test exits 0.

## Figures

none

## Red checks

Read with check-runs filter=all, all pages, at head 0542969c3 (code run 42382930071 attempt 2). Concluded red at this head:

- `pr-contract / pr-contract` (job 128456376784), step "Check the body against the contract": the body lacked an answer for `tests / nightly-status` (below). Class: body contract, not code. Cheaper detector: `tools/pr/prepr.sh --body-check`, which names the same line before the push; standing cost nil beyond the body-check already in the handoff. This re-taken body answers it.
- `gate` (job 128458213401): red only because `pr-contract / pr-contract` is red; no other context under it failed at the head. Class: derived. Clears with the contract.
- `tests / nightly-status` (job 128441348284): `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly, slow failed in the last verification dispatch.` The job grades `main`, not this branch: the last concluded nightly.yml dispatch is run 42369836867 (2026-11-07T11:50Z, head 08fd676, on main), and every one of the seven lanes it names shows conclusion `cancelled`, not failed; a later run, 42382408131, was still in flight. This diff reaches `.github/workflows/governance.yml` (one added step, "Show the gantt drift reader refusing its own fixtures", in the instrument-self-tests job) but none of those lanes: they are jobs of nightly.yml, the diff does not touch nightly.yml, and a cancellation of a run on main at 08fd676 cannot come from a commit on this branch. So this change did not cause the red. Class: main's own, an unfinished nightly dispatch cancelled (superseded or interrupted), outside this PR; owner: the nightly.yml workflow_dispatch run 42369836867, whose re-dispatch (`gh workflow run nightly.yml --ref main`) is the orchestrator's, not this fixer's (no dispatch is made here and none exists from this branch). Cheaper detector: none for a cancellation; `nightly-status` is itself that detector, kept unrequired on main-protect on purpose. Standing cost: nil here.

Reds a later push cleared (earlier head 0ce1f09bd196): `gate` concluded failure four times (128274341527, 128285252987: edit-run deferrals to code run 42329754862; 128289689105 and 128289692210: edit runs 42329758968 and 42333416528 deferring to each other), and code run 42329754862 attempt 1 was cancelled at 02:54Z while attempt 2 was green. Not this diff's code: the mutual deferral is the CI gate instrument owned by R10-PROCESS-SLIM (#3245). Cheaper detector: none for a cancellation.

Also at this head, edit-run `gate` 128436038602 (run 42382931229) concluded failure while `pr-contract` 128436039958 was skipped: the same deferral to the code run above, cleared by it. Class: gate instrument (#3245), not this diff.

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
