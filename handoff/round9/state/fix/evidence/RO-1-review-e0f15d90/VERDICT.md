merge e0f15d909fd5bf0780bd70f57610983b8f364c87

Review round 2 of R9-RO-1, now #1790 (#1789 closed as superseded). Cloud reviewer (opus). Measured at PR head e0f15d90: code head ea3f85c0, plus merge 67ea07d2 of origin/main 5f4f641a, plus the delivery row. The head already contains current main, so it is the merge. Re-read at posting: unchanged.

Round-1 blocker 1 (harness), resolved:
- My 15 mutants re-run at the head (run_mut.py, mutants_r2.txt). G is re-pointed at verdict(), and G2 is added (main() passes enforce=False).
- C, G, M and N are now killed by the new self-test cases. A, B, D, E, F, I and O are killed as before. 17/17 self-test cases pass at the unmutated head.
- Survivors: H, J, K and L (judged non-blocking in round 1), and my G2. G2 is main's --enforce wiring: the self-test does not see it, but the real `--enforce` run does (rc 1 at the head, 0 under G2). It first matters at RO-9, whose carried brief has it run --enforce. Non-blocking.
- The fixer's G2 is a different mutant, inside verdict(); its claim that G2 is killed holds for that mutant.

Round-1 blocker 2 (carry), resolved:
- On handoff/audit-r9-fixplan at 35800d45, the R9-RO-2..9 briefs all carry the index/staging and `since` text.
- RO-4 carries carry-1743/carry-1747. RO-5 carries the .claude/rules dead-arm note. RO-9 carries --enforce and the #1218 pair count.
- brief_lint on that branch's own tree: TOTAL 3 errors, all in R9-F1.7 and R9-EG-B3, none in RO. They come from that tree predating main. The Mac's run reads TOTAL 0.

Usual checks:
- No handoff/ or resume paths in 830f84ad..e0f15d90. The four cherry-picks are tree-identical to the round-1 commits. The only delta from #1789 is tests/layout.py (+20/-5) plus main's merge.
- merge-tree against origin/main: rc 0.
- Report-only: python3 tests/layout.py gives rc 0 and MODE: REPORT. 3113 paths; category 2272, retired 2270, reference 1529, dead 27. The rise from the body's 3094 figures is main's new #1787 files, all under retired prefixes. Category minus retired is still exactly carry-1743 and carry-1747.
- Closure: derive_closures.sh --single tests/layout.py (Linux, strace) records the same 2 files.
- mutation_table.py --scope changed --base origin/main --max 10 --jobs 3: PASSED (empty scope), rc 0.
- prepr.sh (no body): PRE-PR e0f15d90 00000000000000, rc 0.
- CI pr-contract is green on the live body. The body's Head section is now accurate: 67ea07d2 is a real merge.
- codeowners_gap uncovered_files=0; policy_lint TOTAL 0; structure.py PASSED.
- Full gate, GATE_SCOPE=full, 3.14.0rc2 with pinned requirements-ci: 1 TEST SCRIPT FAILED, tests/stress.py alone. shoulder/tariff+cycle read 269.2x against a 268x budget, while my prepr and mutation_table ran on the same box.
- stress.py re-run alone under the gate lease (tests/gate_lock.py auto-lease): ALL 87 STRESS CHECKS PASSED, worst 244.3x.
- The diff touches no custom_components file and not stress.py. The red is load noise, the same judgement as round 1 and the fixer's.
- CI at the head: no red check when read (fast, coverage and closures were still running).
