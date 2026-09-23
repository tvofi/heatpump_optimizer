# D11 — Governance mechanisms and policy — round 7

Baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (round-6 fix wave fully merged), audited in the isolated worktree `/Users/timmalmstrom/audit-r7-D11`. Interpreter `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`, `PYTHONPATH=tests/hastub`, every command run from the worktree root.

> report_note: the finder's `REPORT.md` write was refused, so this file is reconstructed by the orchestrator from the finder's JSON return (the `report_markdown` field), per the round-6 precedent.

Three findings, each with an executed number from a committed harness that hooks a named production symbol and moves under a named perturbation. Two are in the governance loop approved under #959 (the friction histogram's filing), one is in the linter's own `sunset` class. Everything else measured held.

## exposure

- `gh api` against `tvofi/heatpump_optimizer`: rulesets 22628467 and 23698884, `rules/branches/main`, commits' `check-runs`, `actions/runs` and `actions/runs/<id>/jobs` (per-step conclusions), issues and issue search, pull requests and their reviews/files/comments.
- `git log` / `git describe --tags` in the worktree's own `.git`.
- Read in the tree as policy: `.github/CODEOWNERS`, `.github/workflows/*.yml`, `.claude/rules/*.md`, `tools/audit/briefs/*.md`, `tests/delivery_status.py`, `policy_lint.mjs`, `counts.mjs`, `friction_issues.mjs`.

## Findings

### D11-01 — the recurring-friction filing lane is skipped by the step-failure rule

`severity: high` · `stop_rule_class: bug` · `instrumented_symbol: .claude/workflows/friction_issues.mjs:run`

**Claim.** The step that files the friction histogram's would-open verdicts is skipped in every `record`-job run whose preceding disposition-refusal step fails — 39 of the last 40 pushes to `main` — while the histogram that names those keys runs in the same job in 40 of 40. So #959 option B produces its trigger and the actor never runs.

```
RESULT runs_scanned=40 count
RESULT refusal_failed=39 count
RESULT histogram_ran=40 count
RESULT filer_ran=1 count
RESULT filer_skipped=39 count
RESULT filer_ran_with_refusal_failed=0 count
RESULT filer_ran_with_refusal_ok=1 count
RESULT friction_issues_in_repo=14 count        # 0 open, 14 closed
RESULT histogram_names_keys=2 count            # --stats over v6.6.9..origin/main, 31 merges, threshold 3
RESULT filer_planned_file=1 count
RESULT filer_planned_update=1 count
```

The three steps of one job, from GitHub's record of the head commit:

```
5 failure  Every merged pull request has a disposition
7 success  Friction and verdict histograms              (if: always())
8 skipped  Show the friction filer refusing its own fixtures  (no if:)
9 skipped  File the recurring-friction issues the histogram named (no if:)
10 success Rules that have outlived their reason         (if: always())
```

**Mechanism.** GitHub Actions skips a step with no `if:` once an earlier step in the same job has failed. The disposition-refusal step fails on every push that leaves a rowless merge (the protocol's steady state); the histogram steps carry `if: always()` and run; the two filer steps do not.

**Perturbation.** (a) Runnable: delete the two `would open` lines from the histogram and drive `friction_issues.mjs --stats-file <that file> --since v6.6.9 --dry-run` — the planner's count moves 1 → 0. (b) PROVISIONAL: add `if: always()` to step 9 (one YAML line), taking `filer_skipped` 39 → 0; cannot be executed without a push to main, named not run.

**Null control.** The one run in 40 whose refusal did not fail (`35701710582`, 2026-09-22T07:51:26Z) is the one run whose filer ran.

**Harness.** `tools/audit/round7/D11/friction_lane_never_runs.py`

### D11-02 — the friction filer refreshes a CLOSED issue, so a disposed key can never reopen

`severity: medium` · `stop_rule_class: bug` · `instrumented_symbol: .claude/workflows/friction_issues.mjs:decide`

**Claim.** `decide` never reads `existing.state`, so for a key whose issue a seat has disposed by closing it the recurrence is written onto the closed issue and reported as `UPDATED`; the exact-title search suppresses a second issue, so a key disposed once can never be represented by an open issue again — 1 of the window's 2 would-open keys is in exactly that state, and 0 of the 14 issues the lane has ever filed is open.

```
RESULT keys_over_threshold=2 count
RESULT keys_landing_on_a_closed_issue=1 count
RESULT keys_landing_on_a_closed_issue_perturbed=0 count
RESULT keys_with_no_issue_perturbed=2 count
RESULT friction_issues_open=0 count
RESULT friction_issues_closed=14 count
RESULT mutant_left_in_tree=0 count
```

**Perturbation.** One line in a sibling mutant (`.friction_issues.mutant-closedstate.mjs`, the mutation lane's own naming): `if (!existing) return 'create'` → `if (!existing || existing.state !== 'OPEN') return 'create'`. Direction: the closed-issue count moves 1 → 0. Anchor asserted once; mutant swept in a `finally`.

**Null control.** The window's other key (`head-moved`, no issue at all) stays `create` in both arms.

**Harness.** `tools/audit/round7/D11/friction_closed_issue_swallowed.py`

### D11-03 — `--sunset`'s three marker vocabularies occur in none of the 39 policy files

`severity: medium` · `stop_rule_class: bug` · `instrumented_symbol: .claude/workflows/policy_lint.mjs:cmdSunset`

**Claim.** All three arms of the `sunset` class fire only on a self-declared marker (`REFUSED BY`, `SUNSET:`, `HONOUR:`); no policy file in the corpus carries any of them, so the class reports `proposed (0) held (0)` over 39 files in the shape of a measurement while being unable to name a rule that has outlived its reason.

```
RESULT policy_files=39 count
RESULT files_carrying_any_marker=0 count
RESULT marker_refused_by=0 count
RESULT marker_sunset=0 count
RESULT marker_honour=0 count
RESULT sunset_proposed=0 count
RESULT sunset_held=0 count
RESULT sunset_not_evaluated_lines=0 count
RESULT sunset_proposed_perturbed=1 count
RESULT perturbation_file_restored=1 count
```

All eight occurrences of the three markers in the whole tree are inside `.claude/workflows/fixtures/policy-loop/sunset-*.md` plus the regexes themselves.

**Perturbation.** Append `- (harness perturbation) SUNSET: 2020-01-01` to one policy file → `sunset_proposed` moves 0 → 1; bytes restored in a `finally` with both digests printed.

**Null control.** The unperturbed arm prints 0 over the same corpus, and `sunset_not_evaluated_lines=0` separates this zero from the class's own "no friction data" zero.

**Harness.** `tools/audit/round7/D11/sunset_marker_census.py`

## Non-findings

| claim | command | value |
|---|---|---|
| every required context `success` at every merged head | `conformance_sample.py 15` | 15/15 PRs, 16/16 contexts, 0 red or missing |
| the required-context arm reads the live list, not a constant | same, perturbed (one phantom context) | 15 → 0 |
| a code-owned diff always carries the owner's review | same (CODEOWNERS transliterated, last match wins) | 6/6, 0 without @tvofi |
| the author is always the author App | same | 0/15 authored by anyone else |
| a `Fix review:` verdict is never the author's | same | 10/10 verdicts from a non-author |
| the disposition protocol is not generally broken | `python3 tests/delivery_status.py --check` | `30 rowed, 1 pending, 0 overdue`, rc 0 |
| `record`'s red on main is the protocol's steady state, already disposed | `policy_lint --record --since v6.6.9` | 1 of 31 undispositioned (the newest) |
| the mutant lane is alive | `policy_lint_mutants.mjs` | 22 arms + entry-point arm, `MUTANTS ok`, rc 0 |
| the hook control fires, both ways | `--hooks`; `--hooks fixtures/.../self-test-fails.json` | 3 wired 8/16/19; negative arm rc 1 |
| `docs/decisions/` and `docs/HANDOVER.md` out of the corpus deliberately | `policy_lint.mjs docs/decisions/0005-*.md docs/decisions/0009-*.md` | 7 errors the corpus never sees |
| metrics inside caps, no orphan cap | `--budgets`; no-arg run | 39 files; 5 aggregates inside `cap+band`; TOTAL 0 errors |
| the known-bad ratchet is not a hidden waiver | no-arg run | 7 of 7 present, 15 occurrences |
| the contexts carry no `integration_id`, unread by the tree's ruleset reader | `gh api .../rulesets/23698884` | 16 contexts, null on every one (recorded as a gap, not a finding) |
| every `uses:` pinned to a SHA (Pinned-Dependencies) | `grep -h 'uses:' .github/workflows/*.yml \| grep -cE '@[0-9a-f]{40}'` | 65 of 65 |
| no untrusted string reaches a shell line (Dangerous-Workflow) | `grep -nE '^\s{8,}run:' -A 3 .github/workflows/*.yml \| grep -E '\$\{\{(github\.event|github\.head_ref|inputs)\.'` | 4 hits, all hex SHAs or a typed boolean |
| the friction key cannot carry injected text into a filed issue | `grep -n 'FRICTION_ID =' policy_lint.mjs` | `[A-Za-z.][A-Za-z0-9_.#/-]*` admits no backtick/space/colon/newline |

## Standards scorecard (executed, no `scorecard` binary on box)

| check | result |
|---|---|
| Branch-Protection | partial — rulesets active, 1 approval, code-owner review, dismiss-stale; **not** up-to-date-before-merge (`strict=false`), one DeployKey bypass `always` |
| Code-Review | pass — 15/15 author is the author App; 6/6 code-owned diffs carry @tvofi's review |
| Dangerous-Workflow | pass |
| Token-Permissions | pass — `contents: read` floor on all 5 workflows |
| Pinned-Dependencies | pass — 65/65 |
| CI-Tests | pass — 16 required contexts, 15/15 sampled merges green |
| SAST | pass — CodeQL security-extended |
| Maintained | pass |
| Security-Policy | pass |
| Signed-Releases | partial — provenance attestation (SLSA Build L2), no detached signature / SBOM |

## Conformance table (sample of the last 15 merged PRs)

| obligation | fraction |
|---|---|
| every required context `success` at the merged head | 15/15 |
| a code-owned diff carries @tvofi's approving review | 6/6 |
| a `Fix review:` verdict from a non-author identity | 10/10 of those carrying one |
| the verdict and the approval come from different identities | 9/10 (#1426 both tvofi) |
| a disposition row `docs/delivery/<N>.md` | 14/15 (#1446 the pending one) |
| the author is the author App | 15/15 |

## Harnesses

All under `tools/audit/round7/D11/`, runnable by the single command in their headers, from the worktree root with `PYTHONPATH=tests/hastub`:

- `friction_lane_never_runs.py` (D11-01) — needs `gh`, authenticated.
- `friction_closed_issue_swallowed.py` (D11-02) — mutation-proof, both arms.
- `sunset_marker_census.py` (D11-03) — byte-backed-up, hash-verified perturbation.
- `conformance_sample.py` — the conformance table and the required-context arm.

`thread_factor` was 0.9999–1.0001 on every run; every number is a `count` reading and contention-immune, so `load1` is quoted (7.5–10.0 during the fan-out) and nothing needs a quiet-window re-take.
