Fix review: merge 662491b2df8383ca4ff97011807a58f50ed56be0

bus-nonce: b66876453ebe98d6ac476cdbb1522125

## Findings

- P274 quotes 424 commits on main authored `noreply@anthropic.com` (`git log --since=2026-10-21 --format=%ae origin/main`). Re-run at the record's own base b0b2d7697f8c, that command gives 571 (408 with `--no-merges`, 0 with `--first-parent`); no variant gives 424. The ruling does not depend on it: the counted class is the handoff refs, and the 424 is context. Carry: dismissed: context figure only, ACCEPT rests on the handoff-ref count and the P253 hole, both re-derived below
- P274's "28 commits on 8 refs" re-derives only partly at today's refs: 20 on 4 refs (r10-cop-gate 3, r10-rca-friction-residue 4, r10-review-carry 6, r10-review-carry-pr 7); the other four refs show 0 now, having moved or merged since the record's reading. The sequencing note ("refused unless re-authored first") stays correct for the 4. Carry: dismissed: refs are live and moved after the record; direction of the ruling unchanged
- P276 and P277 accept into new groups R10-FLY-ABORT-OWN-MERGE and R10-FLY-OWED-LEVELS, which are in no roster yet. proposal-triage.md line 20 allows "a new group and its brief", and the record carries each brief (scope, files, self-test arms, mutants, null control), so the destination exists as the record itself; the orchestrator owes the roster entries. Carry: dismissed: contract permits a new group named with its brief; roster entry is the orchestrator's step after merge
- P273 leaves a residual (docs/ is INERT, so a drawing change re-renders no figure) and takes no position. It names the existing owners of the gap (tests/card_drift.mjs header, #558 C2/C3, which I read at line 24). Carry: dismissed: the gap is already recorded in-tree at tests/card_drift.mjs, no new work is proposed
- P273's byte-identity (`cmp` of the three rendered hydronic figures against the committed SVGs) and its coil-arc control were not re-run by me; I checked the cited code lines (card.js 4002-4008, 4719) and the 4 `spring` hits in docs/dashboard-card.md, and that 75ac45353 is not an ancestor of 2cc4d5ebc (rc 1). Carry: dismissed: the render comparison is the record's own enumerator; the cited premises it rests on were checked and hold

## Evidence

- Diff (three-dot against origin/main) writes only dev/programme/triage/s6-batch59.md and dev/programme/delivery/2945.md. No role, VERSION, manifest, notes, claim, golden or budget file is touched; dev/governance/roles/ has no diff against main.
- `git merge-tree --write-tree origin/main 662491b2df8383ca4ff97011807a58f50ed56be0` exits 0, no conflict.
- Cited code lines at origin/main match: ref_privacy.py:244 (localhost), remerge_main.sh:21 (no `merge --abort`; none anywhere in the file), pr_args.sh:105 (mut:detach), owed_unactioned.py:50 (FAMILY lacks MERGE-READY and BLOCKED-UNFIXED), orchestrator_tick.py:690 and :696, queue_pre_flight.py:178, body_push.sh:77.
- Existing destinations resolve in dev/programme/rosters/wave-r10-groups.json: R10-FLY-NO-FOOTERS, R10-ORCH-REVIEW-PACKET, R10-FLY-CARRY-DISPOSITION, R10-FLOW-BODY-ONLY. s6-batch51.md holds P253; R10-FLY-SWEEP-DEFAULTS is cited from s6-batch58.md.
- Live counts: 154 handoff refs (record 153) and 397 verdict refs (record 396), one more of each since the record; consistent with drift.
- Checks at this head (check-runs API): the only conclusion=failure is tests / nightly-status. It grades main, and this diff touches none of what it reads, so it is not this PR's (defect-root-cause.md). The review packet's red-unanswered refusal names only that check. browser, closures, fast (3.14) and env-matrix were still in_progress when read; every other check was success or skipped. Mutation is success with no production line in the diff, so no mutant was drawn.
- carry_audit at the head reports 0 findings; the packet's figure_lint resolves 2 and leaves 4 flag-only git commands unverified.
- Mutation proof, null control and finder's harness do not apply: the PR writes no production code and no test.
- Round: first review of this head.
