Fix review: merge 2af71af0769d30c7a509c8c66196aec7af35775b

bus-nonce: be4a7f4cc24564aaffc3afebfccfa427

Round 1. RECORD PR: one ruling file (dev/programme/triage/s6-batch94.md) plus delivery row dev/programme/delivery/3067.md. No production code or policy file, so there is no mutation proof or finder's harness to run.

## Findings

- The P344 figure (12 of 305 dispatches since 10-24, across 11 PRs) cannot be re-derived: it rests on ~/.zcode/bus/dispatched, which is not reachable from this seat. The ruling itself discloses the source, and the ACCEPT holds on the instrument gap alone (bus.sh has no autofix-check refusal at origin/main). Carry: dismissed: the ruling states the out-of-tree source; the figure only prices the carry and does not decide it.
- The ruling's script-census counts (687 files, 60/67 hand copies, 17/24 rebuilt files, 27 payload scripts) and the driver4.py line counts (83/95/96/107) rest on out-of-tree scratch. The ruling says so. Carry: dismissed: cited as out-of-tree by the ruling; the in-tree facts beside each were checked.

## Evidence

- Head measured: 2af71af0769d30c7a509c8c66196aec7af35775b (ev/HEAD.txt). CI classify: GREEN, pending none, red none (ev/classify.txt). Gate digest in the rendered packet: green, no refusals, no advisories; carry_audit 0 findings.
- Merge: git merge-tree --write-tree origin/main head exits 0, so it merges clean. The diff touches no claim files, VERSION, golden, manifest or closures. tests/structure.py: STRUCTURE RATCHET PASSED. policy_lint.mjs --budgets and brief_lint.mjs CARRY fixtures: ok.
- Gate (ev/gate.txt): ruling_verdict reads P336-P339, P341, P342 and P344 as ACCEPT, and P340 and P343 as REJECT. triage_refusal returns None for each ACCEPT. Null: flipping P336 to REJECT in a scratch copy gives "P336 is not an ACCEPT ruling (REJECT)". P340 and P343 are refused the same way.
- (a) P336 citations at a7dd7f50d all match: budget_raise_gate.py MANDATE_ISSUE=201 at line 115, MANDATE_REVOKED at line 120, the inline test at lines 398-402 (owner + revok + whole-number cid); gh_comment.py line 424 has choices post, patch, verify, self-test, and line 442 handles post and patch together. Neither the ruling nor the carry writes the mandate id beside the revocation word. The only long numbers in the diff are comment ids 6322712314 and 6546832523, and the gate message withholds the id as "<id>". The session mandate id (the one seen in the roster is 6175172275) does not occur in the diff. The ruling leaves the live state of the mandate to the orchestrator and owner.
- (b) P340: cloud_dispatch.py has --group, --roster-ref and --publish at lines 1121-1138 and group_brief at line 409; HOME_DIR refusal at lines 54-61 and 89; aabbdff17 and fc6a810eb exist with the cited dates and content (fc6a810eb adds --publish). cloud_relay.sh lines 86-92 describe the handoff arm that runs update_pr.sh, as the ruling says. git grep -l POOL.txt origin/main -- tools returns nothing (rc 1). The REJECT is sound.
- (c) Re-derivation of the P344 figure: see the first finding.
- (d) No ruling silently decides the live mandate state; P336 expressly leaves it out. ledger.py exists on main; open_driver.py, seat_watch.sh, roster_show.py and whatif.py are absent from main, so P337, P338, P341 and P342 are new work, not redundant. proof_watch.py has the pinned-head and --budget logic the P339 ruling cites, and no --wait-only.
- Carries are not on the roster by design, and none was checked there. The "The carry:" text of each ACCEPT is consistent with its ruling.
