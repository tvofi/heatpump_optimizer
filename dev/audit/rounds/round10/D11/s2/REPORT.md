# D11-s2 (round 10) — steps M2, M3, baseline 17f1c55fad1b

Findings: none survived to a harness-backed claim.

## Non-findings
- Scorecard Pinned-Dependencies / Token-Permissions / Dangerous-Workflow (hand): `scorecard_hand.py` -> 13 workflows,
  123 uses refs, unpinned=0, no_top_perms=0, pull_request_target=0; `--perturb` moves unpinned to 1.
- Branch-Protection / Code-Review (API, ruleset 23698884): 1 approving review, code-owner review, 17 required
  contexts, bypass = DeployKey + Integration 5094721; dismiss_stale_reviews_on_push=false and
  require_last_push_approval=false, which is a recorded owner decision in tools/policy/fixtures/required-contexts.json
  (not re-raised). Ruleset 22628467: deletion + non_fast_forward, no bypass.
- Security-Policy: SECURITY.md present.
- M3 policy_lint --budgets: all aggregates inside cap+band (fixer 5917 vs 5852+500).
- M3 policy_lint_mutants: 23 PIN mutants all killed, entry exit-status DRIVEN; "MUTANTS ok".

## Unfinished
- M3 `--stats --since v6.0.0` with GITHUB_TOKEN ran >10 min (541 PRs) without finishing; no histogram.
- M2 SLSA, Best Practices badge, NIST AI RMF/600-1, OWASP LLM evaluation not executed; M3 conformance sample and staleness not executed.

## Exposure
GitHub API: rulesets list, rulesets/22628467, rulesets/23698884, apps/github-actions; git log v7.0.0; policy_lint --stats PR fetch.
