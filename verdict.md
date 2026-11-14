Fix review: merge 2486dc6da9cd53e8cfdf0aa12220698600d6a419

bus-nonce: b0389313dee1d16f8f1aaf02b1f4d10d

## Scope

Delta round over the merge verdict at ece8328001608ff93f5138392f6e6c15420c8929 (third review of this branch by the body's record: 7db7de155f held, ece83280 merge, this head). `tools/audit/seat/review_carry.py ece83280 2486dc6d` prints `FRESH-REVIEW` (the head is not the automatic merge of its parents), so this review is the delta `git diff ece83280 2486dc6d`: one merge of origin/main cc0fb2548a. No pull request exists yet: no review packet, no check runs and no CI to read; nothing here is a red-check answer.

## Evidence

- `git show --remerge-diff 2486dc6d` (ev/remerge-diff.txt): the only hand resolution is one conflict hunk in each of strings.json and translations/de.json, en.json, sv.json, all on `options.step.entities.sections.indoor.data_description.space_setpoint_unit`; each resolution drops the branch side and keeps main's line verbatim (no `+` line in the remerge diff). `tests/closures.json` merged through its ledger driver (`LEDGER-MERGE: resolved`).
- Key union (ev/key-union.txt, own script flattening base ec964501, branch ece83280, main cc0fb254 and head to leaf keys): in all four files the head's key set equals both sides' union less keys either side deleted (1507 keys each), and every head value equals the clean three-way choice (a key one side changed keeps that side, both equal keeps it). The only key both sides changed is sv's `space_setpoint_unit`; head == main there, and main's value starts with the branch's value verbatim, so the branch's "entitet" wording is kept. de, en and sv key sets equal strings.json's. In strings.json the branch never changed `space_setpoint_unit`; the textual conflict came from the adjacent `flow_heat_c` line, whose branch text (and `space_setpoint_entity`'s) is byte-identical at ece83280 and the head.
- Reviewed lines unchanged: pump_arbiter.py, const.py and config_flow.py are byte-identical between ece83280 and the head (ev/reviewed-paths-delta.txt). Every other production path the delta moves (optimizer.py, duty_switch.py, ledger.py, the card JS) is main's own content: on the delta paths only the four string files, tests/features.py and seven mutation-ledger entries main deleted differ from cc0fb254 (ev/head-vs-main-on-delta-paths.txt), and the ledger entries are absent at both. The delta touches no reviewed production code, so per fix-review.md step 12 nothing widens.
- Patch comparison (ev/per-file-patch-compare.txt, ev/patch-lines-delta.txt): the PR's patch against main differs from the reviewed patch only where the stacked #3561/#3576 content has since landed on main; the one main-side line the PR now replaces is `_arm_space`'s `_space_target(inp, inp.plan, now, None)`, rewritten to `boosted=False` exactly as reviewed, with harness M03 re-anchored to it.
- tests/features.py auto-merged (both sides edited it). At the head, `features_block.py` over the pump-duty arbiter block prints `ALL 61 FEATURES BLOCK PASSED` (ev/arbiter-block.txt), matching the body. `tests/config_flow_steps.py` prints `ALL 586 checks PASSED` (ev/config_flow_steps.txt); the body's 580 was measured before main's #3564 added checks, and the 6-check difference is main's, not this PR's.
- Targeted mutant at the head: `_boost_ceiling_c`'s `return min(caps)` -> `return None` turns the arbiter block to `5 of 61 FEATURES BLOCK FAILED`, including the auto-merged R10-HOTFIX-FLOW-SETPOINT-STUCK check that now expects the entity's 63 maximum, which shows the merged features.py carries this branch's reconciliation of #3561's check (ev/mutant-boost-ceiling-return-none.txt); source restored, worktree clean.
- `git merge-tree --write-tree origin/main 2486dc6d` at origin/main fafd6a9ff5 exits 0 (ev/merge-tree.txt): no conflict.
- `merge_train.py owed-reds` read (ev/owed-reds.txt); no check runs exist for this head, so no red is owed an answer.
- Body: its `## Head` names 2486dc6da9cd53e8cfdf0aa12220698600d6a419, the head measured here, and its conflict-round paragraph matches the remerge diff and the key enumeration above. VERSION, the manifest version and the RELEASE_NOTES heading are not in the delta.
- Not re-derived this round: the body's mutation-run counts (36 generated, 34 killed, 2 equivalent) and the `coord_footprint` 2505 -> 2506 figure, both verified in the ece83280 round on production code that is byte-identical here.

## Findings

None.
