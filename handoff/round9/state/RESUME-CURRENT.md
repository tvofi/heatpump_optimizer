# Round 9 current state (regenerated; not a log)

updated: 2026-10-02T09:10Z by the local-orchestrator hand-over thread. Regenerate, never append. Budget: under 10 KB (`wc -c`).
History before 2026-10-01T17:00Z: `RESUME-ARCHIVE.md` (frozen). `RESUME.md` is a frozen stub.
Mirror: `handoff/audit-r9-plan:handoff/round9/state/` (via `sync_state.sh`). The Mac reads the mirror, never `/mnt`.

## Orchestration moved to the Mac (tvofi, 2026-10-02T08:57Z)
Cloud auto-mode blocked too many steps, so a local Claude Code orchestrator on tvofi's Mac finishes the programme. Its startup prompt is `LOCAL-ORCHESTRATOR-PROMPT.md` beside this file. The cloud threads named below stop once the local orchestrator has picked up their branch; all their work is on remote refs.

## Where things live
- Roster: `.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan` (truthed at `26b317b9` against main 492d8401). Read one group with jq, never whole.
- Briefs and plan: `handoff/round9/fix/F*.md`, `handoff/round9/FIX-PLAN.md`, `handoff/round9/fix/TVOFI-ASKS.md` (DECISIONS) on `handoff/audit-r9-fixplan`; `PLAN.md` in this folder.
- Delivery rows `docs/delivery/<N>.md`; live state on #201's newest comment; decisions `docs/HANDOVER.md`.
- Mac merge seat stop-state: `RESUME-mac-merge-seat.md` on `handoff/mac-merge-seat-resume` (68cc7971, last written at the v6.7.13 stamp).
- Bus refs: `handoff/<topic>` code, `handoff-body/<topic>` body, `handoff/verdict/<PR>` verdicts (`tools/audit/seat/bus.sh`, `body_push.sh`, `handoff_push.sh`).

## Main and release
main `492d8401` (#1839). Last stamp v6.7.13 (`4ac63b0a`). Merged since, unstamped: #1823 #1824 #1829 #1830 #1831 #1832 #1833 #1834 #1835 #1836 #1837 #1839 #1840. Next wave stamp after #1838 merges, on a clean main (6.7.x). Close-out v7.0.0 when only #201 remains.

## Open PRs and in-flight work at 09:05Z
- **#1838 R9-F10.4** head `e37cefc6` (fast-forward from 46a70815; merges main 492d8401). Not DIRTY. Budget rows fell in the merge: coordinator_private_reach 89->74, dead_methods 3->0, max_class_loc 9003->8989, seam_cut_total 777->776; none rose. Delta review at e37cefc6 running (cloud thread "F10.4 review"); its verdict goes to `handoff/verdict/1838` (tip 00504b5a still holds the older 46a70815 carry). The required `briefs` check stays red until #1842 merges. tvofi reviews #1838 himself (budget changes). Mac note: features.py R9-F2.1 P3 fails on the Mac at both e37cefc6 and main 492d8401 with identical numbers (110.4366 vs 110.1297); that is BLAS, judge it on CI.
- **#1842** brief_lint pin precursor, draft, `b69961d7`, no delivery row yet (the author seat's command was denied). Merge verdict on `handoff/verdict/1842` (fb2a1171). Merges before #1838. Needs: ready-for-review, delivery row, approval, merge.
- **Budget-gate mandate** (`handoff/budget-gate-mandate`, remote `4e719611`, not yet a PR; a local commit such as d741a894 is unpushed until the Mac pushes it). Cloud thread "Mandate-aware budget raise gate" was asked to push its body to `handoff-body/budget-gate-mandate` (draft at `/mnt/project-files/audit-r9/budget-gate-mandate/PR-BODY.md`, mirrored). Policy-touching: tvofi's approving review. Until it lands, budget-raise PRs need tvofi's own click.
- Built, waiting only on #1838 (then: merge origin/main, prepr.sh, body, hand off):
  - R9-F10.5 `handoff/r9-f10-gate-infra-5` f3e2e445, body `handoff-body/r9-f10-gate-infra-5`. Code-owned files. tvofi owes the `hpo-ledger` App (contents rw, `HPO_LEDGER_PEM`, `HPO_LEDGER_APPID`, main push bypass) before its push job records anything.
  - R9-F11.4 `handoff/r9-f11-governance-4` 2391db77; review round-1 items fixed; round 2 goes to the same reviewer.
  - R9-EG-B5a `handoff/r9-eg-dhw-closure-dedupe-v2` 5a69e874; note `handoff-body/r9-eg-dhw-closure-dedupe:RESUME.md`.
- R9-F10.4b (#1841): after #1838; re-measure first, dead_methods already reads 0 on #1838's head.
- Unblocked by #1838: WEB-1, EG-A1, EG-B3 (EG-B2 merged); F10.6 follows F10.5.

## Record owed
- `docs/delivery/<N>.md` for each PR merged since 2026-10-01 still reads **open** (checked #1808 #1823 #1824 #1829-#1837 #1839 #1840). One record PR truths them with merge SHAs.
- #201 needs a comment for the move to the Mac and for each merge above that has none.

## Critical path
F10.4 -> F10.5 -> F10.6 -> EG-B1 -> SW-1 -> UX-5 -> UX-7 -> RO-9. Roster stages at 26b317b9: done 73, in-review 1, built 3, rca-done 1, not-started 36 (recount with jq before quoting).

## Standing rules (tvofi)
- Never call the owner "Tim"; PR attribution `_Requested by **tvofi**_`.
- Every seat reads CLAUDE.md and all rules first. Authoring as hpo-author via app_push.sh; never push.sh, never force-push; merge main, never rebase.
- Temporary codeowners mandate (2026-10-02T05:36Z): seats may approve code-owned and budget changes as tvofi, each labelled openly as an agent approval. budget-raise-gate refuses agent-labelled reviews until the mandate PR lands.
- Reviews start at handoff, cite the head's CI, never re-run the full gate; rounds 2+ go to the same reviewer.
- Verdict first line: `Fix review: merge <sha>` or `Fix review: blocked <40-hex> <class>: <summary>`, plain text.
- Ratchets: restructure first; a raise is a last resort, stated in the PR body and commit.
- Cheapest model that suffices; opus for reviews, RCA and design.
- Optimizer off means no writes.

## Traps
- A stuck CI run on a superseded head blocks merges: tvofi force-cancels it.
- Code-owned PRs: a new head dismisses approval; re-approve at the new head.
- `app_approve.sh` line 120 `mapfile` fails under macOS bash 3.2 (run it with Homebrew bash 5).
- Carry rule: head = merge-tree(main, code) plus the PR's own delivery row only; a file changed on both sides since the merge base means a re-issued verdict.
- `mergeStateStatus: DIRTY` is GitHub's view; run `git merge-tree --write-tree origin/main HEAD` first.
