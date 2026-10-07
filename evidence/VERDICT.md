Fix review: merge c83ced70b5dc207a53dbf7623030f19cbca85f29
bus-nonce: 78a5504561566846c798cd5fa1e48348

Round 1, reviewer r9c-rev-2017. Measured and live head are both c83ced70b5dc207a53dbf7623030f19cbca85f29 (gh pr view headRefOid); merge-tree against origin/main f060cb4c exits 0.

RESULT enumerator-moves-under-perturbation: PASS. Planted `_zz=self._opt_config; _zz2=self._current_state; self._planted_attr=1` in a dhw-seam method (_dhw_current_hour): dhw hub_loads 11 -> 13 (_opt_config 0->1, _current_state 3->4), owned dhw 3 -> 4 (+_planted_attr), owned_equal dhw True -> False; every other line unchanged. Null (trailing comment): output byte-identical. Not void under judge.md.
RESULT enumerator-agrees-with-structure.py: PASS. Its walk is seam_metrics' (state_root_bindings, is_state_root, hops, methods exclusion); owned counts 3/40/13/31/3 equal the attrs column of tests/structure.py's seam table at this head; each tree loads its own tests/structure.py and seam_map.json, so the base is measured by its own rules. Head hub-load lines equal the body's figures; base tree 31567b71 equal too.
RESULT classification: PASS. tools/audit/ is an INERT prefix (tests/closure.py); repo_root() copy in the file is byte-equal to tools/audit/repo_root.py's canonical text. CI check-runs on the head: closures, closure-scope, fast (3.14), instrument-self-tests, policy-docs, briefs, pr-contract, budget-raise-gate (success twin) all success. The body does not hand-edit closures.json inert_reads and closures-autofix did not ask. My local closure.py select reports MODE: FULL with a scope.json reason on this machine; that is the local recording, not the head, so I cite CI instead.
RESULT red-checks: PASS. delivery-status and nightly-status failed on the head; the body names both and answers them (red on main, diff reaches no file they read). Read the delivery-status log: it lists overdue/pending rows of other PRs (#2001, #2003), not 2017. budget-raise-gate cancelled twin has a success twin. Heavy CI lanes cited from the API, not re-run (load 255).
RESULT forward-carry: PASS. RO-9's roster entry on origin/handoff/audit-r9-fixplan carries, dated 2026-10-07, "once the EG-B7 seam-hub enumerator PR merges, add its row to the kept-instruments table in dev/audit/README". The row is correctly absent here (policy file, owes an ## Approval).

Notes, none blocking.
1. The body's Forward-carry heading says "none" and the README row is described as "left for the owner" without naming RO-9; the destination does carry it. Cosmetic.
2. The body says the earlier head 244dc80f "also had the README row", contradicting the policy-file claim; stale text.
3. The docstring says the two trees run on one seam_metrics text; in fact each tree runs its own. Wording only, figures unaffected.
4. Closes #1744 is in prose; verify #1744 closes at merge and that the halt numbers are posted on it.
5. No code diff, so no mutation proof, goldens, claims or budgets move; VERSION, manifest and notes untouched. Class-open step 6: the enumerator is the rule and returns no seam owed by a diff; the PR's class is the instrument.
