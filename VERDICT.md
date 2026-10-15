Fix review: blocked 6285ed67cee097c853f18112420db23440076f54 mutation-vacuous: the reviewer-prompt sentence that defines root-cause-detectable against root-cause-unrecorded is pinned by no check; deleting it or swapping the two definitions leaves check-wave-script 184 passed, 0 failed
bus-nonce: 3d2ad5c9791bab16d485b40409799443

Round 1. Measured at head `6285ed67cee097c853f18112420db23440076f54` from a detached worktree; merge base `cfe24f8ef`. `dev/governance/roles/` diff merge-base...origin/main: empty.

RESULT mutation_named_M1_delete_vocabulary_line failed=4 (180 passed) -- matches the body
RESULT mutation_named_M2_revert_ROOT_CAUSE_CLASSES failed=2 (182 passed) -- matches the body
RESULT mutation_reviewer_M3_drop_only_root-cause-unrecorded_from_ROOT_CAUSE_CLASSES failed=1 (183 passed)
RESULT mutation_reviewer_M4_reviewer_prompt_reverted_to_base_wording failed=0 (184 passed) -- SURVIVES
RESULT mutation_reviewer_M5_swap_detectable_and_unrecorded_definitions_in_prompt failed=0 (184 passed) -- SURVIVES
RESULT head_unmutated passed=184 failed=0

Why this blocks. The routing is pinned (M1-M3), but the split's only purpose is the measurement, and the measurement is made by a reviewer choosing a word. The one place that tells the reviewer which word means what is the prompt sentence in `reviewerPrompt` ("use root-cause-detectable if a detector cheaper than that check ... root-cause-unrecorded if the cheapest detector is the check that went red"). M5 swaps the two definitions: every verdict written afterwards would file process yields as unrecorded and vice versa, a D13 round would price the inverse, and the suite stays green. `fix-review.md` step 11 does not yet teach the words (carried, below), so for web waves this sentence is the whole definition. The same script already pins prompt text by regex (the judge, sweep, writer and verifier prompts), so the fix is one assertion in group 11b that the reviewer prompt pairs each word with its definition, killing M4 and M5.

Finder's harnesses, window.json sha1 8c4de8e205f9 (185 PRs, api_failures 0), at both ends:
RESULT enumerate.mjs base: seams=13 instances=1 engineering_max=23; root-cause-unanswered count=37
RESULT enumerate.mjs head: seams=13 instances=1 engineering_max=23; root-cause-unanswered count=37 -- flat, as designed
RESULT blocks_friction.mjs base/head: blocked_verdicts=124, block_class[root-cause-unanswered]=37, blocked_outside_grammar=0 -- flat
Companion, my own planted window (window.json plus three blocked verdicts: root-cause-detectable, root-cause-unrecorded, and a control word root-cause-invented; sha1 907f6b3b0638), built by me, not the fixer's window_planted.json:
RESULT enumerate.mjs base: untaught:root-cause-detectable=1, untaught:root-cause-unrecorded=1, untaught:root-cause-invented=1, seams=16
RESULT enumerate.mjs head: root-cause-detectable=1, root-cause-unrecorded=1, untaught:root-cause-invented=1, seams=16
RESULT blocks_friction.mjs head: block_class[root-cause-detectable]=1, block_class[root-cause-unrecorded]=1, block_class[untaught:root-cause-invented]=1, block_bucket[orchestration] 49->52 at both ends (the new words land in orchestration until placed, as the body says)
Null control: the invented word stays untaught at the head, so the vocabulary opened by exactly two words.

Gate not loosened: both new words are in ROOT_CAUSE_CLASSES; group 11b and my M3 show each arm blocks (merged=false) and dispatches the root-cause seat, never a repair.

Class rule (step 6): `git grep -n root-cause-unanswered -- .claude tools tests dev/governance` at the head returns 7 files; all 7 are dispositioned in the body.

Forward-carry (step 10): the body sends fix-review.md step 11 and the D13 M3 / D14 ENG placement to R10-BRIEFS-FOLD. That carry is written only at 239bef9c9 / 318a034e4 (the orchestrator's roster-land clone, visible as a wip-sync ref). It is not on origin/main, not on origin/handoff/audit-r10-roster (db71fe47a, whose BRIEFS-FOLD carry has no GATE-YIELD item), and no roster pull request is open. Not yet in the tree; this alone would hold a merge verdict until the roster lands. Also: BRIEFS-FOLD's files list names neither fix-review.md nor the D13/D14 harness files the carry asks it to change; the body's orchestrator.md disposition says "Carried below" but the carry names only fix-review.md.

Red checks (step 11): head's runs all concluded, none red; the previous head 78a29367f has cancelled (superseded) runs only. VERSION, manifest, notes heading untouched. merge-tree against origin/main b22db919d: clean. Code-owned .claude/workflows/web-fix-wave.js: approval goes through the train under mandate 6175172275.
