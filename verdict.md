Fix review: merge 74a57885a3ef178f2556b4b105063a2b3a2edd9a

bus-nonce: 02524f809df915bd980605802a823223

## Scope

Round 1 (no prior reviewed head). Full review of the three-dot diff against merge base 5825e1346c, the PR's recorded base. Reviewed at head 74a57885a3ef178f2556b4b105063a2b3a2edd9a, from a detached worktree.

## Evidence

- RESULT head: `refs/pull/3640/head` still reads 74a57885a3ef178f2556b4b105063a2b3a2edd9a at verdict time (ev/head-recheck.txt). It matches the body's `## Head`.
- RESULT CI: `merge_train.py classify 74a57885a3 --pr 3640` printed `GREEN 74a57885a3ef178f2556b4b105063a2b3a2edd9a pending: none red: none` with rc 0, on two runs (ev/classify-1.txt, ev/classify-2.txt).
- RESULT merge: `git merge-tree --write-tree origin/main 74a57885a3` at origin/main 6aa7ddc712 exited rc 0. Its only driver line is `LEDGER-MERGE: resolved tests/closures.json` and there are no conflicts (ev/merge-tree.txt).
- RESULT block at head: the `# --- #3616: an implausible slab seed` block of tests/features.py, run through `features_block.py` up to `# --- R10-START-COUNTER-EDGES`, printed `ALL 9 FEATURES BLOCK PASSED` with rc 0 (ev/block-head.txt). This matches the body's unmutated figure.
- RESULT mutant m1 (bound removed: `above_room` returns False): `4 of 30 FEATURES BLOCK FAILED`. The four failures are the zero-plan, model-equivalence, repair and bound checks, which matches the body's "Bound removed" line (ev/mutant-m1.txt). This run continued to the script's end, so it counts 30 checks; every failure is in the #3616 block.
- RESULT mutant m2 (coordinator gating reverted to `not floor_return.ok` at both sites): `3 of 30 FAILED`, on the model-equivalence, hot-water and defrost checks (ev/mutant-m2.txt).
- RESULT mutant m3 (`seed` unconditional): `3 of 30 FAILED`, on the model-equivalence, hot-water and defrost checks. This matches the body's "Early gate removed" line (ev/mutant-m3.txt).
- RESULT mutation table: I did not re-run it, following the "cite CI" rule. CI's `tests / mutation` is green at the head. The 12 sites the mutation-autofix commit 74a57885a3 pinned are ledger files only. The one survivor, `refusal`'s trailing `return None`, is triaged as equivalent in `tests/mutation_ledger/survivor_triage/`. I checked that triage by reading the code: three returning `if` arms come first, so falling off the end returns the same None.
- RESULT class rule: I re-ran the body's `awk ... | grep -oE "reader\.read[a-z_]*\(CONF_[A-Z_]+" | sort | uniq -c` at the head. It prints 13 reads, matching the body (ev/class-rule.txt), and the body gives a disposition for every one of the 13. No seam is open.
- RESULT closures: `slab_seed.py` appears in 22 closures of `tests/closures.json` at the head, which matches the body (ev/closure-count.txt).
- RESULT version and claims: `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` have an empty three-dot diff.
- RESULT architecture: `coord_footprint` 2495 -> 2496 comes from the single `slab_seed.judge` call. The decision, the bound and the repair live in the pure module `slab_seed.py`, which has no Home Assistant import. The `arch-score` check is green. I found no payment the body missed: dropping the early `seed` call would change what learners see on plausible installs, which the body's timing note rules out.
- RESULT red history: the body answers `tests / mutation` (in the owed-reds set) and `pr-contract`. Both trigger answers are present.
- RESULT figures not re-derived by me: the 12.689 kWh head plan and the 11.22 kWh null-control plan. Instead, the block's checks pass at the head and fail under m1, so the zero-plan defect and its repair are pinned. I did not re-take the 714 s features run, the doc_claims count or the entities count; CI is green on them.
- RESULT carry audit: the review packet's `carry_audit` at the head reports 0 finding items in the PR body. `carry_audit.py check` over this verdict printed `2 routed, 0 unrouted, 0 bad destination(s)` with rc 0 (ev/carry-audit.txt).

## Findings

- Residual: the coordinator calls `slab_seed.seed` on the previous cycle's pump signals. On the first cycle after a switch from space heating to hot water alone (or into a defrost), it can therefore merge that cycle's return reading into the published slab. `judge` then refuses it, and the last-resort branch overwrites the slab with `_propagated_slab`, but only when that function returns a value. When it returns None (no replay and no plan trajectory) on an already-initialised install, the merged value stays for that cycle. The exposure is bounded: the reading is at most room + 12 K (anything higher is refused by both calls on its level), it lasts one cycle, and the next accepted reading re-merges. Mutant m3 shows that `judge`'s override covers the case whenever a propagated seed exists. Carry: dismissed: argued from code and not measured, so finding-propagation.md does not carry it; the exposure is one cycle within the plausible band, and only while no plan trajectory exists
- Out of scope: the bound is one-sided, so a floor-return reading below the room is not refused. The body states this. Carry: dismissed: that direction plans more heat rather than none, and no report shows it occurring
- Note: harness: no finder's harness exists, because #3616 is an outside report, not an audit finding. The harness is the fixer's own committed `#3616` block in tests/features.py, disclosed here as the fixer's, and the review drove it at the head and under three of my own mutants. Carry: dismissed: no finder instrument exists to run at both ends
