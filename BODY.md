R10-FLY-OPENPR-ATOMIC (#2719, fly-in, lane F). `open_pr.sh` creates the PR on its first push (p1) and pushes the PR's own delivery row on its second (p2). When any step after p1 failed, the PR stayed open with no row. Now, once `N` is known, the EXIT trap runs `op_close_unrowed` first. This covers every exit before `PR_ATTEMPT=opened`: a refused row push, a step errexit stops (the title edit, `commit_row`, the head note), or a stop signal. That single path reaps the row push, returns the opener's worktree to the pushed head, and closes the draft. Only after the close succeeds does it post a comment, read back by `tools/pr/gh_comment.py`, that quotes the refusal or the `STOPPED` line (`open_pr: CLOSED: #N`). A close that fails prints `ROWLESS` and posts no comment, so `update_pr.sh`'s `ensure_row` can add the row later. The refused-row-push branch now only sets `OP_WHY` and exits; the old inline close is gone, so there is no second copy. `pr_args.sh`'s `pr_stopped` keeps its report in `PR_STOPPED_AT`, and the close quotes it. A conflicted `origin/main` merge is aborted and refused, so `pr_release_wt` removes the clean worktree.

Carries (roster group R10-FLY-OPENPR-ATOMIC, numbered as `review_packet.py` numbers them):
- Carry 1 (#2625/#2629, the rowless PR): closed in this diff, for every exit after the PR exists rather than only a refused row push. The self-test replays a refused row push, a failing title edit, and a row push that lands and then fails.
- Carry 2 (P-D, the exit-trap release): already on main (`pr_exit_trap` with `PR_TIDY` = `pr_release_wt`) and unchanged. `op_close_unrowed` runs before it in the same trap.
- Carry 3 (detach as the opener's last step): already on main. `pr_release_wt` runs in the EXIT trap after the last push, and this diff adds no push after it.
- Carry 4 (P71, default the Closes list from roster `fixes`): not in this diff. It needs `roster_lib` at the default ref inside the opener and can be done separately, so it stays on the roster.
- Carry 5 (P72, remove a clean worktree origin never had on REFUSE/STOPPED): already on main (`pr_release_wt`'s remove arm). This diff's merge-conflict arm exercises it.
- Carry 6 (V64, auto-open in `cloud_relay.sh`): not in this diff. It edits `cloud_relay.sh`, which is outside this group's files, and stays on the roster.
- Carry 7 (V141, delete a merged leftover branch): not in this diff. It touches `pr_args.sh`'s helper and `handoff_push.sh`, and stays on the roster. Until it lands, a re-run after a close opens from `fix/<topic>-pr`.
- Carry 8 (a conflicted main merge kept as dirty work): closed for `open_pr.sh`. The opener aborts its own conflicted merge and refuses. The `handoff_push.sh` seams are outside the group and stay on the roster.

## Re-cut

The row push can fail after its own `git push` has landed. `app_push.sh`'s `push_and_open` refuses a body PATCH or a read-back only after it has pushed, and a stop signal can arrive past the push. So, when `H` (the row commit) is set, `op_close_unrowed` first reads origin's branch tip with `git ls-remote`. It closes `#N` only when that tip is readable and is not `H`. When origin's tip is `H`, `#N` keeps its row and stays open. The run then exits non-zero and prints `open_pr: ROW LANDED: #N has its row on origin at <H>, but the row push then failed (exit status <rc>); #N is left open: <why>` (`op_row_landed`). A tip that cannot be read does not count as absent either, so `#N` is left open there too, with a `ROWLESS` line saying origin was not read.

## Re-cut

The body was replaced at round four (fixer.md, "Past three rounds"). The round-five review at `a11db7fe` was blocked: a row push that landed on origin and then failed closed a PR that had its row, with a comment saying the row was never pushed. That is closed here. Every figure below was re-taken in this pass.

## Re-cut

Round six repairs the red that round four's change caused. That change replaced the literal `pr_exit_trap 'python3 -I "$SEAT/ledger.py" attempt ...'` line with an `OP_LEDGER` variable. `ledger.py --self-test` builds its TERM fixture from the `open_pr.sh` lines that start with that literal, so it found only the `started` line. `r10_ledger_mutants.py`'s plant `O1_no_attempt_on_exit` anchors on the same literal, which then occurred zero times. The line is literal again. `pr_exit_trap` (`pr_args.sh`) now keeps its command in `PR_EXIT_FIRST`, and the second registration, made once `N` is known, is `pr_exit_trap "op_close_unrowed; $PR_EXIT_FIRST"`. So the opener has one attempt line on each exit path, and the O1 anchor occurs once. No ledger test was changed.

## Head

`ba4a8320b652db32dd5ecf3bede0e74c80417e40`: one commit on `083905bdf9650faf4743dbde95f991aac5fc78bd` (round five's handoff), which is one commit on `a11db7fea14bc34633eb65e8111a207142eb45ab`. The merge base with origin/main is `1afdef8872a5da2eedff32916c1095e114198fae`. `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main `e77418f9b48f89421bd72b0ab511c057341c7fa4` (2026-10-30T14:21:44Z).

## Mutation proof

These are in-tree mutants in `pr_args.sh`'s self-test (`bash tools/audit/seat/open_pr.sh --self-test`). Each one deletes its `# mut:<name>` line, and each prints `ok` at the head:
- `mut:roworigin` (new) deletes the line in `op_close_unrowed` that compares origin's tip with `H`. The arm is `mutant mut:roworigin (its line deleted): the PR whose row is on origin is closed as rowless (the defect)`.
- `mut:trapclose` deletes the line that registers `op_close_unrowed` in the EXIT trap once `N` is known. The arm is `mutant mut:trapclose (its line deleted): a failing title edit leaves the PR open, unclosed and without its row (the defect)`.
- `mut:rowclose` deletes the `gh pr close` line. The arm is `mutant mut:rowclose (its line deleted): the PR stays open without its row (the defect), under no comment saying it closed; the next update_pr.sh lands it`.
- `mut:rowreset` and `mut:mergeabort` are unchanged.

Round six's mutants, each run at the head:
- `r10_ledger_mutants.py O1_no_attempt_on_exit` (it turns the exit trap's ledger line into a no-op) prints `RESULT mutant=O1_no_attempt_on_exit rc=1 fails=3`. The FAILs are `open_pr.sh carries both attempt lines`, `a TERMed opener records started then unopened on its handoff ref` and `null control: an opener that ends records opened,PR=<n>`. The summary is `plants: 1, without a FAIL line: none`.
- Deleting the new `PR_EXIT_FIRST=` line from `pr_args.sh` (`grep -v '^  PR_EXIT_FIRST='`) makes `bash tools/audit/seat/open_pr.sh --self-test` give rc=1 and `pr_args self-test: 158 checks, 8 failed`. The failures include the refused-row-push close, the title-edit errexit close and the row-landed arm. Restored, it gives `158 checks, 0 failed`.
- Deleting the `# mut:trapclose` line, which is now `pr_exit_trap "op_close_unrowed; $PR_EXIT_FIRST"`, gives rc=1 and `158 checks, 5 failed`, including `a step errexit stops after the PR exists (its title edit) closes it with a read-back comment naming the stop`.

Red, then green restored, for `mut:roworigin`, re-run at the head in this pass. The head's tree with the `# mut:roworigin` line deleted from `open_pr.sh` itself (`grep -v '# mut:roworigin$'`) gives `pr_args self-test: 158 checks, 1 failed` and rc=1. The FAIL is `open_pr: a row push that lands on origin and then fails leaves the PR open with its row, and says so`. With the line restored, the run gives `158 checks, 0 failed` and rc=0.

Failing test first. The round-five arms, run in this pass with `open_pr.sh` taken from `a11db7fe`, give `pr_args self-test: 158 checks, 1 failed` and rc=1. The FAIL is the same post-push arm. That is the review's probe (`ev/probe-postpush-close.diff`) made an in-tree arm: the stub's call 2 pushes the row and then exits 1 with the body-PATCH refusal text (the `p2postfail` flag).

## Null control

`python3 -I tools/audit/seat/r10_ledger_mutants.py --null` (no plant) prints `rc=0 fails=0` for each owner it runs: bus.sh, cloud_relay.sh, ledger.py and orchestrator_tick.py. The ledger checks the O1 plant turns red are green at the merge base `1afdef88` (`ledger self-test: 77 checks, 0 failed`; `r10_ledger_mutants self-test: 135 checks, 0 failed`), so the red was this branch's own.

The rowless arm (`rowless -`: the stub refuses before it pushes, so origin's tip stays at p1, not `H`) still asserts `closed=1`, the read-back comment and `rowpushed=0`, and prints `ok`: `open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree`. The origin check therefore does not keep a rowless PR open. The success path (`racerun -`) still lands the row, detaches the worktree, and closes nothing; its two arms print `ok`. The new arm asserts `closed=0`, `commented=0`, `rowpushed=1`, rc≠0, the `ROW LANDED` line quoting `body PATCH on #5 was refused`, no `CLOSED` line, and a detached worktree. Under `mut:roworigin` the same scenario closes (`closed=1`, `open_pr: CLOSED: #5 at`), which is what the mutant arm asserts.

## Figures

- The brief's two self-tests (`python3 -I tools/audit/seat/ledger.py --self-test`, `python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test`). At `083905bd` they give `77 checks, 3 failed` and `135 checks, 1 failed`, with the four FAILs the CI job printed at `a11db7fe`. At the head they give `77 checks, 0 failed` and `135 checks, 0 failed`.
- The whole `instrument-self-tests` job, run locally at the head: each `run:` step of the job in `.github/workflows/governance.yml` was executed in order with `bash -e -c` and `RUNNER_TEMP` set. The job has 89 such steps, counted as the steps carrying a `run:` key by `yaml.safe_load`. All 89 exited 0, and none failed. The run was made in two passes, steps 0-69 and then 70 onward, because a background time limit stopped the first pass after step 69. The tree was unchanged between the passes (`git status --porcelain` empty). Null control: the same runner records a non-zero exit as FAIL. The same two self-tests at `083905bd`, above, are the failure it would have recorded there.
- Self-test at the head: `bash tools/audit/seat/open_pr.sh --self-test` exits 0. It prints `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 158 checks, 0 failed`. `grep -c '^  ok'` of that output gives 164: 158 plus delivery_row's 6. At `a11db7fe` the reviewer measured 156 and 162. The two new checks are the post-push arm and its `mut:roworigin` mutant. Null control for the count: the red runs below print 163 `ok` lines, because one check is a FAIL.
- The same self-test with `open_pr.sh` from `a11db7fe`: rc=1, `158 checks, 1 failed` (named above).
- The same self-test with the `# mut:roworigin` line deleted: rc=1, `158 checks, 1 failed` (named above).
- Class seams, part one: the exits between the PR's existence and its row. The rule is `awk '/^N=\$\(grep/{f=1} f{print NR": "$0} f&&/^PR_ATTEMPT=opened/{exit}' tools/audit/seat/open_pr.sh`, which prints lines 120-141. Disposition of each:
  - The `N=` assignment (120): no PR number yet, and it runs before the trap that closes.
  - The trap registration (121), which now chains `op_close_unrowed` before `$PR_EXIT_FIRST`, the ledger line.
  - The title edit (122), `commit_row` (123), `H=` (124), the head-note prefix (125-130), `RO=` (131), the row push and its wait (132-133), and the refusal branch (134-139): each exits through the EXIT trap and so through `op_close_unrowed`. Before `H` is set (122-123), no row exists, so the PR closes. From 124 on, the PR closes only when origin's tip is readable and is not `H`. These are closed in this diff.
  - `PR_PUSHED=$H` (140) and the marker (141): the row has been pushed by then.
  - A stop signal anywhere in that range runs the same EXIT trap (`pr_exit_trap`: TERM, INT and HUP included). `pr_reap` ends an interrupted row push before origin is read.
- Class seams, part two: the review's seam, a row push that exits non-zero after its `git push` succeeded. The rule enumerates every refusal in `app_push.sh`'s `push_and_open` after the `push_rc` check, plus `confirm_readback`'s: `{ awk '/\[ "\$push_rc" = 0 \]/{f=1;next} f&&/^}/{exit} f&&/die "/{print "app_push.sh:"NR}' tools/pr/app_push.sh; awk '/^confirm_readback\(\)/{f=1} f&&/^}/{exit} f&&/die "/{print "app_push.sh:"NR" (confirm_readback)"}' tools/pr/app_push.sh; }`. It returns 8 sites at the head, unchanged: 537, 541, 545, 548 and `confirm_readback`'s 350, 351, 364, 366. Disposition: each is closed in this diff. The close keys on origin's tip, not on which refusal fired, so any exit after the push leaves the PR open when origin holds `H`. The self-test drives 548, the body-PATCH refusal. 537 and 541 (the POST path) are not reached under `--row-only`, because the PR already exists. A stop signal past the push is the same seam and is covered by the same tip read. The one case left unproven: a tip that cannot be read leaves the PR open with a `ROWLESS` line, and no arm drives it.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, and `scope.run` is empty.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and the golden and claim files: `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION RELEASE_NOTES.md tests/golden` prints nothing.

## Unpinned sites

- The unreadable-tip branch (`tip=unread`) in `op_close_unrowed`, and its `ROWLESS` message in `op_row_landed`: no arm drives an `ls-remote` failure. That branch only leaves the PR open and exits non-zero; it never closes. A `tools/` site needs an in-tree mutant harness, and none is added for it here.

## Red checks

- `governance / instrument-self-tests` at `a11db7fea14bc34633eb65e8111a207142eb45ab`: red. The job log printed `ledger self-test: 77 checks, 3 failed` and `r10_ledger_mutants self-test: 135 checks, 1 failed`. Re-measured at `083905bd` above, with the same four FAILs.
  - Cause: round four's `open_pr.sh` change moved the exit trap's ledger command into `OP_LEDGER`. `ledger.py` reads `open_pr.sh`'s text and keys on the literal `pr_exit_trap 'python3 ...` line, and so does the O1 plant. The opener's own self-test passed, because it does not read that line.
  - Answer: the literal line is restored, and the close is chained through `PR_EXIT_FIRST` (see the third Re-cut). Both self-tests give 0 failed at the head, as does the whole job (Figures).
  - Cheaper detector: these local self-tests, which run in seconds. Neither the scoped gate (`MODE: SCOPED -- 0 script(s) run`; `tests/closures.json` does not map seat scripts to the governance self-tests that read them) nor `prepr.sh`'s instrument predict ran `ledger.py --self-test` or `r10_ledger_mutants.py --self-test` for a diff to `open_pr.sh`. Process state: (a). No local step maps a changed seat script to the instrument self-tests that read its text. The countermeasure and its cost test belong to a root-cause seat (`defect-root-cause.md`), not to this fix. None is built here.

## Forward-carry

none

## Friction

none
