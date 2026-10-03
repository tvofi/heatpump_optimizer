R9-F10.14: take `tests/arch_score.py` and `tests/arch_score_head.py` out of the coverage job's tracer, in `tools/audit/w5-partition/coverage_tree.sh` (one filter on the derived script list, plus its comment). They still run untraced in `fast` through `tests/run.sh`.

Why: tvofi asked whether arch_score's ~30 min inside `coverage` is expected. Measured on 14 coverage runs, `arch_score.py` is 23.8 min median (max 25.3) of a 45-50 min job, 48% of the summed per-script time on a main push, against 9.4 min bare in `fast`. It parses `custom_components` as text (AST) and imports none of it, so the tracer recorded nothing from it, and a pure-Python AST walk is the tracer's worst case (1.8-2.7x).

Fixer options rule, A-H from the measurement report:

| option | disposition |
|---|---|
| A. leave both out of the coverage stage | TAKEN: this PR. Identity proven below |
| B. skip on a cache miss when scope says unselected | rejected: subsumed by A, more moving parts, main pushes still pay |
| C. own parallel CI job | rejected: new check name, ruleset change, a second job's setup; A already removes the cost from coverage and `fast` keeps the 9.4 min |
| D. speed the AST walks in structure.py / archscore | rejected here: structure.py defines the ratchet, every one of 85 vectors must stay byte-identical, gain unmeasured; revisit only if 9.4 min in `fast` matters |
| E. cache live vectors by file hash | rejected: every PR that selects the script does so because a key input changed, so it nearly never hits |
| F. raise `jobs` above 4 | rejected: no gain on a 4-vCPU runner; needs a measured CI run |
| G. cache the base score | rejected: no base-vs-head scoring exists in this test (fixed-pin calibration) |
| H. restore-keys on the nearest main commit | REJECTED, see below |

Option H, evaluated. It would key the per-script restore on the nearest main commit holding an entry, with the scope diffed from that commit. Costs: `tests.yml` is a gate file (FULL gate) and the trust marker `push refs/heads/main $BASE` (tests.yml, "Check the restored coverage is main's push run's") was built exact on purpose (#1812, #1822); a fallback needs a cache-listing call to find the restored commit, an ancestry check (a newer main entry would diff in the wrong direction), and a re-derived trust rule. Benefit, measured: on the report's sample 10 of 12 PR coverage jobs and 4 of 4 push jobs missed the cache, because the key exists only after main's push coverage job (49.6 min median) finishes and main merged every 41 min median (first-parent gaps of the last 60 merges at ac255c200: p25 18, median 41, p75 55 min). The exact key can only hit when the next merge is at least one job-length away: 21 of 59 gaps are >= 50 min, 40 of 59 are >= 25 min. So this PR alone moves the push job from ~50 to ~25 min and the share of gaps that outlast it from 36% to 68%, which is most of what H would buy, with no trust-model change. Re-measure the hit rate after this lands; if it stays low, H becomes its own PR with the owner.

## Head

a8718cb09afee55a9c8f008cfabac6fcaf696fd1

## Mutation proof

Break the fix: restore the old derivation (drop the `grep -vxE "arch_score|arch_score_head"` pipe). The stage list then contains both scripts again and the run is the "before" arm below: 19 scripts, `arch_score` 400 s and `arch_score_head` 18 s traced on this machine, against the 17 scripts of the fixed tree. The check that goes red in CI is the coverage job's wall time; the correctness oracle (the JSON) is unchanged by either arm, which is the point of the next section.

## Null control

Same head, same venv, coverage 7.13.1, both arms run concurrently from the worktree by `coverage_tree.sh fast`: the unmodified script from `origin/main` (before) and the edited one (after).

- `coverage.json`: identical after removing `meta.timestamp`, the only field that differs (parsed JSON equal, and equal under `json.dumps(sort_keys=True)`). Totals 19256 statements, 307 missed, 98.4%. `coverage_report.txt` is byte-identical.
- The traced arch scripts left no package line: `.coverage.arch_score` and `.coverage.arch_score_head` hold 0 rows in `line_bits`, while `.coverage.features` holds 70. The union with an empty set is why nothing moves.
- `tests/coverage_ratchet.py --coverage <json>` on both arms: rc 0, identical output ("package coverage 98.41 % >= 96.0 %", "config_flow.py coverage 100.00 % >= 100.0 %", "every module >= 95.0 %", COVERAGE RATCHET PASSED). Mac numbers; the Linux floor is CI's.
- Saving, same arms, summed per-script wall: 1129 s before, 828 s after (the 301 s is the 418 s of the two arch scripts less the contention the concurrent arms added). Expected on CI: 1427 s median traced for `arch_score` plus 24-35 s for the head script, off ~2958 s of summed script time on the push run 37140602095, so the coverage job goes from 45.6 (PR) / 49.6 (push) min median to about 21-25 min. The null control for that claim is this PR's own coverage job: its base-keyed cache misses (the cache key hashes `coverage_tree.sh`, which this PR changes), so it measures every script, and its "Measure the tree" step is compared with the 45.1 min median of the previous misses. The fast job's time must not move.
- What the proof does not cover: a future script that parses text but also imports the package would lose coverage if added to the exclusion; the comment in the script says so.

## Figures

- `grep -vxE "arch_score|arch_score_head"` on the derived list: 19 scripts to 17, from `tools/audit/w5-partition/coverage_tree.sh fast` (`scripts.tsv` of both arms).
- 23.8 min median, 25.3 max, 14 coverage runs: job logs read from `gh api repos/tvofi/heatpump_optimizer/actions/jobs` in the orchestrator's measurement report `seat-archscore/REPORT.md`.
- Merge gaps: `git log origin/main --first-parent -60 --format=%ct` at ac255c200.

## Red checks

none

## Forward-carry

none. Option H's re-measure after merge is recorded above in the PR body for the orchestrator's `docs/HANDOVER.md` update; no later stage depends on it.

## Friction

none

_Requested by **tvofi**_
