Fix review: merge d1051479c6fb2a5898db48b45cd2b0403177d187

bus-nonce: 72cdb0510df30d8b2e1721dc0bca3cf4

Round 1 (first review of #3621; full scope).

## Findings

- Residual: the switch-on arm's no-cadence test matches the cadence by its old names (`CADENCE`, `EVERY_DIM_ROUNDS`, `activeIn`, `DIMS.filter(`), and the arm drives only rounds 9, 11 and 13, so a round-keyed seat filter spelled another way that is active only at rounds outside those three passes: `.filter((s) => !(round % 5 === 0 && s.dim === 'D6'))` on `const SEATS` in p2's `.claude/workflows/audit-find.js`, graded by this head's copy, prints 248 passed, 0 failed (ev/mutants.md M5). Its control: the same filter keyed on `round % 2` fails 27 (M4). The body's sentence "a tree with the denominator and a cadence is refused" holds for the named idioms and for any filter active at 9, 11 or 13, not for every cadence. p2 carries its own unconditional copy of this grader; driving a span of rounds there (e.g. 10 to 21, every seat each) closes it. Carry: R11-PRE-FINDER-CONTRACT

## Evidence

- RESULT figures (body Figures and Null control), re-taken at origin/main e0ad8b2bd3 (the body cites 26dbf7c43e; main moved, grader figures unchanged): main's copy over main's tree 223 passed 0 failed; this head's copy over main's tree 223 passed 0 failed; this head's copy over p2's tree 248 passed 0 failed; main's copy over p2's tree 163 passed 1 failed. ev/main-tree_*.txt, ev/p2-tree_*.txt.
- p2's ref `handoff-wip/r11-pre-finder-contract` is now d761df1655, whose only delta over the cited cb6600d2f1 is `BLOCKED.md` and `p2-BODY.md` (ev/git-checks.txt); the grader inputs are identical.
- Mutation proof (step 1): the body's three mutants reproduce exactly (164/2, 182/28, 247/1), each killed; grader-side deletions show the new no-cadence test is M3's only killer (G1: 247/0 without it). ev/mutants.md, ev/mut-*.txt.
- Finder's harness (step 2, 9): none named; this PR is p1 of a split grader change with no finding harness; the grader itself is the instrument, run at both trees above.
- Step 4, 5: the diff is one file, `tools/policy/check-wave-script.mjs`; no claim file, golden, `VERSION`, manifest or notes heading touched.
- Step 6: no enumeration rule named; a one-file grader change, one seam. The class gap found is the Residual above.
- Step 7: the body's Head section names d1051479c6 (merge of origin/main 646352ff13 into 9259c5e81b), the head measured.
- Step 10: the body's carries name R11-PRE-FINDER-CONTRACT, the group's own split part p2, which `fixer.md` excepts; carry_audit at the head: 4 routed, 0 unrouted.
- Step 13: `git merge-tree --write-tree origin/main d1051479c6` exits 0 (ev/git-checks.txt).
- Step 14: no budget, closure, ledger or score moved.
- CI: `gate` read failure in the packet digest with the log line "run(s) [43738726698] at this head are still being judged; their gate decides"; `merge_train.py classify d1051479c6fb2a5898db48b45cd2b0403177d187 --pr 3621` at 17:33:17Z: `GREEN d1051479c6fb2a5898db48b45cd2b0403177d187 pending: none red: none` (ev/classify-log.txt, ev/classify-last.txt). No required check is red, so no `## Red checks` answer is owed.
- Step 12: the PR head ref read d1051479c6 again after GREEN.
