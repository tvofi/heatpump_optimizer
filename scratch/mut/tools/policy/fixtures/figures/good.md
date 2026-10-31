The null control. Every command below was written by a body in this repository
and really run by a seat, taken from the pull requests open on 2026-09-10. A
rot fixture proves the check can refuse; only a healthy one that exercises the
same code path proves it refuses for the right reason.

## Figures

- The ratchet at this head: `python3 tests/structure.py`.
- The scope selection: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
- The caps: `node .claude/workflows/policy_lint.mjs --budgets`, whose numbers
  are the instrument's own and are not restated.
- The generated rules: `node .claude/workflows/rules_sync.mjs --check`.
- The body contract's own self-test: `bash tools/audit/prepr.sh --self-test`.
- The check runs at each head, paginated with `filter=all`:
  `gh api "/repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?filter=all&per_page=100" --paginate --jq '.check_runs[] | select(.name=="pr-contract") | "\(.conclusion) \(.started_at)"'`
- The open population, one call:
  `gh pr list --repo tvofi/heatpump_optimizer --state open --limit 50 --json number,body,files`
- A pipeline whose first stage is the instrument:
  `gh run view --repo tvofi/heatpump_optimizer --job 102803274073 --log | sort -u`

## Red checks

none
