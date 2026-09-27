# Resume: round-9 fix programme (Mac merge seat), current state

Last rewritten 2026-09-27T14:02Z. The full chronology is in RESUME-v670-log-*.md beside this file.

## Standing rules (tvofi)
- Keep this doc current after every push, review, merge or stamp (cmsg_01EL5jLi4rokGBbkaevYXSJVEVXGUKMEpcz3B9PUdtNmAf).
- Stamp regularly (after each wave or batch, when main's Tests are green), and drive round 9 until only #201 is open (cmsg_01EL5jLi4rokGBbkaevYXSJV5e7dweSaGdT71cUJyexT41).
- Route mechanical work to sonnet or haiku seats (cmsg_01EL5jLi4rokGBbkaevYXSJVDC1kJ5S9ThJsYejnAXbvVc).
- Production hotfixes go to the front of the queue, with a stamp right after the merge.
- Drafts at handoff: open each fix as a draft as soon as it is handed off; merge only on a "Fix review: merge" verdict and green CI.
- Code-owned or policy/budget PRs need tvofi's approving review at the final head.

## State at 15:10Z (session restarted; this seat is now the sole coordinator)
- tvofi (2026-09-27, in session): there are NO cloud sessions anymore. This Mac seat coordinates ALL work: fixers and reviewers run as local subagents (opus for adversarial fix/review, sonnet for specified work with an oracle, haiku for mechanical), per the roster's per-PR model fields. The Mac itself keeps merging, stamping, verdict processing and coordination. PR creation is delegated to fixer seats too.
- MERGED #1720 F11.6 at 2d012406 (closes #1667) at 14:5xZ — merged FIRST to lock tvofi's re-approval at bf2723bc before any main move dismissed it.
- #1722 F1.1: re-merged to 7a9e1c0f (main 2d012406); verdict relabelled (reverdict/evidence-7a9e1c0f); hpo-approver approved; merge job running in bg (CI was 5 checks in progress). On merge: #1665 #1683 close → dispatch F1.2 fixer (opus, roster R9-F1.2, branch handoff/r9-f1-coordinator-2).
- F2.3 HANDED OFF (code head ef071c1a, branch handoff/r9-f2-solver-3 @81fbc185; Fixes #1671): sonnet seat opening its draft PR (claimnotes refusal on claimed_drift.txt resolved by hand: keep the wood_coil claim, claims-for to 6.7.7). Then an opus review seat. Merges after #1718.
- Queue after #1722: #1717 F3.3 (verdict @0c6242a1, head was pre-re-merged to 256afc69 → remerge main again, relabel, merge), then #1718 F4.2 @7fe356f6 (verdict matches; remerge, merge — closes #1672), then F2.3's PR on its verdict.
- F2.5 (opus) dispatches when #1717 AND F2.3's PR have merged (roster after: F2.2✓ F3.3 F2.3).
- Stamp v6.7.8 after the queue drains (rows ride the branches).
- bg jobs die with the session — rerun remerge_main.sh then merge_pr.sh per PR; verdict evidence in reverdict/evidence-<sha8>.

## Exceptional mandate (tvofi, 2026-09-27T18:15Z; EXTENDED to programme completion, max 2026-09-29T05:15Z, THIS SESSION ONLY)
"Keep driving the full programme autonomously to completion until no open issues remain. On an exceptional basis, you have for the next 14 hours full authority to approve as CODEOWNER/tvofi on policy changes and budget raises (as a last resorts, seats should pay first), as well as design choices (go with the recommended), but record the choices so you can summarize them for me later. FOR 14 HOURS ONLY, AND FOR THIS SESSION ONLY." Choice log kept in the session memory (r9-mandate-20260927); approvals cite this verbatim.

## Mac local test environment (STANDING, 2026-09-27 — replaces PREPR_SKIP_CLOSURES's cause)
- The two Mac-local reds (features.py R9-F2.1 P3, optimality.py ftol) are BLAS kernel summation-order sensitivity; no macOS venv fixes them (every macOS wheel links Accelerate; CI's AVX-512 kernel SIGILLs under Rosetta). Fix: container `hpo-ci` (colima, linux/amd64, CI's exact --require-hashes wheels) + `OPENBLAS_CORETYPE=Sandybridge` — features 3474/3474 and optimality 84/84 PASS at main, zero repo changes.
- Run: `docker exec -e PYTHONPATH=/repo/tests/hastub -e OPENBLAS_CORETYPE=Sandybridge hpo-ci python tests/<script>.py`. Setup script /Users/timmalmstrom/macfloat-fix/.container-setup.sh (container needs git for structure.py). Wall clock: features ~18 min, optimality ~6 min, env_drift --all ~50 min.
- The container is Linux, so closures recording can run in-container (gate-scoping.md) — candidate retirement of PREPR_SKIP_CLOSURES=1, per-push until tvofi rules. The Sandybridge pin is load-bearing for optimality (default kernel -0.32%); a tolerance change for unpinned runs is tvofi's.
- /private/tmp was wiped by the 2026-09-27 session restart (age-based cleanup): tooling restored from this branch; keep this branch authoritative.

## Tools (/private/tmp/audit-7/orchestrator/)
- handoff_push.sh <topic> <code-sha> "<title>" [merge-main]
  - env BODYPATH= when the body filename lacks "body"; BRNAME= to update an existing PR from a -vN branch; PREPR_SKIP_CLOSURES=1 when local solver scripts fail (Mac floats); ISSUES= is auto-derived from "Fixes #N".
  - It opens a draft, adds the row, and runs in update mode when the PR exists (merges the new code in).
  - Never edit this script while a run is in flight; bash reads it as it goes.
- remerge_main.sh <pr> <worktree> <branch> <body>: when a stamp leaves a PR DIRTY on the claim files. If card_claimed_drift conflicts, keep the branch's claims with main's claims-for.
- merge_pr.sh <pr> <sha> <evidence-dir> app [issues]: evidence dirs are reverdict/evidence-<sha8>/VERDICT.md, whose first line must be exactly "# Fix review: merge <40-hex>".
- The stamp: write the ## vX section into RELEASE_NOTES.md in the main checkout listing every PR since the last tag, wait for Tests success on origin/main HEAD, then run stamp.py --bump patch --push --push-key ~/.zcode/stamp-deploy.key.

## Traps learned
- A bot commit (mutation or closures autofix) doesn't trigger the other required workflows, so the PR sits BLOCKED. Fix: merge main or re-push as the App.
- A PR whose body names a check that was red earlier (e.g. budget-raise-gate before tvofi approved) needs a Red checks line, or pr-contract goes red.
- zsh doesn't word-split $var in for-loops; use bash -c for loops over "a b" pairs.
- A standalone claims-only PR is refused (RECORD PR CLAIMS). Inherited claims ride with a fixture-moving PR or get cleared by the stamp.

---
## Older log (kept below)
# Resume: finish the v6.6.12 follow-ups, stamp v6.7.0, then round 9

Written 2026-09-25T21:45Z (last updated 2026-09-26T10:21Z) by the fix-wave thread's orchestrator (Mac, /Users/timmalmstrom/heatpump_optimizer).

## Owner instruction (read it from the source; don't trust this copy)
tvofi wrote this in the project timeline at 2026-09-25T21:35:50Z, message `cmsg_01EL5jLi4rokGBbkaevYXSJVTfeni8YJN5HdH97LdRCudt`. Read it with fetch_messages. In short:
- Finish all open work and merge it to main.
- Stamp v6.7.0.
- Start round 9 from the plan.
- Keep a resume document current.
- Work autonomously. The CODEOWNERS approval mandate lasts 12 h, until about 2026-09-26T09:35Z.
Per the coordinator, approve a code-owned PR as tvofi only after a "Fix review: merge" verdict and green CI, and cite the message id in the approval.

## Merge queue, in order

| PR | branch | head (remote) | state | next action |
|---|---|---|---|---|

Then: stamp v6.7.0 with `python3 tools/release/stamp.py --bump minor --title "..." --dry-run`, then `--push --push-key ~/.zcode/stamp-deploy.key`. Before that, add every merged PR to the RELEASE_NOTES section and make sure every merged PR has a delivery row: 1619, 1621, 1622, 1623, 1624 and the rest are owed in a batch record PR. Then tell the coordinator to start round 9.

## Merged since the v6.6.12 stamp (a3473fb8)
#1613 (61242d5c), #1609 (67a0cb98), #1605 (23eaf856, carrying #1602 and #1611), #1618 record (1cf04821), #1622 card history (1f032bd4), #1626 history shape (d1e07037), #1623 mutation speed (c12c62f3), #1627 (565ebf53), #1629 (3c93fab6), #1624 (b957521d), #1625 (7c87d69b).
#1628 (b4e31fa1). #1630 closed as superseded by #1628. #1619 arbiter (9b60705e). #1617 post-wave (7e75ebee), #1621 switch state (c182e1cb) — ledger is now per-row under tests/mutation_ledger/. Issues: only #201 is open.

## Tools and traps
- Push: `bash tools/audit/app_push.sh tvofi/heatpump_optimizer <worktree> <branch> <body.md> [issue numbers as separate args]`. Its prepr step takes the intended closing issues.
- Merge: `bash /private/tmp/audit-7/orchestrator/merge_pr.sh <pr> <sha> <evidence-dir with VERDICT.md> app [issues]`. Owner mode has an expired-mandate check hard-coded; don't use it.
- A merge that moves another PR's merge base dismisses that PR's approval. Merge main into it and re-check.
- zsh: `$b:t` is a modifier, so write `${b}` in paths.
- entities.py needs `PYTHONPATH=tests/hastub`.
- Local git 2.38 lacks newer merge-tree flags; `/usr/bin/git` is 2.50.

## Ledger collision
#1619 edits the single-file tests/mutation_budgets.json; #1617 splits it into tests/mutation_ledger/. Whichever merges second must re-merge main: #1617 re-runs --normalize and re-proves key-for-key; #1619 would use `mutation_table.py --carry-rows`.

## Now (2026-09-26 ~03:10Z)
All feature PRs merged; only #201 open. Record seat building record/v670 (worktree /Users/timmalmstrom/record-v670) + notes draft /private/tmp/audit-7/stamp-6.7.0/. Next: push record PR, add its own row, merge, then stamp v6.7.0 (--bump minor), then tell coordinator to start round 9.

## DONE 2026-09-26 ~04:40Z
v6.7.0 stamped at 81f2c18c (tag pushed). All PRs merged (#1631 record at 8dd27fe0). Only #201 open. Round 9 handed to the coordinator per tvofi's instruction.

## Round 9 readiness (from 2026-09-26 04:32Z)
The coordinator relays four handoff branches. For each: strip the last commit (tools/audit/handoff/<topic>.md is the body), push as the App, add the delivery row, merge on a relayed verdict, one at a time with --match-head-commit.
- handoff/r9-r1-find-driver
- handoff/r9-r3-verify-driver
- handoff/r9-r4-instruments (policy/code-owned; mandate approval until 09:35Z, after verdict + green CI)
- handoff/r9-r6-reboot-toggles (bug 5 reboot half + mode persistence)
All four merge before the round-9 baseline is cut.
- #1632 R4 instruments: head f493fec1 (authored 2bf7faaf + row). Policy: mandate approval after verdict.
- #1633 R1a find checker: head 1a19dd9f (authored a897272a + row). Not code-owned.
- R1 find driver: handoff/r9-r1-find-driver code a87f1ce5, stacked on R1a — push only after #1633 merges (merge origin/main in first). audit-find.js owned → mandate approval.
- Tool: /private/tmp/audit-7/orchestrator/handoff_push.sh <topic> <code-sha> "<title>" (push, retitle, row, re-push).
- Merge order: #1632, #1633, R1, R3, R6, R4b.
- #1633 R1a now 0c14689f (fixed code c6ca4132 + row). R1 new code 173061d3 (stacked on c6ca4132).
- #1634 R4b web-fragments: head 9e9bad63 (authored 26b51272 + row). Policy: mandate approval after verdict.
- #1632 R4: merge verdict at f493fec1; approve under mandate after coverage green, then merge.
- MERGED: #1632 R4 (cb78e997), #1634 R4b (16d811f1), #1633 R1a (c9453921).
- #1635 R3a: head 9534f5ec (9fd82c91 + main + row). Not code-owned.
- R1 (was 173061d3) and R3 (was 241a480f): blocked in pre-review; fixed heads coming. Push each with merge-main via handoff_push.sh; mandate approval before 09:35Z.
- R6 reboot toggles: not yet landed.
- MERGED #1635 R3a (0454645f).
- #1636 R1: head 5f7ca60d, verdict merge; mandate approval after CI green.
- #1637 RC1: head 8c7c1339 (de347318 + row); prepr.sh owned → mandate approval after verdict.
- #1638 R6 reboot toggles: df50ab42 + main + row (pushing). Not code-owned.
- #1639 R3: head 7078363b (bda239b8 + main 0454645f + row); code-owned → mandate approval after verdict; FULL CI ~40 min.
- RC1 root-cause section posted on #1633 (comment 5843568465, gh_comment.py; app_comment only takes verdicts).
- MERGED #1636 R1 (b9956289).
- BASELINE: after #1639 R3 and #1638 R6 merge (or R6 blocked → without it), stamp main (patch → v6.7.1) with notes for every PR since v6.7.0; check clean main, Tests green, delivery rows for #1632..#1639. Send coordinator the stamp SHA + version. #1637 RC1 does not gate.
- MERGED #1639 R3 (2d248e8c). R6 #1638 blocked (startup save clobbers unloaded store); opus fixer on it (await load task in async_set_mode). Then R6 merge → v6.7.1 stamp → RC2 (handoff/r9-rc2-user-state-durable f0396766) after R6.
- MERGED #1637 RC1 (b6234f2c). Remaining: #1638 R6 fix → merge → v6.7.1 stamp → RC2.
- #1638 R6 round 2 pushed ba172336 (fix b0be881f + main b6234f2c). Awaiting re-review. Forward-carry to round-9 D1: async_reset_comfort_weight + cycle-end save startup clobber on main.
- MERGED #1638 R6 (8cca77bc). STAMPED v6.7.1 = round-9 baseline at 1936d5ca (tag pushed). Next: RC2 barrier.
- MERGED #1641 RC2 (4f25b5e3), 2026-09-26, verdict r2 in reverdict/evidence-5188eb54.
- STANDING RULE (tvofi, 2026-09-26T10:19Z, cmsg_01EL5jLi4rokGBbkaevYXSJVEVXGUKMEpcz3B9PUdtNmAf): keep this doc current after every push, review, merge or stamp.
- #1642 Dependabot 66/69/70 (cryptography 48.0.1 → 50.0.1 + pyOpenSSL 26.4.0 in tests/requirements-typing.txt; tests.yml typing install gains --no-deps). Head 22aa8c35 (code 2ca7fb20 + row). Worktree /Users/timmalmstrom/fix-dependabot-cryptography-50. Touches .github/workflows, so it's code-owned and needs tvofi's own approving review (the mandate has expired). Next: CI green, then tvofi approves, then merge_pr.sh, then check the alerts auto-close.
- MERGED #1642 Dependabot cryptography (14b99f40), 2026-09-26. Check that alerts 66, 69 and 70 are fixed or closed once Dependabot rescans.
- MERGED #1643 card plan history (db878b29), 2026-09-26. Owed: 4 surviving mutants as follow-up pins (ghi step mean, overlays over covered, null denominators, askedThrough), and the D1 forward-carry for the indoor-sensor staleness gaps.
- STANDING RULE (tvofi, 2026-09-26T12:21Z, cmsg_01EL5jLi4rokGBbkaevYXSJVDC1kJ5S9ThJsYejnAXbvVc): route seats to sonnet or haiku wherever enough (CI polling, rows, rebases, log reading); opus only for fixes and reviews.
- Round 9 issues: filing the 46 class issues from handoff/audit-r9-issues@788de96d (sonnet seat). The map goes to /private/tmp/audit-7/r9-issues/MAP.json; relay it to the coordinator. Refused: D8-s2-01 and D11-s1-01 (tvofi's cards). Next: wave-1 list from handoff/audit-r9-fixplan; cloud fixers push handoff/<topic>, and I author, approve and merge.
- FILED round-9 issues #1644–#1689 (46; map r9-issues/MAP.json). #1689 closed as not planned (its only finding D8-s2-01 was refused). The D11-s1-01 refusal is noted in #1648.
- Wave 1 started (F2.1 F3.1 F4.1 F10.1 F5.1 F6.1 F7.1 F8.1 F11.1 on handoff/r9-*). F1 and F9 come after F3.1 merges. #1689 is reopened and on hold for a re-asked card; F7.3 is also on hold. Merge one at a time via handoff_push.sh, then review, then merge_pr.sh.
- STANDING RULE (tvofi 2026-09-26T19:56Z, cmsg_01EL5jLi4rokGBbkaevYXSJV5e7dweSaGdT71cUJyexT41): stamp regularly (after each wave, whenever main is green with rows for every merged PR), and drive round 9 until only #201 is open, with minimal rework.
- STAMPED v6.7.2 at 6169b74c (#1641–#1643), 2026-09-26T20:0xZ.
- Wave 1 drafts: F7.1 #1690 (verdict: merge, evidence reverdict/evidence-40b8d23c), F3.1 #1691 (head dc47e38a), F8.1 (verdict: merge, evidence-32854a9b; opening), F5.1, F11.1 and F2.1 opening, F6.1 blocked (CARD_VERSION regress). handoff_push: set BODYPATH= when the body name lacks 'body'. Merge queue: #1690, then F8.1, then #1691 (priority once it has a verdict).
- F11.1 draft #1692 at 99b31739 (code bed5b81).
- MERGED #1690 F7.1.
- Merge order: #1691 (F3.1) before F10.1 (both touch tests/finite_boundary.py). F2.1 has a merge verdict at code 3ddb2eb (body at tip 7f12b039, nit :41 -> :40). F10.1 is opening from ef0849cc.
- F10.1 verdict: merge at code ef0849cc (after #1691).
- #1691 verdict: merge at dc47e38a (merging now, then F10.1). #1694 F2.1 is on hold until backtest/optimality exit 1 is confirmed.
- #1691 BLOCKED: mutation red (1 unpinned survivor; autofix pinned 16 but pushed nothing). Back to the fixer. F10.1 is #1693 (verdict), merging first.
- The local backtest/optimality exit 1 was a missing PYTHONPATH=tests/hastub; handoff_push now sets it for prepr.
- F4.1 held (ledger vs sysid, and carries missing); its preflight also needs ISSUES='1684 1673'. #1692 is being updated to code 4634ff73; F8.1 opens from 4634a54 and F6.1 from a9e56cbe. handoff_push now has an update mode (merges the new code into an open PR's branch).
- F8.1 verdict: merge at code 4634a54 (closures exact, carry-1645 clean, entities 1961). Merge after #1694 once green.
- #1692 CLOSED (it took the bad 4634ff73). F11.1 opens fresh from bed5b81a + 5d4ee699 when that head is sent. Its branch name clashes, so use TOPIC r9-f11-governance-1 with a new BR if the remote branch still exists.
- PRIORITY (tvofi 21:52Z, cmsg_01EL5jLi4rokGBbkaevYXSJV35K1LM8w8JTwE1WAVeVEPp): the flow-setpoint hotfix (optimizer writes 25 °C to a flow-temperature set-point) goes to the front of the queue; stamp a hotfix patch right after it merges. F6.1 held for a clean head. F8.1 is being reopened with ISSUES=1674.
- F8.1 is #1696 (head c891c2dd, verdict in reverdict/evidence-c891c2dd; closes #1674). Queue: hotfix, then #1693, #1694, #1696.
- #1694 BLOCKED: stress solver-work coverage is 36/51 against a floor of 38. Back to the fixer.
- #1694: tvofi's mandate (cmsg_01EL5jLi4rokGBbkaevYXSJVQFSdhZNCSWnQPRJB1bQB3b): if coverage was not lost, the stress floor may be lowered; otherwise add coverage. Cite it in the approval if the new head lowers the floor.
- #1695 (F6.1 from a9e56cbe) CLOSED; it reopens fresh. #1691 is updated to 39ef619e (code 7d32d236).
- F11.1 is #1697 (head 10dbed86, verdict in evidence-10dbed86). Queue: hotfix, #1693, #1691, #1696, #1697, then #1694 once fixed. F5.1 is opening (intended closes from the body: #1675, #1688).
- F5.1 is #1698 (head 91940afd, verdict in evidence-91940afd, body fixed). Queue: hotfix, #1693, #1691, #1696, #1697, #1698; #1694 waits on its fixer.
- MERGED #1693 F10.1 (1ef6a805).
- #1694 is being updated to code 4169b6e8 (stress floor 38 -> 36 under tvofi's mandate). Budget file: needs tvofi's approving review after green CI. Do not merge before that.
- #1696 BLOCKED: harness_headers red (D5 wood_economics_doc_lines header 6 vs 8; D6 claims need re-recording). Back to the fixer. Next up: #1697 and #1698 (verdicts in), #1691 when its re-check lands.
- MERGED #1697 F11.1 (b5501cca).
- MERGED #1698 F5.1 (5abd5f9d); #1675 and #1688 closed.
- Verdicts: #1691 at 39ef619e, #1699 at 6403da32, #1696 (code 7ed99826, update pending), #1694 at c7525f8b (tvofi approved). Merge chain running: 1691, 1699, 1694. #1696 after its update.
- MERGED #1691 F3.1 (917f16c2) and #1699 F6.1 (7428d87a). #1694, then #1696, merging next. F11.2 opening from 3862315d (code-owned: park for tvofi).
- F11.2 is #1701 (head d5ad36e7, code 3862315d); code-owned, park for tvofi.
- #1694: budget-raise-gate red; tvofi's approval is at 8faaa523, not head c7525f8b. Asked tvofi to re-approve, then re-run the gate and merge.
- #1701 has a merge verdict at 3862315d. A hardening commit is coming: update #1701 to it, then ask tvofi to approve the final head once.
- MERGED #1696 F8.1 (62933b18); #1674 closed. Wave 1 merged: 1690 1691 1693 1696 1697 1698 1699. Left: #1694 (awaiting tvofi's re-approval at c7525f8b) and F4.1.
- F9.1 is #1702 (head 2dd9d739, code 31c971cc); awaiting its verdict.
- #1701 updated to a00a9a07 (code 7e7217d2). Awaiting the delta verdict and tvofi's approval at a00a9a07.
- #1701 verdict at a00a9a07 is written; it waits only on tvofi's approval and green CI.
- MERGED #1702 F9.1 (48b696c1). F4.1 is opening from 6799f5a2 (-1c); mutation will refuse until the autofix pins it and any survivor is triaged.
- F8.2 is #1703 (head 1f99ca16, code 91a8fc33); awaiting its verdict.
- HOTFIX (flow set-point) is opening from e2521dec (handoff/flow-setpoint-hotfix-07sk6l). Merge first on its verdict, then STAMP a patch immediately. F6.2 is opening from ff2f905a.
- F4.1 is #1704 (head 30f610f6, code 6799f5a2).
- HOTFIX is #1705 (head 305b90d3, code e2521dec). Merge first on its verdict, then stamp.
- #1704 verdict: merge at code c46d63d1 (update running). Merge after the hotfix is merged and stamped; tell the coordinator on merge so F4.2 can start.
- #1704 is at c46d63d1 (a fast-forward; the row is included). Its verdict is written. Waiting on the hotfix.
- #1703 is updated to code 9eeaae8d (F8.2 v2).
- MERGED #1694 F2.1 (058e89f1, #1666 closed) and #1701 F11.2 (399ef171). Wave 1 is complete except #1704 (merges after the hotfix).
- #1705 HOTFIX verdict: merge. Merging, then STAMP the hotfix, then #1704, then stamp wave 1.
- MERGED hotfix #1705 (6ff749d6). v6.7.3 notes are written into RELEASE_NOTES.md (uncommitted, in the main checkout). The stamp waits on Tests for main 6ff749d6 (background job). Hold #1704 until the stamp lands.
- Plan: v6.7.3 at 6ff749d6 (the hotfix, automatic once Tests are green); then merge #1704; then v6.7.4 as the wave-1 stamp once main is green. stamp.py only stamps origin/main HEAD, so #1704 waits.
- #1703 verdict: merge at 04722eb3. It lands with #1704, before the v6.7.4 stamp.
- F3.2 is #1707 (head d8742fd5c2a090347b83128f5e35f2792de433db; code 0ebf2b4b plus a main merge 02f174eb plus a claims drop 5553446d plus the row).
- HOTFIX 2 (optimizer off = no writes) is opening from a66353e6 (with main merged). Order: v6.7.3, hotfix 2, #1704, #1703, then stamp v6.7.4.
- MAIN RED at 6ff749d6: (1) backtest storage check from F2.1 (#1694), which the fixer owns; (2) inherited claims. A standalone claims-repair PR is refused (RECORD PR CLAIMS), so the repair must ride with F2.1's fix or the stamp. v6.7.3 and the queue are on HOLD per the coordinator; tvofi is being asked about --allow-red.
- HOTFIX 2 is #1708 (head ba0cd8fb; code a66353e6 plus a main merge plus a claims drop plus the row). Parked under the hold.
- F6.2 v2 verdict: merge at code d97fb547; the draft is opening. It queues after #1703.
- F6.2 is #1709 (head 90aa63f5, verdict in evidence-90aa63f5). Parked under the hold.
- #1707 verdict: merge at d8742fd5. #1709's body is refreshed (head unchanged). #1708 is updating to code 36ad4389 (verdict: merge). ORDER after the hold: F2.1 backtest fix, v6.7.3, #1708, #1704, v6.7.4, then #1703, #1707, #1709. If #1707 and the backtest fix conflict on claimed_drift.txt, rebase the second one.
- #1708 is at 81346de1 (verdict written).
- F2.2 is #1710 (head d9e806b7, code 7aa447f5). Opened with closures skipped, because the red backtest breaks the local closures recording. Parked.
- FRONT: the F2.1 storage-basin fix (code b6a708a7, branch handoff/r9-f2-storage-basin) is opening. Then v6.7.3, #1708, #1704, v6.7.4, #1703, #1707, #1709.
- The storage-basin fix is #1711 (head 39651a02, code b6a708a7). FRONT; merge on its verdict.
- #1711 blocked on 2 unpinned mutation sites; a ledger commit is coming. #1710 rebuilds after #1711 (optimizer.py conflict).
- #1711 is updated to e02ea738 (code efb4c6c4, the ledger fix). Waiting for its verdict; then merge, stamp v6.7.3, #1708, #1704.
- #1711 verdict: merge; merging now. Next: wait for Tests on main, add #1711 to the v6.7.3 notes, stamp, then #1708, #1704.
- MERGED #1711 (dbcca5fd). The v6.7.3 notes now include #1711. The stamp waits on Tests at dbcca5fd (background job); then #1708 and #1704 follow automatically.
- STAMPED v6.7.3 (tag 0989b462), release published. #1708 was DIRTY at first try; retrying. #1704 moved to 89b852db (a bot mutant pin).
- #1708 is at b4e33d52 (main merged after the stamp). Merge chain: #1708, then #1704 (at 89b852db).
- F2.2 is #1713 (head df3ed9d5, code 286560f1). #1710 is closed. Closures were skipped because features.py and optimality.py exit 1 during local recording, probably the Mac's float environment. Awaiting its verdict.
- MERGED #1708 (cfa2cb07). #1704 is at 040b1b1a (main merged, because the bot pin commit never ran 3 required workflows). Merging when green; then stamp v6.7.4.
- HOTFIX 3 coming (Boost space: heat only, with heat+dhw as the fallback; tvofi 08:22Z, cmsg_01EL5jLi4rokGBbkaevYXSJVS427AhwTHW5pg7fPWUhsDe). Front of queue; stamp once merged. Finish #1704 and v6.7.4 first.
- #1713 (F2.2) verdict: merge at df3ed9d5. Queue: #1704, stamp v6.7.4, #1703, #1707, #1709, #1713; hotfix 3 goes to the front when it arrives.
- STAMPED v6.7.4 (tag 800d7aab) with only the optimizer-off hotfix #1708, on tvofi's 'Main is green'. The wave-1 stamp becomes v6.7.5 after #1704. #1704 may go DIRTY on claim files after the stamp; if so, re-merge main.
- MERGED #1704 F4.1 (0c9c4000); #1673 and #1684 closed. WAVE 1 COMPLETE.
- NOW: merging #1703 then #1713 (bg); re-merging main into #1707 and #1709 (they went DIRTY after v6.7.4; bg via remerge_main.sh). Then merge #1707 and #1709 on green (write their relabelled verdicts), then stamp v6.7.5 = end of wave 1 plus these.
- #1707 is at 8d6a177c and #1709 at 796797c4c6ca2af37fab2a76f5fd7bc7c80a8d1e (main re-merged); verdicts relabelled.
- MERGED #1713 F2.2 (9c6b923f). #1703 was red because its base predated #1711 (backtest) and had stale card claims; re-merging main.
- Chain running (log orchestrator/chain-w2.log): #1707, #1709, #1703, then stamp v6.7.5. Any PR the chain leaves DIRTY needs remerge_main.sh and a re-run.
- C5 ledger App: BLOCKED by the auto-mode classifier. Manual steps given to tvofi (App hpo-ledger; secrets HPO_LEDGER_APP_ID and HPO_LEDGER_PRIVATE_KEY; ~/.zcode/hpo-ledger.appid and .pem; the ruleset bypass is tvofi's). Do not retry the automated flow.
- C5 DONE: tvofi created the App hpo-ledger (id 5094721), with the key at ~/.zcode/hpo-ledger.pem (0600) and the main-protect bypass set to hpo-ledger (always). I set the Actions secrets HPO_LEDGER_APP_ID and HPO_LEDGER_PRIVATE_KEY from the Mac files. The installation on the repo is not verified (that needs a JWT).
- F9.2 is #1714 (head 59b755b7, code 79eb5c41; fixes #1678). Awaiting its verdict.
- #1703 red again at 075856e6 (fast: 2 scripts; closures and closures-autofix skip-still-fails); a sonnet seat is diagnosing. #1707 and #1709 retrying (their verdict files had a malformed first line; fixed). #1714 queued after them.
- MERGED #1714 F9.2 (624db889); #1678 closed.
- MERGED #1707 (ba60afab) and #1709 (92bce7c4; #1677 closed). v6.7.5 notes are written (#1704 #1707 #1709 #1713 #1714); the stamp waits on Tests at 92bce7c4 (bg). #1703 needs md_tables.mjs wired into run.sh and derive_closures.sh (code-owned, so tvofi reviews).
- HOTFIX 3 (boost heat-only) is opening from b99fc232. FRONT. If v6.7.5 hasn't stamped, fold it in; otherwise stamp v6.7.6 right after its merge.
- F11.3 is #1715 (head 0bac0c6c; code 9dfe6a78 plus a main merge 6caf9d42 plus the row). Policy and code-owned, so it needs tvofi's approval.
- HOTFIX 3 is #1716 (head 499ef159; code b99fc232 plus a main merge plus the row). FRONT.
- #1716 HOTFIX verdict: merge. v6.7.5 is not yet stamped; its job was stopped so the hotfix folds into v6.7.5. Chain: merge #1716, then stamp v6.7.5 on green.
- #1715 is updated to 3aff22a6 (code 33a990a6). Awaiting the re-check and tvofi's approval.
- #1715 verdict: merge at 3aff22a6. Parked for tvofi's approval.
- MERGED hotfix #1716 (fdcc9a08). The v6.7.5 notes include it. The stamp waits on Tests at fdcc9a08 (bg).
- F3.3 is #1717 (head 184ca64d; code 585db36e plus a main merge plus the row). Hold until v6.7.5 is stamped.
- F4.2 is #1718 (head 3fd7705ce6a6284b5c59b22122fe650e2d087857; code 6e31dfc2 plus a main merge plus the row; body figure path fixed to the full card path).
- tvofi approved #1715 at 3aff22a6. Merge it after the v6.7.5 stamp.
- STAMPED v6.7.5 (tag c700b71c): the boost hotfix plus #1704 #1707 #1709 #1713 #1714. #1715 merge job running (bdj1dw0yd); if DIRTY, run remerge_main.sh.
- #1715: pr-contract was red (the budget-raise-gate red wasn't named, and 1648 wasn't intended). Body fixed (same head) and pushed with ISSUES=1648; merge retry running.
- The duty split is #1719 (head 3f264ba7; code 5c391eb6 plus a main merge plus the row). Priority after #1715.
- MERGED #1715 F11.3 (87d780c7); #1648 closed. F11.6 can start.
- #1703 is updated to 784d2263 (F8.2 v3 code 33877937). Code-owned: it needs the verdict and then tvofi's approval.
- #1719 verdict: merge. Merging, then stamp v6.7.6 (#1715 plus #1719).
- #1703 verdict: merge at 784d2263; parked for tvofi's approval. #1717 is blocked (a missing test), back with its fixer.
- F11.6: HOLD. A draft may be opening from 97df6851 (bg b6mopez29); leave it as a draft until the -v3 code head arrives, then update or reopen.
- MERGED #1719 (7ffcf4d8). Batching: the v6.7.6 stamp job was stopped; merge #1703 (tvofi approved at 784d2263), add it to the v6.7.6 notes, then stamp.
- F11.6 is draft #1720 (head 82079d47, from 97df6851 with the OLD body 1b0f8daf). HELD: update to the -v3 head (BRNAME=fix/r9-f11-governance-6-v2) or close and reopen if it doesn't descend.
- #1720 is updated to efde75e9 (code 8bcce59d, v3). Code-owned: verdict, then tvofi's approval.
- MERGED #1703 F8.2 (a67f4d40). STAMPED v6.7.6 (tag 36d3c27a): #1703 #1715 #1719. Open: #1717 (F3.3, back with its fixer), #1718 (F4.2, awaiting its verdict), #1720 (F11.6, verdict then tvofi).
- #1718 is blocked (mypy, stale pins, a header count) and #1720 is blocked (a ci:-commit relocation guard); both are back with their fixers. All three open PRs are waiting on new heads.
- #1718 is at c0cea583 (code 5b523977 plus main v6.7.6). #1720 is at 727d1e97 (code 02f5f81f v4 plus main). tvofi approved #1720 at an older head, so re-approval at the final head is needed after the verdict. handoff_push update mode now also merges main.
- #1720 verdict: merge at 727d1e97; waiting for tvofi's approval at that head.
- #1717 is updated to 0c6242a1 (code 6ea9e6b4 plus main).
- tvofi re-approved #1720 at 727d1e97 (12:18Z); the merge job b3zql1pkc is proceeding.
- MAIN RED (Governance) since #1715: F11.3's ruleset field compare reads bypass_actors, which the Actions token can't see. All open PRs are red on env-matrix, policy-docs and pr-contract. Sent to the F11 fixer as top priority. #1720 is approved but blocked on this.
- #1718: briefs is also red (carry-1395's sysid.py:1258 citation moved to line 81 after F4.2); sent to its fixer.
- #1718 is updated to e38ecc4e (code 3afc8ff8; carry re-anchored).
- The Governance fix will come on handoff/r9-f11-hotfix-ruleset-absent (F11.3's fixer); FRONT, then #1720 (re-merge main first).
- The Governance HOTFIX is #1721 (head 43517c5f, code ea22db6c). FRONT. Code-owned: needs tvofi's approval. It will show 3 expected reds (base-restored graders), and merging over them needs tvofi's explicit words.
- tvofi approved #1721 and OK'd merging over the reds (12:37Z, cmsg_01EL5jLi4rokGBbkaevYXSJVWSbRbVvspUGcoYnwy4gBxc). Merge once the compute helper's verdict names 43517c5f and all checks except policy-docs, env-matrix and pr-contract are green.
- #1721 is HELD: blocked at 43517c5f (its skip line would keep env-matrix red on main). A new head is coming; tvofi must re-approve it.
- F1.1 is #1722 (head e748d389; code a30bf2d6 plus a main merge, an inherited-claims drop and the row). Critical path.
- #1721 is updated to 2044829e (code 39bc45fe, v2). It needs a verdict and tvofi's re-approval at 2044829e; expected reds are policy-docs and env-matrix only.
- #1721 verdict: merge at 2044829e (not code-owned). A merge with --admin is running, but only if the reds are exactly env-matrix and policy-docs (tvofi's OK). Then stamp a hotfix, re-merge main into #1720, and merge it.
- #1721: the verdict is posted. The admin merge over required reds was BLOCKED by the classifier, so tvofi must merge it with the bypass. After: stamp, re-merge main into #1720, merge it.
- #1717 verdict: merge at 0c6242a1. Order: #1721 (tvofi merging by hand), then its hotfix stamp, #1720, #1717.
- MERGED #1721 (8b61aed3) by tvofi with the bypass; ruleset 23698884 is restored to DeployKey only (verified). Stamping v6.7.7 once main is green, then #1720 (re-merge main), then #1717.
- #1718 is updated to 7fe356f6 (code 879c49ae plus main 8b61aed3). #1722 is blocked (a missing DST pin), back with its fixer.
- #1722 is updated to f13b5523 (code 1668198a plus main).
- STAMPED v6.7.7 (tag cdbc2584); main's Tests and Governance are green. Next: re-merge #1720, merge it, then #1717.
- #1720 is at bf2723bc (main v6.7.7 merged); it needs tvofi's re-approval at bf2723bc.
- #1718 verdict: merge at 7fe356f6. Queue after #1717 and #1720: re-merge main, then merge (issue 1672).
- #1722 verdict: merge at f13b5523 (critical path, unlocks F1.2). Chain: after #1717, then #1722, then #1718 (each re-merged). #1720 merges independently on tvofi's approval.
- The resume note and scripts are pushed to origin handoff/mac-merge-seat-resume (d25bbe35). Re-push that branch after each state change.
- 2026-09-27T18:1xZ #1724 CI: three reds (mutation, mutation-autofix, pr-contract) = one root cause (3 unpinned survivors); fixer told to name both check names + run --pin-killed. #1723 fast(3.14) red root-caused: sysid frontier harness hit harness_headers' 240s subprocess timeout (F4.2+F2.3 combination, real: 182s vs 55/46s single); F2.3 fixer's float-identical runtime fix at f0847ae6 (~2.3x), round-2 review dispatched.
- 2026-09-27T18:15Z tvofi 14h mandate recorded (above). Stop-hook caught the #1725 seat working in the ORCHESTRATOR's worktree (its branch checked out over the session tree; its tests/README.md edit +420 tokens over the files_tokens cap) — edit recovered to /private/tmp/audit-7/seat-1725-recovered/, worktree restored, policy_lint 0 errors; seat ordered to relocate to its own worktree and PAY FIRST on the cap.
- 2026-09-27T18:5xZ mandate EXTENDED (tvofi): "your mandate is, on an exceptional basis, extended to the completion of the full programme, maximum 35h. THIS SESSION ONLY." Expiry: completion or 2026-09-29T05:15Z. Remaining plan: 27 roster PRs + #1725, closes all 30 open class issues; F1 lane is the critical chain; est. 24-32h. Stamp plan ~one per 4-6 PRs; programme-close stamp bumps minor (v6.8.0).
- 2026-09-27T19:4xZ STAMPED v6.7.8 (5 PRs: #1717 #1718 #1720 #1722 #1723) on green main 2eef524d; wood_coil claim expired by the bump. F2.5 opus seat running from 2eef524d. #1724 fixer iterating (typing+mutation pins, head 4190b610). #1725 seat building. Records at roster ba1f6392 / mirror a04b2e13.
