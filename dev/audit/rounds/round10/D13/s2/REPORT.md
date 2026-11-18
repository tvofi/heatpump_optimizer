# D13-s2 report (round 10): cells D13.M3, D13.M6. Baseline 17f1c55fad1b

## Method
- Window: first-parent merges `v6.7.16..17f1c55fad1b`, which gives 185 merges, 185 PRs and 0 api_failures. `fetch_window.py` maps each one through `/commits/<sha>/pulls` and reads `/pulls/<n>`, `/issues/<n>/comments` and `/pulls/<n>/reviews`.
- `blocks_friction.mjs` hooks `tools/policy/policy_lint.mjs` (`statsHistogram`, which applies `frictionKey`, plus `waveVerdictRe` and `blockClasses`, which come from the `VERDICT_RE`/`VERDICT_CLASSES` in `web-fix-wave.js`). Its header states the bucketing.
- Commands:
  `python3 dev/audit/rounds/round10/D13/s2/fetch_window.py v6.7.16 17f1c55fad1b $T/window.json`
  `HPO_PLANDATA=$(mktemp -d) node dev/audit/rounds/round10/D13/s2/blocks_friction.mjs $T/window.json [--perturb=verdict|budgets-readme|unbacktick]`

## Findings
- **D13-s2-01 (high, M3).** `root-cause-unanswered` accounts for 37 of the 124 blocked verdicts, so 30% of all blocks are of a class that the prompt itself describes as "fix itself is sound". The largest engineering class, `harness`, has 23. Under `--perturb=verdict` the count goes 37→36 and `blocked_outside_grammar` goes 0→1.
- **D13-s2-02 (medium, M3).** The verdict table that `--stats` prints cannot give block classes. Its `head-moved` row holds 133 entries across 71 PRs, but only 4 blocked verdicts carry that class. The other 129 are rework bumps (`REWORK_CLASS`) added to the same histogram as the classes reviewers wrote. Perturbation: delete the reverify `bump(verdicts, REWORK_CLASS, pr)` line and the row should drop to 4.

## Block classes, three ways (M3)
- 124 blocked verdicts. Of these, 0 fall outside the grammar, 15 are `other` (bare) and 21 use class words the grammar does not teach. There are 20 such untaught words, each on its own row: body-stale 2, defect 2, and 1 each for mutation-unpinned, vacuous, re-cut, closures-under-approximated, body-false, null-control-unpinned, docs-code-mismatch, guard, over-fire, d-unbounded, body-figures, skip-abusable, skip-dead, conflict-resolution, record-stale, resolution-docstring-corruption and instruments-stale.
- Buckets, with every untaught word counted under orchestration: engineering 31, record-and-body 44, orchestration 49.

## Friction keys (M6)
- 89 entries. 68 name exactly one `--budgets` file (share 0.764), 0 are ambiguous and 21 name no file. Per-file spellings are in the harness output. `fixer` is split across three spellings: `fixer.md` 16, `fixer` 1 and `dev/governance/roles/fixer.md` 1. The last stays verbatim because budgets keys use the canonical path `tools/audit/briefs/`.
- Perturbations behave as the brief says: renaming `ratchet-budgets.md` to README.md moves one entry from one_file (68→67) to ambiguous (0→1), and removing the backticks moves nothing.

## Non-findings
- Production verdict rows for the taught classes match the harness counts exactly (root-cause-unanswered 37, harness 23, conflict 9, other 15). `prod_unclassified` is 0.

## Exposure
- GitHub API (read-only): PR bodies, issue comments and reviews for the 185 PRs in `v6.7.16..17f1c55fad1b`, plus `/commits/<sha>/pulls`. The comment content was used only as the population being counted.
