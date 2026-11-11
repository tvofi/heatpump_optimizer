# D13-s3 — round 10, steps M4 and M5 (baseline 17f1c55fad1b)

Harness: `dev/audit/rounds/round10/D13/s3/d13_s3.py` (API responses cached in `cache/`).
Window: first-parent merges `v6.7.17..17f1c55fad1b`, 98 merges, all mapped via `/commits/<sha>/pulls`, api_failures=0.

## Exposure
Read via `gh api` (account tvofi): `repos/tvofi/heatpump_optimizer/commits/<sha>/pulls` and
`commits/<sha>/check-runs` (paginated) for the 98 merge commits and their PR heads; git
first-parent history of the export's `.git`. No comments, reviews or bodies were read.

## Findings
**D13-s3-01 (M4, medium)** — the DORA base the brief names, `dev/audit/rounds/round4/D11/dora_keys.py`,
cannot compute its metric at baseline: it `import d11lib` from its own directory, but `d11lib.py`
stayed in `tools/audit/round4/D11/` (ModuleNotFoundError); with the import fixed, its `CFR_EXCLUSIONS`
still names `.claude/workflows/cfr_exclusions.json`, which no longer exists (the registered artifact
is `dev/governance/config/cfr_exclusions.json`), so `load_exclusions` raises FileNotFoundError.
`RESULT dora_keys_loads=0`; with `D13S3_FIX_IMPORT=1 D13S3_DORA_EXCL=dev/governance/config/cfr_exclusions.json`
it reads 1. Both defects are one phenomenon: the R9 move left the instrument's two path-bound
references behind. Seam rule: `git grep -n "cfr_exclusions\|import d11lib" dev/audit/rounds/round4/D11`.

## Measured (M4, M5) — non-findings with numbers
- CFR merge-keyed raw 0.592, excluded 0.561; head-keyed raw 0.276, excluded 0.276; revert_rule_merges=0.
- Per name (merge/head of 98): record 44/0, ci-ratchet 40/0, record-autofix 30/0, fast (3.14) 9/0,
  env-matrix 6/0, validate-hacs 3/0, merge-main 2/0, closures 1/0, slow 1/0, delivery-status 0/17,
  nightly-status 0/12. Perturbation `D13S3_EXCLUDE_EXTRA=ci-ratchet` moves merge-excluded 0.561 -> 0.418.
- M5: GOV re-derived from the five governance workflow files plus `briefs` equals `governance_cost.py`'s
  carried GOV (both differences empty). Governance s/merge median 466 mean 491; gate median 4114
  mean 6473; governance_share 0.070 (0.064 with `pr-contract` dropped).

## Leads
- Exclusion list reason for `record` ("concludes failure at EVERY merge") no longer matches: 44/98.
  `ci-ratchet` and `record-autofix` fail only at the merge surface (40, 30 of 98) and are neither
  excluded nor in `not_excluded`; owner judgement on the list (dev/governance/config/cfr_exclusions.json).

## Unfinished
- M4 deployment frequency, lead time, time-to-restore were not computed by this harness.

## Cache (added at intake)

The GitHub API cache this seat read (`cache/`, 294 files, 43 MB) is not on `handoff/audit-r10-register`; `cache-MANIFEST.txt` lists every file with its size and sha256. The original is on `origin/handoff/audit-r10-find-B8` at `ee9b898e1b42`: `git checkout ee9b898e1b42 -- dev/audit/rounds/round10/D13/s3/cache/`.
