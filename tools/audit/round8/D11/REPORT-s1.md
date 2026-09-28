# Round 8 — D11 seat s1: mechanism inventory, detector health, budgets, recurrence

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree: `/home/claude/audit-r8/seats/D11-s1` (a shallow worktree). Git-history runs used a full clone at the same SHA, under `/home/claude/audit-r8/tmp/D11-s1/full`. Machine: a 4-vCPU shared container at load1 ~21. Every number below is a count; none is a timing.

The artifact of record is `report-s1.json`. This file carries the method, the inventory and the ranked changes.

## Method
1. Built the inventory from the tree and the REST API:
   - both rulesets, read directly (snapshots in `s1_ruleset_*.json`);
   - each required context mapped to its workflow job, with that job's `if:` evaluated per event;
   - `policy_lint --list` (19 classes), `brief_lint`, `structure.py`, `prepr.sh`, the hooks, and CODEOWNERS.
2. Positive controls:
   - `policy_lint` acceptance;
   - `policy_lint_mutants`;
   - per-file checks emptied by hand (`checkNoGh`, `checkCitations`);
   - `--hooks` self-tests;
   - a historic-red census per required context (`s1_red_census.py`).
3. Budgets (`--budgets`) and recurrence (`--stats --since v6.6.9`).

## Findings (details and numbers in report-s1.json)
- **D11-s1-01 (critical, provisional).** A body edit fires `pull_request: edited`, and the `if:` guards added in #1484 then re-create `policy-docs`, `env-matrix` and `wave-script` as `skipped` at the unchanged head.
  - Tree arm: 3 required contexts skipped on `edited`. The perturbation takes it to 0; the synchronize null control is 0.
  - History arm: 3 of the 15 merges since the guard landed merged with those contexts' latest run `skipped` over a real verdict. No red has been masked so far.
  - The latest-run-wins hop is unprobed.
  - Sibling seam: a `workflow_dispatch` of tests.yml skips `closure-scope`.
- **D11-s1-02 (high).** CODEOWNERS' required-check surface derivation sees only the `<interpreter> <path>` form. A wider rule finds 14 unowned files that decide a verdict:
  - exec: `tests/run.sh`, `tests/derive_closures.sh`, `tools/audit/w5-partition/coverage_tree.sh`;
  - import: `counts.mjs`, `render_md.mjs`;
  - data: the known-bad ledger, both budget files, the exclusion lists, both claim files, `closures.json`, `requirements-ci.txt`.
  - Null control (the round-6 rule): 0 unowned. Perturbation: 14 → 13.
- **D11-s1-03 (low).** `stop-selfcheck.sh` misses staged policy changes: 2 of 4 states exit 0 against a red linter. The one-line perturbation takes it to 0.

## Mechanism inventory
The rows are derived as 4 ruleset rules + 16 required contexts + 19 `--list` classes + brief_lint + structure.py + claim files + prepr.sh + 3 hooks = 46.

| mechanism | refuses | runs | positive control (this seat) | leaves uncovered |
|---|---|---|---|---|
| ruleset main-protect: deletion, non_fast_forward | deleting or force-pushing main | main | read only; not probed (live) | — |
| ruleset main-protect-checks: required_status_checks (16) | merge with a missing, failed or pending context | PR→main | red census: 3 of 16 contexts red in history | skipped counts as a pass (F1); no integration_id pin; strict=false |
| ruleset main-protect-checks: pull_request | merge without 1 approval / code-owner review | PR→main | read only | last-push approval off; code-owner surface gaps (F2) |
| fast (3.14) — tests.yml `fast` (./tests/run.sh) | a red suite | PR, main | 3 red heads | run.sh unowned (F2) |
| browser, briefs, typing, mutation — tests.yml | as named | PR, main | 0 red in 100 heads | skipped on a recheck=false dispatch |
| closure-scope — tests.yml | under-scoped closures | PR only | 0 red | skipped on any dispatch (F1 seam) |
| closures — tests.yml | recording mismatch | PR, dispatch | 1 red | — |
| policy-docs, env-matrix, wave-script — governance.yml | red corpus, env matrix, wave script | PR (not edited), main | 0 red in 100 heads; lint acceptance ok | skipped on edited (F1) |
| pr-contract — governance.yml | body contract, author, red list | PR incl. edited | 12 red heads | title taken from the event payload, not the API |
| hassfest, validate-hacs, Analyze ×3 | HA, HACS, CodeQL | PR, main | 0 red | — |
| policy_lint classes (19: citations … sunset) | as in `--list` | CI + Stop hook | acceptance 91 errors / 187 pins; mutants 22/22 PIN; citations and no-gh emptied → red | loop call site unpinned (self-declared); `figure_lint` and `figure_lint.mjs` key separately in stats |
| brief_lint | roster citations | CI `briefs` | CARRY ok, 10 errors pinned | — |
| tests/structure.py | structural growth | CI fast | PASSED; budgets file unowned (F2) | — |
| claim files / env_drift | unclaimed golden drift | CI fast | not driven this seat | the claim files are unowned (F2) |
| prepr.sh | the pre-PR body check | local + pr-contract | self-test 84/85 (the 1 failure is a no-`gh` artefact) | — |
| hooks: session-start, pre-edit, stop-selfcheck | see `--hooks` | local session | 8/16/19 self-tests pass | pre-edit misses Bash edits and MultiEdit `edits[]`; stop misses the index (F3) |

## Ranked changes
1. Move `pr-contract` into its own workflow and drop `edited` from governance.yml. This closes F1 and costs about 0 s per merge (it removes 3 skipped runs per edit). Standard moved: OpenSSF Branch-Protection, CI-Tests.
2. Widen the CODEOWNERS derivation and add the 14 paths (about 14 lines). This closes F2. Standard moved: Branch-Protection and Code-Review; the NIST AI RMF GOVERN human-oversight point.
3. Add `--cached` to the stop hook's CHANGED line, plus one self-test case (2 lines). This closes F3.

## Non-findings and exposure
Both are in report-s1.json.

## Unfinished
- A sandbox probe of latest-wins.
- The root-cause-record check for the 4 recurring keys.
- The rest of the staleness sweep.
- A schema conflict: the mandated id form `D11-s1-NN` fails finding.schema.json's id pattern.
