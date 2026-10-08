# Round 9: current state (as of 2026-10-08T19:15Z)

Written by hand, rewritten in place at each change. Chronology lives in `RESUME-ARCHIVE.md`. Durable decisions and traps belong in `dev/programme/HANDOVER.md` on main, never here (`writing-for-agents.md`: nothing goes in both). GitHub and git outrank this file: verify every PR head and state below with one `gh` call per 5 minutes before acting, and correct this file first on a disagreement.

Call the owner "tvofi", everywhere.

## Main and releases

- Latest stamp: v6.7.17, stamped at `b296779f`. Stamped with `--allow-rowless` for 9 direct pushes (their dispositions are owed, see Owed records).
- Main after that: `af79f211` (merge of #2060). Merged on 2026-10-08 before the stamp: #2049, #2041, #2051, #2055, #2053, #2056, #2054, #2050.
- #1793 was closed as not prioritised. The eight friction issues were folded into CI-2b (#2057, #2059).
- Remaining stamp: the final round-9 stamp, after every roster group is done and the record is rowed.

## Mandate (tvofi, session-bound)

Codeowner/tvofi approvals, policy changes, budget raises and repo settings. Cite #201 comment 6067089637 (scope all; 2026-10-08T19:30Z to 2026-10-11T12:00Z). Earlier approvals cited comment 5951564627. Approvals go through `gh pr review --approve`, labelled openly as agent approvals, never disguised. Quote the mandate verbatim from the comment and check its window before each use; it dies with its window.

## Open pull requests (heads verified 2026-10-08T19:15Z; re-verify)

| PR | head | what | state |
|---|---|---|---|
| #2025 | 566d9cae | EG-B11 typed entry configuration | serial queue, first |
| #2062 | 5964b583 | fix #2028 contract red history | serial queue, second |
| #2058 | 8b4ce373 | nightly-ha on PRs touching it | serial queue, third |
| #2024 | d916687d | UX-9 feedback sensor recommendation | serial queue, fourth; owes a body nit |
| #2057 | 4ff6152e | CI-2b closures.json in a merge-friendly layout | serial queue, fifth |
| #2059 | afe9cfd8 | CI-2b verdicts carry over bot commits | after #2057; closes #2023 |
| #2010 | d67d8a44 | UX-5 idle reasons, persistent advisor | delta review of the claim resolution after the stamp |
| #2061 | 8c758b72 | RO-9a instrument carries | round 2 blocked; fixer repairing |
| #2063 | f1181615 | policy: review timing | round-3 fix in progress |

All five queued PRs are serial because each touches a workflow, budget, claim or grader file.

## Merge train

- Operator workdir: `/Users/timmalmstrom/hpo-seats/merge-train-0117` (scripts `go5.sh`, `go6.sh`; queues `queue_batch.json`, `queue3.json`; logs `batch.log`, `train3.log`).
- Instrument: `tools/audit/seat/merge_train.py`. It recarries main itself and approves under the mandate when CARRY says yes. Use it; never merge a queued PR by hand.
- Queue order: #2025, #2062, #2058, #2024, #2057.

## Next actions, in order

1. Read the train logs, confirm what has merged, and keep the train going.
2. After #2057 merges: merge main into #2059 with `tools/audit/seat/update_pr.sh`, resolving `tests/closures.json` with `tools/merge/ledger_merge.py --resolve tests/closures.json`. Then a delta review of #2059. #2059 closes #2023. Afterwards close #2020, #2039, #2046 and #2052, each with a reason, and read each closure back.
3. #2010: delta review of the claim resolution at `d67d8a44`. Reviewer seat `/Users/timmalmstrom/hpo-seats/review-2010-delta`.
4. #2061 (RO-9a): fixer repairs the round-2 block (INERT READS skip arm; direct-push mutants). Reviewer seat `/Users/timmalmstrom/hpo-seats/review-2061`. A blocked verdict goes back to the same fixer, never repaired or re-dispatched by the orchestrator.
5. #2063 (policy, review timing): tvofi chose option 2. Rule: a reviewer posts `root-cause-unanswered` only after every workflow at the head has concluded, and the body has been checked by a `pr-contract` run started after the last workflow to conclude red; if none concluded red, the push-time run counts. The `fix-review.md` cap is raised to the minimum. Fixer seat `/Users/timmalmstrom/hpo-seats/r9-review-timing`, reviewer `/Users/timmalmstrom/hpo-seats/review-2063`. Policy merges on the mandate, labelled.
6. Live-install bugs (below).
7. Start the gated groups (below) as their gates merge.
8. Pay the owed records (below), then the final stamp and cleanup.

## Live-install bugs

The user runs v6.7.17. Their diagnostics are private; never commit them. Cause: `heat_pump_max_power` was set to 14 kW but the pump draws at most about 2.55 kW. The COP learner floor of 0.3 x max = 4.2 kW was never reached, so the planner over-credited heat. Investigation: `/Users/timmalmstrom/hpo-seats/live-bugs-6617/seat`. Two fixers:

- COP floor keyed on min power, plus a visible refusal reason, plus persistence. Seat `/Users/timmalmstrom/hpo-seats/live-cop-floor`.
- Nameplate plausibility repair, plus a wind-sensitivity warning. Seat `/Users/timmalmstrom/hpo-seats/live-nameplate`.

Each needs a fix review with the finder's harness, per `dev/governance/roles/fixer.md` and `fix-review.md`.

## Groups that start after merges

- EG-A4, UX-6, UX-7: after #2025. After EG-A4 merges, add `arch-score` to ruleset 23698884 under the mandate.
- UX-10: after #2024.
- RO-9b: after #2010. Carries into RO-9b's brief (finding-propagation): the PR-body machine-path scan question (needs a policy decision) and C4 (author App review dismissal).
- RO-9c: after EG-A4, UX-6 and UX-7.
- Existing seat dirs for these are under `/Users/timmalmstrom/hpo-seats/` (`r9-eg-a4`, `ux-6`, `r9-ux-7`, `r9-ux-10`, `r9-ro-9`). Use a seat only after checking its branch head against its resume note.

## Owed records

- Delivery rows (`dev/programme/delivery/<N>.md`) for every merged PR, plus roster `resume` fields and one #201 comment per state change (`delivery-status-tracking.md`).
- Direct-push dispositions for 618d014, f6ac991, 077f53a, 130c780 and 8107181. The `direct-pushes.md` record was not found on main at 2026-10-08; locate where earlier dispositions were written (search `dev/` for "direct push") before creating one.
- `dev/programme/HANDOVER.md` update. It is policy: the PR owes `## Approval` and the owner's approving review, here the mandate.
- The plan artifact.
- The #2024 body nit.
- The final round-9 stamp (`tools/release/stamp.py`, `--push --push-key`; needs `tests/delivery_status.py --require-rows` to pass).
- Worktree and branch cleanup: `tools/audit/worktree_gc.sh tvofi/heatpump_optimizer`, then prune merged branches. A cleanup seat once deleted live seats, so do it yourself or give exact paths.

## Orchestrator habits

- Keep a `.review-claim` file in the orchestrator worktree; it was garbage-collected once.
- Run the dispatch watcher all session. The old script, `scratchpad/orch/undispatched.sh`, was session scratch and may be gone. Re-create: poll open PRs every 5 minutes against a dispatched list; any open PR head with no seat gets one. Reusable instruments belong in `tools/` on main (decision 0013).
- Dispatch and confirm via `tools/audit/seat/bus.sh`.
- At most one GitHub API call per 5 minutes per seat; back off on 403.
- ETA plan: #201 comment 6067213418.
- Announce on #201 before opening a PR, merging or releasing: intent and files.
- Pull requests are authored by the `hpo-author` App via `tools/pr/app_push.sh`; comments via `tools/pr/gh_comment.py`, read back.
- Route seats by judgement: haiku mechanical, sonnet specified-with-an-oracle, opus adversarial.
