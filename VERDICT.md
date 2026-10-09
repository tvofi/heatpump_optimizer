Fix review: blocked 9d77a97b1edc5ea02b808ab4cee0f4c630f119b3 root-cause-unanswered: briefs went red (FIXTURE VACUOUS wood_share:1152) and mutation plus fast/entities went red on two stale ledger pins, both caused by this round's thermal_model.py change and unanswered

bus-nonce: 247494bc01a8cf279600c5f32c9d44af
seat: review-2066 (fix-review.md, round 4, the re-cut; rounds 1-3 were not posted, and their records are in evidence/)
evidence: /Users/timmalmstrom/hpo-seats/review-2066/ev4
measured at: 9d77a97b1 (code head 42920d3c5), stacked on #2065's head 325960ef6. Every probe ran at 325960ef6 (base) and at 9d77a97b1.

## Blocker 1: briefs

`briefs` is red at 9d77a97b1 and was green at 1d011c887 and at #2065's head 325960ef6 (check-runs). The cause is this round:
- `brief_lint.mjs` freezes an expected error for the 931dffe fixture. W1-G9's anchor `thermal_model.wood_share:1152` must keep failing ("'return' not found near :1152"), so that the anchored-path rule cannot be deleted silently (`REQUIRED_931DFFE`, tools/policy/brief_lint.mjs:1033).
- Round 4 adds `nameplate_power_floor_kw` (+12 lines) at thermal_model.py:666. That moves `def wood_share` from 1657 to 1669 and brings a `return` inside the window around :1152.
- The pinned error is therefore no longer produced: `FIXTURE VACUOUS: 931dffe acceptance pins missing: [W1-G9] path:line (anchored): wood_share:1152`.

My runs of `node tools/policy/brief_lint.mjs`: 1d011c887 rc 0 (the pinned error present), 9d77a97b1 rc 1 (evidence/brief_lint_r3.out, evidence/brief_lint_head.out). The body's "Red checks" section does not name `briefs`.

`pr-contract` independently refuses the body for the same omission: "check `briefs` is red and `## Red checks` does not name it" (evidence/ci_prcontract.log).

Remedy:
- Name the red in the body and answer it. The cheaper detector is `brief_lint.mjs` itself, a seconds-long run, so state its standing cost.
- Make the pin pass without moving production lines to suit a lint. One way is to re-anchor the frozen expectation so it cannot be satisfied by an unrelated `return`. That is an instrument change, so say so.
- This is the known line-shift class ("line-pinned artifacts"). A frozen expected error checked against the live tree is fragile, so it goes to `root-cause.md` if it recurs.

## Blocker 2: mutation and fast (tests/entities.py), stale ledger pins

The body answers `mutation` as "unpinned sites ... mutation-autofix owns the pins". At this head that is not what refused. The lane's whole refusal is two stale dispositions (evidence/ci_mutation.log):
- `thermal_model.py:ThermalParameters.flow_lift_power_floor_kw CLAMP_DROP c0871d84: disposition names no site the inventory generates (old pin 'return max(0.3 * self.max_electrical_power, 0.2)')`
- the same anchor with `RETURN_DEL`

Cause: round 4 moved that line out of `flow_lift_power_floor_kw` into the new `nameplate_power_floor_kw`, so the `killed_by` entries in tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.flow_lift_power_floor_kw.{CLAMP_DROP,RETURN_DEL}.c0871d84.json name a site that no longer exists.

The same refusal is the one failure in `fast`'s `tests/entities.py`: "1 of 2227 ENTITY CHECKS FAILED", the `--anchor re-drives one site` self-test, whose output quotes this refusal (evidence/ci_fast.log).

mutation-autofix pins killed mutants. It does not re-key a stale disposition, so no bot commit will repair this. Remedy:
- Re-key both entries to `ThermalParameters.nameplate_power_floor_kw` with the ledger's own tooling, keeping `--normalize`'s escape rewrites.
- Re-run `tests/mutation_table.py` and `tests/entities.py` (both cheap enough to run locally).
- Correct the body's account of the `mutation` red.

The line-shift class strikes twice in one round here, which is the `root-cause.md` trigger.

## Everything else at this head (measured; synthetic only)

The corrected #201 rule is implemented as decided:
- The new floor always applies (`MeasuredCop.judge_floor`).
- A departure over 15 % with no `follows_ask` evidence folds only where both the ask and the draw clear `nameplate_power_floor_kw` (the old 0.3 x max), and is otherwise refused as `awaiting_draw_evidence`.
- With evidence, `follows_ask` decides.
- The `cop_learner` diagnostics row adds `draw_follows_ask`.
- The body corrects "one day", and the docstring no longer claims "no error is beyond reach".
- A5 is in DESIGN.md.
- Hold-then-replay is carried to fix 3 in `dev/programme/carries/carry-2066.json`, with probe 6 and the 4 kW row as its control (`brief_lint` 0 errors on the file).

Acceptance rows (base -> head):
- matched control `selfmod_matched` 0/96 -> 96/96 1.000. `min1_running` 0/15 -> 15/15.
- probe 7 `narrow_config_true0.75` 0.751 -> 0.751; `wide_config_steady_week_true0.75` 0.750 -> 0.750; varied control 0.750 -> 0.749.
- probe 5 hourly/3h/flat: 1.000 x3 -> 0.978/1.000/1.000. Probe 3: 1.000 -> 0.976.
- probe 6 `selfset_hourly` 1.600 -> 1.170 (no worse than 1.37). Harness `selfmod_independent_4kw` 0.636 -> 0.780; 0.81 was my prototype's figure, not a requirement, and the orchestrator ruled 0.780 accepted.
- probe 6 heat-led true 0.7: noise 0.706 -> 0.705, lag 0.686 -> 0.688, outliers 0.700 -> 0.700, true 1.3 1.304 -> 1.304. Harness true_0.6/0.7/0.8/1.3: 0.604/0.704/0.805/1.307, and `true_0.7_reload150` 0.704.

"No row worse than base", checked over every row of the harness and of my probes 2-7 at both ends (evidence/all_*.out, evidence/r1r2_*.out):
- In production order (fold, then learn), no scale is further from its right value than at base, except probe 4 `follow_noise20`: 1.118 -> 1.123 (right value 1.000), one more fold (96 vs 95). That is 0.005 on an open-loop probe of a correct pump with ±20 % noise, and I do not block on it.
- Partial following at slope 0.5-0.8 is 1.600 at both ends (a residual, unchanged); slope 0.3 improves, 1.600 -> 1.375.
- One driver is outside production order: probe 3b runs the learner with no draw window at all, so there is never any evidence while the asks vary. It reads 0.636 -> 0.590 on the 4 kW nameplate. The cause is the decided rule itself: inside the 15 % tolerance the new, lower floor applies with or without evidence, so in-tolerance intervals of a self-setting pump fold where base's floor refused them. Production reaches that regime only for the first 48 running samples, and the production-order row is 0.780, better than base. A5's sentence "While there is no evidence, fix 1 behaves as base" is therefore true for departures only. Narrow it, or accept it as the ruling's consequence; I do not block on it.
- Fixed-speed rows: duty-average meter 15/15 -> 6/15 folds, instantaneous meter scale 0.834/0.827 -> 1.000. This is the disclosed correction from round 1.

Mutants (mine):
- Deleting the no-evidence fallback (`if min(asked, drawn) >= nameplate floor: return None`) puts probe 7's narrow and steady rows back to 0/400 at 1.000.
- Round 3's slope mutant still applies: with `follows_ask` always True, selfset rows read 0.615-0.707.
Both branches are load-bearing.

`fast` and layout (the other `fast` failure): the head refuses `tools/audit/harnesses/draw_range_evidence.py`, which is #2065's file, inherited through the stack. #2065's head shows the identical refusal (my `tests/layout.py` run at both). The body names it, attributes it to #2065, and gives the cheaper detector and its cost, so that red is answered. Once #2065 moves the file, this branch must re-merge #2065, and the head moves.

CI settled at 9d77a97b1 (evidence/ci_settled_redlist.txt). Red: `briefs` and `pr-contract` (blocker 1); `mutation` and `fast` (blocker 2, plus #2065's layout path in `fast`); `nightly-status`. Every other check is green or skipped. `mutation` (unpinned sites) is mutation-autofix's, and `nightly-status` is red but not this PR's.

Round 4, the re-cut. The remaining repair is instrument-only (the briefs anchor, the ledger re-key and the body's red-checks section), with no production logic change, so it should not need a fifth logic round.
