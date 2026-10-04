# Round 9 current state (regenerated; not a log)

updated 2026-10-04T15:0xZ by the Mac orchestrator at main `7865ba90` (#1896). Regenerate, never append. Budget: under 10 KB.

## Orchestration
Local Claude Code orchestrator on tvofi's Mac drives to completion (tvofi 2026-10-03). Mandate: #201 comment 5951564627 (scope all, agent approvals of code-owned + policy PRs after a merge verdict, labelled), until 2026-10-09T12:00Z. Owner-ask pre-studies fold into the roster without a review seat.

## Where things live
- Roster: `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` (137 groups: done 103, open 34 across waves 1-5; every group wired to its issue — 45 issues filed 2026-10-04, #1897-#1941, mapping in the roster `issues[]`).
- Live state: #201 newest comment. Plan artifact: `handoff/round9/state/PLAN-TABLE.md` (this branch) + the claude.ai copy.
- Bus refs: `handoff/<topic>` code, `handoff-body/<topic>` body. Crash safety: `tools/audit/seat/wt_sync.sh` detached 15-min loop (orchestrator scratch `~/hpo-orch`).

## Main and release
main `7865ba90` (#1896). Stamps: v6.7.15, v6.7.16 (2026-10-04; `--allow-rowless` deferral recorded). Merged 2026-10-04: #1885 #1886 #1889 #1890 #1891 #1892 #1893 #1896 + #1894/#1895 landing. v6.7.17 next once the train drains and rows land (#1930's batch covers #1886/#1891/#1892; #1893-#1896 rows owed).

## Open PRs at 7865ba90
- **#1887 R9-EG-B1** head `13b1b8f0`: r3 in flight — mutation-unpinned (21 sites), fixer pinning locally per the EG-B10 playbook; keep `Closes #1736` armed at the re-post. On merge: dispatch DIAG-1F.
- **#1893 R9-FR-4** at `4b4c0f03`: absorbed (r2 merge verdict carries); merge when CI at that head settles.
- **#1894 R9-WEB-5** at `d6c1f64d`: absorbed (r1 merge verdict carries); prepr re-take at the new head in flight.
- **#1895 R9-FR-5** at `81cc117b`: merge verdict in hand; needs absorb at merge time.
- **#1942 CLAUDE.md instruments** at `0e2ee62b`: r1 blocked on one Red-checks line (name budget-raise-gate); one-line body fix, then labelled approval → merge.
- **#1944 R9-FR-6** at `e9a86cc4`: r1 merge verdict in hand (recarry branch-checkout fix); queue after the above.

## Merge train
`python3 tools/audit/seat/merge_train.py run ~/hpo-orch/train/queue.json --mandate "agent approval under mandate #201 comment 5951564627 (scope all, until 2026-10-09T12:00Z)" --ignore-red nightly-status --repo tvofi/heatpump_optimizer --state-dir ~/hpo-orch/train/state` (detached, log trainN.log). KNOWN BUG: recarry's worktree is detached and cannot push an absorb — absorb manually ahead of the train (worktree at the head, merge origin/main, update the body's head sha, app_push by sha or gh pr edit). The fix is #1944 (R9-FR-6, verdict in hand).

## Ready next
- DIAG-1F (#1935) + DBG-1 (#1939)/DBG-3 (#1941) dispatch at their after-edges (DIAG-1F at EG-B1's merge; DBG-1/3 edges all merged — STARTABLE NOW, fixers not yet dispatched).
- DBG-2 (#1940) after DBG-1. RO-3..RO-8 after RO-2b (merged). SW-1/2/3/4 (#1910-#1913) ready (W2).

## Issues
Every roster group carries its tracking issue (#1897-#1941; FR-6 → #1943). Closed 2026-10-04: #1860, #1825, #1881, plus the 23 delivered-group issues. Flagged for tvofi: #1793 scoping; coordinate-coarsening (DBG-0 doc 8.3); hpo-ledger bypass ratify-or-clear (#201 comment 5902383542); EG-A4 required-context.

## Traps (new since the archive)
- prepr's closures recorder under ambient pyenv 3.11 refuses with truncated-recording — run prepr with `PATH="$HOME/hpo-seats/bin:$HOME/.local/state/hpo/venv-ci/bin:$PATH"`, or after #1895 merges it self-resolves (the recorder adapts; R9-FR-5).
- app_push/post verdicts: body files must live in a seat SUBDIRECTORY; intended-close numbers are trailing app_push args.
- Roster JSON edits: use json load→modify→dump in a `checkout -B` worktree (raw string splices broke JSON twice); lint from a MAIN checkout (stale worktrees phantom-error).
- budget raises: policy_budgets.json `roles.<role>` is an OBJECT (opens list + cap) — set `.cap` only. Budget raise merges need the labelled agent approval AS A REVIEW at the head (#1843), cite the mandate as `mandate #<6+ digits>` (MANDATE_CITE grammar).
- trains: run ONE at a time; on stop, handle + extend the queue; the recarry absorb is manual until #1944 lands.
- Diagnostic-download size cap unknown (DBG-0 §8): DBG-2 owes the nightly_ha check.
