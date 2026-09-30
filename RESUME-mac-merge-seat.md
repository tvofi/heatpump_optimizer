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
