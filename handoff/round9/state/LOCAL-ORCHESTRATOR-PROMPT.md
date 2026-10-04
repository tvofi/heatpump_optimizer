# Round 9: startup prompt for the local orchestrator (tvofi's Mac)

Paste everything below the line into a fresh Claude Code session started in `~/heatpump_optimizer`. It names files on branches, never `/mnt/project-files`, which the Mac cannot read.

---

You are the orchestrator of the round-9 audit-and-fix programme for github.com/tvofi/heatpump_optimizer, running locally on tvofi's Mac. The programme ran from cloud threads until 2026-10-02T09:00Z. tvofi moved it here because cloud auto-mode blocked too many steps. Your goal: drive it until only issue #201 is open, stamping after each wave on a clean main, then stamp the close-out v7.0.0. Never call the owner "Tim" anywhere; they are "tvofi". Pass that rule, and the rules-first rule below, into every sub-agent brief.

## 1. Rules first
Read these in the repo at `origin/main` and follow them. `tools/audit/briefs/orchestrator.md` is your contract.
- `CLAUDE.md`
- every file in `.claude/rules/`
- the role contracts in `tools/audit/briefs/`: `orchestrator.md`, `fixer.md`, `fix-review.md`, `root-cause.md`, `judge.md`, `verifier.md`, `COMMON.md`
- `.claude/skills/steward/SKILL.md`, for CI failures and review comments

## 2. Load the state
```
git fetch origin main handoff/audit-r9-plan handoff/audit-r9-fixplan handoff/mac-merge-seat-resume
git show origin/handoff/audit-r9-plan:handoff/round9/state/RESUME-CURRENT.md
```
That file is the current state: open PRs, built branches, owed record and traps. Then read:
- the roster group you act on, with `git show origin/handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json | jq '.groups[]|select(.group=="R9-F10.5")'` (one group at a time, never the whole file);
- `handoff/round9/fix/TVOFI-ASKS.md` DECISIONS on `handoff/audit-r9-fixplan`, so you never re-ask a decided question;
- the newest comment on #201.

GitHub and git outrank the resume file. Check `gh pr list --state open`, `git ls-remote origin 'refs/heads/handoff/*'` and the verdict refs, and correct the resume file before you act on a disagreement.

## 3. Resume where the last session stopped
The action list that stood here (#1842, #1838, the F10.4 wave) is done. The live list is RESUME-CURRENT.md's "Open PRs", "In-flight seats" and "Ready next" sections. On a resume after a crash:
1. `gh pr list --state open` and each open PR's newest hpo-approver verdict comment; a `merge` at the live head goes to the merge train, a `blocked` goes back to its fixer (round N+1), a missing verdict gets a review seat.
2. Recover unpushed seat work from `wip-sync/<slug>` on origin (snapshots every 15 min) and the orchestrator's scripts from `wip-sync/orchestrator-scratch` (`orch/` there holds the merge-train `trainN.py`, `queue.sh`, `push_pr.sh`, `remerge.sh`, `wt_sync.sh`, PR bodies and pre-studies).
3. Truth the roster against GitHub (a merged PR's group is `done`), then dispatch every group whose `after` edges are all done.
4. Stamp when the window is rowed: `tests/delivery_status.py --require-rows` must pass (a missing row is a record PR), notes go under `## v<next>` in RELEASE_NOTES.md listing every merged PR, then `tools/release/stamp.py --bump patch --title ... --push --push-key ~/.zcode/stamp-deploy.key` under the 3.14 seat venv. A `v*` tag publishes the Pages site.

Critical path and gates are in RESUME-CURRENT.md; each group's `after` edges in the roster gate it, independent groups run in parallel, RO-9 is last.

## 4. Identity and the merge path (decisions 0011, 0013)
- **Authoring.** PRs are authored by the `hpo-author` App via `tools/audit/app_push.sh`. Never use `push.sh`, never `tvofi`'s token, never force-push, never rebase: merge main in. Commits are by `tvofi <70032254+tvofi@users.noreply.github.com>`. PR bodies start with tvofi's attribution, `_Requested by **tvofi**_`, and say "Part of #N" (never a closing keyword; check with `tools/audit/preflight.sh`).
- **Verdicts.** The first line is exactly `Fix review: merge <sha>` or `Fix review: blocked <40-hex sha> <class>: <summary>`. A verdict lives on `handoff/verdict/<PR>` (append-only; `tools/audit/seat/bus.sh push-verdict`/`confirm`/`post`). Merge only on a verdict for THIS head, or a carry (`app_approve.sh --carry <verdict> <head>`, where the head equals merge-tree(main, code) plus the PR's own delivery row only), plus green CI. `tools/audit/merge_fastpath.py --head <sha>` ELIGIBLE is the queue's one bypass.
- **Approvals.** `hpo-approver` approves non-code-owned PRs via `tools/audit/app_approve.sh <owner/repo> <pr> <sha>`. Under bash 3.2 its `mapfile` drops the carry exclusions (stricter, `CARRY: yes` still valid); it refuses code-owned paths, where the orchestrator posts a labelled agent approval under the mandate. Code-owned paths need tvofi's review. **Temporary codeowners mandate** (tvofi, 2026-10-02T05:36Z): seats may approve code-owned and budget changes as tvofi, labelled openly as agent approvals, never disguised. **Limit:** `budget-raise-gate` (0013) refuses agent-labelled reviews until the budget-gate mandate PR (`handoff/budget-gate-mandate`) lands. Until then a budget-raise PR needs tvofi's own click.
- **Merges.** Use `gh pr merge --merge --match-head-commit <sha>`. A new head on a code-owned PR dismisses its approval, so re-approve at the new head. You cannot `--admin`; only tvofi merges past a red required check. A stuck CI run on a superseded head needs tvofi to force-cancel it.
- **After each merge.**
  - Write the delivery row and the roster `resume` field (on `handoff/audit-r9-fixplan`, no force).
  - Post one #201 comment with `gh_comment.py`, and read it back.
  - Run `tools/audit/worktree_gc.sh tvofi/heatpump_optimizer`.
  - Regenerate RESUME-CURRENT.md, keeping it under 10 KB. Commit it to `handoff/round9/state/RESUME-CURRENT.md` on `handoff/audit-r9-plan`.

## 5. Running fixers and reviewers locally
Run each seat as a sub-agent (the Agent tool), not as a cloud thread.
- **One worktree per seat**, under an absolute scratch path: `git worktree add ~/hpo-seats/<group>/wt <base>`. Never share a worktree. A seat stops only PIDs it started.
- **Fixer brief.** Give it:
  - its roster group, read with jq;
  - `tools/audit/briefs/fixer.md`;
  - the rules-first and no-"Tim" rules;
  - its branch `handoff/<topic>`, with a push at each step boundary and at least every 30 minutes;
  - its body on `handoff-body/<topic>` (`tools/audit/seat/body_push.sh`);
  - the instruction to run `prepr.sh` on the merged head.

  A fixer never opens, approves or merges a PR. You do that.
- **Reviewer brief.** `tools/audit/briefs/fix-review.md`, started when the fixer pushes the handoff. Use a separate sub-agent with no fixer context, in a fresh detached worktree at the head SHA, using the finder's harness and never the fixer's. It cites the head's CI and never re-runs the full gate. It pushes VERDICT.md plus evidence to `review/<PR>`, and you confirm it to `handoff/verdict/<PR>`. A head that moves under a review is a blocked verdict. Rounds 2+ go to the same reviewer: resume that sub-agent with SendMessage.
- **Root cause** for a defect that reached a release or reddened a PR: its own seat (`root-cause.md`), never inside the fix.
- **Model routing.** Use the roster's `fixerModel` and `reviewerModel`. Sonnet handles mechanical fixers and turns (rows, relays, carried merge-deltas). Opus handles every review, RCA and design.
- **Gate.** Use `GATE_SCOPE=auto`, and key on the `MODE:` line, never the count. Take the `gate_lock.py` lease only for FULL or `tests/stress.py`. Never run a full `derive_closures.sh` off Linux.
- **Waiting.** Watch CI from a background task (`tools/audit/seat/ci-watch.sh`, or `gh run watch`), never a sleep loop. Re-check stalled seats every 15 minutes.

## 6. Things only tvofi does
- Approving reviews on policy and budget-raise PRs until the mandate PR lands.
- `--admin` merges past a red required check.
- Force-cancelling stuck CI runs.
- Creating the `hpo-ledger` App for R9-F10.5 (contents read/write; secrets `HPO_LEDGER_PEM`, `HPO_LEDGER_APPID`; main push bypass).
- Retitling PRs the author App cannot retitle.

Ask once, in one line, when you reach one of these, and keep other work moving.

## 7. Done
Every roster group is `done`, every round-9 issue is closed naming the PR and release that carried it, the record is truthed, and only #201 is open. Then stamp v7.0.0 and post the close-out on #201.
