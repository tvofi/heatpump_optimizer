# Round 9 — resume document

A fresh orchestrator resumes from this file alone. Read PLAN.md and START-PROMPT.md beside it,
then CLAUDE.md, .claude/rules/ and tools/audit/briefs/orchestrator.md in the repo.
Mirror: branch handoff/audit-r9-plan, handoff/round9/RESUME.md (when /mnt/project-files is unwritable).

updated: 2026-09-26T04:52Z by orchestrator thread "Round 9 audit orchestrator"
(thread cmsg_01EL5jLi4rokGBbkaevYXSJV2mBkzeKerzo5hWb5CAh44d, session cse_01WgT4h2uvK9kbxQbWc5MJis)

## Mandate
tvofi mandate 3 (msg cmsg_01EL5jLi4rokGBbkaevYXSJVTfeni8YJN5HdH97LdRCudt) expires 2026-09-26T09:35Z:
until then the Mac seat may approve code-owned/policy files as tvofi (needs a cloud reviewer's
merge verdict + green CI). After 09:35Z, ask tvofi.

## Phase
R (readiness). Baseline NOT cut.

## Entry criteria (§1), measured 04:40Z
- open issues: only #201 (list_issues state=OPEN, totalCount 1)
- open PRs: none (list_pull_requests state=open → [])
- main = 81f2c18c (v6.7.0 stamp, tag v6.7.0 points at it). Tests run 36217832924 on 81f2c18c
  in progress at 04:28Z; Hassfest/Validate/Governance green; 8dd27fe0 Tests green.
- round-8 register: docs/audit-2026-09.md "## Round 8" section present; tools/audit/round8/ present.
- check_scopes.py --ref 81f2c18c: rc 0, 15 × ok, 42 seats.

## Readiness items
| id | state | notes |
|---|---|---|
| R1 find driver | to dispatch | not in tree (no tools/audit/scopes.json, no check_scopes.py in-tree) |
| R2 policy | DONE | merged as #1627 (565ebf53; commits 1d38497a, d5b64834) |
| R3 verify driver | to dispatch | tools/audit/judge_batch.py absent |
| R4 instrument notes + stale docs | to dispatch | round4-file keep already done in prepare_baseline.sh; folded in: playwright 1.49.0 refs (D4.md, prepare_baseline.sh), steward S6 + tools/audit/README.md vs gate-scoping.md. Policy files → code-owned approval |
| R5 ledger preconditions | DONE | #1577 content anchors, ledgermerge in .gitattributes, #1617 ledger layout merged 7e75ebee |
| R6 bug 5 reboot half + mode persistence (owed in docs/delivery/1621.md) | to dispatch | production fix; reached a release → RCA seat beside it |

## Seats
All four run as Agent sub-seats inside the orchestrator container (lost if it is reclaimed; re-dispatch
from the table and check the handoff branch on origin first). Scratch: /tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/seats/<id>
| seat | handoff branch | state |
|---|---|---|
| R1 fixer | handoff/r9-r1-find-driver | running (04:50Z) |
| R3 fixer | handoff/r9-r3-verify-driver | running (04:50Z) |
| R4 fixer | handoff/r9-r4-instruments | HANDED OFF ~05:05Z: code head 2bf7faaf, body commit d8d3374d; review brief reviews/R4.md → Cloud compute helper; Mac asked to push. Policy → tvofi approval (mandate 3) |
| R6 fixer | handoff/r9-r6-reboot-toggles | running (04:50Z); RCA seat owed once cause named |
Coordinator asked (04:50Z) to: warn the Mac seat; line up Cloud compute helper / Cloud reviewer 2 as reviewers;
start 10 box threads for phase A from /mnt/project-files/audit-r9/briefs/B<n>.md when the baseline is cut.
Coordinator ack 04:32Z: Mac warned; reviews R1+R4 -> Cloud compute helper, R3+R6 -> Cloud reviewer 2; send head SHAs and review briefs to the coordinator.

## Verdicts received
(none)

## Next step
Dispatch R1, R3, R4, R6 fixers; reviewers via coordinator (Cloud compute helper / Cloud reviewer 2);
Mac seat pushes as hpo-author from handoff/<topic>, approves, merges one at a time. Then cut baseline.

## Owed (not blocking the baseline)
- .claude/workflows/web-fragments.md + synced web-*.js still describe the pre-v6.7.0 lease → dispatched as R4b fixer (handoff/r9-r4b-web-fragments), policy.
- tests/card_browser.mjs coarse-pointer comment and carry-1320.json control measured on Playwright 1.49 Chromium; unmeasured on 1.56.1 (lead for D4-s1).
