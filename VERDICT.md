Fix review: merge 1788c2e540f65ace3b94e18a1f9fcadd718015e8

bus-nonce: eeac4c79776a28db4b44b36619eee969
pending-ci: gate

Round 1 (first round, full scope). Reviewed from detached worktrees at head 1788c2e540f65ace3b94e18a1f9fcadd718015e8 and at its merge base with origin/main.

## Evidence

- RESULT mutation (the named line): deleting `maxBuffer: GIT_MAX_BUFFER, ` from `gitRead` in `tools/policy/counts.mjs` turns `assertTreeRev` red, rc 1, with `the rev listing over the default maxBuffer threw (ENOBUFS)` and the same for checkout. The unmutated head prints `TREEREV ok`, rc 0. A second mutant that puts `treeListing` back on a raw `execFileSync` with no maxBuffer is also killed, with the same two lines.
- RESULT finder's harness, both ends (`treeListing(<rev>, <repo>)` loaded from each tree; ev/harness.txt). At the merge base: origin/main ok at 1033586 bytes; #3822 head 89ec15b79b and #3824 head 4b0f3eb96a both `ENOBUFS`. At the head: all three ok, at 1033586, 1074652 and 1069422 bytes, which match `git ls-tree -r --name-only <rev> | wc -c`. The body's 1033283 for origin/main 6fdc15354f re-derives exactly. Main has grown since that measurement, and still sits under the 1 MiB cap.
- RESULT null control: a listing under the cap works at both ends, so the defect is the cap. The probe's guard asserts its listing is over 1048576 bytes. I did not re-run the 512 KiB shrink, but the guard's code is in the diff.
- RESULT class enumeration: running the body's `git grep` rule at the head (ev/class_grep.txt) returns 13 lines. Every one maps to the body's disposition: brief_lint 115/147/1320 and agreement 343/600 now go through `gitRead`; counts 83/128/148/149 already did; policy_lint 188/216/1539 have a 64 MiB helper (policy_lint.mjs:100); card.mjs and card_rig.mjs are stubs or untracked-file reads. A wider scan for git `*Sync` calls without maxBuffer (ev/git_sync_nomaxbuf.txt) finds only single-object, fixture or probe reads. `card_drift.mjs`'s helper runs only rev-parse and merge-base.
- Full `node tools/policy/brief_lint.mjs` at the head: rc 0, TREEREV ok, 113 s wall on this host (ev/brief_lint_head.txt).
- The three-dot diff touches 4 files. VERSION, the manifest, RELEASE_NOTES and both claim files are untouched, and there is no golden drift to claim.
- `git merge-tree --write-tree origin/main 1788c2e540` gives rc 0, one tree. The roles directory has not changed on main since the merge base.
- The body names the head 1788c2e540 (a row-only commit over code head 54700c2fe4, plus the orchestrator's main merge 4b83f5c41e), and that matches the PR head.
- No metric is moved: no budget, closure, INERT, golden or ledger change.
- CI: I polled `merge_train.py classify 1788c2e540f65ace3b94e18a1f9fcadd718015e8 --pr 3840` from 23:46 to 00:17 UTC (ev/classify.txt holds the last run). Every run printed `WAIT 1788c2e540f65ace3b94e18a1f9fcadd718015e8 pending: gate red: none` (rc 3), so no red has concluded. When the packet was rendered, every required context except `gate` was green, skipped or in progress, and the last classify names no red. No owed red is drawn at this head.

## Findings

- Follow-up: two of the call sites the body lists as "closed in this diff" are unpinned. Putting `brief_lint.mjs`'s `git` helper (`refFiles`, `assertGrepExcludeBounded`, `symbolInTree`) back on a raw `execFileSync` survives the full `node tools/policy/brief_lint.mjs`, rc 0 (ev/mutant3.diff, ev/mutant3_brief_lint.txt). Doing the same to `agreement.mjs`'s `git` helper survives the agreement lane (`AGREEMENT ok`) and its self-test (233 of 233) (ev/mutant4.diff, ev/mutant4_agreement.txt, ev/mutant4_selftest.txt). Neither overflow can be reached at today's listing sizes, and the PR's own mutation target, `gitRead`, is killed, so this is not a vacuous proof. The static refusal the body hands to the root-cause seat (a Node `*Sync` git read without maxBuffer outside `gitRead`) would kill both survivors. Carry: dismissed: owned by the orchestrator's parallel root-cause seat for this hotfix, whose static-refusal question kills both survivors; not this fix's seam.

## Friction

- The comms addendum path in the dispatch (`COMMS.md`) does not exist at 6c17b87e62; that commit holds `ADDENDUM.md`, which I followed.
