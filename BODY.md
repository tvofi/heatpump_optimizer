Part 1 of 2 of R10-HOTFIX-RESTORE-BASE-SKEW (orchestrator ruling, mandate 6715477401: two pull requests, never a red merge). CI grades every pull request with the base's copies of `dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (governance `policy-docs`) and `tools/pr/prepr.sh`'s "pinned graders" step (pr-contract). Both read each `PINNED:` line against an exact-form allowlist, so they refuse the workflow fix's new restore source until this admission is on main. This pull request carries only the admission: ahead of an already-admitted form, a `PINNED:` line may open with the restore source that ci.yml's prelude resolves (`inputs.restore_source`, `needs.prelude.outputs.restore_source`, `needs.gate.outputs.restore_source`, `steps.source.outputs.sha`, each followed by ` || `). Any other leading alternative stays refused.

Taken from handoff-wip/r10-hotfix-restore-base-skew: e8d0311b2f (cherry-picked as 9c99eca14d). Added in 5ec2425619:
- `_pinned_ok` reads the source match once. The cherry-picked form's `bool(PINNED_SOURCE.match(val))` conjunct was an equivalent mutant: on no match the re-prefixed value carries a doubled `${{ `, which no admitted form holds.
- The self-test now has a null for every one of the four alternatives (two of them had none).
- prepr.sh's self-test fixtures read main's own pin form (the cherry-picked fixture used part 2's form, which is absent on main, and so tripped `assert t != s`). They also drive each of the four sources through the "both" reader and the restore source through the PR-only callee reader, and assert that a foreign input leading the pin stays refused with step 3e's run present.

Code-owned paths (`tools/pr/prepr.sh`, `dev/audit/`): this merges on a tvofi review or a mandate in force.

PART 2 IS OWED. The workflow fix is 4f9fc83dc7, 5ab1c861c8 and 033d619595, plus the harness `dev/audit/harnesses/r10_restore_base_skew.py`, all on handoff-wip/r10-hotfix-restore-base-skew, which is left in place. It lands as topic r10-hotfix-restore-base-skew-p2, taken onto the then-current origin/main, only after this pull request has MERGED. This pull request alone does not fix the base skew. Part 2 starts from handoff-wip/r10-hotfix-restore-base-skew (tip 1cb96d4430); the blocked note there records the self-test as 58 probe(s), 17 null(s), which this head's 19 nulls supersede, so the part-2 fixer re-takes that figure.

The group's two roster carries are answered by part 2, not here. Both act on the restore-skew census in tests/entities.py, which arrives with 5ab1c861c8 and is not in this diff (`git diff a7628041dc...5ec2425619 -- tests/` is empty). Carry 1 (e41acc16) is the `tests.yml` `mutation-pins` seam: a payload-base blob written into the checkout by `git show "<event base>":<path> >`. Its control is a planted `git show "$PR_BASE":x > y` under an env reading `github.event.pull_request.base.sha`, which the census must refuse. Carry 2 (530feedf) is the census arm's cost: a median 1.98 s per entities.py run, against 0.222 s with the parse cached by text. Part 2 builds both and re-measures them at its own head.

## Head

5ec2425619, merge base and origin/main a7628041dc (re-fetched 2026-11-11 06:12 UTC). No commit on main since the cut, so no merge commit was made.

## Mutation proof

Each mutant was applied by hand to a copy of the file at the head (the specs are below). KILLED means the file's own self-test fails.

codeowners_gap.py (`python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --self-test`):
- KILLED  M1 admission off (`or bool(source) and` -> `or False and`, the exact-set test): `SELF-TEST: 58 probe(s), 19 null(s), 4 wrong`
- KILLED  M2 any input leads (`inputs\.restore_source` -> `inputs\.\w+`): `1 wrong`
- KILLED  M3 gate alternative dropped (`(?:prelude|gate)` -> `(?:prelude)`): `1 wrong`
- KILLED  M4 step alternative dropped (`|steps\.source\.outputs\.sha` removed): `1 wrong`
- KILLED  M5 separator not required (` \|\| ` removed from PINNED_SOURCE): `4 wrong`
- SURVIVED NULL (`bool(source) and` -> `source is not None and`): `0 wrong`

prepr.sh PIN_AWK (`bash tools/pr/prepr.sh --self-test`, each run in its own worktree):
- KILLED  PM1 source group dropped from the "both" regex: rc=2, `FAIL governance.yml perturbed (restore-input|restore-prelude|restore-gate|restore-step), with step 3e's run present, passes (null control) (got 1, wanted 0)`
- KILLED  PM2 source group dropped from the "pr" regex: rc=2, `526 passed, 1 failed`, `FAIL and led by the restore source ci.yml's prelude resolves, it is still that class`
- KILLED  PM3 `inputs\.restore_source` -> `inputs\.[a-z_]+` in both: rc=2, `525 passed, 2 failed`, `FAIL and led by any other input, it stays unclassified (null control)` and `FAIL governance.yml perturbed (foreign-source), with step 3e's run present, is still refused (got 0, wanted 1)`
- KILLED  PM4 `needs\.(prelude|gate)` -> `needs\.(prelude)` in "both": rc=2, `526 passed, 1 failed` (restore-gate)
- KILLED  PM5 `|steps\.source\.outputs\.sha` dropped from "both": rc=2, `526 passed, 1 failed` (restore-step)
- SURVIVED NULL `(prelude|gate)` -> `(gate|prelude)` in both: rc=0, `527 passed, 0 failed`

Test first: with main's copies, the new form is refused. Main's prepr.sh pin reader, run over main's workflows with one governance.yml `PINNED:` led by `inputs.restore_source`, prints `unclassified .../governance.yml:policy-docs` and `verdict_rc=1`; the head's copy prints `verdict_rc=0`. Main's codeowners_gap.py has none of the new nulls (`SELF-TEST: 55 probe(s), 15 null(s), 0 wrong`), and M1 at the head reproduces its exact-set test.

## Null control

INERT on main: no workflow on main uses the new form. Graded by the base's copy and by the head's copy, main's workflows read identically:
- `codeowners_gap.py --check`: both copies print `rc=0`, `RESULT enforcement_surface_files=206`, `covered_by_an_owner=68`, `pinned_by_base_restore=138`, `of_which_no_pr_job_runs=119`, `uncovered_files=0`, and the two RESULT blocks diff empty.
- prepr.sh's pinned-graders read: `pin_read graders|paths|problems` plus `pinned_verdict` over `.github/workflows/*.yml`, with main's and the head's PIN_AWK. The two 81-line outputs are byte-identical (`cmp` exit 0), and both end `verdict_rc=0`.

The admission must still refuse other forms, and it does: `PINNED from the head ahead of the restore source`, `PINNED from the restore source, else the head` and `PINNED from another input ahead of the base` are probes, all refused at the head. prepr.sh's foreign-source perturbation (`inputs.head ||` leading) is refused with 3e's run present.

## Figures

- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --self-test` at the head: `SELF-TEST: 58 probe(s), 19 null(s), 0 wrong`
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` at the head: `RESULT uncovered_files=0 count`
- `bash tools/pr/prepr.sh --self-test` at 5ec2425619: exit 0, 527 `ok` lines
- `python3 tests/closure.py select --diff a7628041dc`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/harness_headers.py)
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2707 ENTITY CHECKS PASSED`
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`

## Red checks

none

## Forward-carry

- tests/entities.py's two `gate lease priority` checks ("an urgent waiter takes before an older normal one, after its ticket rewrite" and "the heavy-slot pool orders by the same rule") inherit the caller's `HPO_GATE_PRIORITY`. prepr.sh exports it, and on a hotfix branch exports 2, so step 6b's local recording of entities.py fails there. Measured at this head: `HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py` prints `2 of 2707 ENTITY CHECKS FAILED` with `order=['normal', 'urgent']`; the null control with `HPO_GATE_PRIORITY=0` prints `ALL 2707 ENTITY CHECKS PASSED`. This pull request does not touch entities.py, so the clean prepr.sh run below was taken with `HPO_GATE_PRIORITY=0` in its environment. The check should pin its own waiters' priority rather than read the caller's. Carry: R10-PROCESS-SLIM

## Friction

none
