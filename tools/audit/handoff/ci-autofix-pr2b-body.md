<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: when `mutation` refused a pull request with "N unpinned site(s) against M at the ratchet base", nothing repaired it. A seat had to run `--pin-killed` itself, commit the ledger and push again, so every such refusal cost a full red cycle and a manual step.

After: a third autofix job, `mutation-autofix`, pins the kills for it. When `mutation` refuses on unpinned sites, the same job measures which of the new sites a driver kills and uploads only those `killed_by` entries. `mutation-autofix` then writes them into the pull request's ledger and pushes `ci: pin killed mutants`, the way `closures-autofix` and `claims-autofix` already push theirs. Survivors are never written: they stay unpinned, the lane stays red for a seat, and the job's summary line says so. A measurement that did not happen reddens the job instead of reading "nothing was killed".

How:
- **Measuring, without a write grant:** a step in the `mutation` job runs only on a ratchet refusal on a same-repo pull request. The measuring program is the **base's** copy of `tests/mutation_table.py`, run with `--pin-killed`, so a pull request that edits the tool cannot change how its own kills are measured. The status and the apply step are still this head's code, which is the trust every autofix job already extends. The drivers are the pull request's code, so they run only in this read-only job, never beside a token that can push. The base copy is listed in `.git/info/exclude`, so the worker overlay does not carry it into every driver's tree.
- **Grading the measurement:** `mutation_table.measurement()` reads the base program's own `PIN KILLED:` summary line, not the ledger diff alone. A red baseline (INCONCLUSIVE, rc 0), a refusal or a crash prints no summary and becomes `skip-measure-failed`; a summary that disagrees with the diff does too.
- **Carrying entries, not the file:** the checkout is the merge ref, so the artifact `mutation-pins` holds only the `killed_by` entries the run added, the status, and the pull request's head SHA.
- **Applying:** `mutation_table.apply_pins` refuses a measurement of any other head (`skip-head-moved`). It keeps an entry only where the head's inventory has the same anchor and the same `old` text and no disposition yet, and writes the ledger through `normalize`.
- **Grading the job:** `closure.AUTOFIX_QUIET` keeps `changed`, `skip-not-allowed`, `skip-not-unpinned`, `skip-nothing-killed` and `skip-head-moved` green. `skip-measure-failed`, `skip-nothing-drivable`, `skip-no-measurement`, `skip-no-base-program` and `skip-unchanged` redden, and the printed remedy tells the seat to run `--pin-killed` itself.
- **Loop guard and held runs:** the same `closure.autofix_allowed` subject guard, dispatch and held-run approval as the other two jobs. `policy_lint.mjs`'s `AUTOFIX_BOT_COMMITS` accepts the new commit on top of `## Head`, limited to `tests/mutation_budgets.json`. Its comment now says plainly that a forged pin commit is not re-checked: it can add a `killed_by` entry no run measured, exactly as a seat's own ledger edit can.
- **Policy:** `.claude/rules/ci-autofix.md` said "add no third job". It now lists `mutation-autofix` in its table and says survivor triage is never automated. It pays for that by condensing the failed-recording paragraph and shortening its own added lines, so the corpus stays inside its band (`policy_lint.mjs --budgets`). The `CLAUDE.md` index row, steward S1, `claim-files.md`, `tests/README.md`, `codeql.yml` and `nightly_status.py` stop saying "two jobs", and so do the comments in `tests.yml`, `closure.py` and `entities.py`. `.cursor/rules/*.mdc` is regenerated.
- **Pins:** `tests/entities.py` pins every status `measurement` and `apply_pins` return, the exact quiet row, and the workflow wiring (the base copy, the exclude, the `measurement(` call, the status write, the refusal grep, the pull request's head SHA recorded from `pull_request.head.sha` and compared against the checkout's own `git rev-parse HEAD`, both same-repo guards, `needs.mutation.result == 'failure'`, and the push grant only in `mutation-autofix`), and `mayAdd` on each autofix commit subject.

## Approval

This is a policy change. tvofi's approving review is owed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`HEADSHA`

## Mutation proof

Each mutant below turned `tests/entities.py` red. Unmutated, the tree printed `ALL 1908 ENTITY CHECKS PASSED`.
- `measurement`: the summary check removed; `"measured"` returned unconditionally; the `nothing to pin` arm removed.
- `apply_pins`: the head check removed; the `killed_by` presence check removed; `normalize` skipped; `ValueError` dropped from the unreadable-pins arm.
- `closure.AUTOFIX_QUIET`: `skip-measure-failed` added to the quiet row; `skip-head-moved` removed from it.
- `tests.yml`: the head's `mutation_table.py` copied instead of the base's; the `.git/info/exclude` line removed; the measure step's same-repo guard removed; `failure()` changed to `always()`; `needs.mutation.result == 'failure'` changed to `!= 'success'`; `apply_pins` handed `HEAD^`; the status write replaced by a constant `measured`; the refusal grep bypassed with `true ||`; the head recorded from `git rev-parse HEAD` (the merge ref); `PR_HEAD` taken from `github.sha`; `apply_pins` handed the recorded head instead of the checkout's.
- `policy_lint.mjs`: `mayAdd: false` on `ci: pin killed mutants`.

That is 21 of 21 killed.

## Null control

On the unmodified tree, `apply_pins` with no measurement returns `skip-no-measurement` and leaves `tests/mutation_budgets.json` byte-identical. The entities pin also feeds it a stale entry, an entry with no `killed_by` and an entry for an anchor the tree lacks, and refuses all three with `skip-unchanged`. A measurement of another head is `skip-head-moved` and writes nothing.

## Figures

End-to-end probe, the review's harness, run at `dc66cc87` (since then the measure and apply steps changed only in comments): a `git clone --shared` of that head with `origin/main` at main's `e0b83bbd`, plus a probe commit that rewrites two `repairs.py` guards without changing their meaning (one that `tests/features.py` killed at the base, one triaged equivalent), drops their two ledger entries, and adds a short full-line comment so a null control exists. The measure and apply steps were cut out of `tests.yml` and run with `RUNNER_TEMP` set.
- The lane printed `MUTATION TABLE REFUSED -- 3726 unpinned site(s) against 3724`.
- The measure step: 9 baselines green (entities included), the null control survived every driver, then `PIN KILLED: 1 pinned, 2 left unpinned` and `measure: measured, 1 anchor(s)`. `pins.json` holds the killed guard, `killed_by: tests/features.py`.
- The apply step on a fresh checkout of the probe head printed `AUTOFIX: changed`: 5 lines were added to `tests/mutation_budgets.json`, and the unpinned count fell to 3725 against 3724.
- The same pins applied after one more commit printed `AUTOFIX: skip-head-moved`.
- Before the fix, this probe ended INCONCLUSIVE with a green `skip-nothing-killed`. The same probe with no null control, and a run whose baseline was red because the clone's origin was a local path, now both end `skip-measure-failed`, and `closure.py autofix-report` exits 1 on that status.

## Red checks

- `policy-docs` is red at this head, inherited from main: after #1589 and #1592 merged, `codeowners_gap --check` reports `tests/delivery_status.py` and `tests/nightly_status.py` uncovered, and it still does on main `f5d4743b`. This branch edits one comment line in `tests/nightly_status.py`, but the check grades CODEOWNERS coverage, not file content, so the red is main's. The fix is #1604, which re-owns both; the detector is `codeowners_gap --check` on the merge result, and the root cause is answered in #1604.

## Forward-carry

none

## Friction

none
