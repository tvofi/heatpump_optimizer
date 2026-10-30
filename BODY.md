R10-FLY-OPENPR-ATOMIC (#2719, fly-in, lane F). `open_pr.sh` creates the PR on its first push (p1) and pushes the PR's own delivery row on its second (p2). When any step after p1 failed, the PR stayed open with no row. Now, once `N` is known, the EXIT trap runs `op_close_unrowed` first. This covers every exit before `PR_ATTEMPT=opened`: a refused row push, a step errexit stops (the title edit, `commit_row`, the head note), or a stop signal. That single path reaps the row push, returns the opener's worktree to the pushed head, and closes the draft. Only after the close succeeds does it post a comment, read back by `tools/pr/gh_comment.py`, that quotes the refusal or the `STOPPED` line (`open_pr: CLOSED: #N`). A close that fails prints `ROWLESS` and posts no comment, so `update_pr.sh`'s `ensure_row` can add the row later. The refused-row-push branch now only sets `OP_WHY` and exits; the old inline close is gone, so there is no second copy. `pr_args.sh`'s `pr_stopped` keeps its report in `PR_STOPPED_AT`, and the close quotes it. A conflicted `origin/main` merge is aborted and refused, so `pr_release_wt` removes the clean worktree.

Carries (roster group R10-FLY-OPENPR-ATOMIC, numbered as `review_packet.py` numbers them):
- Carry 1 (#2625/#2629, the rowless PR): closed in this diff, for every exit after the PR exists rather than only a refused row push. The self-test replays a refused row push and a failing title edit.
- Carry 2 (P-D, the exit-trap release): already on main (`pr_exit_trap` with `PR_TIDY` = `pr_release_wt`) and unchanged. `op_close_unrowed` runs before it in the same trap.
- Carry 3 (detach as the opener's last step): already on main. `pr_release_wt` runs in the EXIT trap after the last push, and this diff adds no push after it.
- Carry 4 (P71, default the Closes list from roster `fixes`): not in this diff. It needs `roster_lib` at the default ref inside the opener and can be done separately, so it stays on the roster.
- Carry 5 (P72, remove a clean worktree origin never had on REFUSE/STOPPED): already on main (`pr_release_wt`'s remove arm). This diff's merge-conflict arm exercises it.
- Carry 6 (V64, auto-open in `cloud_relay.sh`): not in this diff. It edits `cloud_relay.sh`, which is outside this group's files, and stays on the roster.
- Carry 7 (V141, delete a merged leftover branch): not in this diff. It touches `pr_args.sh`'s helper and `handoff_push.sh`, and stays on the roster. Until it lands, a re-run after a close opens from `fix/<topic>-pr`.
- Carry 8 (a conflicted main merge kept as dirty work): closed for `open_pr.sh`. The opener aborts its own conflicted merge and refuses. The `handoff_push.sh` seams are outside the group and stay on the roster.

## Re-cut

The body was replaced at round four (fixer.md, "Past three rounds"). The review at `50b19564` was blocked because a step failing between p1 and p2 left the PR open (`open_pr.sh` lines 80-87 at that head). Its finding was that the closing comment was posted before `gh pr close`. Both are closed here, through one EXIT-trap path. Every figure below was re-taken in this pass.

## Head

`4d6538d7fd65f9d268590e034b0aa2b4fbdb1c19`: one commit on `50b1956485ea01e78d97a0619a32cdc9dd923cdd`, merge base with origin/main `e8cb7e68302b1d350bb8219fea99e911170af030`.

## Mutation proof

These are in-tree mutants in `pr_args.sh`'s self-test (`bash tools/audit/seat/open_pr.sh --self-test`). Each one deletes its `# mut:<name>` line, and each prints `ok` at the head:
- `mut:trapclose` deletes the line that registers `op_close_unrowed` in the EXIT trap once `N` is known. The arm is `mutant mut:trapclose (its line deleted): a failing title edit leaves the PR open, unclosed and without its row (the defect)`.
- `mut:rowclose` deletes the `gh pr close` line. The arm is `mutant mut:rowclose (its line deleted): the PR stays open without its row (the defect), under no comment saying it closed; the next update_pr.sh lands it`. It now also asserts that no comment was posted, which pins the finding.
- `mut:rowreset` (the reset to the pushed head) and `mut:mergeabort` are unchanged.

Red, then green restored:
- The head's tree with the `# mut:trapclose` line deleted from `open_pr.sh` itself (`grep -v '# mut:trapclose$'`), run with `bash tools/audit/seat/open_pr.sh --self-test`, gives `pr_args self-test: 156 checks, 3 failed` and rc=1. The FAILs:
  - `open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree`. One path serves both triggers, so p2's close goes too.
  - `mutant mut:rowclose ...`
  - `open_pr: a step errexit stops after the PR exists (its title edit) closes it with a read-back comment naming the stop`
- Restored: the unmodified head gives `pr_args self-test: 156 checks, 0 failed` and rc=0.

Failing test first: the head's tree with `open_pr.sh` taken from `50b19564` gives `pr_args self-test: 156 checks, 2 failed` and rc=1. The two FAILs are the title-edit arm (the review's demo: the stub's `gh pr edit` exits 1, and the PR is left open and unclosed) and `mutant mut:rowclose ...`, which fails because the old code posted "Closed by open_pr.sh" before a close that then failed (the finding).

## Null control

At the head, the success path (`racerun -`) still lands the row and detaches the worktree, and no close happens. These arms pass: `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin` and `open_pr: a successful open leaves its worktree detached at the pushed head`. The guard `[ -z "${PR_ATTEMPT:-}" ] || return 0` is what keeps an opened PR open. The unmodified tree (`open_pr.sh` at `50b19564`) leaves the PR open after a failing title edit, as the FAIL above shows.

## Figures

- Self-test at the head: `bash tools/audit/seat/open_pr.sh --self-test` exits 0. It prints `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 156 checks, 0 failed`. `grep -c '^  ok'` of that output gives 162. At `50b19564` the reviewer measured 154 and 160. The two new checks are the title-edit arm and its `mut:trapclose` mutant.
- The same self-test with `open_pr.sh` from `50b19564`: rc=1, 2 failed (named above).
- The same self-test with the `# mut:trapclose` line deleted: rc=1, 3 failed (named above).
- Class seams. The rule that enumerates them is every top-level step from the assignment of `N` to `PR_ATTEMPT=opened`: `awk '/^N=\$\(grep/{f=1} f{print NR": "$0} f&&/^PR_ATTEMPT=opened/{exit}' tools/audit/seat/open_pr.sh`. The awk prints lines 103-124. Disposition of each:
  - The `N=` assignment (103): no PR number yet. It runs before the trap that closes, which is out of this group's class.
  - The trap registration (104).
  - The title edit and ready (105), `commit_row` (106), `H=` (107), the head-note prefix (108-113), `RO=` (114), the row push and its wait (115-116), and the refusal branch (117-122): each exits through the EXIT trap registered at 104, and so through `op_close_unrowed`. This is closed in this diff.
  - `PR_PUSHED=$H` (123) and the marker (124): the row has been pushed by then.
  - A stop signal anywhere in that range runs the same EXIT trap (`pr_exit_trap`'s contract: TERM, INT and HUP included). `op_close_unrowed` calls `pr_reap` before it closes, so an interrupted row push ends first.
  - The self-test drives two of these triggers: the refused row push and the failing title edit. The rest share the trap by construction and have no arm of their own.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none. No CI has run on `4d6538d7`. On `50b19564` the check-runs the review read showed no failure, and some were still in progress.

## Forward-carry

none

## Friction

none
