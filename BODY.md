Root-cause analysis for #1985, the friction key `root-cause-unanswered`. It adds `dev/audit/rca/R9-RCA-1985.md`, its raw evidence under `dev/audit/rca/1985/`, and one `_rca` entry in `tools/audit/bugclasses.json`. It changes no production, workflow or policy file.

**Process state: (c).** I reproduced the count: 12 PRs and 17 verdicts in `v6.7.16..origin/main`. 13 of the 17 verdicts name a lane that tests the fix's own code (typing, mutation, closures, fast, env-matrix, CodeQL and others). The other 4 are body-only debt. The cause is that the body is written at the handoff, when the fixer pushes, and CI's reds arrive after it. `fix-review.md` step 11 sends every red the body does not answer to the one word `root-cause-unanswered`.

The cheaper detector already exists: `pr-contract` with its re-run workflow. It fired on 17 of 17 entries, 11 before the verdict and 6 when the `Tests` workflow completed. So no check is built. A separate `red-check` verdict class was also considered and declined, by the orchestrator under mandate 5951564627. It would leave the key at the threshold (12 to 3 PRs), and its value is direction, not hours. Both refusals share one revisit trigger: body-only repairs reaching 3 PRs in one window.

Closes #1985

## Head

1dad91c6d872c27c8666fd61fc03977e97b43a59. The analysis was measured against `origin/main` 3910026e on 2026-10-07; this head adds this PR's delivery row and merges `origin/main`.

## Mutation proof

n/a: no production or check code changes. The change is an analysis document, its evidence files and one register entry. `python3 tools/audit/fold_ledger.py check` reads the register entry, and it reported `0 violation(s)` with 97 rca entries.

## Null control

n/a: no detector is built. I did run a control on the measurement itself. The default `check-runs` listing (`filter=latest`) showed `pr-contract` green at #1993 and #1996. With `filter=all` and the per-attempt API, each head shows three failed attempts. The analysis uses the `filter=all` reading. Section 2 of the document records this trap.

## Figures

- 12 PRs / 17 entries, 57 merged: `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v6.7.16` (output in `dev/audit/rca/1985/stats_v6.7.16.txt`)
- 17 entries, enumerated independently with 0 API failures: section 6 of `dev/audit/rca/R9-RCA-1985.md` (`entries.txt`, `seq.txt`)
- 12/17 bodies passed `pr-contract` at the first run; 11/17 had `pr-contract` failed before the verdict; 6/17 verdicts came before `Tests` completed: `gh api "repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?filter=all&per_page=100" --paginate` (`timeline_all.txt`)
- 11/370 verdict-carrying PRs before 2026-10-02 against 27/97 from then: every `Fix review:` first line on the 501 PRs merged since 2026-09-16 (`verdicts_since_0916.txt`)
- `python3 tools/audit/fold_ledger.py check`: 0 violation(s)
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `GATE_SCOPE=auto bash tests/run.sh`: `MODE: SCOPED -- 0 script(s) run, 31 scoped out.`

## Red checks

- `delivery-status`: red because it grades `main`. It reads main's merges that have no delivery row after the move from `docs/delivery/` to `dev/programme/delivery/`; #2011 is fixing that on `main`. This diff reaches nothing it reads except its own new row, `dev/programme/delivery/2013.md`. Cheaper detector: none for this PR. The cause is on `main`, and its owner is #2011.
- `nightly-status`: red because it grades `main`. Main's scheduled Tests run failed only at `record-autofix`, which is the same delivery-row defect #2011 fixes. This diff reaches nothing `nightly-status` reads. Cheaper detector: none for this PR. The cause is on `main`, and its owner is #2011.

## Forward-carry

`dev/audit/rca/R9-RCA-1985.md` section 5 records two items:

- The `red-check` grammar split: declined, with its revisit trigger recorded.
- The `web-fix-wave.js:489-495` route. It sends `root-cause-unanswered` to a root-cause seat with no body-repair round. This is owed by whoever next edits that script, and it is recorded for the orchestrator's record.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
