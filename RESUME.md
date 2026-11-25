# fix-3885 handoff note

- Code: handoff/ci-3885-nonprod-scope at 7eb9b2fd81, base origin/main 0f63320c96, fix A c0dcc352f9 unchanged.
- Green locally: prelude self-test (134), gate (120), codeql_scope (94), selftest_scope (161), structure.py,
  policy_lint --budgets, rules_sync, fragments_sync, layout --guard, ci_predict, mutants 16/16, brief_lint on carry-3885.json,
  non-code prepr rc=0. The FULL gate is CI's: the local one timed out on a loaded host.
- entities.py locally: one coverage-stage timing check fails on files this diff does not touch; both pins this diff moved are fixed.
- Carries: dev/programme/carries/carry-3885.json (duplicate-dispatch reuse; env_drift warm cache). PR leaves #3885 open.
