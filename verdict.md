Fix review: merge 4379fac37a259d1d4ac74c124c12cd1e934379bd

bus-nonce: 686b057146b5506d4368bec0285d6f7d

Round 1. Docs-only triage record: one file under dev/programme/triage/ plus this PR's own delivery row. No production code, so there is no mutation target; the body's mutation proof is the triage gate itself, which I re-ran.

## Evidence
- RESULT classify: GREEN 4379fac37a259d1d4ac74c124c12cd1e934379bd pending: none red: none (rc 0).
- RESULT merge-tree origin/main 4379fac37a259d1d4ac74c124c12cd1e934379bd: rc 0, no conflict (head is behind main but merges cleanly).
- RESULT three-dot diff: 2 files, dev/programme/delivery/3390.md and dev/programme/triage/s6-batch136.md; VERSION, manifest, RELEASE_NOTES and golden/claim files untouched.
- RESULT gate re-run (roster_edit.ruling_verdict / triage_refusal at head): P434, P435, P436 read ACCEPT; P425-P433 read unreadable; P437 reads None. With P435 flipped to REJECT its citing carry is refused ("is not an ACCEPT ruling (REJECT)"). Carry texts citing P435 and P436 return refusal None. With the file absent a citation is refused ("not on the roster branch or origin/main"). All match the body.
- Red checks: none required red in the digest; the body says none.
- The body's claim of a brief_lint pass on a simulated roster at 439aebb50 I did not re-run (roster branch simulation).
- The ruling figures (47.9 h CI study, 170.42 h replan base, 55 PRs, etc.) come from the author seat's local logs (s12/, s13/) that are not in the tree, so I could not re-derive them; I checked only internal consistency (e.g. 1338/70400 = 1.9 %, 1963/70400 = 2.8 %). Not verified against source.
- Forward-carry: the body states none. The carries to R10-ROSTER-WRITE-SWEEP, R10-HOTFIX-TRAIN-DEFER-WAIT and R10-RCA-GATE-BUSY-DEFER-2 are described as ops the orchestrator applies after the merge; they are not in this diff, so I could not open them at a roster SHA.
- carry_audit at head: 0 finding items.
