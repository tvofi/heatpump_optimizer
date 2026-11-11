Rides out four GitHub-read residues left after #3361: the App push, the #201 comment guard on a second checkout, a partial re-run's carried-over CodeQL jobs, and the ci-ratchet gather. Closes none; Carries 1-4 of R10-GH-READ-RESIDUE (roster numbering, from 1). Carry 5 is part 2 and is not built here (P549, merge_train.py page= reads); any later PART 2 ITEM is likewise out of this part.

## Head

Repair round on the review's blocked verdict (M2b, M3b). Head measured: 2ca01646b7de3856de2e19c2301489db48134436; the previous head was 7cbfa680134ea1ddb34d202ef1ab11e0efb93807.

## Mutation proof

- Carry 3: making `carried_over` return False in tools/ci/codescan_wait.py turns `codescan_wait.py --self-test` red on "21 carried-over step-less success jobs are settled and all legs uploaded" (1 failed of 24); restored.
- Carry 1: tools/pr/app_push.sh --self-test arm "a push that fails once on a 502 still lands" and "the push was tried twice" fail if the push goes straight to git (the stub push-flaky marker then refuses the first push and the script exits non-zero).
- Carry 2: gh_calls.py --self-test carries its own mutant "the worktree registration dropped lets an unlisted clone through" (killed: rc 7 only under the mutant).
- Carry 4: tests/ci_ratchet.py --self-test arm "one injected 502 on a jobs listing still gathers" fails if `api` makes a single read (the first jobs read raises the refusal).

### Repair round: surviving mutants M2b and M3b

- M2b (Carry 2, seat-gh `ls-files --error-unmatch` tracked check replaced by `true`): new arm t5, a registered worktree of the baked tree whose tools/pr/gh_comment.py is `git rm --cached` (untracked, still on disk), must stay refused. Mutant applied to tools/audit/seat/shims/seat-gh: `gh_calls.py --self-test` prints `FAIL second tree: null control: a registered worktree whose script is not tracked` and `gh_calls self-test: 206 checks, 2 failed` (the t5 shim run returns rc 7 instead of 1; the in-test mutant arm fails with it). Restored: `206 checks, 0 failed`.
- M3b (Carry 3, ` and "steps" not in j` dropped from `carried_over`): new arm 23b, completed/success jobs with `steps: []` and with a lagging `steps` row (conclusion null) must be unsettled and upload no leg. Mutant applied: `codescan_wait self-test: 25 checks, 1 failed` (23b red). Restored: `25 checks, 0 failed`.
- M4c (ci_ratchet empty-stdout branch, pre-existing, moved verbatim): not pinned here; dismissed in the review as a follow-up, not introduced by this PR.

## Null control

- Carry 3 (re-measure of the brief's listing): three CODEQL jobs completed/success with no steps key gave settled() False and legs_uploaded() [] at base; arms 22-24 pin the controls: a step-less non-success job, a lagging step row (steps present, conclusion null) and an in-progress step-less job all stay unsettled.
- Carry 2: a clone git does not list beside the baked tree, and an untracked file of the same path, are still refused; the existing spoof/basename/symlink arms are unchanged and green.
- Carry 4: a 404 refuses after one read with no sleep; a sustained 502 refuses after the read rule's 4 reads (3 sleeps).
- Carry 1: a refused push (non-transient wording) is tried once.

## Figures

- `bash tools/pr/app_push.sh --self-test` (instrument: its own check count line)
- `python3 -I tools/ci/codescan_wait.py --self-test`, `python3 -I tools/audit/seat/gh_calls.py --self-test`, `bash tools/audit/seat/seat_venv.sh --self-test`, `PYTHONPATH=tests/hastub python3 -I tests/ci_ratchet.py --self-test`: each prints its own "N checks, 0 failed" line, green at the head.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints MODE: FULL (a gate file is in the diff); CI runs it.
- Instance count for carry 3 at the merge base was not re-measured from tests.yml push runs here: no GitHub API read of Actions was made in this seat. The brief's two instances (96346fdec3, 45adb0c3b4) stand as stated.

## Red checks

none

## Forward-carry

- Carry 2's "install reaches every daemon PATH" half is not built: no tracked code puts the seat bin dir on tick_loop, cloud_relay or the opener driver's PATH (daemonize.py --path-prepend callers not found); the guard now admits a second registered worktree's script, but who installs the shim onto those PATHs is outside the tree and unmeasured here. Carry: dismissed: no tracked caller exists to change and the seat's launch environment is not in the tree; the next daemon-PATH audit reads the install, not this guard
- "Registered seat root" was read as: a git worktree listed by the baked tree (`git worktree list --porcelain`) whose tools/pr/gh_comment.py is tracked. A separate clone is refused. If the owner wants separate clones admitted, that is a policy call. Carry: dismissed: the choice is recorded in the shim comment at the admit block and pinned by the t3 null control, so the owner's reversal is one arm


## Friction

none
