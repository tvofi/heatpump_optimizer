Fix review: blocked 774e53f751c2c13e67b957cd7d05fd22b98f1fee rule-dropped: the orchestrator.md section 4 trim deletes the held-open-stdin warning for preflight.sh (blocks silently, reports 143 when killed), which no other policy file or the script states

bus-nonce: 72ee57197001f8b1a60e103c7fa5f2f3

Round 1. Measured head 774e53f751c2c13e67b957cd7d05fd22b98f1fee (re-checked with ls-remote just before writing: still the head, ev/head_recheck.txt). Merge base and origin/main are both 4a3cbcf62. Role file current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## RESULT lines
RESULT budgets orchestrator.md 319/319 lines, 4507/4513 tokens; nudge.md 115/115, 3812/3814. Matches the body, and no budget file changed (ev/budgets_head.txt)
RESULT lint-head TOTAL: 0 error(s) across 41 policy file(s) (ev/lint_head.txt)
RESULT lint-base (null control) TOTAL: 0 error(s) across 41 policy file(s) (ev/lint_base.txt)
RESULT known-bad 6->1 is genuine. At head, a recorded count of 6 errors with "1 occurrence(s) left of 6 recorded"; at base, a recorded count of 1 errors with "6 occurrence(s) ... 1 recorded" (ev/knownbad_*.txt). The drop comes from deleting most of section 8 (about 20 lines down to 5); the remaining sentence restates CLAUDE.md in condensed form.
RESULT mandate: comment 6175172275 is by tvofi, 2026-10-14T18:14:58Z. Its first line is quoted byte-exact in ## Approval: "MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z". Today is inside the window.
RESULT merge-tree with origin/main 4a3cbcf62: exit 0, tree 4d5372a9d (ev/merge_tree.txt)
RESULT version: VERSION, the manifest and the notes heading are untouched (pr-contract log: "no version edit")
RESULT mutation proof: n/a. This is prose, and its only detector is policy_lint budgets and known-bad, re-run above.

## Removed-sentence audit (ev/orchestrator.diff)
- s3 "Describing another artifact": bold removed and "another" became "an". Same rule.
- s3 "rather than adding one": rhetoric only.
- s4 preflight "Empty stdin prints clean ... filename as an argument": kept in nudge.md 18 ("reads the body on stdin. A filename argument reads nothing and prints clean.").
- s4 preflight **"Held-open stdin blocks silently and reports 143 when killed. Neither looks like a failure."**: NOT kept anywhere. `git grep -i -E "held.open|blocks? silently|143"` over dev/governance, CLAUDE.md and .claude/rules at head finds nothing, and tools/pr/preflight.sh has no guard or comment for it. The new text also changes the count to "It misleads two ways" (stdin plus per-number), so the third failure mode is gone, not moved. This is the blocking item. The brief requires that the trims remove no rule. Fix: add the clause to nudge.md 18 next to the stdin sentence (nudge has 2 tokens of headroom, so it is probably tight), or keep it in orchestrator.md and pay for it elsewhere.
- s5 reviewer dispatch "not when CI settles; until the handoff it prepares against the merge base only": the second half is in fix-review.md preamble ("Before the fixer's handoff message ... prepare against the merge base only"). The first half is implied by "when the fixer pushes". Acceptable.
- s8 "not a way of recording that you noticed", "Out of scope is not a licence to file", the duplication rationale, and "A precedence rule only one side can see is not one": the first three are in CLAUDE.md's section of the same name, which the new text names as the rule. The last is a justification, not an obligation. Acceptable.
- s10 "a tag citation is no reflex fix: the symbols measured biting here exist at no tag": kept in brief-citations.md lines 26 and 34. Acceptable.
- Added text in section 13 and the nudge.md 18 pointer match the brief: look up first, a new helper lives in tools/, sweep_render.py, re-check briefs on a merge, and seed or reconcile the ledger.

## CI on this head (check-runs API, 41 runs, ev/check_runs.txt)
- pr-contract is **red twice** (jobs 118319333102 and 118319667719). The cause is `carry_audit.py check`: "UNROUTED body item 7889a2ee (## Forward-carry) [section]: 'none. Each instrument in the measured cases ...'" and "CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted" (ev/pr_contract_tail.txt). The audit reads the explanatory clause after "none." as a finding with no destination. ## Red checks says "none", so the red check is also unanswered. fast (3.14) and coverage were still in_progress, so per fix-review 11 I am not using root-cause-unanswered as the verdict class. It still needs fixing: make ## Forward-carry a bare "none" (or route the item), and answer pr-contract in ## Red checks.
- pr-contract's figures check lists 336 and 4794 (the pre-deletion measurements quoted in ## Mutation proof) as figures not in ## Figures. These are advisory "check" lines, not a refusal.
- All other completed runs passed or were skipped, including budget-raise-gate, policy-docs, briefs, mutation and instrument-self-tests.

## Steps not applicable
2, 3 and 6: no finder harness. This is a policy change, and its harness is policy_lint, run at both ends above. 4: no golden or claim file touched. 10: Forward-carry is "none". All instruments named are in tools/audit/seat/INSTRUMENTS.md, which I did not re-enumerate one by one. 14: I re-derived the known-bad and budget movements above, and they come from deletion, not from the instrument.
