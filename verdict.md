Fix review: blocked 103b2097a38f972d1cb048c9ffbedcf6b1ba6d61 figure-wrong: body quotes orchestrator.md at 4507 tokens (Mutation proof, Figures); this head measures 4512 against cap 4513 -- 4507 is round-1 head 774e53f7's figure

bus-nonce: 038428ed586b586b1d21b557644de260

Round 2 of PR #2462 (round 3 is still a repair, not a re-cut). Measured head 103b2097a38f972d1cb048c9ffbedcf6b1ba6d61, still the branch head at verdict time. Merge base 4a3cbcf62e6f5e7b6594d376d714388caf2915cf = origin/main.

## RESULT lines
- RESULT lint: `node tools/policy/policy_lint.mjs` at head -> `TOTAL: 0 error(s) across 41 policy file(s)`, exit 0 (ev/lint_head.txt). Matches body.
- RESULT budgets orchestrator.md: `319 319 4512 4513` (ev/budgets_head.txt). Body says `319 319 4507 4513` -> WRONG. Re-measured with only orchestrator.md checked out from each commit: 774e53f75 -> 4507, 26189a1fd -> 4512. The round-2 restorations cost 5 tokens and the body was not updated. The brief's 4512/4513 is correct; the body's is stale.
- RESULT budgets nudge.md: `115 115 3812 3814`. Matches body.
- RESULT caps: `policy_budgets.json` is unchanged by the diff (orchestrator 319 lines and 4513 tokens, nudge 115 and 3814). No raise. Both files are at or under cap.
- RESULT rules_sync --check: `RULES-SYNC ok`. Matches "no .cursor rule changed".
- RESULT known-bad 6->1 (step 14): the move is earned. Restoring the base orchestrator.md at head gives exit 1 with `6 occurrence(s) of a recorded defect, 1 recorded: duplicates|...orchestrator.md|repeats 12 words from CLAUDE.md` (ev/mut_revert_orch.txt). The s8 deletion is the mechanism. Setting the count back to 6 at head is refused as stale headroom.
- RESULT mutation proof: n/a (prose). Reverting orchestrator.md to base turns lint red, as above.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 103b2097a38f972d1cb048c9ffbedcf6b1ba6d61` -> exit 0, clean (ev/merge_tree.txt).
- RESULT CI on head (check-runs API, ev/check_runs.txt): no red. browser, coverage and fast (3.14) were still in_progress. pr-contract, policy-docs, budget-raise-gate, delivery-status and arch-score are success. The body's "Red checks: none" holds so far.
- RESULT mandate: comment 6175172275 by tvofi, 2026-10-14T18:14:58Z. Its first line is byte-identical to the body's quote; scope all, valid until 2026-10-28 (ev/mandate.txt).
- RESULT VERSION, manifest and notes heading: untouched by the three-dot diff.
- RESULT instruments named in the new s13 text: tick_loop.sh, cloud_relay.sh, sweep_render.py, merge_train.py, cloud_dispatch.py and daemonize.py all exist under tools/audit/seat/, with INSTRUMENTS.md and sweep_template.md beside them.

## Removed-sentence audit (each cut diffed against base and where the rule now lives)
- s4 preflight: "three ways" is restored. Empty stdin (the filename-argument case), held-open stdin (blocks silently, 143 when killed) and per-number-not-per-occurrence are all present. Dropped "which this section encourages" (rationale). OK.
- s6 "not when CI settles": restored. The "until the handoff it prepares against the merge base only" clause is cut. It is a reviewer obligation and lives verbatim in fix-review.md line 8. The orchestrator's own obligation (dispatch at push) is intact. Cut accepted.
- s1 fixer.md step 9 pointer: restored, folded into the "Describing an artifact" bullet. OK.
- s10b tag-citation clause: restored; only "measured" dropped. OK.
- s2 "no claim stands on one agent's word": it now appears nowhere in the policy tree, but it is the reason behind "write it". The obligation (could a seat do this with a brief? then write it) and the independence argument above it both remain. Rationale, cut accepted.
- s8 "Out of scope is not a licence to file": the operative clause stays ("A real finding you must not touch goes to that stage's brief (section 10)"), and CLAUDE.md:187 states the sentence verbatim. Cut accepted.
- s8 four-issues anecdote: compressed to "one filed issue asked for a mechanism already in the tree"; CLAUDE.md keeps it in full. Rationale, accepted.
- s8 "a precedence rule only one side can see is not one": both sides still state precedence. orchestrator.md: "if the two disagree, CLAUDE.md is the rule and this copy is the bug". CLAUDE.md names orchestrator.md section 8, which is still s8. Rationale, accepted.
- Also cut: "duplication is deliberate ... binds you hardest" (in CLAUDE.md), "not a way of recording that you noticed" (in CLAUDE.md), "propagates further than a wrong pull request" (reduced to "nothing gating it"), and s2 "from the programme rather than adding one" and s7 "are the one who breaks" (both wording only). None drops an obligation.

## Why blocked
Everything substantive passes. The cuts are rationale, not obligation, and no rule is dropped. The block is step 8/14: the body twice asserts a figure (`319 319 4507 4513`, "measures 319 and 4507") that its own command does not print at this head. The remedy is body-only: change 4507 to 4512 in Mutation proof and Figures. The head need not move.
