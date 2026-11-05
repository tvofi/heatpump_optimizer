R10-BODY-CONTRACT: the body contract at the head (V115), roster ref, review trailers, fold grammar, closed-destination refusal, dismissal pointer and the refused-body keep. Four carries are not built; each is named under Forward-carry.

## Head

`5471917b846176500a023b1e9816afd5e4416bd3`, with origin/main `6125b263d94e7ea8c43d31eb483869f8d8c83019` merged (taken `date -u` 2026-11-05); `tools/pr/prepr.sh` was rerun after that merge.

## Mutation proof

Each item was red first on the unchanged code where the arm can be red there, and each has a mutant that turns its arm red:
- V115 tree revision: dropping `BRIEF_LINT_TREE_REV=$head` (the sed mutant on the `# mut:contract` line) fails the `treerev` assertion in `body_patch.sh --self-test`; `assertTreeRev` in `brief_lint.mjs` fails if the revision is ignored.
- Roster ref: removing the argument (`# mut:rosterref`) fails "carry_audit check --body runs ... at the freshly fetched round roster branch" and the fetch-refusal arm.
- Trailers: deleting the new alternation fails `TRAILER reads 'Round: 3'` and `TRAILER reads 'bus-nonce: abc123'` (red on the base too).
- Dismissal pointer: forcing the pointer branch off fails `Carry: <done group> | dismissed: <reason> routes`.
- Closed destination: testing against `DONE_STAGES` instead of `roster_lib.CARRY_CLOSED` turns the absorbed-group arm red; listing every live group instead of the after-edged ones turns both closed-group arms red.
- Fold grammar: disabling the unanswered-fold test fails the "(a)-(d) answered, (e) named" arm first (red on the base too, which is the defect).
- Keep ref: replacing the `# mut:keep` calls leaves nothing at `handoff-wip/<topic>-body` and fails all four refusal arms.

## Null control

- V115: a path the head deletes refuses with the revision set; the first-commit listing in `assertTreeRev` is the opposite-direction control and the checkout listing must differ from the head listing.
- Folds: all five answered (built / Carry: / dismissed:) is accepted; an issue with no `Fold (x):` line is accepted unchanged; `Fold (e): dismissed:` with no reason is refused; free prose without the prefix is not counted.
- Dismissal: `Carry: <done group>` alone is still refused; an unknown token with `| dismissed:` is refused.
- Closed destination: a live after-edged group and a not-yet-started group are accepted as before.
- Keep ref: a successful push publishes `handoff-body/<topic>` and leaves no keep ref; a refused body is not in the code head's ancestry.
- Roster ref: in `carry_audit.py --self-test` the worktree-only carry arm passes on the unchanged code; it pins existing behaviour and was never red.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test | tail -1` (carry_audit self-test; the count is its own line)
- `bash tools/audit/seat/body_patch.sh --self-test | tail -1`
- `bash tools/audit/seat/body_push.sh --self-test | tail -1` (new self-test, wired in `governance.yml` beside body_patch's)
- `python3 tests/structure.py | tail -1` (ratchet passed; no budget raised)
- `node tools/policy/brief_lint.mjs; echo rc=$?` exits 0
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`: MODE: SCOPED. The scoped scripts named were not run beyond the self-tests above; CI is the authority.
- The finder's harness for V115 is #2852 (body fa8458d7 at head 6353b624, 2026-10-26); it was not re-run, and the in-tree `assertTreeRev` plus the `treerev` mutant stand in for it.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` OK; numpy and scipy match tests/requirements-ci.txt (`python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'`). No golden was touched; claim files are byte-identical to origin/main (prepr step).

## Red checks

`tools/pr/prepr.sh` leaves one REFUSE, `closures`: "failed while being recorded: tests/entities.py". `tests/entities.py` dies in this sandbox with `ModuleNotFoundError: No module named 'paho'` on this branch and on a detached origin/main worktree, so it is red on the base's ancestry (origin/main 6125b263) and not caused by this diff; the diff adds no tracked file. CI settles it. The cheaper detector is a toolchain refresh of the cached HA venv (cloud-setup.sh did not provide `paho`); none cheaper than CI exists for the closures table itself.

Earlier prepr refusals this branch caused and repaired: `instrument-self-tests UNWIRED body_push.sh` (the run line is now in governance.yml), and the throwaway-git check on two raw `git init` sites (now `throwaway_git_init`). Each was a local prepr refusal, not a CI red.

## Forward-carry

Not built, each waits and is owed by this group's continuation:
- Card 7, every body figure from a generated block: touches the PR template and `checkPrBody` (owner review at merge) and the body-only job. Not started. Carry: R10-BODY-CONTRACT
- brief_lint (i), lint a carry's `control` like a brief: built and then removed, because it failed 28 errors across 15 existing carry files (path-less or unresolvable controls, plus `carry-1795` below). Repairing those carries rewrites other groups' controls. Re-measure with `node tools/policy/brief_lint.mjs` at the merge base. Carry: R10-BODY-CONTRACT
- A1, `rosterIssues()` default reading `dev/programme/rosters`: built and removed. Measured with a node call to `rosterIssues()` with and without the directory, the default indexes 1 issue and the explicit directory 54. Enabling it refuses `carry-1795.json` because issue 1795 is covered by live group R9-UX-6 (`resume.stage: handoff`); resolving it means moving 1795's content into that group and deleting the carry file, an owner call. Carry: R10-BODY-CONTRACT
- A2, the orchestrator writing each `Carry: <GROUP>` item into the destination brief with a post-fold id assertion: not started. Carry: R10-BODY-CONTRACT
- Closed-destination arm (s9-opt-2b): `carry_audit.py check` now takes `--pr-group G` to list the live after-edged consumers, but `pr-contract.yml` does not pass it yet, so the refusal prints `unknown (no --pr-group)`. The roster has no stage called "closing"; `carries-open` is left accepted (it is the stage `closing_stage` writes to keep a group open). The brief renderer companion is R10-DISPATCH-AT-HANDOFF's. Carry: R10-DISPATCH-AT-HANDOFF
- Fold grammar scope: only the issue body is read, not its comments; `Fold (x): Carry:` is checked for a well-formed destination, not against the roster; wired into `check --body` only, not `pr`. Carry: R10-BODY-CONTRACT
- Hot files: `body_push.sh` is also edited by open PR #3221 (receipt trailer); this diff adds only new functions (`keep_refused`, `drop_keep`, the self-test) and one call per refusal path, so expect a merge-resolution round if #3221 lands first. Carry: R10-BODY-CONTRACT
- `cloud_dispatch.py` fixer prompt tail now allows `handoff-wip/<topic>-body` (4 changed lines). `ref_privacy.py` guards any ref and `prune_refs.py` classifies the ref as residue with no edit; the relay and bus globs never list `handoff-wip/`. Carry: dismissed: a recorded precondition check, nothing owed.

## Friction

- finding-propagation: unenforced: a roster-wide default (`rosterIssues()` with no argument) cannot be switched on while a carry collides with a live group, and nothing flags the collision until the default changes. Carry: R10-BODY-CONTRACT

## Brief carries by number

Numbered in the order the group brief lists them.
- Carry 1 (`--roster-ref` on the contract arm): built.
- Carry 2 (card 7, generated figure block): not built, under Forward-carry.
- Carry 3 (V115 body contract at the head): built.
- Carry 4 (`bus-nonce:` and `Round:` trailers): built.
- Carry 5 (`Fold (x):` grammar): built, scope limits under Forward-carry.
- Carry 6 (s9 closed-destination refusal): built, with `pr-contract.yml` not yet passing `--pr-group`, under Forward-carry.
- Carry 7 (`Carry: G | dismissed:` pointer): built.
- Carry 8 (A1 and A2): not built, under Forward-carry.
- Carry 9 (#2438 control lint): not built (built and removed), under Forward-carry; the `fix-review.md` and `judge.md` sentence (ii) was not written.
- Carry 10 (refused-body keep ref): built.
