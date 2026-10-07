# DRAFT — Remainder-of-programme plan (round 9, with structural endgame folded in)

**STATUS: DRAFT FOR tvofi'S REVIEW. Not implemented. The roster JSON, briefs and
standing template are UNTOUCHED. No dispatch decision below has been made.**
Written 2026-09-28 ~18:0xZ by the Mac merge seat from the live roster
(handoff/audit-r9-fixplan) and the two structural pre-studies
(handoff/round9/state/{surfaces,integration}-prestudy.md).

## Where we are

Merged and stamped through v6.7.9 + this session's PRs: F1.1-F1.4 (#1735 in
round-2 repair), F2.1-F2.3, F2.5, F3.1-F3.3, F4.1-F4.2, F5.1-F5.2, F6.1-F6.2,
F7.1, F8.1-F8.3, F9.1-F9.2, F10.1, F11.1-F11.3, F11.6, plus #1725-#1730
(instruments/records/hotfix). Remaining roster: 20 PRs (F1.4-F1.11 minus done =
F1.5..F1.11 with F1.4 in repair; F2.4; F6.3, F6.4; F7.2; F9.3; F10.1b-F10.6;
F11.4, F11.5).

## The structural items (from the pre-studies, with their constraints)

| id | item | size | hard constraints |
|---|---|---|---|
| EG-0a | roster-generator resume sidecar (gen.py:457) | ~35 lines | none — cheapest, do early |
| EG-0b | symbol-anchor the 19 remaining line-anchored pins | small | BEFORE any split/move PR |
| EG-S1 | surfaces identity core (entity.py) + merged-config helper + `_data()` | ~-60 lines | after #1668-carry (MERGED); avoids config_flow/services (F8/F10.4 hard-excluded reads) |
| EG-C1 | clock/helper dedup: `_utc_step_starts` x2, 70 raw clock sites in coordinator | small | rides the F1.6 window (same files) |
| EG-O1 | optimizer_dhw.py carve-out (2,237 lines, 4 inbound edges) | medium | after F2.4 (F2 drains); OPEN QUESTION vs F10.2 ordering (below) |
| EG-X1 | closures.json per-script directory split | medium | BEFORE EG-X2; touches derive_closures.sh (code-owned) |
| EG-X2 | tests/features.py per-class package split | largest, highest move-PR risk | after EG-X1; inter-wave window; after the last features.py-block lane lands (post-F1.11); both-ends adversarial diff mandatory (#324/#340 hazard) |
| EG-S2 | availability canonical rule (18 overrides) | medium | AFTER F1.11's predicate registry; re-keys class-a pins + climate BOOLOP |
| EG-N1/2 | coordinator seam moves, OPT-IN (dhw cut 73, views cut 109) | medium each | after F1.11; tvofi decision — the study recommends NOT the 3-7 split (cross-seam 0.43; #193 history) |

## Sequenced draft (waves with EG items slotted)

**W-next (in flight/queued):** F1.4 (#1735, round-2 repair) → merge → F1.5.
**Infra wave (parallel, immediately):** EG-0a, EG-0b (no lane conflicts;
removes recurring chores before the dense lanes).

**W1:** F1.5 → F1.6 (+ EG-C1 riding its window) → F9.3 (after F1.6) and F7.2
(after F8.3 ✓) in parallel lanes.
**W2:** F2.4 (after F1.6+F7.2) → then **EG-O1** (F2 drained).
   * OPEN QUESTION for review: EG-O1 before or after F10.2 (F10.2's barrier
     measures the solve F2.5 sped up; moving optimizer code under a fresh
     barrier argues EG-O1 FIRST, its brief re-cut; counter: F10.2 is
     instrument-critical and shouldn't re-measure post-move. Recommendation:
     EG-O1 first, F10.2's brief re-cut to the new layout — flagged for tvofi.)*
**W3:** F1.7 (after F2.4) → F1.8 → F6.3, F6.4 (after F1.8+F6.3) → F1.9.
   **EG-S1 slots here** (F7.2/F9.3 landed; sensor/button/entity quiet).
**W4:** F1.10 → F1.11 (closes #1644, #1651 — P2 registry lands).
**W5 (post-registry):** **EG-S2**; F10.1b (after F1.7 ✓) → F10.2 → F10.3.
**W6:** **EG-X1** (closures split) → **EG-X2** (features.py split, inter-wave:
all F-lanes done except F10.4-F10.6/F11.4-F11.5 — OPEN QUESTION: X2 before
F10.4 (its barrier adds features blocks) or after F10.6 (all lanes drained)?
Recommendation: after F10.4 but before F10.5/F10.6 — those are instrument
PRs touching the ledger, not features blocks. Flagged.)*
**W7:** F10.4 (after F10.3+F1.11) → F11.4 → F10.5 → F10.6 → F11.5.
   **EG-N1/N2 (opt-in seam moves) window here**, post-F1.11, pre-register.
**Endgame (unchanged):** friction dispositions (#1640, #1700, #1706, #1712),
#1655 close (last F1 carry), #1730's row, the round-9 register PR (harnesses,
salvage keepers, seat tooling, generator, pre-study reports), **stamp v6.8.0**,
branch prune (last, after the register lands everything worth keeping).

## Estimates

Roster remainder 20 PRs + 9-11 EG PRs ≈ 29-31 PRs. At the session's measured
~0.8 PR/h with 3 lanes: ~30-34h of lane work; with the daily light window and
review rounds, **~2.5-4 days** calendar. Mandate expires 2026-09-29T18:15Z —
the EG tail (W5+) likely runs past it; the plan assumes renewal or tvofi
availability for the tail's code-owned/raise items.

## Open questions for review

1. EG-O1 vs F10.2 ordering (recommendation above).
2. EG-X2's window: before F10.5/6 (recommended) vs after all lanes.
3. EG-N1/N2 (coordinator seam moves): opt-in yes/no.
4. Whether EG items get reviewer seats like fix PRs (recommendation: yes —
   adversarial both-ends review is the move-PR hazard's only defense).
5. Mandate coverage for the EG tail past 2026-09-29T18:15Z.
