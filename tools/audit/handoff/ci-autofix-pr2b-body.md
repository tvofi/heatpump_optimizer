<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: when `mutation` refused a pull request with "N unpinned site(s) against M at the ratchet base", nothing repaired it. A seat had to run `--pin-killed` itself, commit the ledger and push again, so every such refusal cost a full red cycle and a manual step.

After: a third autofix job, `mutation-autofix`, pins the kills for it. When `mutation` refuses on unpinned sites, the same job measures which of the new sites a driver kills and uploads only those `killed_by` entries. `mutation-autofix` then writes them into the pull request's ledger and pushes `ci: pin killed mutants`, the way `closures-autofix` and `claims-autofix` already push theirs. Survivors are never written. They stay unpinned and the lane stays red for a seat, and the job's summary line says so.

This stacks on #1594, the `--pin-killed` pull request, including its review fix (an anchor is pinned only when every site under it died), and merges after it.

How:
- **Measuring, without a write grant:** a step in the `mutation` job runs only on a ratchet refusal on a same-repo pull request. It runs the **base's** copy of `tests/mutation_table.py` with `--pin-killed`, so a pull request that edits the tool cannot write its own kills. The drivers are the pull request's code, so they run only in this read-only job, never beside a token that can push.
- **Carrying entries, not the file:** the checkout is the merge ref, so the artifact `mutation-pins` holds just the `killed_by` entries the run added, plus a status file.
- **Applying:** `mutation_table.apply_pins` keeps an entry only where the head's inventory has the same anchor and the same `old` text and no disposition yet, then writes through `normalize`. Its statuses are graded by `closure.AUTOFIX_QUIET`: `changed`, `skip-not-allowed`, `skip-not-unpinned` and `skip-nothing-killed` stay green. `skip-no-measurement`, `skip-no-base-program` and `skip-unchanged` redden, and the remedy printed tells the seat to run `--pin-killed` itself.
- **Loop guard and held runs:** the same `closure.autofix_allowed` subject guard, dispatch and held-run approval as the other two jobs. `policy_lint.mjs`'s `AUTOFIX_BOT_COMMITS` accepts the new commit on top of `## Head`, limited to `tests/mutation_budgets.json`.
- **Policy:** `.claude/rules/ci-autofix.md` said "add no third job". It now lists `mutation-autofix` in its table and says survivor triage is never automated. The `CLAUDE.md` index row follows, and `.cursor/rules/ci-autofix.mdc` is regenerated. The rule stays inside its line cap, which `policy_lint.mjs --budgets` prints.
- **Pins:** `tests/entities.py` pins `apply_pins` across every status it returns, and the job in the existing autofix-job loops, the commit-subject loop and the permissions census (now four jobs).

## Approval

This is a policy change. tvofi asked for the CI autofix candidates in the project thread on 2026-09-24 ("do 1-4"), and this job is candidate 2's CI half. Under tvofi's mandate to 2026-09-25T08:40Z, the fix thread may approve it as tvofi after a merge verdict and green CI. tvofi also chose this option ("Add the CI job") on the thread's decision card.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`664248ded9b4a998a52b77d722752432f864d8fa`

The code is at this commit. The handoff commit after it only carries this body. The full gate at this commit printed `ALL TEST SCRIPTS PASSED` (MODE: FULL, because the diff touches `tests.yml`).

## Mutation proof

Each of these turned `tests/entities.py` red with `FAIL mutation-autofix applies only a measured pin whose anchor and text this tree still has`, `1 of 1875 ENTITY CHECKS FAILED`. Restored, it printed `ALL 1875 ENTITY CHECKS PASSED`.
- `apply_pins` accepting an entry whose `old` text differs from the head's site;
- `apply_pins` returning `changed` when it added nothing;
- `apply_pins` flattening every non-`measured` status to one value.

## Null control

On the unmodified tree, with no measurement present, `apply_pins` returns `skip-no-measurement` and `tests/mutation_budgets.json` is byte-identical afterwards. The entities pin also feeds it a stale entry (same anchor, different `old` text) and an entry for an anchor the tree does not have; both are refused with `skip-unchanged`. A second apply of the same fresh pin is `skip-unchanged` too.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
