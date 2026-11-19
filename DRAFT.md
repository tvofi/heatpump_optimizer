# Design review draft: R11-SEAM-learners

Design ref tip 31ba57ec6c0ba6df06310bf1ae6d8a51fe8fb036, base 9d65fe80b0 (= origin/main).

Draft points (unconfirmed):
- class-open N-confounded-learner: ISSUES.json #3760 sweep lists coordinator.py _fold_measured_cop and _async_learn_lower_floor_loss (via _interval_measured_heat_kw); note section 5 names neither.
- class-open P5: #3767 sweep lists SystemIdentification.step[cop] and step[outdoor_temp]; note silent.
- D2-s3-11 shape: per-hour sample count does not exist (coordinator.py:3666, 4737 store only the profile); persistence and restart behaviour undeclared vs the store invariant.
- D7-s2-02: night_gains_prior_kw (sysid.py:1291) returns one float mixing learned and configured hours; the learned/configured branch has no defined signal. Ridge duplicated at sysid.py:999 and :1021.
- Carries 2-3: note says the harness does not exist; dev/audit/harnesses/cop_dither_fabric.py exists at origin/main (carry 3's instrument).
- "today's eight" reasons: _learning_frozen (coordinator.py:6850-6929) lists 7 categories / 9 strings.
- Budgets: tests/structure.py at base reads every metric at its budget (coordinator_attrs 136/136, seam_cut_total 415/415). A per-hour gains count stored on the coordinator is +1 coordinator_attrs; undeclared.
- Interface: dhw_learning gets a str-returning callable (coordinator.py:3765); draw_range.fold gets frozen: bool (coordinator.py:9999, draw_range.py:671). Note's "replace(facts, evidence)" has no facts value in either module; the crossing is undefined.
- D12-s3-03 null control --plan-only: predicate "unobserved and tank rose" also refuses plan-scheduled charge spans unless conditioned on the plan putting no DHW in the span.
- class-open N-confounded-learner: _fold_measured_cop (coordinator.py:5290) named by #3760 sweep; not in note.
