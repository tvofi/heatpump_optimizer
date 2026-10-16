Fix review: merge 2e819456954548351ba8fd2d0c375fa3355d9543

bus-nonce: d484b4236f77d43daf05300a30d2a153

Round 4, the minimal re-cut (round 3 blocked 60c4b9b13 for class-open F1/F2 with no destination). I judged the delta only, as dispatched: one main merge and the re-cut body. The preamble diff of dev/governance/roles/ against origin/main is empty.

RESULT delta: 2e8194569 has parents 60c4b9b13 and c42d7cea6. Its tree 0ffc72832 is identical to `git merge-tree --write-tree 60c4b9b13 c42d7cea6`, so the merge carries no hand resolution. The authored diff against the new merge base c42d7cea6 is unchanged from round 3. merge-tree against origin/main exits 0, with the ledger driver resolving tests/closures.json.
RESULT ci: all 45 check-runs at 2e8194569 completed, 30 success and 15 skipped, none red. All 17 required contexts are success, among them fast (3.14) 116719376564, closures 116728944256, mutation 116718533087, pr-contract 116718886229 and Analyze (python) 116718531635.
RESULT arm at 2e8194569: PASS on both checks. It reads 41 policy files and 8 carries and finds 5 cited programs, all of which run; stale spellings []. This is my own driver, re-run after main's tests/entities.py changes merged.
RESULT destination: R10-STALE-PATHS-2 is on origin/main (roster PR #2309, 071b8e431 is an ancestor of origin/main 12cf1764d). It holds issues=[2312], fixes=[2312] and class N-move-stale-path. Its brief carries F1 with the round-1 plant list as the control, F2 and F4. #2312 is OPEN with the same three items.
RESULT carried from round 3 (code unchanged): finder dora_keys_loads 0 -> 1; corpus_churn rc 1 -> 0; M9 and M10 killed; 0 moved spellings in any carry's remeasure.

Round 3's block is answered. The body's ## Forward-carry names #2312 and R10-STALE-PATHS-2 for F1, F2 and F4, and the destination exists on main. That satisfies fixer.md step 8 ("a distinct finding named by id") and finding-propagation.md. #2227 can close with these seams named. The re-cut body keeps the required headings, the mutation proof, the null control, the figures, the red-check answers and the forward-carry, with round history removed.

Notes, not blocks:
- The body's figures, including the "CI at this head" check-run ids, were taken at 60c4b9b13, as its ## Head section states. I re-took CI at 2e8194569 above, and the code figures carry because the merge is resolution-free.
- R10-STALE-PATHS-2's brief places the stale-path arm "in tests/layout.py". The arm is in tests/entities.py, in the block between `# --- N-move-stale-path (#2227)` and `# --- D11-04 (#1194)`; only the F4 reference arm is tests/layout.py's. That is for the roster seat, before the group's fixer is dispatched.

Evidence: the evidence/ directory of this verdict's bus ref. It holds:
- head.txt and checkruns.tsv;
- arm_head_r4.out;
- group_stale_paths_2.txt and roster_main.json;
- pr_body_r4.md;
- the round-3 artifacts: arm.py, drive_d13.py and scan_all_paths.py (my own drivers and probe), mutants_r3.txt, d13_both_ends.txt and churn_*.out.
