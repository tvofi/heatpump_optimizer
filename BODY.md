A stopped pusher must not leave its work running, and no pusher, or launcher of one, may join the tree without the same guarantee.

A shell does not forward TERM, INT or HUP to a foreground child. So a stopped pusher exited, its subtree was reparented, and the subtree kept burning CPU. On 2026-10-20 six survivors were swept up, aged 26 to 62 minutes, on a box at load 77 on eight cores.

**The mechanism.** `tools/audit/seat/pr_args.sh`'s `pr_exit_trap [<command>]` sets one EXIT trap. It runs `<command>`, then `pr_reap`, then `$PR_AFTER_REAP`. bash runs an EXIT trap when TERM, INT or HUP ends the shell, as well as on every other exit. Each push or child runs asynchronously, and the shell `wait`s on it. An INT does not end a shell that is waiting on a foreground child, but all three signals interrupt `wait`. `pr_reap` walks `pgrep -P` from `$$` and TERMs each pid. It KILLs whatever outlives a 2 s grace (`# mut:grace`), and it ignores further stop signals while it runs (`# mut:sigign`). A runner whose child is itself a runner names that child `PR_REAP_LEAD`. `pr_reap` TERMs the lead alone first (`pr_lead_stop  # mut:lead`), but only when the walk returned it (`# mut:leadwalk`). It then waits up to `PR_REAP_LEAD_TENTHS` for the lead to stop its own tree in its own order. Every signal goes to a numeric pid that the walk returned, never to a pattern or a group, because on a shared box a group can hold other seats' processes.

**Seams closed in this diff:**
- The runners `open_pr.sh`, `update_pr.sh`, `handoff_push.sh`, `remerge_main.sh` and `tools/pr/app_push.sh` (its prepr and its own `git push`).
- The runner-py `merge_train.py`. `Train._run` TERMs its tool rather than SIGKILLing it, and `stop_on_signal()` makes a stop unwind.
- `train.sh`, with `merge_train.py` as its lead.
- `cloud_relay.sh`, with `update_pr.sh` as its lead. `update_pr.sh` holds the branch lock (`pr_branch_lock`, kept from main), and it frees that lock only after its own reap.

**This round** clears the review of `a01627177715`. That review found `cloud_relay.sh`'s production update launch unexercised: every relay arm took the `HPO_RELAY_UPDATE` stub's branch.
- The relay now picks its command and runs it from one backgrounded line, named `PR_REAP_LEAD`. The stub arms therefore run the production launch line.
- A new arm runs the production route with no stub. It copies the relay and the real `pr_args.sh` beside an `update_pr.sh` that is the lead stub.
- The same sweep, applied to every launch the body names, found two more gaps, and both are closed here:
  - `handoff_push.sh`'s new-PR route ran its asynchronous push inside `out=$(push_app 2)`. The shell waited on that command substitution in the foreground, so an INT waited behind the whole push. That was a defect this PR claimed to have removed, and the new INT arm caught it at the unmutated head. `push_app` now leaves its lines in `PUSH_OUT`, and the open route reads that variable.
  - Running the push or prepr in the foreground at `update_pr.sh`, `handoff_push.sh`, `remerge_main.sh` and `app_push.sh` was caught only by the census's text check, or, for app_push's prepr, by nothing. Each of the four now has an INT stop arm.
- Main's new `tools/pr/app_mint.sh`, merged here, restored, inside `mint_token`, the `trap mint_cleanup EXIT` and `trap 'exit 130' INT TERM HUP` that this PR removed from app_push.sh. After the mint they would replace the reap's EXIT trap, so a pusher stopped mid-push would wait behind the push and never reap it. The merge resolves it: app_push.sh sets `MINT_TRAP=caller` and its `pr_exit_trap` runs `mint_cleanup`, and `mint_token` installs its own traps only for a caller that does not own the EXIT trap, so `body_patch.sh` is unchanged. A new arm stops app_push mid-push, after the mint.
- app_push.sh's own `git push` ran in the foreground, so an INT waited behind it. It now runs asynchronously, as prepr does, and the mid-push arm runs under TERM and INT.
- The review's F-TR-RC finding is fixed rather than carried: a new train.sh arm pins that the child's exit status reaches `TRAIN_RC`, `$state/rc` and train.sh's own exit.

Part of #2502, which stays open when this PR merges. That issue's SIGKILL clause, and the Revision-12 self-test isolation that the roster puts on this group, are routed under `## Forward-carry`.

## Head

`db0d88377ff07d5c4d8eb45aadf1295951989783` is the code head, and everything below was measured there unless a line names another commit. origin/main was `543c8087c57973ee58033a0c62520b5ec3a58621`, read 2026-10-22T11:50:38Z, and it is this head's merge base.

This head is the reviewed head `a01627177715d6f363eee2f8add5b19f7a97945d` plus these commits, in order:
- `af7eb2d9a` adds the production-route arm and `dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh`. It leaves the reviewed head's two-branch launch unchanged, so the review's two mutants run there unchanged too.
- `788a882d7` makes the update one launch line.
- `68c54879a` merges origin/main `1602f934`. It touches only `dev/programme/delivery/` rows.
- `8cedc3328` records the harness in `tests/closures.json` (`ci_predict.py --apply-inert`).
- `078ce3d67` adds the harness's CR-FG-BOUND row.
- `41f9fc826` adds train.sh arm 8b (the exit status).
- `acfad45d0` contains the handoff_push fix, the INT arms, and the MT-KILL anchor.
- `356841113` merges origin/main `16a8240f`. `tests/closures.json` merged through its ledger driver, and the merge changed no file of this PR's other eleven. `tools/audit/seat/tick_loop.sh` moved on main to add a heartbeat; its relay launch is unchanged (`## Figures`, level 2).
- `8a8238bd4` merges origin/main `b787c7d4`. It adds only `tests/mutation_ledger/killed_by/` records: `git diff --name-only 356841113 8a8238bd4 | grep -vc '^tests/mutation_ledger/'` printed 0.
- `e4654445a` merges origin/main `01cf1398`. Of this PR's twelve files it touches `tests/closures.json` (merged by its ledger driver) and `tools/audit/seat/merge_train.py`, where main's three hunks rename `tests.yml` to `nightly.yml` in two comments and in one self-test read. It merged clean.
- `60f293beb` merges origin/main `c409c9b1`. Its one conflict was app_push.sh against main's `app_mint.sh` extraction, resolved as above (`## Conflict resolution`), which also touches `tools/pr/app_mint.sh`.
- `0731b3b9c` makes app_push's own `git push` asynchronous and adds the TERM and INT mid-push arms and the AP-PUSHFG and AP-MINTTRAP harness rows.
- `3b1797ee1` gives the census entries for main's new `body_patch.sh` and `app_mint.sh`, both `mention`. At `0731b3b9c` the census printed `2 OPEN` for them.
- `89874b6be` merges origin/main `cd4aaed4`, the v7.0.3 stamp. It touches none of this PR's thirteen files (`git diff --name-only 3b1797ee1 89874b6be | grep -xFf <the PR's files>` printed nothing, rc 1). `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` exited 0, so the branch claims nothing and moves no version.
- `139a1a038` merges origin/main `6c8903a4`. It adds `dev/programme/delivery/2603.md` and moves the roster, and nothing else (`git diff --name-only 89874b6be 139a1a038`). No script this PR's self-tests or harness run names the roster: `grep -lE 'wave-r10-groups|rosters/'` over them printed nothing (rc 1). So the mutant sweep and the finder's harness, taken at `89874b6be` and named so below, describe this tree. The self-test table and the entities run were re-taken at `139a1a038`.
- `db0d88377` merges origin/main `543c8087`, again only a delivery row (`2608.md`) and the roster (`git diff --name-only 139a1a038 db0d88377`). Every figure not named with another commit was re-taken here.

## Conflict resolution

- **`tools/pr/app_push.sh` against main's `app_mint.sh` (`60f293beb`).** Main replaced app_push's `cleanup` and the inline mint with `. app_mint.sh`, `mint_identity` and `mint_token`. This branch had replaced the mint's two trap lines with `pr_exit_trap cleanup`.
  - Kept: main's mint, sourced and called as main does. This branch's `pr_exit_trap`, now running `mint_cleanup`. This branch's copy of `pr_args.sh` into the self-test's `audit/seat/`, and main's copy of `app_mint.sh` beside the tool.
  - Added: `MINT_TRAP=caller` in app_push.sh, and in `app_mint.sh` the guard `if [ "${MINT_TRAP:-}" != caller ]` around its two trap lines.
  - Measured: deleting `MINT_TRAP=caller` (row AP-MINTTRAP) turns app_push's self-test red (`## Mutation proof`). `bash tools/audit/seat/body_patch.sh --self-test`, the mint's other caller, prints `body_patch self-test: 62 checks, 0 failed`.
- **Kept from earlier rounds:**
  - `pr_branch_lock`'s own traps are replaced by `PR_AFTER_REAP` (`# mut:unlock`) and `PR_REAP_SPARE`.
  - update_pr.sh's `--row-only` (`# mut:rowonly`) passes through the asynchronous push.
  - handoff_push.sh's `push_app` seam and its `# mut:push-*` anchors.
  - app_push.sh's `row_only_checks` runs after the asynchronous prepr.

`prepr` runs with `PREPR_SKIP_CLOSURES=1` (the owner's ruling). The scoped gate was derived separately and is in `## Figures`.

## Mutation proof

**The harness.** Every mutant below is a row of `dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh <rev> [MUTANT...]`. Each row applies an exact-once text replacement (a row refuses an anchor that occurs any other number of times) in a fresh detached worktree at `<rev>`, then runs the named self-tests under `timeout 900` with `PREPR_SKIP_CLOSURES=1`, and removes the worktree afterwards. Self-tests: CR is `cloud_relay.sh --self-test`, TR is `train.sh --self-test`, PA is `pr_args.sh --self-test`, AP is `app_push.sh --self-test`, and MT is `merge_train.py --self-test`.

**The block, failing test first.** The review's two mutants of the production branch, run at both ends:
- At `a01627177715` (the blocked head), `... r10_pusher_reap_launch_mutants.sh a01627177715 F-CR-ELSEFG F-CR-ELSELEAD` printed `cloud_relay self-test: 83 checks, 0 failed` for each mutant, in 3 of 3 runs. The block is reproduced.
- At `af7eb2d9a` (the new arm, with the production code unchanged), the same command printed `cloud_relay self-test: 84 checks, 1 failed` for each mutant, in 3 of 3 runs. The failing arm was `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order`.
- **train.sh arm 8b, failing test first.** `... 078ce3d67 TR-RC` printed `train.sh self-test: ok`, which reproduces the review's F-TR-RC survivor. `... 41f9fc826 TR-RC` printed `train.sh: REFUSE: self-test: a child exiting 3 left train.sh rc 0, state/rc '0', log 'TRAIN_RC=0'`.
- **handoff_push's INT arm, failing test first.** In a detached worktree at `acfad45d0` with `handoff_push.sh` checked out from `41f9fc826` (the file before the `push_app` fix, with the INT arms present), `bash tools/audit/seat/pr_args.sh --self-test` printed `pr_args self-test: 93 checks, 1 failed` in 3 of 3 runs. The failing arm was `FAIL handoff_push: INT reaps the tree too -- the push runs asynchronously, so the INT does not wait behind it`. With `acfad45d0`'s own `handoff_push.sh` restored, the same command printed 93 checks, 0 failed in 3 of 3 runs.

**The sweep:** `bash dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh 89874b6be932` (every row), at `89874b6be`. It printed identical lines at `3b1797ee1` (`diff` of the two outputs, less the sha, exited 0).
- **M0 (no change):** CR `cloud_relay self-test: 84 checks, 0 failed`; TR `train.sh self-test: ok (…, the child's exit is the train's, a stop reaps the tree, merge_train.py first)`; PA `pr_args self-test: 93 checks, 0 failed`; AP `app_push self-test: 197 checks, 0 failed`; MT `merge_train self-test: 200 checks, 0 failed`.
- **CR-FG, the relay's one update launch in the foreground (` &` dropped):** CR rc=1 with no summary line. The self-test ends at its first in-process handoff arm, because `PR_REAP_LEAD=$!` with no background job is `$!: unbound variable` under `set -u` (`bash -c 'set -u; f(){ true >&2; x=$!; echo after; }; f'` printed `$!: unbound variable`, rc 127). The production relay would die the same way, so the mutant is loud, but no stop arm judges it. Hence:
- **CR-FG-BOUND, the same launch in the foreground with `$!` kept bound (`… >&2; : &`):** CR 84/4. The failures are `a failed update is tried once`, `and logs OWED handoff-update`, the stub lead arm, and the production-route arm.
- **CR-LEADNAME, `PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD"` renamed to a plain variable:** CR 84/2, the stub lead arm and the production-route arm.
- **CR-PRODPATH, the default command pointed at `update_pr.missing`:** CR 84/1, the production-route arm alone.
- **F-CR-ELSELEAD, the production route not named the lead (`u=$!; [ -z "${HPO_RELAY_UPDATE:-}" ] || PR_REAP_LEAD=$u`):** its anchor still exists at this head. CR 84/1, the production-route arm. F-CR-ELSEFG's anchor (the split line) no longer exists, so the row prints `NOT APPLIED`; its successors are CR-FG and CR-FG-BOUND.
- **TR-FG, train.sh's launch in the foreground:** TR refuses at arm 4, `the stubbed --ignore-red run did not succeed`.
- **TR-LEAD, train.sh's `PR_REAP_LEAD` renamed:** TR refuses at arm 10, `a TERMed train did not stop merge_train.py first (alive 0, marks 'G early ', pidfile removed)`.
- **TR-RC, `wait "$PR_REAP_LEAD" || rc=$?` turned into `|| :`:** TR refuses at arm 8b, `a child exiting 3 left train.sh rc 0, state/rc '0', log 'TRAIN_RC=0'`.
- **OP-FG1, open_pr.sh's first push in the foreground:** PA rc=124 (the 900 s timeout), with 9 arms already failed. Among them are `open_pr: INT reaps the tree too …` and both census arms.
- **OP-FG2, open_pr.sh's second push in the foreground:** PA 93/3, both census arms and `mutants mut:oplock and mut:unpushed …`.
- **UP-FG, update_pr.sh's push in the foreground:** PA rc=124, with 7 arms already failed. Among them are `update_pr: INT reaps the tree too …`, `update_pr: after the stop the lock is free …` and both census arms.
- **HP-FG, handoff_push.sh's push in the foreground:** PA 93/3, `handoff_push: INT reaps the tree too …` and both census arms.
- **RM-FG, remerge_main.sh's push in the foreground:** PA 93/3, `remerge_main: INT reaps the tree too …` and both census arms.
- **AP-FG, app_push.sh's prepr in the foreground:** AP 197/2, `app_push INTed mid-prepr ends within 4 s, not behind prepr (got 'alive', want 'gone')` and `and leaves none of prepr's tree alive (got '3', want '0')`. Before this round's INT arm the same mutant left AP at 186/0, and the only check on it was the census's text check.
- **AP-PUSHFG, app_push.sh's own `git push` in the foreground:** AP 197/16. The arm it targets fails: `app_push INTed mid-push, after the mint, ends within 4 s (got 'alive', want 'gone')`, `and leaves none of the push's tree alive (got '3', want '0')`, `and revokes the token it minted (got '0', want '1')`. The other 13 failures are the push-result arms, because the `wait $!` that follows the line then waits on an earlier job.
- **AP-MINTTRAP, `MINT_TRAP=caller` commented out (main's mint traps restored over the reap):** AP 197/2, `and leaves none of the push's tree alive (got '3', want '0')` in both the TERM and the INT mid-push arm. With the push asynchronous, the mint's `trap 'exit 130'` still ends app_push and its EXIT trap revokes the token, but nothing reaps the push. At `60f293beb`, before the push was asynchronous, the same mutant failed 3 checks: alive after 4 s, the tree alive, and the token not revoked.
- **MT-KILL, `Train._run`'s `p.terminate()` turned into `p.kill()`:** MT 200/1, `a TERMed train exits 143 and leaves none of its tool's tree alive (R10-PUSHER-REAP)`.

Every row turns its self-test red, and M0 is green. The rows that are new since the reviewed head were also measured before the arms that kill them existed:
- `… 41f9fc826 …` (before the INT arms): AP-FG printed `app_push self-test: 186 checks, 0 failed`. HP-FG and RM-FG printed 90/2, killed only by the census arms.
- `… 078ce3d67 TR-RC` printed `ok`.

**Built-in mutants.** `pr_args.sh`'s self-test runs each of these on copies of the scripts, and each arm passes only when its mutant shows the defect: `mut:exitreap`, `mut:grace`, `mut:sigign`, `mut:stop`, `mut:unlock`, `mut:watch`, `mut:lock`, `mut:oplock`, `mut:unpushed`, `mut:rowonly`, `mut:lead`, `mut:leadwalk`, and the sed mutant `afterreap`. All of them pass in M0 (`pr_args self-test: 93 checks, 0 failed`).

**Unpinned.** TR-EXEC deletes train.sh's `exec ` before `python3 -u tools/audit/seat/merge_train.py`. The review measured it equivalent on bash 5.2, which execs a subshell's last simple command itself. The explicit `exec` is for macOS's `/bin/bash` 3.2. No test on a bash that execs anyway can tell the two apart. Its disposition is the review's: dismissed, equivalent on bash 5.2.

## Null control

- **The production-route arm reads the production command alone.** CR-PRODPATH points the default command at a missing `update_pr.missing`. Only the production-route arm goes red, and every stub arm stays green (`## Mutation proof`). So that arm, and no stub arm, is what runs `bash "$HERE/update_pr.sh"`.
- **The bystander.** An unrelated sleeper outside any pusher's tree survives every TERM arm (`open_pr: the null control -- an unrelated sleeper survives`, in M0). The finder's train harness was run at `89874b6be` with a `sleep 60` started outside it, and printed `survivors=0/5 bystander=alive` in 3 of 3 runs.
- **The stale lead.** The `staleld` arm sets `PR_REAP_LEAD` to a sleeper outside the host's tree. That sleeper survives the host's reap, and the host's own child does not. Its mutant, `mut:leadwalk`, shows that the probe can see the sleeper TERMed.
- **The lead arms' probe.** Each lead arm's child G writes a mark when TERMed. Once TERMed, the lead writes `early` if G was marked before the lead ended it. With the lead removed (CR-LEADNAME, TR-LEAD) the arm reads `early` or loses its mark, so the probe can see a whole-tree TERM.
- **The census.** On a scratch tree the census refuses three plants: an undispositioned `new_pusher.sh`, a deleted `pr_exit_trap`, and a dropped `&`. At the merge base, `--pushers 543c8087c579 | grep -c OPEN` printed 6, so the census sees the tree without this PR.
- **No vacuous reap arm.** Every reap verdict first requires that the tree started: 4 recorded pids (`treen`) in pr_args, 5 in train.sh arm 9, 3 in each of app_push's four stop arms, 3 in the relay's tree arm and 2 in its lead arms.

## Figures

All measured at `db0d88377ff07d5c4d8eb45aadf1295951989783`, with origin/main at `543c8087c57973ee58033a0c62520b5ec3a58621` (read 2026-10-22T11:50:38Z), unless a line names another commit.

- **The launch class: every production launch the diff adds, each against the arm that exercises its real branch (new this round).** The rule returns every added, non-comment shell line that holds a job-control `&` (neither `&&`, `>&` nor `&>`):

      git diff -U0 $(git merge-base origin/main HEAD)...HEAD -- 'tools/*.sh' | perl -ne 'if(/^\+\+\+ b\/(.*)/){$f=$1;next} if(/^@@ .*\+(\d+)/){$n=$1;next} if(/^\+/){ my $l=substr($_,1); print "$f:$n: $l" if $l!~/^\s*#/ && $l=~/(?<![&>|])&(?![&>\d])/; $n++ } elsif(/^ /){$n++}'

  Python launches come from `git diff -U0 <base>...HEAD -- 'tools/*.py' | grep -E '^\+.*Popen'`, which returns merge_train.py's `Train._run` and its own self-test driver. The shell rule returns 38 lines in 8 files. 9 are production launches, and the table gives each the arm that runs its real line:

  | launch (file, what it starts) | arm that runs the real line | mutant it kills |
  |---|---|---|
  | `cloud_relay.sh`, `"${upd[@]}" … >&2 &` then `PR_REAP_LEAD=$!` (update_pr.sh, or the stub) | the production-route arm, plus the stub tree arm and the stub lead arm, which now run the same line | CR-FG, CR-FG-BOUND, CR-LEADNAME, CR-PRODPATH, F-CR-ELSELEAD |
  | `train.sh`, `( … exec python3 -u tools/audit/seat/merge_train.py batch … ) >> "$log" 2>&1 &` | arms 4 to 10, each with a stub `merge_train.py` or `python3` at the real path the line runs | TR-FG, TR-LEAD, TR-RC |
  | `open_pr.sh`, both `bash "$_push" … &` | `open_pr: TERM` / `INT reaps …` arms, and the `mut:oplock`/`mut:unpushed` arm (the second push), each with a stub `app_push.sh` at the path `_push` resolves | OP-FG1, OP-FG2 |
  | `update_pr.sh`, `bash "$_push" … > $WT.log 2>&1 &` | `update_pr: TERM` / `INT reaps …`, `heldrun` and the lock arms | UP-FG |
  | `handoff_push.sh`, `push_app`'s `bash "$_push" … &` | `handoff_push: TERM` / `INT reaps …` (the new-PR route), and main's self-test (the update route) | HP-FG |
  | `remerge_main.sh`, `bash "$_push" --recarry … &` | `remerge_main: TERM` / `INT reaps …` | RM-FG |
  | `app_push.sh`, `( cd "$wt" && bash "$prepr" … ) & prepr_pid=$!` | `app_push TERMed mid-prepr …` and `app_push INTed mid-prepr ends within 4 s …`, with a stub prepr.sh at the path the copy resolves | AP-FG |
  | `app_push.sh`, `git … push "https://github.com/$repo.git" "$br" &` (after `mint_token`) | `app_push TERMed mid-push, after the mint, …` and `app_push INTed mid-push, after the mint, …`, with the self-test's stub `git` on PATH, which that line runs | AP-PUSHFG, AP-MINTTRAP |
  | `merge_train.py`, `Train._run`'s `subprocess.Popen(argv …)` | the self-test driver runs the real `m.Train._run` on a bash tool | MT-KILL |

  Every other line the rule returns is inside a self-test or its fixtures: the relay's `tree.sh`/`lead.sh` printfs and `stoprelay`'s `bash "$1" pass … &`; everything `pr_args.sh` adds inside `pr_args_self_test` (the reap-stub heredoc, test hosts and launches), plus the census's own `sed` filter, which launches nothing; train.sh's arm 9 and 10 stubs and launches; and app_push.sh's stub prepr, stub git and stop-arm launches. None of them is a production launch.
- **Level 1, the pusher census.** Rule: `bash tools/audit/seat/pr_args.sh --pushers <rev>`, which is `git grep -lE '(^|[^A-Za-z0-9_])(app_)?push\.sh'` over tracked `tools/` scripts, with each path given exactly one disposition in `PR_PUSHERS`.
  - `bash tools/audit/seat/pr_args.sh --pushers HEAD | awk '{print $1}' | sort | uniq -c` printed `18 ok`, and the census exited 0.
  - `--pushers 543c8087c579 | grep -c OPEN` printed 6, this PR's six runner seams.

  | seam | disposition |
  |---|---|
  | `handoff_push.sh`, `remerge_main.sh`, `open_pr.sh`, `update_pr.sh`, `tools/pr/app_push.sh` | runner, closed in this diff |
  | `merge_train.py` | runner-py, closed in this diff |
  | `tools/pr/push.sh` | retired: decision 0011's retired author path; the level-2 rule returns no caller of it |
  | 11 `mention` paths: `pr_args.sh`, `handover_prompt.py`, `ref_privacy.py`, `app_approve.sh`, `approve_held_runs.sh`, `head_note.py`, `check-wave-script.mjs`, `friction_issues.mjs`, `policy_lint.mjs`, and main's `body_patch.sh` and `app_mint.sh` (comments only; body_patch PATCHes a body and runs no push) | mention, each with its reason in `PR_PUSHERS` |

- **Level 2, who launches a runner.** Rule:

      git grep -nE '(bash|exec|python3?)([[:space:]]+-[A-Za-z]+)*[^#|;]*(handoff_push|open_pr|update_pr|remerge_main|cloud_relay)\.sh|\$\{[A-Za-z_]+:-[^}]*(handoff_push|open_pr|update_pr|remerge_main|cloud_relay)\.sh|python3?([[:space:]]+-[A-Za-z]+)*[^#|;]*merge_train\.py|tool\("(remerge_main|app_push)"\)' <rev> -- 'tools/*.sh' 'tools/*.py'

  It returns 27 lines in 9 files at this head, and 24 lines in 9 files at the merge base. Each file's disposition at this head:
  - `cloud_relay.sh`, 3 lines:
    - `upd=(bash "$HERE/update_pr.sh")`, launched as the lead: **closed in this diff**, by the launch-class row above.
    - The self-test's `dispose` run of the CLI.
    - A comment inside the self-test.
  - `train.sh`, 1 line, `exec python3 -u tools/audit/seat/merge_train.py batch`: **closed in this diff**, with merge_train.py as the lead.
  - `tick_loop.sh`, 1 line, `relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}`: **left running by documented choice, no code.**
    - The relay runs detached under a flock holder. The script's header says a relay still in flight when the pass's wait ends "is left running, never killed (its update_pr.sh may be mid-push)", and that relay reaps its own tree when it is stopped.
    - Main's heartbeat addition (`timeout 60 bash heartbeat.sh --once`) is bounded, and the census does not return it, because it runs no PR pusher.
  - `merge_train.py`, 6 lines: 2 are runner-py `tool("remerge_main")` and `tool("app_push")` runs, and 4 are docstring usage lines.
  - `orchestrator_tick.py`, 4 lines: self-test `procs` stub strings. It launches nothing.
  - `pr_args.sh`, 9 lines: self-test fixtures.
  - `handoff_push.sh`, 1 line: main's self-test fixture, which runs the script's copy in a scratch clone.
  - `r9_rc_bus_fetchhead.sh`, 1 line: a round-9 measurement harness that runs `handoff_push.sh` in a scratch fixture.
  - `tmp_paths.py`, 1 line: a self-test string.
- **Level 2-py, every Python child a seat script starts.** Rule: `git grep -nE '(^|[^A-Za-z0-9_./-])python3?([[:space:]]|$)' <rev> -- 'tools/audit/seat/*.sh' 'tools/pr/*.sh' | grep -vE '^[^:]*:[^:]*:[0-9]+:[[:space:]]*#'`.
  - It returns 176 lines in 23 files at this head, and 172 at the merge base. The 4 added lines are this PR's INT-resetting `python3 -I -c '… SIGINT, SIG_DFL … execvp("bash", …)'` wrappers, in `pr_args.sh`'s `stopreap` and `stoprun` and in `app_push.sh`'s mid-prepr and mid-push INT arms. Each is a self-test launcher that execs bash at once.
  - A child is long-lived when the program it runs polls. The test is `grep -cE 'time\.sleep|\.wait\(|while True'` on each module the lines name, and on the inline programs. It is non-zero for `merge_train.py` (6), `tests/gate_lock.py` (28), `tests/closure.py` (1), `tests/layout.py` (1) and `tools/pr/contract_rerun.py` (1). It prints 0 for `ci_predict.py`, `ref_privacy.py`, `pr_cap.py`, `orchestrator_tick.py` and `gh_comment.py`.
  - Each file's disposition:
    - `open_pr.sh` (3), `update_pr.sh` (1), `handoff_push.sh` (6), `remerge_main.sh` (1), `app_push.sh` (32): runners whose reap walks every descendant, Python children included. Closed in this diff.
    - `train.sh` (3): its `merge_train.py` is long-lived and **closed in this diff**. Its other 2 lines are self-test refusal strings.
    - `pr_args.sh` (5): the branch-lock holder is long-lived by design. It is spared by the reap, ended by `PR_AFTER_REAP`, and exits within 2 s of losing its parent (`# mut:watch`). The other lines are self-test fixtures, `pr_cap.py --self-test`, and the two INT wrappers.
    - `tick_loop.sh` (2): `RELAY_HOLDER` is detached by documented choice, as at level 2. `orchestrator_tick.py` prints 0.
    - `body_patch.sh` (17, from main): JSON filters, `carry_audit.py check` (0 on the long-lived test) and self-test fixtures; finite. `app_mint.sh` (2, from main): the mint's two JSON reads; finite.
    - `heartbeat.sh` (1, from main): `ref_privacy.py guard`, which prints 0, under the tick's `timeout 60`.
    - `prepr.sh` (49; main's two new lines are self-test fixtures that edit a scratch `closures.json`, finite): `gate_lock.py`'s slot wait, `closure.py`, `layout.py` and `contract_rerun.py` poll. Under a pusher, prepr runs asynchronously under that runner's reap (app_push's launch row). Run directly by a seat, a TERM leaves its foreground check running. **A distinct finding, already routed:** R10-FLOW-JIDOKA's roster carry from #2528 (R10-PREPR-CAP) states this seam and its fix shape.
    - `body_push.sh` (2), `bus.sh` (2), `ci_predict_replay.sh` (1), `merge_pr.sh` (4), `wt_sync.sh` (3), `app_comment.sh` (10), `approve_held_runs.sh` (3): finite. Each prints 0 on the long-lived test.
    - `app_approve.sh` (15): finite JSON filters, plus a self-test `RUN_TIMEOUT_PY` that bounds its own child.
    - `cloud-setup.sh` (5) and `seat_venv.sh` (8): one-shot environment builds.
    - `push.sh` (1): retired.
- **The finder's harness at both ends, re-run (the `9629ae17` block).** The review's harness is not in this tree. It is exported with `git archive da7bf22ba evidence/harness_reviewer | tar -x -C $EXPORT` from `origin/review/2524`: `$EXPORT/evidence/harness_reviewer/train/run_train.sh` (sha1 `35c7d548`), `$EXPORT/evidence/harness_reviewer/stub.sh` (`64758b0b`) and `$EXPORT/evidence/harness_reviewer/train/C/tools/audit/seat/merge_train.py` (`04cc1898`). Each end's `train.sh` ran beside that end's `pr_args.sh`, 3 runs per cell, with `kill -TERM` replaced by `kill -$SIG` for INT and HUP:
  - Base `9629ae17`: TERM `launcher=gone pidfile=removed survivors=5/5`; INT `launcher=alive pidfile=present survivors=5/5`; HUP `launcher=gone pidfile=removed survivors=5/5`. Each 3 of 3 runs.
  - Head (`89874b6be`): TERM, INT and HUP each `launcher=gone pidfile=removed survivors=0/5`, 3 of 3 runs.
  - Env recipe: the harness needs `$HPO_STATE_DIR/venv-ci/bin/python3`, so `hs/venv-ci/bin/python3` beside it is a symlink to the ambient `python3`, as train.sh's own self-test arranges.
- **Self-tests at `139a1a038`** (`PREPR_SKIP_CLOSURES=1`; `db0d88377` adds only a delivery row and the roster, which none of them names):

  | command | result |
  |---|---|
  | `bash tools/audit/seat/open_pr.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `pr_args self-test: 93 checks, 0 failed` |
  | `bash tools/audit/seat/update_pr.sh --self-test` | the same two lines |
  | `bash tools/audit/seat/handoff_push.sh --self-test` | `delivery_row self-test: 5 checks, 0 failed`; `handoff_push self-test: 2 checks, 0 failed` |
  | `bash tools/pr/app_push.sh --self-test` | `app_push self-test: 197 checks, 0 failed` |
  | `bash tools/audit/seat/body_patch.sh --self-test` | `body_patch self-test: 62 checks, 0 failed` |
  | `bash tools/audit/seat/cloud_relay.sh --self-test` | `cloud_relay self-test: 84 checks, 0 failed` |
  | `python3 tools/audit/seat/merge_train.py --self-test` | `merge_train self-test: 200 checks, 0 failed` |
  | `bash tools/audit/seat/train.sh --self-test` | `train.sh self-test: ok (5 refusals shown, root and options reach the child, no unasked flag, the child's exit is the train's, a stop reaps the tree, merge_train.py first)` |
  | `bash tools/audit/seat/tick_loop.sh --self-test` | `tick_loop self-test: 12 checks, 0 failed` |
- **The scoped gate.**
  - `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
  - At `139a1a038`, `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py` (Python 3.14.7, the seat venv) printed `ALL 2388 ENTITY CHECKS PASSED`, rc 0.
- **Checks before push:**
  - `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
  - `python3 -I tests/throwaway_git.py --check` printed `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
  - `git diff $(git merge-base origin/main HEAD)...HEAD | grep -nE '^\+.*\bgit\b.*\b(init|clone)\b'` printed nothing (rc 1).
  - `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against 543c8087c579`.
  - `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 43 policy file(s)`.
  - `git merge-tree --write-tree origin/main HEAD` exited 0.
- **prepr.** `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash tools/pr/prepr.sh <this body>` printed `PRE-PR: db0d88377ff07d5c4d8eb45aadf1295951989783 00000000000000000000000000`, with no REFUSE. `pr-body` printed `PR-BODY: 0 error(s)`, `claim files` printed `byte-identical to origin/main`, and the figures step printed `FIGURES: 26 resolved, 35 not verified, 0 refused`.
- **Rule 3 / rule 4.** `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E 'VERSION|manifest|RELEASE_NOTES|claimed_drift'` printed nothing (rc 1). `git diff --stat $(git merge-base origin/main HEAD)...HEAD` printed `13 files changed, 904 insertions(+), 83 deletions(-)`.
- **Carry.** `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` printed `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`. R10-UPDATE-PR-SIGNALS is on origin/main's roster (`dev/programme/rosters/wave-r10-groups.json`) at `resume.stage` `in-progress`.

## Red checks

Read from the check-runs API for this PR (`pull_request_read get_check_runs`, 49 runs at `a01627177715`): `nightly-status` failure 1, and every other run success or skipped. `pr-contract`, `closures`, `fast (3.14)` and `mutation` concluded success.

The earlier rounds' reds, by commit, as the earlier bodies recorded them (the `a01627177715` review re-read those from `9629ae17` on, in its `red_per_commit.txt`):
- `6fd073c9`: `PR contract` failed twice. `CodeQL`, `Governance` and `Tests` were cancelled by `cancel-superseded`.
- `50571afa` and `c071fa5f`: `PR contract` failed twice at each, and `nightly-status` failed.
- `9629ae17` and `a01627177715`: `nightly-status` failed.

This round's commits have no CI yet. The orchestrator's push is their first run.

Answers:
- **`pr-contract` at `6fd073c9`, `50571afa` and `c071fa5f`.** The body caused it, not the code: carry_audit refused unrouted items. A cheaper detector exists: `carry_audit.py check --body`, offline, in seconds. It is run on this body before the push (`## Figures`, Carry). I am naming the trigger; its analysis belongs to `root-cause.md`'s seat.
- **`nightly-status` at `50571afa`, `c071fa5f`, `9629ae17` and `a01627177715`.** It grades the last scheduled run on `main`, not this branch, and this diff (`tools/` scripts, one harness, `tests/closures.json` and one delivery row) does not reach what it reads. Main was red from 2026-10-22 02:52Z to 04:35Z: `orchestrator.md` was over its cap, fixed by #2595. This head merges that fix, and `policy_lint.mjs` here prints 0 errors. No cheaper detector applies to a red this branch did not cause.
- **This round's own defect.** handoff_push's INT seam was not a red check; the new INT arm found it at the unmutated head. It reached no release, so `defect-root-cause.md`'s triggers do not fire.

## Forward-carry

- #2502's SIGKILL clause: "a TERM, INT, HUP or SIGKILL of a running update must not free the branch lock while its push still runs".
  - This PR meets TERM, INT and HUP: the `heldrun` arm, the INT arms, and the lead for a relay or a train above `update_pr.sh`. It does not meet SIGKILL.
  - A SIGKILLed run runs no trap, and its holder exits within 2 s of losing its parent (`# mut:watch`), while the push that run started may still be running.
  - Meeting it needs the holder to keep the lock until the run's former tree is gone, by a drain that is deterministic across containers. The group's roster carry records that #2469's round-4 drain arm failed 7 of 7 runs in a container whose PID 1 reaps orphans late.
  - So #2502 stays open, with the group that owns the clause. Roster append, to `R10-UPDATE-PR-SIGNALS.carry`: "Revision (fixer, PR #2524 round 4): #2524 meets TERM/INT/HUP, including a runner above update_pr.sh (PR_REAP_LEAD); #2502 stays open. Owed: SIGKILL of a running update must not free the branch lock while its push still runs -- the holder keeps the lock until the run's former tree is gone, by a drain that waits on a condition, never a fixed window, and passes in a container whose PID 1 reaps late." Keep `resume.stage` at `in-progress` past #2524's merge.
  - Carry: R10-UPDATE-PR-SIGNALS
- The roster's Revision-12 prevention item on this group: "every self-test runs under a timeout in its own process group, reaped on exit". This PR does not build it.
  - The self-tests it touches are bounded only by their callers (CI's step timeout, or `timeout` in a seat's own run), and the relay's new stop arms bound their own waits.
  - Doing it for "every self-test" reaches files outside this group. A process-group kill is also a design question against `pr_kill`'s never-a-group rule.
  - Roster append, to `R10-UPDATE-PR-SIGNALS.carry`: "Still owed after #2524: the Revision-12 self-test isolation (a timeout and a reap on exit for every self-test); #2524 did not build it."
  - Carry: R10-UPDATE-PR-SIGNALS

## Friction

none
