Fix review: merge e530ff16701d78656e458acc4da6b40d6ad204ef
bus-nonce: 4beaafd2bc855474ebda1f87aae592bd
reviewer: r10-ratchet-reviewer
round: 3 (round 1 body-stale at 25418620f; round 2 closures-red at 25418620f; rework 0963ab414; main merged at e530ff16)

Head e530ff16701d78656e458acc4da6b40d6ad204ef, re-read at post time: unchanged. Merge base = origin/main 2ff04949f.

RESULT delta 0963ab414..e530ff16: the tree is byte-identical to `git merge-tree --write-tree 0963ab414 2ff04949f` (tree 5aa241da6, empty diff), so there is no hand resolution. The LEDGER-MERGE driver resolved tests/closures.json. Against 2ff04949f, closures.json differs only in closures["tests/entities.py"]: +tools/coverage/coverage_tree.sh, nothing lost, still sorted (267 entries).
RESULT fix files byte-identical 0963ab414 vs head (git diff --quiet over ci_ratchet.py, closure.py, derive_closures.sh, entities.py, run.sh, coverage_tree.sh: rc 0). Every round-1 and round-2 measurement carries.
RESULT classification: coverage_tree.sh moves to INERT_EXCEPT and into entities.py's closure. This follows 476dac6e0's composed_proof.sh and R9-RO-4's tools/pr/README.md, the same case of entities.py reading a file under an INERT prefix. An inert_reads entry would not select entities.py on an edit to the emitter it pins. CI's Linux recording agrees: closures success at head (04:17Z), closures-autofix skipped.
RESULT M6: the emitter check is now `(?m)^\s*unset HPO_CI_METRICS\s*$`. My harness (evidence/emitter_check.py, copied from 0963ab414's entities.py) gives null 0 fails. M6 (run.sh `: # unset ...`) killed; M6b (coverage_tree.sh `# unset ...`) killed; M6c (derive_closures `echo unset ...`) killed.
RESULT red runs graded. Run 38639862216: base 69 GREW, head 54 (17 not counted). Rebuilt window: base 69/67, head 54/54. Zero real rows dropped across all 15 runs. Main's second red, run 38672094207: fast 15 closures + 2 fast, closures 34 + 1 fast, coverage 20 + 1 fast; base 69 GREW, head 54.
RESULT mutants carried: M1, M2, M3, M4, M5, M7, M8 killed (round 1). M6 now killed.
RESULT check-runs at head (API, 04:37Z), all concluded, no failure. Green: closures, fast (3.14), coverage, coverage-ratchet, composed-proof, lane-proofs, wave-script, pr-contract x2, nightly-status, typing, mutation, CodeQL and the rest; the remainder were skipped. mutation green with no production line, so no mutant drawn.
RESULT conflict: `git merge-tree --write-tree origin/main e530ff16` rc 0.
RESULT body: re-read in full at head. Head SHA matches, 8 files listed correctly, closures and wave-script reds named and answered with the cheaper-detector discussion, M6 named. The nightly-status paragraph is historical (that check is green at head), which is harmless.
RESULT budgets: ci_budgets.json and every *_budgets.json untouched. Not a raise. VERSION, manifest and notes untouched.
RESULT code-owned paths: tests/run.sh, tests/derive_closures.sh, tests/closure.py. tvofi's approving review is still required.
