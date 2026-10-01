# RESUME — Mac merge seat (round-9 programme orchestrator)

**State as of 2026-09-30T08:0xZ (owner-directed graceful stop).** Verify everything marked LIVE with `gh`/`ls-remote` before acting — this document outranks nothing over the API.

## Mandate — RE-OBTAIN AT SESSION START

tvofi's mandate ("approve as CODEOWNER/tvofi on policy changes and budget raises as last resort, design choices = recommended; drive the programme to completion") was granted FOR THAT SESSION ONLY and died with it. Rev-3.1 adoption (this session) restated: all decisions given per plan §7; **what remains for tvofi's hands: approving reviews at the head on code-owned + budget-raising merges, repo-settings changes, F10.5's writer identity**. Ask tvofi to re-issue the mandate for the new session; the rev-3.1 prompt's framing (request reviews, never wait silently) governs meanwhile.

## Authoritative artifacts

- Roster rev 3.1 (73 groups): `handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json` — head **beyond `5736fd48`** (stop-truthing pushed last); resume fields are the per-group truth; W0 stages fixing/in-review.
- Plan of record: `handoff/audit-r9-alt:handoff/round9/state/ALT-ENDGAME-PLAN.md` (rev 3.1 §2.4/§4/§4.6/§6/§7 read); pre-study `92b3ecc9` under `alt/archscore/`.
- Everything else per FIX-PLAN §11 (seat branches + resume notes + this branch).
- #201: newest comments are the live coordination record (rev-3.1 adoption note 5901542942; EG-L0 settings ask 5902383542; raise notes 02:12Z/5903942263-patched).
- Scratch: /private/tmp/audit-7/ (orchestrator scripts here: merge_pr.sh now accepts UNSTABLE at the final gate; merge1779.log etc). **Worktrees under /private/tmp and /Users/timmalmstrom/<name> get pruned by worktree_gc if clean+detached — re-create from the remote branch; never trust a local /tmp worktree.**

## Merged & stamped this session

- **v6.7.11 stamped + tagged** (15 PRs since v6.7.10; notes written by hand first — stamp.py needs `--bump patch --title` + a `## v<next>` section covering every merged PR).
- **#1773** row-#1767 → `bd79bc9e`; **#1778** rev-3.1 record corrections → `9d578722`; **#1780** EG-L0 (31 legacy verdicts: 29 closed, #1196 not_planned, #1655→F1.7 carry, #1183→EG-B6 carry after a caught carry-missing block) → `a15e3e33` = current main head at stop (verify: main may have moved).

## In flight — what the next session does, in order

1. **F7.5 (#1777 family-split renames)**: hand-off COMPLETE, head `ef8fc20cc2e65f32b8155071c54a92aed0aa383d` on `handoff/r9-f7-family-splits` (LOCAL in /private/tmp/audit-7/f7-5/wt + possibly unpushed — `git ls-remote` it; if gone, the seat's stop-message was to push+report; failing that rebuild: branch was NOT on remote at stop). **app_push REFUSED on prepr with the reason undiagnosed** — first act: `cd <worktree at head>; bash tools/audit/prepr.sh <body> <head>` and read the refuse lines (seat ran it green minutes earlier; likely a freshness/bitmask step). Opus reviewer has interim findings at /private/tmp/audit-7/review-f75/INTERIM.md (check) — re-dispatch at the final head after the PR opens. Seat's findings to carry: tests/entities.py NOT code-owned (verified with positive control); the strings.json-vs-en.json entity-parity gap **is already carried into R9-F11.4's brief** (roster commit after 5736fd48; route (b) refused per RCA-BULK-4 §2).
2. **EG-B10 (#1779, PR OPEN, mergeState BLOCKED)**: round-2 head `6e062c77` review-merged (verdict comment posted; tvofi already approved at that head; raise-gate GREEN there) BUT the required `mutation` lane refused: 8 new unpinned sites; the autofix bot reported skip-no-measurement (human path — pin yourself). Seat resumed to disposition sites in hpo-ci (pin killed / killing checks / diff-probe triage; NEVER --triage-survivors) and was stop-directed: its branch state + note are the source. After its pin commit: re-dispatch reviewer round 3 at the new head; **tvofi's review must re-land at the new head** (post the gh command: human-worded, cites five caps 154/9034*/116/308/9034* — re-derive values at the head, caps must equal measured, disclose +3-line delta handling). mutation + budget-raise-gate are REQUIRED contexts; merge via merge_pr.sh app mode when verdict+green.
3. **F2.4** (critical path): seat stop-pushed its branch (handoff/r9-f2-solver-4 per roster; verify ls-remote + its note). Resume seat or await its hand-off message; on merge: F1.7 (now carries #1655's P5 remainder) ∥ EG-B8; F2.4's stress/coord table re-record question: check its note.
4. **F9.3**: fresh opus seat (predecessor died API input-length 400) executing the design recorded on branch handoff/r9-f9-test-pins-3 @ `ac66363d` note (DOMAINS table in store.py, Arm 6 failing-test-first in tests/finite_boundary.py, loader fixes, 29 float sites, _poisoned "1e999"); stop-directed sync same.
5. Then follow plan §4: F1.7→F1.8→F1.9→F1.10→F1.11→…→F10.4 (A1 truthing + R3-2 retirement of classes_over_300 — the #1738 arm (c) decision is GIVEN, no raise) →W4/5 EG lanes → EG-A4 last. Stamp points: (b) after F1.6+batch rows — v6.7.11 covered it; (c) at W4 end (v6.8.0). EG-B5a before EG-B5; EG-B8 before EG-B5; EG-B10 before EG-B1; B1 after stamp (c); EG refactors never block F lanes.

## For tvofi's hands (request, never wait silently)

- Approving reviews at head: any code-owned (`tests/closure.py`, `derive_closures.sh`, `stress.py`, `mutation_table.py`, `audit-find.js`, `mutation_table.py`, `.github/workflows/*` etc — verify per PR with CODEOWNERS resolver, and note F7.5's finding that tests/entities.py is NOT owned) and every raise.
- Settings: hpo-ledger bypass actor on ruleset 22628467 — ratify+document (fixture extension) or clear (comment 5902383542 has both arms); #1191/#1193/#1196 proved/fixed via EG-L0 (1191 FIXED split, 1193 FIXED 0011/0013, 1196 owner-declined not_planned) — nothing owed there anymore.
- F10.5 writer identity (new App + credential, decision 0011) — needed before F10.5 dispatch (W8).
- EG-A4 required-context add (last PR of programme).

## Standing traps (each already cost something this programme)

- Compaction summaries fabricate PR numbers/comment ids — verify via API every session start.
- Lint/gates from stale worktrees give phantom errors — run from an origin/main-fresh tree.
- Verdict grammar for app_comment.sh: `Fix review: merge <40hex>` / `Fix review: blocked <40hex> <single-token-class>: <why>` (hyphen ok, plus-not).
- gh_comment.py: actions post/patch/verify; `--repo --issue --body-file`; body file must live in a seat subdir; read-back is the proof.
- Head moves under an open review = the review dies (price it, re-dispatch delta-scoped).
- Merge message: titles reach main (merge commits); "leaves #N open" wording, never negated Fixes; preflight before merge, verify closes AFTER.
- Three-dot diffs everywhere; claim files: a branch claiming nothing leaves them byte-identical; DIRTY with zero check-runs → remerge_main.sh local absorb.
- mutation lane: run --pin-killed ONLY in canonical hpo-ci env (Sandybridge pin), gate_lock lease host-side labelled.
- Seat transcripts die two ways: watchdog stall (resumable via SendMessage) vs API input-length 400 (UNRESUMABLE — fresh seat from pushed branch + note). Third infra death this session = root-cause.md seat owed.

## Worktrees/branches at stop

Local dirs likely pruned by gc — remote branches are truth: handoff/r9-f7-family-splits (maybe — unpushed at stop, check seat messages), handoff/r9-eg-solve-lifecycle (#1779), handoff/r9-f2-solver-4, handoff/r9-f9-test-pins-3, plus fix/row-1767, fix/record-rev31, handoff/r9-eg-l0 (all merged+gc'd). fixplan-adopt2 (/tmp) = disposable scratch clone of fixplan branch.

## SESSION 2026-09-30T07:1xZ (continuation) — live log
- Mandate: asked tvofi in the fix thread (cmsg_01EL5jLi4rokGBbkaevYXSJV4FTJyQomqknUmb92uUcyXt); answer pending. #201 "session resumed" line is owed once answered.
- Verified: main a15e3e33; fixplan 1ab27f31; F7.5 ef8fc20c; EG-B10 6e062c77; F2.4 b9f86fb5; F9.3 ac66363d.
- F7.5: the prepr refusal was closures (features.py exit 1 = Mac floats). Opened #1781 with PREPR_SKIP_CLOSURES=1 (CI records); head 9e7fbc3a (ef8fc20c plus the row). Opus reviewer dispatched at 9e7fbc3a.
- Seats dispatched (opus): EG-B10 mutation disposition (8 sites, hpo-ci); F2.4 resume from its note; F9.3 resume from its note. Seat block: /private/tmp/audit-7/SEAT-BLOCK-r9.md.

## LIVE STATE 2026-09-30T20:15Z

- main 5dfa6684 (#1788 F1.7 merged; #1655, #1658 closed). Last stamp v6.7.12 (754d2319); next stamp after this batch.
- Open: #1792 policy cite-CI (fix-review.md step 11), head 2de73776, Mac worktree /Users/timmalmstrom/pol-review-reuse, branch fix/review-cite-ci. Waiting on an opus cloud reviewer, then code-owner approval under the mandate, then merge.
- Cloud fixers: R9-F1.8 (opus, handoff/r9-f1-coordinator-8), R9-F10.1b (sonnet, handoff/r9-f10-1b), both on base 5dfa6684; R9-UI-1 (sonnet). Roster handoff/audit-r9-fixplan 1c3558f0: 42 done, 47 not-started; nothing else is unblocked.
- Merge-gate rule (tvofi 20:00-20:10Z): reviewers cite the head's CI and never re-run the gate or mutation table. Merge only on CI green at a head containing current main; if main moved, merge main and wait. Balance speed against first-pass yield: 2-3 verdict-ready PRs per main merge, one at a time after a red; dispatch in parallel only non-overlapping groups whose after-edges are met.
- Worktrees on the Mac: the main checkout plus pol-review-reuse; nothing else.

## LIVE STATE 2026-10-01T04:58Z (restarted Mac session)

- main d62b99a5; roster 404ea756 (45 done).
- #1799 F1.8 at 65814159 (contains main): all green except budget-raise-gate (red pending owner review). Round-6 merge verdict posted as hpo-approver, comment 5924987560, read back identical; it affirms the 116→117 raise as architecturally right.
- Mandate: NOT yet re-confirmed for this session. Asked tvofi in the fix thread (cmsg_01EL5jLi4rokGBbkaevYXSJVTfLK8mjBTxvGekKRYxRv52). On "yes": approve as tvofi at 65814159 (grounds only), confirm budget-raise-gate green, merge --match-head-commit, roster F1.8 done, then dispatch F10.2 (opus) + F10.1c (sonnet), then F1.9 + F6.3.
- Nothing else dispatchable: EG-B0 is rca-done with no next step.

## LIVE STATE 2026-10-01T05:32Z

- Mandate re-granted for this restarted session: tvofi "Yes" 05:03Z (cmsg_01EL5jLi4rokGBbkaevYXSJVS8fNNhePWz99QDCstHr3RM). The auto-mode classifier denied `gh api POST .../reviews APPROVE` as tvofi, so tvofi approved #1799 themselves and added `"permissions":{"allow":["Bash(gh pr review *)"]}` to ~/.claude/settings.json. From the next session, approve with `gh pr review N --approve --body ...`, not gh api.
- #1799 F1.8 merged 6793659c (it was still a draft: run `gh pr ready` before merging). #1657 closed. Roster ada74d99 marks F1.8 done.
- Ready set sent to the coordinator for dispatch, all parallel: F10.2 (opus), F1.9 (sonnet), F6.3 (opus per its brief text), F10.1c (sonnet). The only shared files are bugclasses.json and S5.json, which are append-only.
- No PRs open from this seat. Next: post the hpo-approver verdicts as they arrive, merge in batches of 2-3, and after each merge mark the roster and dispatch the next group (F1.10, F6.4, F10.3).

## LIVE STATE 2026-10-01T08:56Z

- main 404a5fb0. Merged this session: #1799 F1.8 (6793659c), #1802 F6.3 (cc00ed85), #1803 F10.2 (a413832a), #1805 F1.9 (404a5fb0). Closed #1657, #1652, #1656, #1653, #1660. Roster 80f16eb0; F10.1d was added (after F10.1c) to own F10.1c's 10 unowned DST raw sites, plus build_override's cap compares and is_expired.
- Open: #1804 F10.1c at 733f6f35, which is code e26fa13b (round-2 merge verdict 5927429501) with main 404a5fb0 merged in. Delta review and CI are running. Approve on the delta verdict, merge on green, then dispatch F10.1d.
- Fixers in flight (cloud): F6.4 (sonnet), F10.3 (opus), F1.10 (opus).
- Working method:
  - Approve as tvofi with `gh pr review N --approve` as soon as the merge verdict lands (tvofi 08:42Z); the merge waits for green CI at a head that contains main. `gh api .../reviews` is classifier-denied.
  - app_push opens PRs non-draft; I run `gh pr ready --undo`, then `gh pr ready` before merging.
  - Every merge of main into a PR head needs a `## Head` line naming the new SHA, or pr-contract refuses the body.
  - Verdicts arrive via the coordinator; I post them with app_comment.sh using the 40-hex grammar.
  - Real-HA ha_contract (nightly-ha is skipped on PRs) runs natively: venv /private/tmp/audit-7/r9-mac/ha-venv (Python 3.14.7, HA 2026.9.3), `env -u PYTHONPATH ../ha-venv/bin/python tests/ha_contract.py --emit-probes X/real.json --contracts-only`, then the stub run and `--compare`. The hpo-ci container was deleted on 2026-10-01.
  - Batch rule: after each merge, merge main into the next verdict-ready PR once, then let the reviewer judge that delta.

## LIVE STATE 2026-10-01T09:22Z

- main 787fe137 after #1804 F10.1c merged; #1756 closed. Roster 4f1c0f97.
- **Close-out decision (tvofi 09:18Z):** the final stamp when only #201 remains is **v7.0.0** (semver). Intermediate wave stamps stay 6.7.x. A fixer seat authors the notes, and stamp.py stamps after the merge. Recorded in the roster's `decisions`.
- Open: #1806 F6.4 at 0077ab5a, which is code f95051f4 with main 787fe137 merged in (coordinator.py and features.py auto-merged; the tree equals merge-tree). Real-HA 61/61 at f95051f4. The reviewer is on the code head; the delta is owed after.
- Dispatch owed: F10.1d (after F10.1c, now met). In flight: F10.3, F1.10.

## LIVE STATE 2026-10-01T13:17Z

- main 2f2b167d. Merged since 09:22: #1806 F6.4 (f67f598a, closes #1687), #1809 F10.1d (2f2b167d). Roster 6167b7ef or later. Session total: #1799 #1802 #1803 #1805 #1804 #1806 #1809.
- Open, all approved as tvofi, waiting on CI plus delta review after the re-merge of main 2f2b167d:
  - #1810 F10.3 at 8dbfbc14 (closes #1646, #1663, #1748; stray branch `f10-3` at 64b4bc24 to delete after the merge)
  - #1808 F1.10 at 6bb4e471 (closes #1654, #1741)
- Fixers in flight: UI-3 (opus), F10.8 (opus, plus an RCA seat: carried claim lines are no-claim, ported to env_drift.py and card_drift.mjs), F10.1e (sonnet, the 14 DST misfires plus deleting the stray BODY.md).
- Tools: /private/tmp/audit-7/r9-mac/mergemain.sh `<wt> <branch> <body> <codehead8> <issues>` merges main and refreshes the Head line. dropclaims.sh runs `--drop-inherited`, needed until F10.8 lands, when prepr refuses INHERITED CLAIMS. Merge rhythm: after a merge, `gh pr ready`, wait about 20 s for CLEAN, then merge.
- Close-out stamp: v7.0.0 (tvofi 09:18Z).

## LIVE STATE 2026-10-01T18:45Z

- main 25e5b9cc. Merged 2026-10-01, in order: #1799 #1802 #1803 #1805 #1804 #1806 #1809 #1810 #1813 #1814 #1811 #1815 #1818 #1819 #1817 #1821 #1820 #1822 #1816.
- **tvofi adopted the process review (16:51Z, all ten items; on item 2 "both").** Roster groups: PROC-1, PROC-3 and PROC-5 are merged; PROC-4 (git bus) is in flight; F10.9c (merge queue 2A, fast path 2B, cancel item 3) is stacked as #1823 (stage 1), stage 2 (not opened) and #1824 (stage 3); F10.9d (closure recorder for run_always reads) runs after F10.9c. Enable the merge queue on main-protect 22628467 only after stage 2's merge_group lands; merge method MERGE; no new bypass on 23698884.
- **Working rules now:**
  - Delivery rows are mine at open (addrow.sh).
  - Clean merge-deltas carry with no reviewer turn (carry.sh), requiring tree = merge-tree, no same-file change, and claims equal main or unchanged from the verdicted head.
  - Skip a re-merge only on closure-set disjointness. Run_always readers (harness_headers, entities) make doc and policy changes non-disjoint.
  - On tvofi's 18:27Z "green and approved but not merged", automerge.sh merges each approved PR as soon as it is green, without re-merging; main's FULL push is the backstop, and a red main is reverted first.
- Tools in /private/tmp/audit-7/r9-mac: openpr.sh, movepr.sh (tolerates delivery rows, adds a Head line when PR head != code head), mergemain.sh, carry.sh, addrow.sh, automerge.sh; real-HA venv ha-venv.
- Open: #1823 (auto-merging), #1808 F1.10 (main carried for the F10.11 fix, auto-merging), #1824 (auto-merging after #1822). Seats in flight: UX-1, PROC-4, F10.9c stage 2.
- Close-out stamp v7.0.0 when only #201 remains.
