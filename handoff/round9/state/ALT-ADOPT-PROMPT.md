# Prompt (rev 2): the round-9 fixing orchestrator adopts the ALT endgame plan's rev 2

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting;
nothing below loosens them.

**The background.** You adopted rev 1 of the ALT endgame plan on 2026-09-28: roster deltas at
`handoff/audit-r9-fixplan` `0f1f5263`/`27049219`, record PR #1749. After the EG-B0 root-cause analysis (RCA-1736),
tvofi commissioned a follow-up. Its results are rev 2, on branch `handoff/audit-r9-alt`:

- `handoff/round9/state/ALT-ENDGAME-PLAN.md` (rev 2):
  - §2.3: the new findings;
  - §4: the schedule regenerated from roster rev 2;
  - §6: adoption;
  - §7: the owner decisions.
- `handoff/round9/state/ALT-ROSTER.json`: roster rev 2, the live roster plus the deltas below. It lints with
  `TOTAL: 0 error(s)`, is acyclic, and has 66 groups. `alt/build_roster_rev2.py` rebuilds it from the live file.
- `handoff/round9/state/alt/SCREEN-1736-SHAPES.md`: the shape screen, with its probes in `alt/evidence/screen/`.
- `handoff/round9/state/alt/register/`: register v2.
  - `bugclasses.v2.json` (commit `53a9bbab`), built by `build_v2.py` from `rows_v2.tsv`; run `--check` to verify. It is 574 rows, including 88 round 1–7 survivors the old source omitted (`RECON.md`).
  - `REGISTER-V2.md`.
  - `RCA-INVENTORY.md`.
- `handoff/round9/state/alt/rca/RCA-BULK-1..4.md`: the owed RCAs, conducted in bulk, with their helpers.
- Issues #1752 to #1760: filed, read back, and each carrying its disposition. #1736 carries the screen addendum
  (comment `5879641429`).

Read the plan's §2.3, §4, §6 and §7 and the four bulk RCAs before step 1. The rev 1 rules and the ratchet stance
(§3) stand.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `5a2a62ff` (rev 2 is current to it: #1750 re-checked, F1.5 in review as #1751, F7.2 fixing).
   - Apply each to roster rev 2's `resume` fields.
   - If a merge touched a file a new carry or brief cites, re-run
     `node .claude/workflows/brief_lint.mjs <roster>` with the evidence refs fetched: `handoff/audit-r9-evidence`,
     `handoff/audit-r9-sweep-*`, `handoff/r9-rca-*`, `handoff/r9-eg-b0`, `handoff/audit-r9-alt` and
     `handoff/audit-r9-plan`.
   - It must print `TOTAL: 0 error(s)`.

2. **Adopt roster rev 2** on `handoff/audit-r9-fixplan`: replace `.claude/workflows/wave-r9-groups.json` with
   `ALT-ROSTER.json`.
   - If the live file moved after `27049219`, run `alt/build_roster_rev2.py <live> <ALT rev-1 roster> <out>`
     instead. It applies:
     - resume truthing: the live file shows 17 merged groups as `not-started`, and has EG-B0's `rca-done` on EG-B1;
     - carries into R9-EG-B1, F1.7, F1.8, F2.4, F10.3, F10.4 and F11.4;
     - new groups: EG-B9, EG-B10, EG-R0, EG-R1, F7.4, F10.1c, F10.7 and F11.7;
     - edges: F1.6 after EG-B9; EG-B1 after EG-B9 and EG-B10.
   - **Then assert that every group whose PR is merged on main reads `done`.** The 17-group regression reappeared
     after rev 1's adoption, so something in regeneration or merging still drops them. Find it and fix it, or stop
     regenerating.
   - Lint and read back.

3. **Land one record PR** via `tools/audit/app_push.sh` (never `push.sh`):
   - disposition #1752 to #1760 in the plan of record (`delivery-status-tracking.md` step 5);
   - correct #1070's row, which says "root-cause seat in flight": no seat ran, and the band landed as #1124;
   - give the PR its own `docs/delivery/<N>.md` row.
   - It adds no budget and no `VERSION` edit.
   - Every new carry lives in a roster brief whose stage has not started, so no carry file is owed. If one of
     those stages starts before the roster lands, the carry goes in-tree first (`finding-propagation.md`).

4. **Post one #201 comment** with `.claude/workflows/gh_comment.py post` and read it back. It says:
   - rev 2 is adopted;
   - the roster SHA;
   - EG-B9 is sev:high and next in the F1 slot;
   - register v2 awaits tvofi's review;
   - what is dispatched now.

5. **Dispatch.**
   - **F1.5 is in review** (PR #1751, CI green at `e3ad93d0`). When it merges, **R9-EG-B9 is next** in the F1 slot, and F1.6 waits for it.
   - **F7.2 is being fixed** (`handoff/r9-f7-entities-2`); F7.4 follows its merge.
   - Then follow §4, one merge at a time, respecting every `after` edge.

## Rules specific to rev 2

- **R9-EG-B9 (#1752, #1753) is a sev:high behaviour fix.**
  - Normal fix protocol: failing tests first (`alt/evidence/screen/S1.py` and `S2.py`, probe arms against null arms),
    then mutation proof.
  - The Root cause section on #1752 is owed (trigger 1). RCA-1736 supplies the class cause and process state; the
    section adds this instance's escape and cost.
  - Do not wait for stamp point (c) to release it. Stamp at the next point after it merges (FIX-PLAN's point (b)
    follows F1.6).
- **EG refactors still never block an F lane.** EG-B9 is the one exception, and it is a behaviour fix.
- **R9-EG-B10 (#1754, #1755)** lands after EG-B9 and F1.6, and before EG-B1 (plan principle 3).
- **R9-EG-R0 is data only.** It needs tvofi's review of the move list and the open questions in `REGISTER-V2.md`
  before merge:
  - copy `bugclasses.v2.json` over `tools/audit/bugclasses.json`;
  - move the `class_guess` enum in the same PR;
  - put the RCA documents under `tools/audit/rca/` (the 14 round-9 class RCAs from `763b0ba4`, RCA-1736 from
    `08304c9a`, and RCA-BULK-1..4).
  - Run `build_v2.py --check` before copying.
  - If a round's findings are classified before R0 lands, add them through `rows_v2.tsv`. Never hand-edit the JSON.
- **R9-EG-R1 is owner-gated.** Its four policy clauses (judge.md, defect-root-cause.md, where an RCA is recorded,
  D8.md) are asked of tvofi before the push. `audit-verify.js` and the briefs are code-owned.
- **Carries.** Carries already in roster briefs bind their fixers:
  - F1.7: the P10 kernel-count barrier;
  - F1.8: the P8 feed currency (ask tvofi about the displayed currency before the push);
  - F2.4: the P4 refusal (no class widening);
  - F10.3: the I2 strace oracle;
  - F10.4: structure-blind reachability, and the `qs_py_typed_files` check;
  - F11.4: `merge_shape_guard`; the N-silent-zero barrier is tvofi's call;
  - EG-B1: H1–H4 and P12.
- **Rev 1's rules stand:**
  - structure-budget writers are serialised (EG-B5a, EG-B5, EG-B1, EG-B7);
  - B1 lands after stamp point (c);
  - B5 per `alt/EG-B5-DESIGN.md`;
  - EG-B8 before EG-B5;
  - raises confirmed before the push and merged on tvofi's approving review.
- **Mandate.** It expires 2026-09-29T18:15Z. W0 and W1 fit inside it, including EG-B9. Everything owner-gated
  after that waits for renewal.

## Stop and ask tvofi when

- a §7 owner decision is reached;
- `brief_lint` is non-zero after re-basing, and the fix would weaken a citation instead of correcting it;
- a merge since `5a2a62ff` changes what the screen, register or RCAs measured (the boost overlay, the in-flight
  guard, the DST tracer, the currency resolver, the entity names);
- the resume-truthing assertion in step 2 fails again after a regeneration.
