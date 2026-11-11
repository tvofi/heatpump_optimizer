CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-worktree-gc-live, at head 9e2c18ff8af69a2f1f4269d655761665c2af6dc2. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-worktree-gc-live before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-worktree-gc-live, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-worktree-gc-live, even with no code. Then push the code to refs/heads/handoff/r10-worktree-gc-live, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-worktree-gc-live <body.md>`, which pushes refs/heads/handoff-body/r10-worktree-gc-live; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-worktree-gc-live`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-worktree-gc-live and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-worktree-gc-live and refs/heads/handoff-wip/r10-worktree-gc-live-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
SECOND REPAIR ROUND for R10-WORKTREE-GC-LIVE, pull request 3423, head 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 (branch fix/r10-worktree-gc-live; handoff/r10-worktree-gc-live df7b7ac6b33e14fe959ee32eb77d83a59dd02d52). Continue from the PR head and that handoff; do not re-cut. The roster carry of the group, Carry 1, is built or answered in the existing body; keep it named `Carry 1` in the body.

THE NEXT REVIEW IS ROUND 3. Steer to closure in ONE pass. Do not fix only the two named mutants. On the added argv-inside awk line (tools/audit/worktree_gc.sh, about line 722) ENUMERATE EVERY member of the argv terminator set (today: "", /, ", ', :, ,) and for EACH member do one of:
  (a) add a fixture that is kept (named argv-inside) or collected on that member, and show its own mutant (that member dropped) killed: quote the failing run with the mutant applied and the passing run restored; or
  (b) remove the member from the set where no real caller shape needs it, with a stated disposition under `## Unpinned sites`.
A smaller set, every member of which is pinned, is the PREFERRED outcome. Name in the body the caller shape each kept member serves (for example: `sh -c 'cd "<wt>"; ...'` shows the token `"<wt>";`; `--paths=<wt>:/tmp`; `--paths=<wt>,/tmp`; a single-quoted `'<wt>'` token). Keep the sibling-prefix null control (<wt>2).
Then run `python3 tools/audit/seat/mutant_run.py --diff <the PR's three-dot diff against origin/main>` over the PR's added lines (see `mutant_run.py --help`) and quote ZERO unanswered survivors in the body before handing off, so a third review finds nothing left on the added lines. The residual the review lists (the `[ -n "$out" ] || return 2` line in cwd_inside) is a pre-existing main line and is out of scope. Re-run fixer.md steps 2-8; hand off via body_push.sh. Merge origin/main only if `git merge-tree --write-tree origin/main HEAD` conflicts.
RED-CHECK RULING (owner, 2026-11-09): no merge may be blocked on a non-required red. Only the reds that `merge_train.py owed-reds` lists for this PR and head are owed a `## Red checks` answer.

THE BLOCKED VERDICT, verbatim (probe/rev-3423-23bb0265, verdict.md):

Fix review: blocked 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 mutation-survivors: argv terminator members quote and colon/comma survive on the added argv-inside awk line

bus-nonce: 23bb0265faaee10ee3d83b62292fff79
pending-ci: gate

## Block

Round 3 of review (delta re-review of 032e758e4..9e2c18ff8; `review_carry.py` prints FRESH-REVIEW). The four mutants the round-2 verdict named now fail, but the `argvterm` class is only partly pinned. The argv-inside awk line added by this PR (`tools/audit/worktree_gc.sh:722`) accepts six terminators: `""`, `/`, `"`, `'`, `:`, `,`. The repair pins `""` (`seat-argvco`) and `/` (`seat-argvscr`), and the null control pins the upper bound (`seat-argvsib`). Nothing pins the other four:

- `argvterm-quote` (drop `t=="\""` and `t=="\x27"`): 154 checks, 0 failed.
- `argvterm-colon` (drop `t==":"` and `t==","`): 154 checks, 0 failed.

Each one is a keep decision that matters in practice. A `sh -c 'cd "<wt>"; ...'` relay shows up in `ps -eo args=` as the token `"<wt>";`, and a `--x=<wt>:<other>` or `<wt>,<other>` list argument ends in `:` or `,`. Delete any of these four members and the sweep collects a live checkout, which is the P453 failure. The suite still stays green. The body's `## Unpinned sites` lists `argvterm` as pinned, and that is true only of the `""`/`/` members.

Fixtures owed: one argv-fixture seat per uncovered terminator, for example `bash -c cd "<wt>/x"` with no space, a `'<wt>'` token, `--paths=<wt>:/tmp` and `--paths=<wt>,/tmp`. Each must be kept and named `argv-inside`. The alternative is to remove a member from the set with a stated disposition under `## Unpinned sites`. Then re-run the two mutants above, plus one mutant per member.

## Findings

- Residual: `[ -n "$out" ] || return 2` in `cwd_inside` (an empty `lsof -a -d cwd` listing counts as unreadable) survives its deletion mutant (`lsofcwd-empty`, 154/0). The line comes from main at d08ed3104 (the old `cwd_inside`, line 651 there), so this PR does not owe it. Carry: dismissed: pre-existing line on main, not added or changed by this PR, and not in this PR's mutation scope

## Evidence

- Head reviewed: 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 (ev/HEAD.txt). It matches the PR head in the GitHub API and the body's `## Head`.
- RESULT selftest-head: `bash tools/audit/worktree_gc.sh --self-test` at the head gives 154 checks, 0 failed, rc 0 (ev/selftest-head.txt). This matches the body's figure.
- RESULT mutants: each applied alone in a detached worktree at the head, the self-test run, then restored (ev/mutants.py, ev/mutant-*.txt):
  - lockglob (both globs dropped): 4 failed. lockglob-star alone: 2 failed (x.lock). lockglob-dot alone: 2 failed (.x.lock). Pinned.
  - argvterm-slash (drop `/`): 2 failed (argvscr). argvterm-empty (drop `""`): 4 failed (argvuse and argvco). Pinned.
  - argvterm-any (accept any terminator): 1 failed, the argvsib null control. The null control moves under its own perturbation.
  - lsofall (`lsof -Fn` with no `|| return 2`): 2 failed (noopen). Pinned.
  - nopsbin/psunread (`ps -eo args=` with no `|| return 2`): 3 failed (nops and nopsbin). Pinned. The deleted `command -v ps` line is redundant with this arm, since an absent ps exits 127. I accept the disposition.
  - argvterm-quote: 0 failed. argvterm-colon: 0 failed. SURVIVORS, see Block.
  - lsofcwd-empty: 0 failed. Pre-existing, see Findings.
- Null controls: argvsib moves (above). The binnops no-ps PATH check is in the self-test and passes. deadpid is unchanged from the prior round.
- The body now has a `## Unpinned sites` section (brief check 2). It is accurate except for the argvterm partial-pin claim.
- Cost figure: the body states the per-candidate reads (one `lsof -d cwd`, one `ps`, one `lsof -Fn` per candidate worktree) and the reason for rejecting a once-per-sweep read. I could not re-derive its exact numbers, because they come from another container. On this container (4164 `lsof -Fn` lines): `lsof -Fn` 0.060 s, `ps -eo args=` 0.009 s, `lsof -a -d cwd -Fn` 0.027 s real (ev/cost.txt). The order of magnitude agrees (tens of ms per candidate), but which of the two reads is slower comes out the other way round here.
- `git merge-tree --write-tree origin/main 9e2c18ff8` rc 0: merges cleanly.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The three-dot diff touches only `tools/audit/worktree_gc.sh` and `dev/programme/delivery/3423.md`. VERSION, the manifest and the notes heading are untouched. There are no claim files and no budgets.
- The prior round's other findings are resolved: lockglob, the argvterm `/` member, lsofall and nopsbin are pinned, and `## Unpinned sites` is present.
- CI: `merge_train.py classify` was polled every ~60 s from 03:12 to 03:33 UTC and printed `WAIT 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 pending: gate red: none` (rc 3) throughout (ev/classify.txt). No required red at review time. This verdict's block does not depend on CI.
- `merge_train.py owed-reds` (ev/owed-reds.txt) lists the required contexts. No red is owed an answer at the time of review.
