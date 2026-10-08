head aa88452dfef01782eddc5d31c9ea3a350926504e
pr-contract jobs 113310735049, 113311725784: ERROR [pr-body] checks delivery-status (and nightly-status) red and '## Red checks' does not name them; diff touches .github/workflows/tests.yml which they read.
body says '## Red checks: none'; body promises 'next head adds a docstring line to tests/nightly_ha.py' (fires half) - head has no such change (diff --stat: tests.yml, entities.py, delivery/2058.md).
check-runs at head: closure-scope success, nightly-ha skipped (expected: no pathspec touched). Ruleset 22628467 required contexts contain no nightly entry (unchanged, diff has no ruleset file).
Fires-evidence: run 37764931838 was a dispatch on a throwaway branch, not a pull_request event.
