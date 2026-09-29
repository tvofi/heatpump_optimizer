# Prompt (rev 3): the round-9 fixing orchestrator adopts the ALT endgame plan's rev 3

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md` before acting.
Nothing below loosens them.

## Background

You adopted rev 2 of the ALT endgame plan. The live roster on `handoff/audit-r9-fixplan` (`c5af8f3a`) carries its 66
groups, and EG-R0, EG-B9, F7.4 and F1.6 (#1767, `f88e6af8`) have merged.

tvofi then commissioned a pre-study of an architecture score, a plan to improve it 2× honestly, and this revision.
They are all on branch `handoff/audit-r9-alt`:

- `handoff/round9/state/ALT-ENDGAME-PLAN.md` (rev 3):
  - §2.4: the score, its calibration and the 2× plan;
  - §3: one added bullet;
  - §4: the schedule regenerated from roster rev 3, with expected ΔS per PR;
  - §6: adoption;
  - §7: the decisions R3-1 to R3-6, with rev 2's still-open decisions.
- `handoff/round9/state/ALT-ROSTER.json`: roster rev 3, commit ROSTER_COMMIT.
  - It is the live roster plus the deltas in `alt/build_roster_rev3.py`.
  - 70 groups, acyclic, and `brief_lint` prints `TOTAL: 0 error(s)`.
- `handoff/round9/state/alt/archscore/`: the pre-study, commit PRESTUDY_COMMIT.
  - `PRE-STUDY.md`;
  - its evidence: `a1/` (metric perturbations), `a2/` (the historical corpus), `a3/` (nine new metrics),
    `b/` (score, weights, calibration, gate variants, sensitivity, trajectory, 2× arithmetic) and `redteam/`;
  - `status/LIVE-STATUS.md`: the live status at `4d33b25c`, and seven disagreements between the record's sources.
    F1.6 merged after it; rev 3 is re-based to `f88e6af8`, where the score vector is unchanged (#1767 scores ΔS 0).

Before step 1, read the plan's §2.4, §4, §6 and §7, and the pre-study's §1, §6, §7 and §8. The rules of rev 1 and
rev 2 and the ratchet stance (§3) stand.

## Steps, in order

1. **Re-base.** List every merge on origin/main since `f88e6af8`. Rev 3 is current to it: 34 groups merged, F1.6
   last, as #1767.
   - Apply each merge to roster rev 3's `resume` fields.
   - If a merge touched a file a rev-3 carry cites (`away.py`, `boost.py`, `pump_arbiter.py`, `sensor.py`,
     `thermal_model.py`, `config_flow.py`, `optimizer.py`, `tests/structure.py`), re-measure that carry's figure with
     the prototype at PRESTUDY_COMMIT and correct the figure, not the citation.
   - Re-lint with `handoff/audit-r9-alt` and the evidence refs fetched:
     `node .claude/workflows/brief_lint.mjs <roster>` must print `TOTAL: 0 error(s)`.

2. **Adopt roster rev 3** on `handoff/audit-r9-fixplan`: replace `.claude/workflows/wave-r9-groups.json` with
   `ALT-ROSTER.json`.
   - If the live file moved after `c5af8f3a`, run `alt/build_roster_rev3.py <live> <out>` instead, and replace
     `PRESTUDY_COMMIT` in its output with the pre-study commit. It applies:
     - F1.6's resume truthing (done at `f88e6af8`);
     - the carries into F10.4, EG-B1, B2, B3, B5, B6 and B7;
     - the new groups EG-A1, EG-A2, EG-A3 and F7.5.
   - Find out why the live file kept F1.6 `not-started`, with an empty commit, through two review rounds. The
     record must move at each state change (`delivery-status-tracking.md`).
   - Assert that every group merged on main reads `done` at its merge SHA.
   - Lint, then read the result back.

3. **Land one record PR** via `tools/audit/app_push.sh` (never `push.sh`). It fixes what `LIVE-STATUS.md` found:
   - the disposition rows for #1752/#1753, #1759, #1760 and #1736 in `docs/plan-2026-09-open-issues.md`;
   - `docs/delivery/1771.md`, which says "open";
   - `tools/audit/round9/fixplan/standing.md`, which lacks the "Enumerators run INSIDE the tree" rule;
   - `tools/audit/round9/prestudy/ALT-ROSTER.json`: label it a rev-2 snapshot or remove it.
   - Give the PR its own delivery row. No budget, no `VERSION`.

4. **Comment on #1738** with the eleven verified metric defects from the pre-study's §2, each with its perturbation
   and null. Post it with `gh_comment.py` and read it back. File no further issue for them: they are carried in
   F10.4's brief.

5. **Post one #201 comment** with `gh_comment.py` and read it back. It says:
   - rev 3 is adopted, with the roster SHA;
   - F1.6 merged (#1767), and the v6.7.11 stamp (EG-B9, sev:high, and F1.6 are unstamped);
   - the score is proposed as report-only and awaits R3-1 to R3-3;
   - what is dispatched now.

6. **Dispatch.**
   - Stamp v6.7.11 first (`web-stamp`).
   - Then F2.4 ‖ F9.3 ‖ EG-B10, and follow §4, one merge at a time, respecting every `after` edge.
   - Issue files for EG-A2 and EG-A3, and for F7.5 on renames, wait for tvofi's approval of those groups (R3-5, R3-4).

## Rules specific to rev 3

- **The score is report-only.**
  - No PR fails for its ΔS.
  - An EG PR puts its measured per-metric deltas in the body. Until EG-A1 lands, it uses the prototype:
    `b/arch_score.py --delta` on two vectors from `b/measure_vec.py` and `b/metrics_v1.py`.
  - The reviewer compares them with the brief's expected ΔS. A rise in any score metric is explained in the body.
- **Honest improvement only.**
  - A key typed `Any`, a public passthrough over a private, a rename or re-spelling that hides a defect, and the
    other moves in the pre-study's §7 are review findings, not progress.
  - A target is met where the defect is gone, not where the count is.
- **EG-A1 lands the instrument as it stands at the pre-study commit, plus two changes:**
  - the red team's proven counters, each with its attempt script as a planted case;
  - an `untyped_payload_keys` that no longer counts `Any` as typed.
  - Its self-check re-runs the calibration and must reproduce §6 exactly.
  - The weights stay at their recorded hash (R3-3).
- **F10.4 takes the metric review.**
  - Retirements are loosenings: tvofi confirms the list before the push (R3-2).
  - New metrics enter at their measured baseline, as a re-record with the reason in the commit message.
- **EG-A2 may move solver floats**, because it consolidates the scalar and batch physics.
  - Claim drift in `tests/golden/claimed_drift.txt` with its direction. Never re-record.
  - It is a structure-budget writer, serialised with EG-B5a, EG-B5, EG-B1 and EG-B7.
- **The rev-3 groups never block an F lane, and add no edge to a planned group.**
- **Rev 2's rules stand:** EG-B10 before EG-B1; EG-R1 owner-gated; the carries bind their fixers; EG-B8 before EG-B5;
  B5 per `alt/EG-B5-DESIGN.md`; B1 after stamp point (c); raises confirmed before the push.
- **Mandate.** The 2026-09-29T18:15Z mandate has expired. Owner-gated steps (R3-1 to R3-5, F7.5, EG-R1, and every
  raise) wait for its renewal. Ungated fixes proceed under the standing rules.

## Stop and ask tvofi when

- a §7 decision is reached;
- `brief_lint` is non-zero after re-basing, and the fix would weaken a citation instead of correcting it;
- a merge since `f88e6af8` changes a figure a rev-3 carry states by more than re-measurement explains (a new hub
  writer, a new private reach, a new clone);
- the resume-truthing assertion in step 2 fails;
- a PR's measured ΔS is negative and its body does not explain the rise.
