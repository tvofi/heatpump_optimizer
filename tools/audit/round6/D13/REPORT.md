# D13 — process yield and cost — audit round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), worktree `~/audit-r6-D13`. Window `v6.6.0..e336cc2c` = 5.12 days. `api_failures=0` on every harness; no timing claim (the one timing-shaped figure is GitHub's own run durations), so nothing provisional.

> Reconstructed by the orchestrator from the finder's inline return (REPORT.md write refused; 6 harnesses + fixtures on disk, untracked).

## Metric tables

1. **First-pass yield**: merges 67; yield **0.925** (62/67); rounds/merge mean 1.104 / max 3; zero-verdict merges 4; `blocked` 1 (`claims`). Rework: 7 PRs, 11 extra rounds, all 11 name a moved head.
2. **Verdict coverage**: bot-cycle 47 (4 no-verdict), fix-feature 9, other-lane 11, record-chore 0. 4/67 (6.0%) no-verdict: #1358, #1362, #1261, #1257.
3. **Block classes**: `claims` × 1, all else 0; outside-grammar 1 (#1287 class word no colon).
4. **DORA**: deploy freq 1.95/day; lead time median 7.81 h; change-failure rate (excl) 0.090 (6/67); time-to-restore median 2.09 h (Tests) / 6.95 h (Governance).
5. **CI seconds**: GOV = 8 jobs (no drift); governance share 0.0406; median governance 159 s vs gate 4133 s.
6. **Friction keys**: 45 entries / 20 keys; 35 name exactly one file (0.778); 0 ambiguous; 10 verbatim. Top: `fixer.md` 9 entries.

## Findings

### D13-01 (high, hygiene) — every rework round is head-moved re-verification, and the class that names it is never used
Over the window, 11 of 74 parseable verdicts are rework; **11 of 11 name a head sha other than that merge's first verdict's**; `head-moved` (the class `web-fix-wave.js` defines for exactly that) has **0** verdicts; `blocked` = 1 (`claims`), engineering 0. Instrumented `web-fix-wave.js:VERDICT_RE` (compiled from source, not transcribed). Perturbation (reshaped) → extra_rounds 11→10; (no-merge arm) → rounds 74→1. Null control reproduces 0.925/1.104/11/11/0/1/74. Fix: emit `blocked <sha> head-moved: …` on a moved head, or count a second `merge` on a different head as rework in `statsHistogram`; do not widen `VERDICT_RE`.

### D13-02 (medium, hygiene) — 6% of merges carry no verdict, all automation-authored; the histogram denominator is 64
4/67 merges (#1358, #1362, #1261, #1257) carry no parsable verdict; `policy_lint.mjs --stats` reports merge 63 + claims 1 = 64. Instrumented `policy_lint.mjs:statsHistogram`. Perturbation (covered) → no-verdict 4→3, yield 0.925→0.940. Fix: print a coverage line beside `STATS: N merged pull request(s)`.

### D13-03 (medium, hygiene) — the exclusion list is keyed where the excluded job cannot gate a merge
`record` is skipped at 67/67 PR heads and fails 58/67 merge commits; at the PR head the failures are `nightly-status` 7/67 and `delivery-status` 2/67, so head rate 0.134 stays 0.134 with the exclusion applied (merge-keyed rate 0.090). Instrumented `.claude/workflows/cfr_exclusions.json`. Perturbation (add nightly-status) → head rate 0.134→0.030. Fix: report both keyings; do not add `nightly-status`.

## Non-findings (10, each executed)
1/75 verdict lines outside grammar (the one `--stats` flags); 0 review-only verdicts; 0 unreleased/reverted merges; GOV=8 no drift; 2 governance jobs cost a PR nothing; 52 unenumerated commits are `/pulls/<n>` 404s (stamp-skip path); exclusion entry still does work (record 58/67); friction resolver never ambiguous; frictionEntries driven not copied (census diffs 0); top friction key is the fixer contract.

## Exposure
The brief/schema files; `round4/D11/{dora_keys,d11lib,governance_cost}.py` (the base D13.md names — enumerators and GOV only); `policy_lint.mjs`, `web-fix-wave.js`, `cfr_exclusions.json`, `governance.yml`, `tests.yml`; GitHub records (`/commits/<sha>/pulls`, `/pulls/<n>`, comments, reviews, check-runs, actions). No D11 finding read; `round3/round5` not opened.

## Harnesses
`d13lib.py`, `yield_rounds.py`, `dora_keys.py`, `ci_seconds.py`, `friction_keys.mjs`, `make_fixtures.py` (+ `fixtures/`).

## Orchestrator note
The file list is untracked and must be classified (measured closure or `tests/closure.py` INERT) before `tests/entities.py` will accept the commit.
