# BLOCKED: R11-SEAM-learners (fixer seat)

Question: design/R11-SEAM-learners (bee723ac, approved 9e06a05e) section 3.3 prices three new terms into the sysid adoption gate: the 0.3 kW unlearned intercept width (D7-s2-02), the regressor-noise term (D2-s3-10) and the told COP and outdoor widths (P5, #3767). Built as specified, each one alone refuses most of the derived presets' noise-free nights. The 0.3 kW width refuses all of them, and it applies to every install without a learned gains profile, which is every new install. Which of these should the fixer do: (a) build section 3.3's terms as specified and accept that sysid adopts nothing until the gains profile is learned, plus the cost of the other two terms; (b) take a design revision of section 3.3 that prices the three terms against liveness, with a keep table for each term, not only for P5's widths; (c) ship section 3.3's mechanical parts in this PR (ADR-003 switch, the shared Jacobian, one ridge spelling taking its width, the D5-s4-02 comments) and route the three priced terms to a revision, with the D7-s2-02, D2-s3-10 and P5 findings left open?

## The measurement

Driver: `dev/audit/harnesses/sysid_told_keep.py` at this branch's head, `night()`. It is the features check `_r9p5_derived_night`: noise-free, plant equal to its declaration, 21 degC, outdoor 0 degC. The 8 nights are those that check reads (4 structures x pre_1960 and 1960_1980), and the check requires at least 6 to adopt. Each arm switches the head's terms by patching module attributes (the scratch driver `attr.py`, not tracked):

| arm (head code, other terms off) | adopted |
|---|---|
| none of the three (unlearned width 0.1 kW, noise term 0, told widths 0) | 7/8 |
| unlearned width `SLAB_INTERCEPT_UNLEARNED_SD_KW` 0.3 kW alone | 0/8 |
| regressor-noise term (`_regressor_noise`) alone | 4/8 |
| told `TOLD_COP_LOG_SD` 0.03 and `TOLD_OUTDOOR_SD_K` 0.5 K alone | 1/8 |
| all three, as section 3.3 specifies | 0/8 |

The keep table over all 20 derived presets (the 4 structures x 5 eras), with the 0.3 kW width and the noise term in place, reads 0/20 at every told-width pair it reached. So that table cannot price P5's widths until the D7-s2-02 width is settled.

Findings as measured at both ends (base 93e490842f = origin/main 78d3b40221 + #3737 head 2b95078faf):
- D7-s2-02 `m2_sysid_plant.py` (ported, `_SID_ON`): biased_admitted 3 -> 0. But the told cell `heavy_old_told_s0` is admitted at weight 0.670 at the base against 0.016 at the head, and 20 cells are admitted at the base against 4 at the head.
- P5 `probe_told.py` (32a372faae, run from an untracked copy): base tree admitted_past_bar=6, null 0. Head not measured: it would read 0 only because nothing is admitted.
- D5-s4-02 `comments.py --file sysid.py`: unresolved_units 1 -> 0. Mechanical; not blocked.

## What is done and pushed (this ref)

Sections 3.1, 3.2, 3.4 and 3.5 are built, tested and measured. The figures:
- D7-s2-01: one predicate (`learning_freeze`). Away holds gains, quiet comfort and the tank usage and draws, but not standby; the recovery holds the curve tracker.
- D12-s3-03 / #3760: `counter_spans.py --sees-dhw --no-mode`: inflated_spans_folded 2 -> 0. The `--plan-only` null is equal at both ends.
- D2-s3-08: `m5_tankfall.py` long_max 3.016 -> 0.000 kWh.
- D2-s3-09: `m5_drawrange.py --run-samples 200` narrowing 4.100 -> 0.000. It reads flat at the default 60 samples, because the floor in force is still the configured value there.
- D2-s3-11: `m5_crosscov.py` gain_recovery_mean 0.5573 -> 0.7748.
- Carries 0-1: the derate 0.684 -> 1.000 once the verdict reads ignored.
- Carry 3: no lost cycle is a freeze reason.

Raised as well, not built:
- Section 5's heated-flag (unplanned charge) arm books 3.016 kWh at both ends. The design's mechanism is a no-op on today's `DrawStats.take_back`, which takes back charge-folded energy only. Widening it erases the real draw that starts a self-setting pump's own charge. Carry: R11-OUTSIDE-SELF-SETTING-PUMP
- The sysid head is red on the features liveness check (at least 6 of 8) until the question is answered.

Not yet run: the full suite at this head, the mutation proofs, `prepr.sh`, closure classification of `learning_freeze.py` and the new harness, and the PR body.
