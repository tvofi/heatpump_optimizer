Review of PR #2209 at head 4666a7dd8d43e7bd8d5cae9c51268c31db031dd9 (merge base 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef), detached worktree /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev2209, python 3.14.7.
roles diff merge-base...origin/main -- dev/governance/roles/: empty (contract current).
check_scopes.py --repo . --ref HEAD rc=0 (ok D15 mode=cells seats=3; s1 M1-M4, s2 M5-M6, s3 M7-M8)
check_scopes.py --self-test rc=0 (both perturbed scopes refused)
check-wave-script.mjs (head grader) 180 passed 0 failed rc=0
CI wave-script job 116154063244: grader restored from 554e2ecfa, 173 passed 3 failed (two D15-s1 negative controls, ISOLATED_DIMS lacks D15) -- pending #2214
policy_lint rc=0 (0 errors / 41 files); --budgets rc=0: D15.md 39/39 lines, 728/728 tokens; corpus 61026 cap 61026 (+band 500). Base corpus 60283 vs cap+band 60949; head overshoot without raise = 77 tokens.
rules_sync --check rc=0; brief_lint rc=0; tests/structure.py PASSED; tests/layout.py ok
Mutants: BUNDLE_DIMS.has->false: 179/1 FAIL (killed). abs-path refusal disabled: 179/1 FAIL (killed). Own mutant BUNDLE_DIMS=new Set([]): 180/0 SURVIVES.
merge-tree origin/main(c698d504a) x head: rc=0, clean.
budget-raise-gate red (raise: corpus_tokens 60449->61026 + new D15 caps); needs tvofi approving review at head. nightly-status red: main's (#2205).
Referenced symbols exist at head: tools/replay/{export,dbg_bundle_gen,debug_ingest(--bundle,--corrupt accuracy),debug_replay(--bundle,--start,--end)}.py, tests/replay.py LEAK_PROBES, export.violations, store._sanitize, store.DOMAINS, tests/seam_map.json, Cusum/observe_bias/async_bundle.
