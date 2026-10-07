Fix review: merge 4f7df25a8500b1adf0f296edd1e48f6e42b1ea5f

bus-nonce: fed5f168d8e52ad4912b482154322310

Measured head 4f7df25a (re-read via API at post time: still the PR head). Merge base 143e2d0a (= origin/main).
1. policy_lint.mjs: origin/main -> 1 error (fixer.md ~4867 vs cap 4866, files_tokens); head -> TOTAL 0 errors. Logs: lint-main.txt, lint-head.txt.
2. rules_sync.mjs --check at head: rc 0 (sync.txt).
3. Meaning: "says why that is safe" -> "says why". tests/README.md "The scoped gate" gives the reason (run only the scripts the change can reach); the dropped word is an unneeded evaluative. Intact.
4. Three-dot diff (diff.txt): only that sentence in fixer.md plus the new dev/programme/delivery/2042.md row. VERSION, manifest, notes, claim files untouched.
5. Body ## Head already names 4f7df25a as the PR head and 1101a2fb as the authored code head; pr-contract is success on 4f7df25a (both runs). Accepted.
CI at 4f7df25a: policy-docs, env-matrix, pr-contract, briefs, closures, mutation, hassfest green. Reds: delivery-status (UNCHECKED, 0 overdue, not required) and nightly-status (last concluded nightly failed on mutation-ledger/mutation-nightly/record-autofix); neither reads this diff. coverage/Analyze(python) were still running at post time; not gate checks for a policy-doc diff.
