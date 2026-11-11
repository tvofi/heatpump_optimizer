Rides out four GitHub-read residues left after #3361: the App push, the #201 comment guard on a second checkout, a partial re-run's carried-over CodeQL jobs, and the ci-ratchet gather. Closes none; Carries 1-4 of R10-GH-READ-RESIDUE (roster numbering, from 1). Roster Carry 5 (P549, merge_train.py page= reads) is not built: its own text leaves it to the group's next part once this fixer is past handoff, and this brief was rendered before it.

## Head

Measured at the head of handoff/r10-gh-read-residue; base 45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6 (the dispatch base). b660583bb17f721662bec4c89807c16b1614e15e

## Mutation proof

- Carry 3: making `carried_over` return False in tools/ci/codescan_wait.py turns `codescan_wait.py --self-test` red on "21 carried-over step-less success jobs are settled and all legs uploaded" (1 failed of 24); restored.
- Carry 1: tools/pr/app_push.sh --self-test arm "a push that fails once on a 502 still lands" and "the push was tried twice" fail if the push goes straight to git (the stub push-flaky marker then refuses the first push and the script exits non-zero).
- Carry 2: gh_calls.py --self-test carries its own mutant "the worktree registration dropped lets an unlisted clone through" (killed: rc 7 only under the mutant).
- Carry 4: tests/ci_ratchet.py --self-test arm "one injected 502 on a jobs listing still gathers" fails if `api` makes a single read (the first jobs read raises the refusal).

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
