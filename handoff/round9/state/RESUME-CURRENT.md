# Round 9 current state (regenerated; not a log)

updated: 2026-10-04T07:30Z by the Mac orchestrator, measured at main `4efc5b63e`; session shut down gracefully at tvofi's request. Regenerate, never append. Budget: under 10 KB (`wc -c`).
History before 2026-10-01T17:00Z: `RESUME-ARCHIVE.md` (frozen). `RESUME.md` is a frozen stub.

## Orchestration
A local Claude Code orchestrator on tvofi's Mac drives the programme to completion without interruption (tvofi, 2026-10-03): update roster, this file and #201 at every merge, stamp and seat result. Startup prompt: `LOCAL-ORCHESTRATOR-PROMPT.md` beside this file. Owner-ask pre-studies fold into the roster without a review seat (tvofi, 2026-10-03); fix reviews still run.

## Where things live
- Roster: `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` (head `7c4374cec`). Stages: done 97, rca-done 1, in-review 3, building 1, not-started 21. Read one group with jq; lint a change with `brief_lint.mjs` from a checkout of origin/main (it resolves citations against that tree; cite a branch-only symbol with the branch head SHA).
- Live state: #201's newest comment. Delivery rows: `docs/delivery/<N>.md`. Decisions: `docs/HANDOVER.md`.
- Bus refs: `handoff/<topic>` code, `handoff-body/<topic>` body (BODY.md, RESUME.md).
- Crash safety: every worktree with unpushed or uncommitted state is snapshotted every 15 min to `wip-sync/<slug>` on origin, and the orchestrator scratch (merge-train scripts, PR bodies, pre-studies, sweep reports) to `wip-sync/orchestrator-scratch` (`orch/wt_sync.sh`, detached loop, pid in `orch/wt_sync.pid`). Recover a seat's work from its `wip-sync/` branch.
- Plan artifact (swimlane, ETA): https://claude.ai/artifact/7Mdnn5vXzmDoSnmTfPwEHo

## Main and release
main `4efc5b63e` (#1888). Last stamp v6.7.15 (`ac255c200`, 2026-10-03; its tag published the GitHub Pages site, https://tvofi.github.io/heatpump_optimizer/). Merged since, unstamped: #1880 #1879 #1882 #1883 #1874 #1884 #1878 #1888. v6.7.16 is next, once #1889 merges (it carries the rows for #1888 and itself; `tests/delivery_status.py --require-rows` must then pass); RELEASE_NOTES `## v6.7.16` is not yet written; it publishes #1883's site fixes and ships #1882's card.

## Open PRs at main 4efc5b63e
- **#1889 record/handover** head `8920402b`: docs/HANDOVER.md round-9 section current, `tools/audit/seat/wt_sync.sh`, rows for #1888 and #1889. Policy (HANDOVER.md): needs a review verdict, then the orchestrator's mandate approval. No reviewer dispatched yet.
- **#1885 R9-F10.13** head `7162a2d8`: triage sites driven by every driver but entities.py, pin re-verification in the nightly, `--anchor` re-drive, legionella pin re-attributed to features.py (via dst_checks), `stamp.py --dry-run` runs the D6 register. Round 2 `merge` (5977616991); round 3 asked by the orchestrator: stub the worktree in entities.py's `--anchor` check (a full disk crashed the whole run).
- **#1886 R9-RO-2** head `a607db2a`: dual-path graders and listed restore steps ahead of the reorg. Round 1 `blocked` (5974991221): base copies of codeowners_gap/layout break on the new restore form (policy-docs, wave-script red); shadow copy at a new path passes a grown policy file; pin-list swap still graded PINNED; closures entry owed by hand. Round 2 with the fixer.
- **#1887 R9-EG-B1** head `6b68bca0`: one frozen SolveRecord per solve, setback as a value, H1-H4, closes #1736; one-line D1.md policy edit. In review.

## Seats at shutdown
Each was told to stop at a clean point and push code to its handoff branch and RESUME.md to its handoff-body branch; read those refs before acting.
- Fixers: F10.13 (round 3), RO-2 (round 2), F10.15 (CI lanes: coverage two lanes, fast lanes actually parallel, closures three lanes).
- Reviewers: #1887.
- Merge queue: detached `orch/queue.sh` reading `orch/queue.txt`, log `orch/queue.log` (one `trainN.py` per PR; it re-carries onto main, waits CI, checks the verdict carry, approves (App, or tvofi agent approval under the mandate for code-owned paths), merges with `--match-head-commit`).

## Ready next (after-edges done)
After #1887 merges: R9-EG-B6, R9-EG-A3, R9-SW-1 become ready; R9-SW-5 (tvofi's block DHW / block space heating 2 h switches) follows R9-EG-B6. After #1885: R9-F10.16. RO-3..RO-8 wait on RO-2.

## Owner rulings since 2026-10-02
- Mandate #201 comment 5951564627 (scope all, until 2026-10-09T12:00Z) covers code-owned and policy approvals; the orchestrator approves policy PRs after a merge verdict.
- Audit instruments are not code-owned; reusable tools live in `tools/` on main (`tools/audit/seat/` per decision 0013, #1879); never only in /tmp.
- Reviewers look for metric gaming; fixers take the better code even at more cost; a budget cap is paid by an objective improvement first, and a raise is asked only when it is the only truly better option, with all options shown (#1877).
- Owner asks of 2026-10-03, folded: R9-UX-8 card insight panel (merged #1882), R9-SW-5 block switches (Tier A overlay; legionella releases a block with a notice; 15 C economy floor, no frost promise), R9-WEB-4 site fixes (merged #1883), R9-F10.14 arch_score out of coverage tracing (merged #1884), R9-F10.15/F10.16 from the CI-placement sweep.
- Orchestrator decisions in R9-UX-5's brief (tvofi may overrule): the card what-if honours an active setback; the thermal view publishes the effective floor.

## Owed by tvofi
- Check: after #1848 (merged), App 5094721 off the bypass list of ruleset 22628467 and the repo-level `HPO_LEDGER_*` secrets deleted.

## Critical path
EG-B1 (#1887) -> EG-B6 / SW-1 -> SW-5, UX-5 -> UX-6/UX-7 -> RO-9.

## Standing rules (tvofi)
- Never call the owner "Tim"; PR attribution `_Requested by **tvofi**_` as the body's first line (never under `## Friction`).
- Every seat reads CLAUDE.md and all rules first. Author as hpo-author via `tools/audit/app_push.sh`; verdicts via `app_comment.sh` (hpo-approver) at the live head with an absolute Evidence dir; never force-push; merge main, never rebase.
- Agent approvals of code-owned and policy changes are labelled and cite the mandate.
- Each merged PR carries its own `docs/delivery/<N>.md` row (three did not tonight; record PR #1888; carried to R9-F10.16).
- Cheapest model that suffices; opus for reviews, RCA and design.

## Traps
- Seat interpreter: `~/.local/state/hpo/venv-ci` (built by `tools/audit/seat/seat_venv.sh`, shims in `~/hpo-seats/bin`). The old `/private/tmp/audit-7` venv is temp. pyenv's `python3` is 3.11 and cannot parse the tree (a 3.11 stamp refused on a 3.12 f-string, 2026-10-03).
- `~/hpo-seats/bin/approve.sh` is retired (moved to `~/hpo-seats/bin-retired/`); `tools/audit/app_approve.sh` refuses code-owned paths, where the train posts the mandate approval instead.
- `run_in_background` jobs die at 2 h: long loops and merge queues run detached (nohup) with a log.
- Disk: the workstation filled at ~00:30Z on 2026-10-04 (seat worktrees, mutation-table temp extractions); a full disk makes every Bash call fail. Seats run heavy scripts one at a time and delete their own temp; the orchestrator deletes only finished seats' scratch.
- zsh: `$c:r...` in `"$c:refs/..."` is a modifier, write `${c}`; `for x in $LIST` does not word-split.
- The PR's `nightly-status` stays red until a scheduled nightly passes on main; every PR body names it under `## Red checks` or pr-contract refuses.
- A cancelled check run followed by a re-run is not red; the train ignores `cancelled`.
- The App JWT can be refused transiently; retry once before treating it as a failure.
- `GIT_AUTHOR_NAME` is exported and beats `-c user.name`; use `--author`.
- Never commit in the main checkout `/Users/timmalmstrom/heatpump_optimizer`; prepr runs from it.
- features.py R9-F2.1 P3 and card_browser P9 fail on the Mac at main too; judge them on CI.
