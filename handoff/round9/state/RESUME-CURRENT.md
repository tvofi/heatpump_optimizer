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

## Open PRs at main 4efc5b63e (nothing is in flight; every seat stopped and pushed)
- **#1889 record/handover** head `8920402b`: docs/HANDOVER.md round-9 section, `tools/audit/seat/wt_sync.sh`, rows for #1888 and #1889. Policy: needs a review verdict, then mandate approval. Merging it unblocks stamp v6.7.16.
- **#1885 R9-F10.13** head `c983b977`: round 3 (entities.py `--anchor` check stubbed, no worktree; closures.json lines dropped). Needs a round-3 review; round 2 had `merge` at `7162a2d8`. Linux `closures` must show no UNDER-SCOPED for tests/entities.py.
- **#1890 R9-F10.15** head `d6877750`: CI lanes (coverage two lanes, `fast` lane count fix with a `lane count:` probe line, closures three lanes). Needs a review; the body names which job log proves each claim; drop commit (b) if `fast` goes red on a timing-sensitive script.
- **#1887 R9-EG-B1** head `6b68bca0`: round 1 `blocked` (5977790144): conflicts with main (#1874) so no CI ran; the hub barrier misses a record sharing the hubs' containers. Round-2 list in the roster's R9-EG-B1 resume. Fixer worktree `/Users/timmalmstrom/fix-r9-eg-b1`.
- **#1886 R9-RO-2** PR head `a607db2a`, branch head `c0ae0371` not yet pushed to the PR: round 2 three of four items done and split (new group R9-RO-2b); owed: closures repair for tests/entities.py, entities/prepr self-tests, prepr on the body, push. Exact steps in RESUME.md on `handoff-body/r9-ro-2`.

## Seats at shutdown
None running. Each pushed code to `handoff/<topic>` and its stop state to `handoff-body/<topic>:RESUME.md`. Detached loops (worktree sync, merge queue) are stopped; restart `tools/audit/seat/wt_sync.sh` in the new session.

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
