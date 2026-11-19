# D13-s3 -- round 11, steps D13.M4 and D13.M5

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Window: the 271 first-parent
merge commits whose committer date lies in 2026-11-09T12:00:00Z .. 2026-11-16T12:00:00Z
(seven days, closed 7 h before the baseline commit so every run at a window
merge had concluded). Enumerator for both steps:
`PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D13/s3/enum_merges.py`
(271 lines, `api_failures=0 unnamed=0`).

## Method

- The round-4 instruments (`dora_keys.py`, `governance_cost.py`) need
  `d11lib.merged_prs()`, which is GraphQL; this seat's token reaches REST only
  (`gh api graphql` answers HTTP 403), and `gh --paginate` follows Link
  headers in the `repositories/<id>` form the proxy refuses. So
  `d13s3lib.py` reads REST alone and walks `&page=N` itself; the round-4
  instruments' own symbols (`cfr_keyings`, `cfr_by_name`, `latest_by_name`,
  `load_exclusions`, `GOV`, `bare`, `dur`) are imported and driven on the
  live data, so every number is computed by the instrument under audit.
- M4 (`dora_by_job.py`): all four keys. CFR per check-run name at the merge
  commit and at the PR head, with the exclusion list applied raw (as
  `cfr_keyings` does) and by job id, and the brief's revert rule. TTR per
  check-run name over the merge sequence. DF and LT as `dora_keys.py`
  defines them.
- M5 (`ci_seconds.py`): seconds per merge at governance_cost.py's surface
  (final head, default listing) and at every surface the merge paid (every PR
  commit with `filter=all`, plus the merge commit); GOV re-derived from the
  workflow files.
- Redispatched C1 (DF, LT, TTR not computed): examined -- all three computed
  below.

## M4 results (dora_by_job.py, api_failures=0)

| key | value |
|---|---|
| deployment frequency | 12 `vN.N.N` tags in 7.0 d = 1.71 releases/day; 22.6 merges per release |
| lead time | n=260, median 6.94 h, p90 16.86 h; 11 merges unreleased at baseline (censored) |
| CFR, merge commit, `cfr_keyings` as written | 0.808 (excluded) = 0.808 (unexcluded) |
| CFR, merge commit, list keyed by job id | 0.797 |
| CFR, PR head | 0.439 (`tests / nightly-status` alone 107/271 heads) |
| reverted merges (brief's rule) | 0 |
| TTR | 17 names with a red episode; table below |

Per name and TTR (merge-keyed and head-keyed counts of 271):

```
  per name 'governance / instrument-self-tests': merge=0.738 (200) head=0.066 (18)
  per name 'gate': merge=0.122 (33) head=0.007 (2)
  per name 'tests / fast (3.14)': merge=0.07 (19) head=0.0 (0)
  per name 'governance / record': merge=0.059 (16) head=0.0 (0)
  per name 'tests / ci-ratchet': merge=0.048 (13) head=0.0 (0)
  per name 'record-autofix': merge=0.022 (6) head=0.0 (0)
  per name 'nightly-ha (2025.2.0)': merge=0.007 (2) head=0.0 (0)
  per name 'nightly-ha (stable)': merge=0.007 (2) head=0.0 (0)
  per name 'slow': merge=0.007 (2) head=0.0 (0)
  per name 'governance / env-matrix': merge=0.004 (1) head=0.0 (0)
  per name 'mutation-ledger (1)': merge=0.004 (1) head=0.0 (0)
  per name 'mutation-ledger (2)': merge=0.004 (1) head=0.0 (0)
  per name 'mutation-ledger (3)': merge=0.004 (1) head=0.0 (0)
  per name 'mutation-ledger (4)': merge=0.004 (1) head=0.0 (0)
  per name 'mutation-nightly': merge=0.004 (1) head=0.0 (0)
  per name 'prelude': merge=0.004 (1) head=0.0 (0)
  per name 'sweep': merge=0.004 (1) head=0.0 (0)
  per name 'codeql / Analyze (python)': merge=0.0 (0) head=0.004 (1)
  per name 'governance / delivery-status': merge=0.0 (0) head=0.03 (8)
  per name 'pr-contract / pr-contract': merge=0.0 (0) head=0.004 (1)
  per name 'tests / nightly-ha (2025.2.0)': merge=0.0 (0) head=0.004 (1)
  per name 'tests / nightly-ha (stable)': merge=0.0 (0) head=0.004 (1)
  per name 'tests / nightly-status': merge=0.0 (0) head=0.395 (107)
  per name 'tests / replay': merge=0.0 (0) head=0.004 (1)
  ttr 'gate': episodes=19 median_h=0.34 max_h=9.25 still_open=False
  ttr 'governance / env-matrix': episodes=1 median_h=0.07 max_h=0.07 still_open=False
  ttr 'governance / instrument-self-tests': episodes=2 median_h=65.82 max_h=106.19 still_open=True
  ttr 'governance / record': episodes=2 median_h=3.11 max_h=3.65 still_open=False
  ttr 'mutation-ledger (1)': episodes=1 median_h=27.48 max_h=27.48 still_open=False
  ttr 'mutation-ledger (2)': episodes=1 median_h=27.23 max_h=27.23 still_open=False
  ttr 'mutation-ledger (3)': episodes=1 median_h=27.01 max_h=27.01 still_open=False
  ttr 'mutation-ledger (4)': episodes=1 median_h=27.5 max_h=27.5 still_open=False
  ttr 'mutation-nightly': episodes=1 median_h=25.74 max_h=25.74 still_open=False
  ttr 'nightly-ha (2025.2.0)': episodes=1 median_h=7.62 max_h=7.62 still_open=False
  ttr 'nightly-ha (stable)': episodes=1 median_h=7.84 max_h=7.84 still_open=False
  ttr 'prelude': episodes=1 median_h=0.53 max_h=0.53 still_open=False
  ttr 'record-autofix': episodes=3 median_h=0.63 max_h=2.21 still_open=False
  ttr 'slow': episodes=1 median_h=24.01 max_h=24.01 still_open=True
  ttr 'sweep': episodes=1 median_h=2.91 max_h=2.91 still_open=False
  ttr 'tests / ci-ratchet': episodes=5 median_h=1.31 max_h=7.94 still_open=False
```

## M5 results (ci_seconds.py, api_failures=0)

| reading | head surface (governance_cost.py's) | full surface |
|---|---|---|
| governance s/merge, median | 1933 | 14038 |
| gate s/merge, median | 6628 | 45334 |
| total s/merge, mean | 11442 | 106627 |
| governance share | 0.204 | 0.186 |
| total seconds | 3,100,885 | 28,895,795 (27,443,801 unique runs) |

omitted_share 0.893; by day 0.857..0.921; lowest day dropped 0.896.
Hidden re-run attempts at the final heads: 37,189 runs, 5,331,965 s. Null
control (single-commit PRs with no re-run attempt): 0.492, the merge-commit
push run alone. Perturbations: `D13S3_HEAD_ONLY=1` gives 0.0;
`--gov-drop pr-contract` gives shares 0.197 / 0.181.
GOV re-derived from governance.yml, pr-contract.yml, budget-raise-gate.yml,
gate-sweep.yml plus `briefs` equals GOV (none missing, none extra).

## Findings

- D13-s3-01 (M4, medium): `cfr_keyings` exclusion is inert under `<unit> / <job>` names; delta 0.0 vs 0.011.
- D13-s3-02 (M4, medium): `governance / instrument-self-tests` red at 200/271 merge commits, green at 186 of their heads; TTR max 106.19 h, still open; alone it carries CFR 0.24 -> 0.808.
- D13-s3-03 (M5, medium): governance_cost.py reads 10.7 % of the CI seconds merges pay (omitted 0.893).

Each is in `findings/` with command, perturbation and seam rule.

## Non-findings

- GOV is complete against its own rule at the baseline (`gov_missing_from_GOV=none`, `gov_extra_in_GOV=none`).
- The revert rule changes nothing in this window: `reverted_merges=0`; `--fixture-revert <sha>` moves it to 1.
- Scheduled nightly reds attached to merge commits (`slow`, `mutation-nightly`, `mutation-ledger`, `nightly-ha`) are the only red at 1 merge of 271 (`merges_failing_only_schedule_jobs_merge=1`): an attribution artefact of at most 0.004.
- The required `gate` restores fast: 19 episodes, median 0.34 h, max 9.25 h, none open.

## Harnesses

`d13s3lib.py` (library), `enum_merges.py`, `dora_by_job.py`, `ci_seconds.py`.

## Not finished

Nothing in M4 or M5. Counts are exact at the window; a later re-run of an old
workflow on GitHub can add seconds to M5's full surface only.

## Exposure

GitHub REST read for this window: `/commits/<sha>/pulls`,
`/commits/<sha>/check-runs` (default and `filter=all`), `/pulls/<n>/commits`,
and `/actions/jobs/<id>/logs` for four `instrument-self-tests` failures; main's
git history and tags. No comment, review or body was read.
