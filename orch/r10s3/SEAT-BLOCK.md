# SEAT-BLOCK (round 10, session 3) — a convenience copy, NOT policy

Policy is the tree: read `CLAUDE.md` at a FRESH `origin/main` checkout, then your
role contract under `dev/governance/roles/` (fixer: `fixer.md`; reviewer:
`fix-review.md`; root-cause: `root-cause.md`; judge: `judge.md`), then the
`.claude/rules/` file each task touches. Where this block and the tree disagree,
the tree is right. Call the owner only "tvofi".

## Where you work
- Your scratch is the ABSOLUTE directory your brief names, under
  `/Users/timmalmstrom/hpo-seats/r10s3/<SEAT>/`. Your worktree is `<scratch>/wt`
  (create it with `git -C /Users/timmalmstrom/heatpump_optimizer worktree add`).
  Never work in `/Users/timmalmstrom/heatpump_optimizer` itself: the main
  checkout must stay clean (open_pr.sh runs prepr from it). Never `git stash`.
- Interpreter: put `/Users/timmalmstrom/heatpump_optimizer/tools/audit/seat/shims`
  first on PATH and use `seat-python` (venv 3.14); never system python.
- Stop only PIDs you started; never `pkill -f` a pattern (it kills other seats).
- A job longer than ~2 min runs as a background task whose exit wakes you;
  never end your turn on a detached job. Heavy scripts (the full gate, the
  mutation table, stress.py) are CI's: cite CI check-runs, do not re-run them.
  Up to four heavy slots via `tests/gate_lock.py`; never clear a live lease.
- Commit before any in-place mutation proof (a restore can wipe uncommitted work).
- Merge `origin/main`, never rebase, never force-push.

## Identity (decisions 0011, 0013)
- Seats push REFS ONLY: code head to `handoff/<topic>`, body to the orphan
  `handoff-body/<topic>` via `tools/audit/seat/body_push.sh <topic> <BODY.md> [RESUME.md]`.
  Never open, edit, comment on, approve or merge a pull request; never post on
  an issue. Every GitHub write is the orchestrator's.
- Commit identity: `git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com commit --author='tvofi <70032254+tvofi@users.noreply.github.com>'`,
  trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- No host path, account name or home directory in any ref name or commit
  message (`tools/audit/seat/ref_privacy.py guard`, #2310).
- Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md` heading.

## Fixer flow
1. Worktree from fresh `origin/main`. Read only your roster group:
   `git show origin/main:dev/programme/rosters/wave-r10-groups.json | jq '.groups[]|select(.group=="<G>")'`.
2. `fixer.md` steps 1-18: failing test first importing the production symbol,
   mutation proof (mutate the predicate), finder's harness both ends, a null
   control for every quantified claim, enumeration rule for the class with every
   seam dispositioned, step 17 soundness, `python3 tests/structure.py` before push,
   `tools/audit/archscore/score.py --diff` not regressed.
3. Budget: pay first with a change that improves the code. A raise is allowed only
   once you have PROVEN no architecturally sound payment exists: list every payment
   tried with its `Architecture score: dS` (archscore before/after), in the body's
   `## Raise justification`, and STOP and report to the orchestrator before pushing
   a raise. Never game a metric.
4. Run `tools/pr/prepr.sh <BODY.md> <intended-issue-numbers>` from your worktree
   (it takes a heavy slot); fix what it refuses. Body headings per
   `.github/PULL_REQUEST_TEMPLATE.md`; `## Head` names the code head SHA (commit
   first, write the body against the SHA, then push — steward S10).
5. Hand off: push the code head to `handoff/<topic>`, `body_push.sh` the body.
   Report to the orchestrator: topic, code head SHA, body ref SHA, intended
   closing issues (only those in your group's `fixes`; `Part of #N` for the rest
   — never a closing keyword in a code span or near a number you do not close).
6. After the PR opens you watch its CI with the orchestrator. Reds on REQUIRED
   checks are yours to fix (commit, re-take figures, re-body, push to the handoff
   ref, report). Before the reviewer's handoff only; after it the head is frozen
   and only the orchestrator moves it. Read the autofix summary before fixing a
   closures/claims/mutation red (`ci-autofix.md`: wait for the bot when it says `changed`).
7. New finding inside your group's files: fix it in the group. Touching other
   files: report it to the orchestrator (do not file issues yourself).

## Reviewer flow
`fix-review.md` in full, from a DETACHED worktree at the head SHA under your
scratch. Finder's harness, never the fixer's. Publish with
`tools/audit/seat/bus.sh push-verdict <pr> <VERDICT.md> <evidence dir>` (the
evidence dir is ABSOLUTE and holds a file naming the head; VERDICT.md carries
your brief's `bus-nonce:`). First line of VERDICT.md exactly
`Fix review: merge <40-hex head>` or `Fix review: blocked <40-hex head> <class>: <reason>`.
Report the push-verdict output and the review commit SHA to the orchestrator.

## Reporting
End every turn with: what you did, the SHAs, what is red/green (from the
check-runs API, latest run per name), and what you need from the orchestrator.
Never state a number you did not execute; never print a conclusion beside a command.
