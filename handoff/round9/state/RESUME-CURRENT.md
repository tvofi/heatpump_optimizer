# Round 9 current state (regenerated; not a log)

updated: 2026-10-02 by the record seat (record-1002b), measured at main `aab94eea2`. Regenerate, never append. Budget: under 10 KB (`wc -c`).
History before 2026-10-01T17:00Z: `RESUME-ARCHIVE.md` (frozen). `RESUME.md` is a frozen stub.
Mirror: `handoff/audit-r9-plan:handoff/round9/state/` (via `sync_state.sh`). The Mac reads the mirror, never `/mnt`.

## Orchestration is on the Mac (tvofi, 2026-10-02T08:57Z)
A local Claude Code orchestrator on tvofi's Mac finishes the programme. Its startup prompt is `LOCAL-ORCHESTRATOR-PROMPT.md` beside this file. The cloud threads have stopped; all their work is on remote refs.

## Where things live
- Roster: `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` (truthed at `255cc4fe0` against main `aab94eea2`; adds group R9-EG-B3b). Read one group with jq, never whole. Stages at that head: done 75, in-review 5, built 1, rca-done 1, not-started 33 (recount with jq before quoting).
- Briefs and plan: `handoff/round9/fix/F*.md`, `handoff/round9/FIX-PLAN.md`, `handoff/round9/fix/TVOFI-ASKS.md` (DECISIONS) on `handoff/audit-r9-fixplan`; `PLAN.md` in this folder.
- Delivery rows `docs/delivery/<N>.md`; live state on #201's newest comment; decisions `docs/HANDOVER.md`.
- Mac merge seat stop-state: `RESUME-mac-merge-seat.md` on `handoff/mac-merge-seat-resume`.
- Bus refs: `handoff/<topic>` code, `handoff-body/<topic>` body, `handoff/verdict/<PR>` verdicts (`tools/audit/seat/bus.sh`, `body_push.sh`, `handoff_push.sh`).

## Main and release
main `aab94eea2` (#1849). Last stamp v6.7.13 (`4ac63b0ae`). Merged since, unstamped: #1823 #1824 #1829 #1830 #1831 #1832 #1833 #1834 #1835 #1836 #1837 #1838 #1839 #1840 #1842 #1843 #1844 #1849 (`git log v6.7.13..origin/main --first-parent`). Stamp 6.7.14 comes after #1845 to #1849 and the F11.4 precursor #1850 merge; EG-A1 (#1851) and EG-B3a take the next stamp. Close-out v7.0.0 when only #201 remains.

## Open PRs at main aab94eea2 (all draft, all BLOCKED on review or CI)
- **#1845 R9-EG-B5a** head `c5dad850`, one builder for the two solve paths' objective closures.
- **#1846 R9-WEB-1** head `e42b1cdd`, the product page with its doc_claims arm.
- **#1847 R9-F11.4** head `1517fa2d`, the agreement lane. Lands by option 3 with `--admin` past policy-docs, after its precursor.
- **#1850 R9-F11.4 precursor** head `b660da55`, resolvePrFromCommit and policy_lint rulePaths. Merges before #1847.
- **#1848 R9-F10.5** head `4f594b42`, ledger drain through the hpo-ledger App. In round 2 (security block).
- **#1851 R9-EG-A1** head `c9d6168c`, the architecture score in-tree. The calibration move is accepted.

## In-flight seats
- F10.5 reviewer and fixer: round 2 on #1848.
- F11.4: precursor #1850 first, then #1847.
- EG-B3 built at `8eba0f49` on `handoff/r9-eg-typed-payload`; delivers as B3a, PR opening. It needs a tvofi-visible `tests/hastub` edit (Generic on the coordinator classes). The remainder is R9-EG-B3b (#1737 stays open); B3b does not gate R9-UX-4 or R9-EG-B4.
- Record: `handoff/r9-record-1002b` truths five delivery rows (#1838 #1842 #1843 #1844 #1849); its body is `handoff-body/r9-record-1002b`; the orchestrator opens the PR.

## Owner rulings, 2026-10-02
- Mandate: #201 comment 5951564627, scope all, until 2026-10-09T12:00Z. An edited #201 comment does not revoke a mandate.
- PyPI installs are allowed into seat-local venvs.
- #1847 lands by option 3, `--admin` past policy-docs.
- Stamp 6.7.14 follows #1845 to #1849 plus the precursor; EG-A1 and EG-B3a go in the next stamp.
- EG-A1's calibration move is accepted.

## Owed by tvofi
After #1848 merges: remove App 5094721 from the bypass list of ruleset 22628467, and delete the repo-level `HPO_LEDGER_*` secrets (the `ledger` environment holds them).

## Critical path
F10.4 (done) -> F10.5 -> F10.6 -> EG-B1 -> SW-1 -> UX-5 -> UX-7 -> RO-9.

## Standing rules (tvofi)
- Never call the owner "Tim"; PR attribution `_Requested by **tvofi**_`.
- Every seat reads CLAUDE.md and all rules first. Authoring as hpo-author via app_push.sh; never push.sh, never force-push; merge main, never rebase.
- Agent approvals of code-owned and budget changes are labelled openly and cite the #201 mandate; `budget-raise-gate` counts them since #1843.
- Reviews start at handoff, cite the head's CI, never re-run the full gate; rounds 2+ go to the same reviewer.
- Verdict first line: `Fix review: merge <sha>` or `Fix review: blocked <40-hex> <class>: <summary>`, plain text.
- Ratchets: restructure first; a raise is a last resort, stated in the PR body and commit.
- Cheapest model that suffices; opus for reviews, RCA and design.
- Optimizer off means no writes.

## Traps
- `GIT_AUTHOR_NAME=Tvofi2` is exported and beats `-c user.name`; unset it before every commit.
- `python3` is 3.11 and cannot parse the tree; use `~/hpo-seats/bin`. There is no numpy without a seat venv, so numeric scripts run on CI.
- bash 3.2 has no `mapfile`; use the shim `~/hpo-seats/bin/approve.sh`.
- A ruleset change needs its fixture re-recorded (#1849 was that repair).
- A base-pinned grader cannot pass on the PR that adds it.
- A stuck CI run on a superseded head blocks merges: tvofi force-cancels it.
- Code-owned PRs: a new head dismisses approval; re-approve at the new head.
- Carry rule: head = merge-tree(main, code) plus the PR's own delivery row only; a file changed on both sides since the merge base means a re-issued verdict.
- `mergeStateStatus: DIRTY` is GitHub's view; run `git merge-tree --write-tree origin/main HEAD` first.
- features.py R9-F2.1 P3 fails on the Mac at main too (BLAS); judge it on CI.
