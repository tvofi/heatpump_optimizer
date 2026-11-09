Fix review: blocked f29c16fac7d846ac098fb30eb466c6961c7f9038 ci-red: classify exits 1 on GATE (an older check suite's edit-run gate, "still being judged", never re-run); the newest gate is success

bus-nonce: 8a1fa8c23d57ba81d9bcd3b62703ff98

Round 1 (first review of this head). Measured head: f29c16fac7d846ac098fb30eb466c6961c7f9038, still the PR head when written.

## Block

`python3 tools/audit/seat/merge_train.py classify f29c16fac7d846ac098fb30eb466c6961c7f9038 --pr 3364` exits 1: `RED ... pending: none red: gate`. `latest_runs` keeps the worst of the latest gate run of each check suite. Three gate runs exist at this head (ev/check-runs-gate.txt): 128932744205 (failure, 01:39:31Z) and 128932822087 (failure, 01:40:15Z, log: "FAIL run(s) [42544869339] at this head are still being judged; their gate decides", WORKSET arch-score budget-raise-gate), then 128938522291 (success, 02:00:37Z). Run 42544869339's checks have since concluded green, so this reads as a deferred gate that nothing re-ran, not a defect in the diff. The brief gives no exit-0/4 route for it, so I cannot judge the head GREEN. A re-run of the failed gate (or of the CI run that owns it), then `classify` to exit 0, clears this block; the code review below found nothing else. Carry: dismissed: this block is this verdict's own result, cleared by a gate re-run and a new review at the same head

## Findings

- Instrument observation: a deferred gate failure (the edit run's "still being judged; their gate decides") stays red in `classify` after the run it deferred to has finished green, until the gate is re-run; here it cost a block on a clean diff. Not this PR's change and not measured at other heads. Carry: dismissed: one instance, an orchestrator re-run of the gate clears it, no class measured

## Evidence

- Head ev/HEAD.txt. `git merge-tree --write-tree origin/main f29c16fac7d846ac098fb30eb466c6961c7f9038` rc 0 (ev/merge-tree.txt), no conflict, no MERGE-CLAIM line. Three-dot diff is 6 files (harness, delivery row, cloud_dispatch, instrument entry, merge_train, proof_watch); VERSION, RELEASE_NOTES, tests/golden and dev/governance/roles untouched. The head carries main merges beyond fb39908 (roster_edit.py, roster_sync.py), outside the PR's patch. Commit messages hold no Co-Authored-By or Claude trailer.
- Self-tests at head (ev/selftests.txt): merge_train 579 checks 0 failed; proof_watch 47 0; cloud_dispatch 131 0. Same as the body.
- Mutants, my own single-occurrence replacements, restored by git checkout (ev/mutants.txt, ev/mut-*.log): M1 `if mt < bt` -> `if False`: 3 failed (STALE, same-second tie, dispatch-time-decides), as the body. M2 same-nonce admission off: 1 failed (SAME null control). M3 NONCE_LINE unanchored: 5 failed. M5 the `stale_verdict` call removed from `posted_verdict`: 13 failed. M7 blocked-head filter widened (`or True`): 4 failed. M6 (fetch guard off): my replacement text did not apply, so not re-taken; the body's fetch-guard and early-exit kills are unverified by me.
- Null controls are in the self-test (LATER, SAME, other-head blocked with the history read asserted) and pass at head.
- Finder's harness, empty events log (ev/harness-base-stale.txt, ev/harness-head-stale.txt), at one fetch of 716 verdict refs: base harness `same=4 unknown=64`, head harness `same=3 unknown=65`, 68 instances each. This reproduces the body's one false SAME (PR 2465) at a newer bus snapshot; the 64-instance counts in the body are its snapshot's. I did not re-run the `guard` arm or PR 3232's registry: the registry is host-local and the body's 3232 figures are not re-derived.
- Class rule `git grep -n -E 'parse_verdict\(|posted_verdict\(|VERDICT_MERGE' -- tools` and its dispositions I read in the body against the diff; not re-run by me beyond reading the diff, which shows both admission paths share `posted_verdict`.
- Forward-carry: the body's two items each end in a `Carry: dismissed:` (carry_audit in the packet: 2 routed, 0 unrouted).
- Checks (ev/check-runs-gate.txt): every check green at this head except `governance / delivery-status` (failure). That grades main and the diff adds only its own row dev/programme/delivery/3364.md, so it owes no answer (defect-root-cause.md). The PR body's `## Red checks` says none; the gate reds above are an early deferral, not a check the diff turned red.
- Budgets: no *_budgets.json, closures.json or claim file in the diff; the packet's structure.py and archscore lines are ok; the body reports dS +0.0000 NULL, not re-run by me.
