Fix review: merge 1788c2e540f65ace3b94e18a1f9fcadd718015e8

bus-nonce: 45122ed1cebad50afc2fc291bd6304d1

Round 1 at this head: a re-dispatch with a new nonce. A previous fire reviewed the same head 1788c2e540 under nonce eeac4c79 (probe/rev-3840-eeac4c79 at 4f361528c5). This fire re-took the named-line mutation, the merge check, the roles-drift check and the CI state itself. The finder's-harness, class-enumeration and survivor figures carry from that fire, because the PR's own diff has not changed, and they are copied into ev/ as prior_*.

## Evidence

- RESULT mutation, re-taken in this fire from a detached worktree at the head (ev/mutants_refire.txt). The unmutated head prints `TREEREV ok`, rc 0. Mutant 1 deletes `maxBuffer: GIT_MAX_BUFFER, ` from `gitRead` in `tools/policy/counts.mjs`. It is killed: `TREEREV VACUOUS`, `the rev listing over the default maxBuffer threw (ENOBUFS)`, the same for checkout, rc 1. Mutant 2 puts `treeListing` back on a raw `execFileSync` with no maxBuffer. It is also killed, with the same two lines and rc 1. The worktree was clean after both mutants were restored.
- RESULT finder's harness, both ends, carried from the prior fire (ev/prior_harness.txt). At the merge base, origin/main reads ok at 1033586 bytes, while #3822 head 89ec15b79b and #3824 head 4b0f3eb96a both throw `ENOBUFS`. At the head, all three read ok, at 1033586, 1074652 and 1069422 bytes, which match `wc -c`. The body's figure of 1033283 for origin/main 6fdc15354f re-derives.
- RESULT null control: a listing under the 1 MiB cap reads ok at both ends, so the cap is the defect. The probe asserts that its own listing is over 1048576 bytes, so a probe that shrank under the cap would refuse rather than pass.
- RESULT class enumeration, carried from the prior fire (ev/prior_class_grep.txt, ev/prior_git_sync_nomaxbuf.txt). The body's `git grep` rule returns 13 sites, and the body gives each one a disposition. Open-axis rule (addendum 9): the quantified set is the Node `*Sync` git reads under `tools/policy/`, and it is named by a rule, the grep, rather than by examples. No `class-open` block applies.
- Merge with main: `git merge-tree --write-tree origin/main 1788c2e540` exits 0 with one tree (ev/merge_tree.txt). The roles directory has not changed on main since merge base 4ebd430fbf (ev/roles_drift.txt).
- The three-dot diff touches 4 files: counts.mjs, brief_lint.mjs, agreement.mjs and delivery/3840.md. VERSION, the manifest, RELEASE_NOTES, both claim files, budgets, closures and golden fixtures are untouched.
- CI: I polled `merge_train.py classify 1788c2e540f65ace3b94e18a1f9fcadd718015e8 --pr 3840` from 01:45 to 02:19 UTC (ev/classify.log). Every run printed `WAIT ... pending: gate red: none` until the last, which exited 0 with `GREEN 1788c2e540f65ace3b94e18a1f9fcadd718015e8 pending: none red: none`. No red, so no owed red is answered.

## Findings

- Follow-up: two of the call sites the body lists as "closed in this diff" are unpinned. Putting `brief_lint.mjs`'s `git` helper, or `agreement.mjs`'s `git` helper, back on a raw `execFileSync` survives the full brief_lint run and the agreement lane with its self-test (ev/prior_mutant3*.txt, ev/prior_mutant4*.txt, from the prior fire at this head). Neither overflow can be reached at today's listing sizes, and the PR's own mutation target, `gitRead`, is killed. Carry: dismissed: owned by the orchestrator's parallel root-cause seat for this hotfix, whose proposed static refusal of a Node `*Sync` git read without maxBuffer outside `gitRead` kills both survivors; not this fix's seam.

## Friction

- The dispatch names `COMMS.md` at 6c17b87e62, but that commit holds `ADDENDUM.md` and `seat_comms.sh`. I followed `ADDENDUM.md`. Carry: dismissed: a dispatch-text path slip, already recorded by the prior fire at this head; nothing in the tree to change.
