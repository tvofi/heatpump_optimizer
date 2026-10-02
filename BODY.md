_Requested by **tvofi**_

Part of #1857 (its fix), RCA `rca/RCA-closures-autofix-skip.md` on `handoff/r9-rca-closures-autofix-skip`.

Before: `closures-autofix` printed `skip-not-under-scoped -- nothing owed to a human` and stayed green beside a red `closures` job whose check printed `INERT READS UNDER-APPROXIMATED` (PR #1864 at head 54bfc9934041d594510309310ec427896e6d715e, run 37068702869, artifact 11254298147: `tests/doc_claims.py` reads `docs/site/docs.css`, not in its `inert_reads`). After: the quiet status is earned only by the closures job's own check passing. `check()` now prints its success line from one constant (`_CHECK_OK_LINE`); where `check.txt` (the tee #1857 added) exists and lacks that line, the pinned-classifier branch returns `skip-classifier-disagrees` if it carries an `UNDER-SCOPED: ` line and otherwise the new red `skip-manual-repair-owed`, whose remedy names the by-hand repair (INERT READS: `--single` the named script; PHANTOM: `closure.py prune`). An absent `check.txt` stays quiet (runs from before #1857). The file is read as data and can only redden the job.

**Red, not neutral.** `ci-autofix.md` already reads the summary line and says a red autofix job means no bot commit is coming; the job's verdict is an exit code (`autofix_report`: 0 or 1), so a neutral state does not exist without a new mechanism, and the wait the rule tells a reader to hold has to end when the check is red for a reason the bot cannot repair (#523's shape). The cost is one extra red beside an already red `closures`, the same trade #1857 made.

**A premise changes, and I say so.** #1857's null control (a46a91c: INERT READS must stay quiet) assumed a failure the bot does not repair owes nothing. #1864 shows it owes a human. That control is rewritten, not deleted: the quiet status is now pinned to a *passing* check.txt (and to an absent one); the INERT READS log, now byte-for-byte #1864's, expects the new red. Untouched on purpose: `skip-clean` (the documented moved-head case, where `closures` printed UNDER-SCOPED and the newer head is measured by its own run), `skip-not-allowed`. Not covered, named: a `closures` failure from a step after `check` (`no-copies`, NOT-A-FILE is in `check` and is covered) leaves a passing `check.txt`, so the job stays quiet; `claims-autofix` and `mutation-autofix` keep their own quiet statuses (the RCA's optional item 4).

`.claude/rules/ci-autofix.md` (policy) is edited: the red list and "What green means" name `skip-manual-repair-owed`; the bullet that said a red on failed recordings would fire on "INERT failures" is corrected, since INERT READS now reddens by design. It is paid for inside the file (under the cap: `policy_lint.mjs` `TOTAL: 0 error(s)`), no cap raised; `.cursor/rules/ci-autofix.mdc` is regenerated.

## Root cause

Instance 4 of the class on `handoff/r9-rca-closures-autofix-skip` (`rca/RCA-closures-autofix-skip.md`): a quiet autofix status beside a red `closures` job. State (d), the process was sound and its precondition changed: the quiet `skip-not-under-scoped` assumed the classifier and the grader agree and that any failure the bot does not repair is not worth saying. D11-s1-03 pinned the classifier to the base (instances 1-3, #1846 x2 and #1851: UNDER-SCOPED masked); #1857 closed exactly that and kept INERT READS quiet as its null control; #1864 is the same false message from the sibling failure the control protected. The countermeasure here is the same as the RCA's for (d): the autofix reads the grader's own result instead of inferring it from its pinned copy. Cost test: one file read of a ~1 KB text file in a job that runs only after a failed `closures`, well under 1 s, against a seat waiting on a green tick for a repair only a human makes.

## Approval

Owed, under the mandate (round 9, `ci-autofix.md` is policy: the owner approves before merging). Not a budget raise.

## Head

d7a3e963ad8a4cb67455cf358be683bbf249c14e

## Mutation proof

`tests/mutation_table.py --scope changed` draws nothing (no `custom_components` line changed). The guard `if lines is None or _CHECK_OK_LINE in lines:` in `tests/closure.py` was mutated in place (python rewrite, BSD sed first applied nothing, so it was redone and checked with `cmp` against the good copy), `tests/entities.py` run each time, good copy restored:
- `if True:` (always quiet): 2 of 2082 FAIL, `a pinned classifier that disagrees ... reddens (#1846)` and `a closures check that failed without UNDER-SCOPED reddens naming the owed manual repair (#1864 INERT READS)`.
- `if lines is None:` (never quiet on a present file): 1 of 2082 FAIL, `and stays quiet only when the closures check passed, or no check.txt exists`.

## Null control

Failing test first: with only `_CHECK_OK_LINE` added (the tests' import) and no guard, `entities.py` printed `2 of 2082 ENTITY CHECKS FAILED`, and the non-planted FAILs were exactly `a closures check that failed without UNDER-SCOPED reddens ...` and `every status the two apply functions return is classified here`. With the guard: `ALL 2082 ENTITY CHECKS PASSED`. The cases run the real `apply_under_scoped_recordings`, over: the #1846 log (red, `skip-classifier-disagrees`), #1864's INERT READS log (red, new status), an empty `check.txt` (red), a passing log (`note:` line plus the success line: quiet) and no `check.txt` (quiet). #1857's cases for the first and last still pass unchanged.

## Figures

- Instrument: `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py`, Python 3.14 venv, at head d7a3e963ad8a4cb67455cf358be683bbf249c14e (merge base `03ba7f70f007147bda32ac0fc5dd83b11499bbaf`, origin/main tip `03ba7f70f007147bda32ac0fc5dd83b11499bbaf`, 2026-10-02T22:50:10Z): `ALL 2082 ENTITY CHECKS PASSED`.
- `~/hpo-seats/R9-F11.4-venv/bin/python3 tests/structure.py`: rc 0; `node .claude/workflows/policy_lint.mjs`: `TOTAL: 0 error(s) across 40 policy file(s)` (it printed `1 error(s)`, 1467 tokens against the cap of 1428, before the file paid for itself); `node .claude/workflows/rules_sync.mjs --check`: ok; `node .claude/workflows/brief_lint.mjs`: rc 0.
- The log is the real artifact: `gh api repos/tvofi/heatpump_optimizer/actions/artifacts/11254298147/zip`, `check.txt`, five lines, copied byte for byte into `_AF8_NULL_LOG`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL` (`tests/closure.py` is a gate file); the one script that exercises the change is `tests/entities.py`, run above; the rest is CI's.
- `git diff --stat origin/main...HEAD` (three-dot): 4 files, 75 insertions, 46 deletions (`tests/closure.py`, `tests/entities.py`, `.claude/rules/ci-autofix.md`, `.cursor/rules/ci-autofix.mdc`). `VERSION`, manifest and RELEASE_NOTES untouched.

## Red checks

none on this branch (no push has run CI). Local only: `policy_lint` budget error above, answered by paying in the file; `structure.py` and `brief_lint` were green.

## Forward-carry

`.claude/rules/ci-autofix.md` itself carries the status. Recorded as not done, for the orchestrator: the same "grader printed X, pinned classifier says not X" guard for `claims-autofix` and `mutation-autofix` (RCA item 4); no brief changed.

## Friction

ci-autofix: stale: the bullet saying a red on a failed recording would fire on unrelated "INERT failures" described #1857's world; corrected here.
