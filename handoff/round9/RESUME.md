# Round 9 — resume document

A fresh orchestrator resumes from this file alone. Read PLAN.md and START-PROMPT.md beside it,
then CLAUDE.md, .claude/rules/ and tools/audit/briefs/orchestrator.md in the repo.
Mirror: branch handoff/audit-r9-plan, handoff/round9/RESUME.md (when /mnt/project-files is unwritable).

updated: 2026-09-26T06:10Z by orchestrator thread "Round 9 audit orchestrator"
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
| R1 find driver | DONE: R1a #1633 c9453921, R1 #1636 b9956289 | not in tree (no tools/audit/scopes.json, no check_scopes.py in-tree) |
| R2 policy | DONE | merged as #1627 (565ebf53; commits 1d38497a, d5b64834) |
| R3 verify driver | R3a MERGED #1635 0454645f; R3 #1639 merge verdict, full CI | |
| R4 instrument notes + stale docs | MERGED #1632 cb78e997 | round4-file keep already done in prepare_baseline.sh; folded in: playwright 1.49.0 refs (D4.md, prepare_baseline.sh), steward S6 + tools/audit/README.md vs gate-scoping.md. Policy files → code-owned approval |
| R5 ledger preconditions | DONE | #1577 content anchors, ledgermerge in .gitattributes, #1617 ledger layout merged 7e75ebee |
| R6 bug 5 reboot half + mode persistence (owed in docs/delivery/1621.md) | #1638 in review | production fix; reached a release → RCA seat beside it |

## Seats
All four run as Agent sub-seats inside the orchestrator container (lost if it is reclaimed; re-dispatch
from the table and check the handoff branch on origin first). Scratch: /tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad/seats/<id>
| seat | handoff branch | state |
|---|---|---|
| R1a checker | handoff/r9-r1a-find-checker | MERGED #1633 at c9453921 (05:28Z). PR #1633; FIXED after block: code c6ca4132, body 2bb0f8e6 (was a897272a); re-review by Cloud reviewer 2; not code-owned; review brief reviews/R1a.md → Cloud reviewer 2; Mac relayed to push; merges before R1 |
| R1 driver | handoff/r9-r1-find-driver | MERGED #1636 at b9956289 (05:55Z). | FIXED after vacuous-pins block: code 2b1ddd10 (merges main c9453921), body c55db14e; sent to Mac 05:32Z; was 173061d3; push only after R1a merges + main merged in; audit-find.js @tvofi-owned; review brief reviews/R1.md |
| R3a checker | handoff/r9-r3a-verify-checker | MERGED #1635 at 0454645f (05:50Z). Was: code 9fd82c91 (stacked on R1a c6ca4132), body 518c333a; not code-owned; brief reviews/R3a.md; push after #1633 merges |
| R3 driver | handoff/r9-r3-verify-driver | PR #1639 @7078363b (bda239b8 + main 0454645f), full CI running, final re-check Cloud reviewer 2. B2 FIXED 06:00Z: code bda239b8 (one commit on 7934e6ce), body 1b8834f4; PR head was 5d6afe07; Mac merges main in after #1635, pushes; code-owned (audit-verify.js, tests/closure.py); MODE FULL; brief reviews/R3.md; push after R3a merges |
| R4 fixer | handoff/r9-r4-instruments | MERGED #1632 at cb78e997 (05:10Z). Was: PR #1632 open at f493fec1 (2bf7faaf + delivery row); in review by Cloud compute helper; review brief reviews/R4.md → Cloud compute helper; Mac asked to push. Policy → tvofi approval (mandate 3) |
| R4b fixer | handoff/r9-r4b-web-fragments | MERGED #1634 at 16d811f1 (05:27Z). Was: code 26b51272, body e3872880; policy (@tvofi); review brief reviews/R4b.md; sent to coordinator ~05:10Z |
| RC1 countermeasure | handoff/r9-rc1-pinned-local | PR #1637 @8c7c1339 in review (compute helper); #1633 Root cause comment posted+read back (gh_comment.py, owner account). Was: code de347318, body a7ea0387; prepr.sh 3e/3f/3g; state (c); #1589-class claim refuted; review brief reviews/RC1.md; #1633 Root cause section at rca/RC1-root-cause-section.md for Mac to post; merge after R1 |
| R6 fixer | handoff/r9-r6-reboot-toggles | PR #1638 @325c59a5 in review (Cloud reviewer 2). HANDED OFF 05:50Z: code df50ab42, body 16ed158f; (b) fixed, (a) unexplained beyond Optimizer active; not code-owned; brief reviews/R6.md; RC2 brief rca/RC2-bug5-reboot.md → root-cause seat |
Coordinator asked (04:50Z) to: warn the Mac seat; line up Cloud compute helper / Cloud reviewer 2 as reviewers;
start 10 box threads for phase A from /mnt/project-files/audit-r9/briefs/B<n>.md when the baseline is cut.
Coordinator ack 04:32Z: Mac warned; reviews R1+R4 -> Cloud compute helper, R3+R6 -> Cloud reviewer 2; send head SHAs and review briefs to the coordinator.

## Verdicts received
- RC1 #1637 fixed by root-cause seat at 8b6eb090 (ff on 8c7c1339); re-review pending. RC2 cause CONFIRMED (06:09Z): under HA 2026.5 switch PARALLEL_UPDATES=1 semaphore queued v6.6.12's turn-offs behind the solve; restart cancelled them (3/3 repro); R6 head leaves all four off. Barrier report pending.
- #1637 (RC1) @8c7c1339: BLOCKED (Cloud compute helper, 05:58Z): class still open for check-wave-script.mjs reading prepare_baseline.sh; 3g parser passes 9/13 shape changes; 6/12 mutants survive. Back with the root-cause seat. DECISION: RC1 does not gate the baseline.
- #1639 (R3) @7078363b: MERGE (Cloud reviewer 2, 05:51Z); Mac approves (mandate) + merges once full CI green.
- R3 re-check @5d6afe07 (PR head = 7934e6ce + main c9453921), Cloud reviewer 2 05:43Z: B1/N1/N2/pins verified; BLOCKING B2 restore() (empty untracked file unnoticed; staged edit not restored). R3 seat resumed: one commit on 7934e6ce.
- #1636 (R1) @5f7ca60d: MERGE (Cloud compute helper, 05:33Z), relayed to Mac for tvofi approval (mandate) + merge.
- R3 full list (Cloud reviewer 2, 05:33Z): B1 tree restore; M1 to_zero, M2 tolerance, M3 _shard, M4 THREAD_FACTOR_MAX pins; N1 nested flock; N2 non-dict field. R3 seat resumed to add M1-M4, N2 on dd72e18a and push.
- #1635 (R3a) @9534f5ec: MERGE (Cloud reviewer 2, 05:32Z). R1 2b1ddd10 pre-check clean (Cloud compute helper); merge verdict at PR head pending.
- Pre-review (Cloud compute helper, 05:26Z): R1 173061d3 BLOCKED vacuous-pins (3 refusals unpinned in check-wave-script.mjs; test-only fix + 6 non-blocking pins + rotation.json text + leads-seat branch paths). R1 seat resumed.
- Pre-review (Cloud reviewer 2, 05:23Z): R3a 9fd82c91 clean so far; R3 241a480f BLOCKING — judge_batch runs all commands in one tree without snapshot/restore (a perturbation leaks into the next finding's row). R3 seat resumed on the fix + nested-lease note; full list to follow.
- #1633 (R1a) re-review @0c14689f: MERGE (Cloud reviewer 2, 05:06Z). Mac merges after #1632, then pushes R1 (173061d3).
- #1634 (R4b) @9e9bad63: MERGE (Cloud compute helper, 05:12Z); may merge ahead of R1 (disjoint files).
- #1632 (R4) @f493fec1: MERGE (Cloud compute helper, ~04:58Z); relayed to Mac for approval+merge. Non-blocking: orjson pin read from running checkout's lock not baseline SHA's; printed `$PYTHON -m pip` fix fails in pip-less uv venv; requirements file prints empty when pin line missing; one D4.md line over wrap width.
- #1633 (R1a) @1a19dd9f: BLOCKED codeowners_gap (check-wave-script.mjs:1159 fixture quotes boost.py) — Cloud reviewer 2, 04:53Z. R1 seat resumed to fix both R1a and R1 heads (+2 optional nits). Mac holding #1633.

## Next step
06:21Z RC2 returned: handoff/r9-rc2-user-state-durable code f0396766, body 2dda53b4 (strip), stacks on R6 df50ab42, merges AFTER R6. R6 REGRESSION found by RC2 (mode set during startup saves before accuracy load; 7 comfort-learner overrides -> 0; repro tools/audit/handoff/r9-rc2/r6res.py). Coordinator told Mac to hold R6 and fix; Cloud reviewer 2 folds it into its verdict. Baseline waits on the R6 fix. Barrier (4 released instances: v2.4.1, v3.13.0, #1249, bug 5): action returns <0.5 s + state reads back after restart; 10 mutants killed, 1 survivor held by #1621 sweep. Closures will report UNDER-SCOPED (autofix records it).
06:27Z Cloud reviewer 2 BLOCKED #1638 R6 @325c59a5 on the RC2 startup-save regression (fix: await accuracy load handle in async_set_mode); rest sound. Mac fixing. RC2 review -> Cloud compute helper after RC1 re-review.
06:33Z #1639 R3 MERGED at 2d248e8c (mandate approval after merge verdict + green CI). Baseline waits only on R6 fix. #1637 RC1 awaiting re-review.
FORWARD-CARRY (finding-propagation): set_thermal_parameters runtime fields lost at restart -> lead for D1 seats; add to B4/B5/B6 box briefs when generating.
BASELINE: after #1639 (R3) and #1638 (R6, with the RC2-found fix) merge, Mac stamps v6.7.1 (stamp.py); baseline = that stamp SHA (PLAN §1.3). Then check_scopes.py --ref <sha>, generate box briefs, start 10 box threads.
(older:) Dispatch R1, R3, R4, R6 fixers; reviewers via coordinator (Cloud compute helper / Cloud reviewer 2);
Mac seat pushes as hpo-author from handoff/<topic>, approves, merges one at a time. Then cut baseline.

## Transport
Other cloud seats get I/O errors on /mnt/project-files. Every seat/review brief is ALSO committed to branch
handoff/audit-r9-plan under handoff/round9/ (reviews/*.md, briefs/B*.md, RESUME.md). Local worktree for it:
scratchpad/plan-wt (branch r9-plan-transport). Verdicts come back as text via the coordinator.

## Phase A mechanics (from R1)
audit-find.js with args.box runs one box's seats and pushes to handoff/audit-r9-find-<box>; args.from:"intake"
gathers all boxes, then runs the leads seat, the D3 confirmation and intake. Box briefs B1..B10 must tell each
box thread to run it with args.box=<Bn> (round 9, baseline, repo, rotation, scopes).

## Phase A briefs
Generator: boxgen/gen.py <baseline> <outdir> (with boxgen/pre.md) writes B1..B10.md. At baseline cut: run it into /mnt/project-files/audit-r9/briefs/ AND handoff/round9/briefs/ on handoff/audit-r9-plan, push, then ask the coordinator to start one thread per box with context_message_ids=[cmsg_01EL5jLi4rokGBbkaevYXSJVTfeni8YJN5HdH97LdRCudt] (tvofi's words authorising the round, and so the Workflow run).

## Phase B note
The verify driver cannot place a triple's three verifiers on different containers (PLAN §5): orchestrator dispatches each triple's verifiers to three different box threads.
JUDGE-* header lines are optional; where absent the dedup judge writes judge_batch overrides.

## Owed (not blocking the baseline)
- RC1 root-cause thread STARTED: "Round 9 root cause seat" (cse_01BUrtj7jMHAoX2hsiwBfXwL), requested 05:20Z (brief rca/RC1-base-graded-checker.md @ f1876c82): #1589 class recurred on R1a (check red only on main: policy-docs grades with base .mjs; codeowners_gap.py --check ~0.8 s in no local path, prepr.sh never calls it). Brief together with R6's RCA.
- R4 non-blocking notes (see #1632 verdict) — small instrument follow-up after the round starts, or fold into a round-9 D11 lead.
- tools/audit/README.md toolkit list doesn't name scopes.json / check_scopes.py (policy).
- .claude/workflows/web-fragments.md + synced web-*.js still describe the pre-v6.7.0 lease → dispatched as R4b fixer (handoff/r9-r4b-web-fragments), policy.
- tests/card_browser.mjs coarse-pointer comment and carry-1320.json control measured on Playwright 1.49 Chromium; unmeasured on 1.56.1 (lead for D4-s1).
