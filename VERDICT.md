Fix review: merge 8247d388352f415275395e2022b796e9f89a480d

bus-nonce: 81a150fce67bdb8ab667a47e8c47d916

## Findings

none

## Evidence
- Head reviewed: 8247d388352f415275395e2022b796e9f89a480d (detached worktree). Diff is the ruling file dev/programme/triage/s6-batch95.md plus dev/programme/delivery/3068.md (names #3068); no production code or policy file. Merge with origin/main (61b0076f4): git merge-tree --write-tree is clean.
- CI: merge_train.py classify at this head exits 0 (GREEN, pending none, red none). Packet gate digest green.
- (a) P345 citations opened at a7dd7f50d: budget_raise_gate.py 490-492 (no decisive review) and 503-505 (approval on another commit); gate.py 76 (pr event lists budget-raise-gate); merge_train.py gating_names 386-394, classify 434-445, raise_hold begins 1531 and its approval call ends near 1588, subcommand classify 6631; orchestrator_tick.py 876-882 (NOT REVIEWABLE line); bus.sh 462-473 (classify rc case) and self-test rows 1439-1453; ci.yml 261/309. All say what the ruling says.
- (b) ruling_verdict over the file: P345 ACCEPT, P346 unreadable (no verdict line; the text says an earlier REJECT draft does not stand), P347 REJECT, P348 ACCEPT, P349 REJECT. triage_refusal returns None for the P345 and P348 carries; P346, P347, P349 are refused (unreadable / REJECT / REJECT). Null control: flipping P345 to REJECT in a scratch copy gives "is not an ACCEPT ruling (REJECT)".
- (c) P347: prepr.sh selftest_owed at 1508, BASE merge-base at 3525, step 3h 3737-3746 confirmed. The five-and-five split of today's ten opens rests on the opener's driver4.log, which is out of tree; not re-derived.
- (d) P348: orchestrator.md line 172 region is the clause on --reviewed-head / review_carry CARRY; bus.sh refusal at 484-494 and blocked_rounds at 396-403 confirmed. The ruling proposes the edit in the carry text and makes none.
- (e) P349: git ls-remote origin refs/heads/fix/<topic> is empty for all four topics (r10-996-runner-claims, r10-orch-review-packet, r10-fly-relay-review-ff, r10-train-overlap-grade).
- Figures rest on out-of-tree logs and could not be re-derived: seat-ledger lines (3115, 3150, 3171), job 124647394312, the 13-PR budget-raise-gate list, the 1184/437/97/38 verdict counts (re-derivable from 493 verdict refs, not re-run), the 35/29/6 prepr log counts and slot minutes, opener timings. #3045 head 9ef51b82 confirmed by ls-remote.
- policy_lint.mjs: 0 errors across 50 policy files; --budgets reports no breach. tests/structure.py: STRUCTURE RATCHET PASSED. Claim files not in the diff (byte-identical). Delivery row present and in the three-dot diff. brief_lint over the roster not run: the carries are not on the roster yet by design.
