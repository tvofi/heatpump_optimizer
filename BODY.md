Main's Governance `record` and `record-autofix` stayed red after the delivery rows moved from `docs/delivery/` to `dev/programme/delivery/`. Two stale spellings: `record-autofix` in `.github/workflows/tests.yml` still ran `git add docs/delivery` (matches nothing, so each beat read "nothing-owed" and no row was ever pushed), and its pin in `tests/entities.py` hard-coded the same string, so the pin blessed the bug. Separately the `record` job's friction step spawned `.claude/workflows/policy_lint.mjs` (gone since the move), so `friction_issues.mjs` refused: "did not answer for all 20 existing friction-issue key(s) (exit 1)". The pin now derives the directory from `record_row.row_path` (one source); `friction_issues.mjs` spawns whichever policy_lint home exists. The `record` job's own error (rowless #1995, #2003) is real and clears once the autofix lands. No policy file, budget or claim file touched. #2002 untouched.

## Head

e1531dbb832acf793a4c92572694aa1dee79ea21

## Mutation proof

- Old spelling restored in the pin (before the workflow fix): `tests.yml's record-autofix job: ... guarded write set` FAIL, adds=['git add docs/delivery', ...].
- `STATS_RUN = STATS_TOOL` in `friction_issues.mjs`: `FAIL the spawned stats tool exists on disk`, 100 passed, 1 failed.

## Null control

Unmodified main: run 37577849702 `record` job fails on #1995/#2003 and on the friction step (exit 1). With the fix: `tests/entities.py` 2188 of 2188 pass, `friction_issues.mjs --self-test` 101 passed, `record_row.py --self-test` all checks pass.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2188 ENTITY CHECKS PASSED`
- `node tools/policy/friction_issues.mjs --self-test` prints `101 passed, 0 failed`
- `python3 tools/audit/seat/record_row.py --self-test` prints `all checks passed`
- Class enumeration: `git grep -nE 'docs/delivery|docs/HANDOVER\.md' -- ':!dev/audit' ':!tools/audit/round*' ':!tools/audit/bugclasses.json' ':!dev/programme' ':!RELEASE_NOTES.md'` after merging origin/main. Fixed: `tools/audit/fastpath_census.py:58`, `tools/audit/seat/record_row.py:449` (self-test fixture dir). Closed by handoff/r9-rca-1990: `tools/audit/seat/merge_train.py`, `bus.sh`, `open_pr.sh`, `handoff_push.sh`, `handover_prompt.py`. Left as written, deliberately: `tools/release/stamp.py` and `tools/policy/policy_lint.mjs` record-class regexes (already carry both spellings), `tools/policy/brief_lint.mjs:1103` (probes both), `tools/policy/record-predicate/*` and `tests/layout.json` (old-to-new map), fixtures and self-test inputs in `tools/audit/merge_fastpath.py`, `tools/pr/prepr.sh`, `tools/pr/app_approve.sh`, `tools/audit/seat/state_docs.py` (path-independent), historical prose in decisions, RCAs, `tests/entities.py` comments and `INSTRUMENTS.md`; `.claude/rules`, `.cursor/rules` and `dev/governance/rules` `paths:` globs, which carry-1922 sequences with R9-RO-9 (policy, owner-approved edit); `docs/HANDOVER.md` mentions in tests/card.mjs, hooks and CODEOWNERS comment (policy or fixtures, outside this fix).
- Row: `dev/programme/delivery/2011.md`.
- Scoped gate: `GATE_SCOPE=auto ./tests/run.sh` printed `MODE: FULL` (tests.yml is a gate file); not run to completion locally, CI is authoritative.

## Red checks

- `delivery-status`: red because main's `record-autofix` could not stage rows (`git add docs/delivery` matched nothing after the move), so rowless merges #1995 and #2003 stayed unrowed. This PR is the countermeasure. Cheaper detector: the `tests/entities.py` pin now derives the staged directory from `record_row.row_path` instead of repeating the string, so the generator and the job cannot disagree. This diff touches what it reads (`.github/workflows/tests.yml`, `dev/programme/delivery/2011.md`).
- `nightly-status`: grades main's last scheduled Tests run, 37440269774 (2026-10-06T09:03Z), whose only failed job is `record-autofix`: the same defect. This diff reaches it, since it edits that job; the next scheduled run after merge is the verification.
- main `record` (rowless #1995, #2003) clears once the autofix lands; its friction step is fixed here (`friction_issues.mjs` spawned a moved file), pinned by a self-test arm.

## Forward-carry

none

## Friction

none
