R11-PRE-RCA-LATCH-CLAUSES lands the item card E11-INJECTED carries to round 11. The card is read at eval/r11 `c6ce415b7711d76cf6c08f926f30da91f7bda924`, whose `review` field reads `approve` (round 3, at 02a48db212). It is `decision: accepted`, and tvofi ruled "Accept, pay by deletion" on 2026-11-15. Three things land:

- `dev/audit/rca/R10-RCA-SETPOINT-LATCH-DEADLOCK.md`, byte-identical to the record at 2e20aa5d4e (`archive/handoff-wip/r10-rca-setpoint-latch-deadlock`). It holds the cause, process state (a), the cost test and the built detector. The detector `dev/audit/harnesses/r10_rca_setpoint_latch.py` was already on main through 8fc6be183d, so the record is the only file added.
- `fix-review.md` step 16, the record's section 5 text verbatim. The outside-reviewer clause now reads "steps 1 to 16".
- `fixer.md` step 3: the record's one sentence, verbatim, placed after "measured at both ends of its input range".

Budgets, paid by deletion with no raise. Each cut removes prose that a rule loaded with the same contract already states:
- `fixer.md` loses its section "Before you hand off: answer any check your branch turned red". `defect-root-cause.md`'s Enforcement section already states that obligation for the fixer, and the role pack loads that rule beside `fixer.md`. The section's `UNDER-SCOPED`/`INHERITED CLAIMS` clause appears in no rule (`ci-autofix.md` lacks it), so it moves into step 5's `ci-autofix.md` parenthesis.
- `fix-review.md` step 11 loses its restatement of the body's answer. It also loses the owed-reds paragraph (`defect-root-cause.md` Enforcement) and keeps the `classify --pr` INTRODUCED pointer, which no rule states.
- `fix-review.md` step 10 loses its restatement of `finding-propagation.md`'s Enforcement (the reviewer opens the carry the body names, at the roster SHA).
- `fix-review.md` step 8 loses ": say so" and shortens "had to build" to "built". The same step's "write that in the verdict" already says it.
- `fix-review.md` step 2 loses "printing your own `RESULT` lines", which the closing paragraph's "Return a verdict with your RESULT lines" already requires.
- `fix-review.md` step 12 loses "as you post it", which its own heading already says.
- `fix-review.md` step 13 drops its second `(claim-files.md)` citation; the same step cites that rule two sentences earlier.
- Two cuts were tried and reverted because a check pins the text. The note "The wave routes an old `blocked <sha> root-cause-detectable: <check>`" is required by `tools/policy/check-wave-script.mjs` (`fix-review.md teaches "root-cause-detectable"`, plus its negative control). "never widen it" in step 12 is pinned by `tools/audit/seat/review_packet.py --self-test`.

Rows from `node tools/policy/policy_lint.mjs --budgets` (the `tools/audit/briefs/` keys are these two files' budget rows): `tools/audit/briefs/fixer.md` and `tools/audit/briefs/fix-review.md`, each at or under its line and token cap at the head. `dev/governance/config/policy_budgets.json` is untouched.

## Approval

Pending; none is claimed here. This is a policy pull request (`dev/governance/roles/fixer.md`, `dev/governance/roles/fix-review.md`). It merges on tvofi's approving review at the head, or, under mandate 6893738184 (scope all, in force to 2026-12-15T12:00Z), on the orchestrator's declared approving review after the fix review. The clause texts are the record's drafts, verbatim, which card E11-INJECTED's ruling accepts ("Accept, pay by deletion", tvofi 2026-11-15). The deletions that pay for them are this seat's and are the owner's to change at review. No budget is raised.

## Head

`66437eb001d6ad51d11ed1fa8a58ed4a5a7602bf`, merge base `98847b99d7bb3238686efd6869f805c89c6d1ff1`; `origin/main` merged at its tip `921214bf4246338c1a83fbc5269eaa0bfe91b7d5` (see Conflict resolution).

## Conflict resolution

After #3626 (R11-PRE-RULINGS-FILE) merged, the branch conflicted with main in `dev/governance/roles/fixer.md` step 5. The resolution is a union. #3626's rulings sentence (opening paragraph, "The owner's rulings in `dev/programme/RULINGS.md` bind you.") and main's scoped-prepr sentence stay verbatim. This PR's step-3 clause ("its release needs no person") and its step-5 clause ("a red `UNDER-SCOPED` or `INHERITED CLAIMS` is answered by naming it") stay too. `fixer.md` stays within its per-file cap (`node tools/policy/policy_lint.mjs --budgets` rc 0, `node tools/policy/policy_lint.mjs` 0 errors). Text-only `prepr.sh` (`PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1`) rc 0 at the head. The resolution delta is `git diff 79524a752f 66437eb001`.

## Mutation proof

n/a: the diff adds no production, tool or test line (`git diff --stat 98847b99d7bb3238686efd6869f805c89c6d1ff1 79524a752fded9a11643f02d5e8a3a33f4f1c630 -- custom_components/ tools/ tests/` prints nothing), so `prepr.sh` draws no mutant. The countermeasure that is a check is the record's detector, which is already on main. It is re-run at both ends under Figures. The record states 6 of 6 hand mutants killed.

## Null control

The detector's null control is v7.1.11, before #3404: rc 0, 9 states, 0 failed.

The new step's null control: on a merged PR that adds no refusal on an actuator write, step 16 asks nothing. #3614, the merge base itself, changes no `custom_components/` line: `git diff --quiet 98847b99d7^1 98847b99d7 -- custom_components/ && echo NO-PRODUCTION-DIFF` prints `NO-PRODUCTION-DIFF`. Against that, #3404 (`1aeaf273a4`) adds `_arm_space`, the refusal the record names: `git diff 1aeaf273a4^1 1aeaf273a4 -- custom_components/ | grep -c '^+.*def _arm_space'` prints 1. That is the case the step does ask about.

## Figures

- detector at v7.1.11: `python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <worktree at v7.1.11>` -> rc 0, `states=9 failed=0` (harness sha1 c6f2734378b2a6328b79b3c2f6e68611a6285e53)
- detector at v7.1.12: same command at v7.1.12 -> rc 1, `states=36 failed=4` (the defect, released)
- detector at the head: same command at this head -> rc 0, `states=36 failed=0` (main carries the hotfix 8fc6be183d)
- record identity: `git diff --quiet 2e20aa5d4e HEAD -- dev/audit/rca/R10-RCA-SETPOINT-LATCH-DEADLOCK.md && echo IDENTICAL` -> IDENTICAL
- budgets: `node tools/policy/policy_lint.mjs --budgets`, rows `tools/audit/briefs/fixer.md`, `tools/audit/briefs/fix-review.md` and the `corpus` aggregate, all within cap at the head with no budget file change
- `node tools/policy/policy_lint.mjs` -> 0 errors; `node tools/policy/check-wave-script.mjs` -> 0 failed; `python3 tools/audit/seat/review_packet.py --self-test` -> 0 failed; `node tools/policy/rules_sync.mjs --check` -> RULES-SYNC ok
- gate: `python3 tests/closure.py select --diff 98847b99d7bb3238686efd6869f805c89c6d1ff1` -> MODE: SCOPED; `tests/doc_claims.py` and `tests/entities.py` run green, as do the `run_always` scripts (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`) and `tests/structure.py`

<!-- figure-block: scope-line mb=2104e34d8696aaf74d319cb38377c2997d78426c head=66437eb001d6ad51d11ed1fa8a58ed4a5a7602bf -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

- fix-review.md: unclear: step 16's drafted text says `blocked` but names no class. `web-fix-wave.js` `VERDICT_RE` routes an untaught class word to `other` and keeps the word, so the verdict still parses and routes. Teaching a class word is the owner's change to the drafted text, which was accepted as written. Carry: dismissed: the verdict parses and routes as drafted, and the owner accepted the text verbatim
