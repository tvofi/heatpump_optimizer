# R11-OUTSIDE-SELF-SETTING-PUMP: revalidation at d9100de781 after both parts merged (architect note, round 4)

Designer seat, re-dispatched at base d9100de781ec174960655fdab1a5af48c303d7bd (origin/main). It answers the round-3 verdict (design-verdict/R11-OUTSIDE-SELF-SETTING-PUMP 7062403121, `Design review: approve 0acbbc8b91`) point by point, and the roster carries 5, 6 and 7. The round-3 note (0acbbc8b91) and the owner's three decisions under it stand unchanged. This note adds no design and writes no code.

Predecessors read, all ancestors of the base: part 1 #3662 (merge 3f7f29e778, the (a2) probe), part 2 #3722 (merge 412ada3942: departure A for carry 5, departure B1 for carry 6, carry 7 measured), and R11-CARRY-DRAWMAP 5455c39e21 (an experiment cycle takes no dither step; coordinator.py:5302 passes `not experiment` as `owed_scale`'s read flag). Since 412ada3942, the only commits touching accuracy.py, `dev/audit/harnesses/cop_duty_floor.py` or `dev/audit/harnesses/cop_dither_fabric.py` are R11-CARRY-DRAWMAP's (`git log --oneline 412ada3942..d9100de781 -- <those three>`).

## 1. Re-measured at the base

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`: 106 RESULT lines, rc 0. `cop_dither_fabric.py`: 12 RESULT lines, rc 0. Each row the carries and the verdict name prints the figure #3722 recorded at its head e26b512006. The drawmap change moves none of them.

| row | at d9100de781 |
|---|---|
| `sub_min_true_0.6_x1440` (carry 5) | 470/1440, 0.599, probes=1, follows |
| `sub_min_true_0.6_x384` / `_x480` | 0 folded, 0.933, pending (undecided; on a dither level) |
| `repriced_heat1.2_true_0.8_x672` (carry 6) | 0/672, 1.000, off5=20, probes=4, pending |
| `heatled_true_0.8_flat_x672` (control) | 672/672, 0.800, probes=1, follows |
| `null_dither0_heatled_true_0.8`, `null_dither0_selfset_2.2` (null 1) | 0/672, 1.000, band 0.000, pending |
| `true_0.6_max_cycle_move` / `heatled_true_0.68_flat_max_cycle_move` (carry 3) | 0.292 / 0.308 |
| `dither_true0.8_2C` vs `null_dither0_true0.8_2C` (carry 7) | house_scale 1.1000 both; samples 578 vs 671; max gap 0.0174 |
| `dither_true0.8_9C` vs null | 1.1000 both; 646 vs 671; gap 0.0101 |

Gap checks: rule `grep RESULT | grep selfset | grep -c verdict=follows` reads 0 of the 54 rows naming `selfset`, and `grep RESULT | grep heatled | grep -c does_not_follow` reads 0 of the 8 rows naming `heatled`. (#3722's body counted 48 and 4 by a narrower grep; the zeros are the claim.)

## 2. The round-3 verdict, point by point

- **Decision, carry 1 extended to the dither.** Ruled by the orchestrator and built in #3662: the owed scale is applied past the freeze gate (coordinator.py:5290 returns `COP_REFUSED_FROZEN` before coordinator.py:5302 calls `owed_scale`), so a frozen or unpowered stretch keeps the last level, inside base × 1.15^(±½), for the stretch's length; the next live cycle returns to the base (#3662 item 76b936b7, check "two admitted rows then a frozen cycle, an unread one ..."). "About a day" in the round-3 note counts live cycles only.
- **Decision, the follow-up's destination.** Exists now. Its four items: closed-loop harness and the re-pricing row → R11-SEAM-learners carry 2 (from #3722 item c25b53cc); dither tuning and the fabric sample loss → R11-SEAM-learners carry 3 (from #3722 item 4a5e147b); the defrost control (item 0116e1a6, with #3662 item dcd51e15 recording that the control exists) → R11-SEAM-learners carries 0 and 1, the swing rows it must cite (`selfset_2.2_swing0.4_p3_s1`, `selfset_2.2_swing0.3_p4_s1`) reading does_not_follow at the base.
- **Decision, carries 1 to 4 restated.** Carry 1 built (above). Carry 2 kept, not owed (orchestrator); its check "a replayed interval folds the scale and not the capacity envelope" is in `tests/features.py`. Carries 3 and 4 dismissed by the owner (2026-11-16, "Accept both"); carry 3's rows re-measure 0.292 and 0.308 above.
- **1b98ae3f** (re-priced pair gives no contrast): built in #3662 as a void for a pair whose heat asks moved under `FOLLOW_SLOPE_MIN` of the step; the re-priced row never reads does_not_follow. Its endless restart is carry 6, below.
- **1ff86b5f** (rows ageing out while pending): held for replay; the aged-out exit drops while pending (check "release: no fold lands on a pending heat-ask probe however long it lasts").
- **76b936b7** (scale on a cycle that admits no row): superseded by #3722's departure A (carry 5): an unread-row cycle keeps the pair in flight and the slot is held until a row is read, voiding past `COP_HOLD_HORIZON_S`.
- **5bb6a355** (reset while pending): base applied the same cycle (check "a reset mid-probe returns the scale to the base in the same cycle").
- **ffb019e7** (stored learner values under the dither): carry 7, below.
- **740366bf** and **7aa61215**: counted in #3662's body (382 pending rows, all self-setting; `probes` column), re-readable from the harness above.

## 3. Carries 5, 6, 7

- **Carry 5** (never-consecutive admitted rows never decide): built, departure A, #3722. Control `sub_min_true_0.6_x1440` follows at 0.599; null 1 reads pending.
- **Carry 6** (re-priced plan restarts without end): "without end" built, departure B1, accuracy.py:1132 `PROBE_VOID_CAP` = 3: 56 probes became 4. "Learns nothing" remains: identification needs the heat ask itself moved (option (c1) of the round-3 note), which is the planner's ask; that is two owners, a stop under `designer.md` step 2, and is at R11-SEAM-learners carry 2.
- **Carry 7** (fabric replays at the dither level): measured in #3722 and again here. The stored house value equals null 1 to four decimals in every cell; the residue is lost house samples (578 and 646 of 671). The instrument's reach is limited, and that limit is carried with it: the house scale reads 1.1000 in every arm, the lower-floor learner is not reached (lower_samples=0), and #3722's sensitivity control moved the stored value by 2e-5. At R11-SEAM-learners carry 3.

## 4. Recommendation and alternatives

No fixer dispatch for this group. Everything its brief and carries owe is built (carries 0, 1, 5, B1 of 6), ruled not owed (carry 2), dismissed (carries 3, 4) or held by a live group (the rest of 6, the rest of 7). The roster should mark carries 5 and 6 `[implemented: 412ada3942]`, and carry 7 measured, with the residue moved to R11-SEAM-learners. The group then closes on its carries.

Alternatives that lost:
- Design (c1) here. Lost on ownership: the heat ask is set by the planner and written by the actuator path, and the learner owns the scale only (`designer.md` step 2). It would also give carry c25b53cc a second destination beside R11-SEAM-learners carry 2, which `brief_lint.mjs` refuses.
- Apply the dither as a factor on the commanded write while the planner prices at the probe base. This moves the heat ask without the planner, but the actuator write path is a third owner, and every write site (D16) would carry the factor.
- Tune `PROBE_VOID_CAP` or the dither step here. Lost because #3722's null control found no row separating N = 1, 2, 3, 5 other than the re-priced one, and dither size is R11-SEAM-learners carry 3's item. With no closed-loop harness there is nothing to tune against.

Sibling sites: `git grep -n -e "owed_scale(" -e "PROBE_VOID_CAP" -e "ScaleDither(" -e "\.admit(" -- custom_components` reads accuracy.py and coordinator.py:5302 only (wear.py:172's `admit` is another class). No site is outside the merged parts.

Evidence plan, hot files, serial position: none owed, because no change is proposed. accuracy.py and coordinator.py are R11-SEAM-learners' files (PR 3835). Whoever builds (c1) re-measures the section-1 rows at its own merge base, with null 1 (`ScaleDither.levels` returning the base twice) and the gap checks.

## Notes for the fixer

None: no fixer is owed. The two open items carry their controls in R11-SEAM-learners carries 2 and 3.
