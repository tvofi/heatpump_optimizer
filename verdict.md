Fix review: merge 3134798017b1d26994c410206349b06d187559a0

bus-nonce: b2105ebb24c3ec63b0c50e076bdb16a7

Round 4 (body re-take for round 3's red-checks block; no code change since 31347980). Measured head 3134798017b1d26994c410206349b06d187559a0, detached worktree; merge base 28d46c4918285d36c409c1fb2f72eb77e04e569e.

## Evidence

- Self-tests at the head (bash 5.2.21, Linux): cloud_relay 372 checks 0 failed; bus 159/0; orchestrator_tick 283/0; ledger 101/0; tick_loop 27/0; policy_lint rc 0; structure.py STRUCTURE RATCHET PASSED. At the base (null control): cloud_relay 332/0, bus 152/0, orchestrator_tick 280/0. Every figure in the body's Figures section that I re-ran matches. ev/RESULTS.txt.
- Mutant M1 (cloud_relay.sh relay(): the line `[ -z "$dup" ] || die ...` replaced by `:`): 372 checks, 4 failed. Killed.
- Mutant M2 (the round-4 repair reverted in order: the ev_case_collision check moved back after the extract, after the `no ev/ directory` check): 372 checks, 2 failed, so the "refused before any write" rows (tar never ran, TMPDIR empty) pin the orchestrator's APFS finding that the check ran after the write. Killed. ev/mutM2.diff.
- Mutant X2 (bus.sh unpack: `if cc=$(git ls-tree ...)` to `if false; then`): 159 checks, 2 failed. Still killed.
- Mutant Y1 (orchestrator_tick.py relay_owed `if n > 0:` to `if False:`): 283 checks, 1 failed. Still killed.
- Merge with origin/main 53273de4d: `git merge-tree --write-tree` rc 0, tree f915c5a2, no conflict. ev/merge-tree.txt.
- custom_components/, VERSION, the manifest, RELEASE_NOTES.md and every *budgets.json are untouched in the three-dot diff. The delivery row dev/programme/delivery/3252.md is in it.
- CI: `merge_train.py classify 3134798017b1d26994c410206349b06d187559a0 --pr 3252` printed `GREEN 3134798017b1d26994c410206349b06d187559a0 pending: none red: none`, rc 0. The latest gate runs (128496140338, 128496134349, 128496131112, 128495898003) are success. The latest pr-contract 128495675518 (18:51:27-18:52:19Z) started after the last red concluded (gate 128471344242, 17:15:10Z) and concluded success, so the body check passed at this body.
- Red checks, checked against the commit's check-runs with filter=all across both pages (total_count 160; ev/check-runs-filter-all.tsv). The body names all six failures by their first-attempt ids (gate 128448828285, 128452383371, 128471344242; pr-contract 128446411039, 128449815767; nightly-status 128455324026) and answers each one. The remaining failure ids, 128496135074, 128496141046 (pr-contract) and 128496129422 (nightly-status), are re-run-attempt copies of those same jobs: same run, same check suite, identical start and end timestamps. They are not new reds. The two unnamed cancels are gate 128444855841 (0 s at 15:27:40Z, cancelled when superseded; later gates in that run are success) and prelude 128441647474. prelude is outside the required set, so under the 2026-11-07 owner ruling neither blocks.
- The nightly-status red is not this PR's: its diff reaches no nightly lane (fix-review.md step 11).
- The finder's harness is not named in the packet. I used the carries' own self-test rows plus my own targeted mutants M1/M2 (disclosed as mine, step 9).

## Findings

- Finding (a), carried: bash 3.2 / APFS is still not demonstrated. This container has only bash 5.2. Claim: `cloud_relay.sh --self-test` passes under macOS bash 3.2 on APFS. Evidence: none at this head. Mutant M2 shows the after-write ordering the orchestrator saw is now pinned, but the fixture never materialises names only by reasoning on ext4. Harness: `/bin/bash tools/audit/seat/cloud_relay.sh --self-test` on the orchestrator's macOS. Metric: failed-check count, expected 0. Perturbation: M2. Carry: R10-RELAY-SWEEP

## Friction

- The frugal inline-op guard counted a test-run Bash call as a search op, so the run went through a mechanic subagent. Carry: dismissed: tooling friction, not a finding of this PR
