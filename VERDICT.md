Fix review: merge 2d9aa137c09236f8bf08a90ab9038c438fff23ff

bus-nonce: 54e15a4cdbb93dcdc7b4fb1821316a2d

## Evidence

- Round 1 (first review, no reviewed head). Head re-read before the verdict: origin's PR branch still at 2d9aa137c09236f8bf08a90ab9038c438fff23ff. Role contract unchanged between merge base and origin/main.
- Merge: `git merge-tree --write-tree origin/main 2d9aa137c09236f8bf08a90ab9038c438fff23ff` exit 0, no conflict (ev/merge_tree.txt).
- CI: `merge_train.py classify 2d9aa137c09236f8bf08a90ab9038c438fff23ff --pr 3697` prints `GREEN 2d9aa137c09236f8bf08a90ab9038c438fff23ff pending: none red: none` (ev/classify.log, re-run at verdict time). The head's reds `tests / replay` and `tests / nightly-status` are outside the `owed-reds` set, so they owe no answer. The owed reds at aedd62fd38 (`tests / fast (3.14)`, `tests / mutation`, `tests / briefs`, `pr-contract / pr-contract`, `gate`) are each named and answered in the body's `## Red checks`.
- Mutation proof (step 1): deleting the two lines of `OptimizationConfig.start_price` (ev/mutant.diff) makes the honest-starts block fail 2 of 60 checks: the start_price table and the failing case, with `[edges 5, at the default 2, default patched to zero 5]` (ev/mutant_start_price_block.txt). The head passes all 60 (ev/head_block.txt).
- Harness at both ends (step 2): `r11_honest_starts_runs.py grid` at the merge base 8e76c192 gives the clamped unpriced row edges 5 / energy_kwh 2.93; at the head, edges 2 / 2.75. The priced clamped null row reads edges 2, objective 8.1664 at both ends. Unpriced duty-cycle cells entering the stage: 0 at both ends.
- `defaults` at both ends: both ends print the same ladder. At 0.1: grid 5->2 starts, everything_on 5->4, and the lowest room is not lower (20.19->20.22, 17.91->17.97). The cycling_cost fixture stays at 7 starts, as the body's table says. `null pairs that differ 0`, rc 0 at both ends. The harness is the group's own instrument (no finder harness exists for outside PR 3529), committed in the tree and disclosed as such in the body.
- Class (step 6): `git grep -n "\.cycling_cost\b\|cycling_cost=" -- custom_components/` returns 3 sites at the head, as the body says. Raw `.config.cycling_cost` readers in optimizer.py: 7 at the base, 0 at the head. The fixture rule `clamp=True.*cyc=0.0` returns 3, all patched. The rule misses three implicitly-zero clamped fixtures: tests/features.py:71210 (`_r10s_solve`), tests/features.py:74732 (`_sp_solve`) and dev/audit/harnesses/r10_setpoint_power.py:48. A reader checked each one: none of their checks or comments depends on an unpriced start, and CI's `tests / fast (3.14)` is green on them. So the class is not open.
- Steps 4 and 5: the three-dot diff leaves VERSION, the manifest, RELEASE_NOTES.md and both claim files untouched.
- Mutation ledger (step 14): every added or renamed row's `old` line is a line this diff writes, and the deleted rows anchor the removed `_commit_runs` early return and the renamed reads. The movement comes from the change. I did not plant a no-improvement move.
- Step 16: the change adds no actuator-write refusal.
- Not re-run (heavy, CI cited): the SkylakeX kernel sweep, the full gate and `--pin-killed`.

## Findings

- Note: stale-figure: the body's mutation proof says the honest-starts block has 54 checks ("2 of 54", "ALL 54"). At this head it has 60 (the merged main added checks). The two failing checks are the ones the body names. Carry: dismissed: paperwork figure, the result reproduces at the head
- Note: ui-copy: the `compressor_cycling_cost` field description in custom_components/heatpump_optimizer/strings.json still says "Leave at 0 ...". It does not say that on an install that cannot duty-cycle, 0 now plans at 0.1. The text states nothing this change contradicts, and docs/configuration.md states the rule. Carry: dismissed: no false statement in the field text; the user-facing rule is documented in docs/configuration.md
