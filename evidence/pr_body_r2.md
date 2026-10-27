The owner's request on #2261: an optional delivered-heat energy meter (`heat_pump_heat_energy_entity`, "Heat pump heat energy meter", a `total_increasing` kWh sensor in the options' Power and energy group), read per span, with the heat split between space heating and hot water by the pump's own mode entity when one is live. `heat_energy.py` (new, free of Home Assistant) owns the counter, the span, the mode dwell and the attribution; the coordinator hands it values. An install with neither the counter nor a live single-duty mode entity reads what it read before: every coordinator golden capture is byte-identical to the merge base. The approved design is `dev/programme/designs/R10-HEAT-METER.md` on `design/R10-HEAT-METER` at `21f4fbfe9`, approved by `design-verdict/R10-HEAT-METER` `ad376684f` ("Design review: approve 21f4fbfe9").

Part of #2261

## Re-cut (round 4)

Round 3's review blocked `7e9fea6ac` with two findings, and the re-cut rule applies: this body is replaced, not patched, and every figure in it is re-taken at the head it names.

**Finding 1 (architecture-unsound): a counter-only install now folds its span COP.** At `7e9fea6ac` `_fold_measured_cop` returned `no_measured_power` as its first gate, before its counter branch, so on an install with the heat counter and the electric counter and no power entity `clean["cop"]` was False every cycle, `close_span`'s cop gate stayed shut and `_async_learn_heat_span` never folded the span's heat over electricity. A heat counter is now exempt from that refusal (the counter branch still sits after the frozen, frost and distorted gates, so the design's per-cycle gates still AND across the span, and a cycle that passes them reads `span_open`); the duty floor is judged per cycle where a per-cycle draw exists and at the span close on the span's mean ask and draw otherwise, through the same `MeasuredCop.judge_floor` predicate, so a low-duty span still cannot fold a COP dominated by standby draw. Three checks now cover the shape, none of which existed: they fail at `7e9fea6ac` and pass here.

**Finding 2 (class-open): the seam rule's full output is dispositioned.** The body's step-8 rule returns fourteen lines in `coordinator.py` at this head. Each one is in `## Figures` with its disposition: six lines across four functions are converted here, one is the span's plan split by design, and the other seven are the approved design's own out-of-scope list. The review's `_fold_flow_lift` claim is settled by measurement, not by argument: its stated case does not fire, and the residual it does not cover (a switch-back window whose dwell is hot-water-dominant while the plan split stays space-dominant) is real, measured with its nulls, and carried to R10-COP-GATE, which already owns the plan-vs-observed duty decision (carries 3 and 4) and lands after this group.

## Head



`8c4bec5c27cf4c46af6b572c00dc33a4feffba90` merges the live head `69d4bb2be9` (mutation-autofix's killed-mutant pins) and `origin/main` `524c1896b` (#2874) into this branch. Both merges are clean at the roster: the branch's earlier resolution already carries #2871's rows, and #2874 changes no roster file, so no group id needed choosing. The head still carries the two real `tests / typing` errors this branch introduced at `coordinator.py:5109` and `:5122`; the repair is a code change in `_fold_measured_cop` and belongs to the fixer (it moves two mutation pins), so it is reported, not made here. Nothing under `VERSION`, the manifest version, `RELEASE_NOTES.md` or either claim file is touched.

The two carry texts the blocked review at `64d33242659f` asked for are already in the tree and are not re-authored here: `dev/programme/rosters/wave-r10-groups.json` carries them at `origin/handoff/audit-r10-roster` `e3f4db710` and on `origin/main` at `629674e0c` (the last commit to touch the roster there), where R10-COP-GATE holds 13 carry items and R10-UX-HEALTH 17, both naming `span_open` and `counter_reset`. The verdict's remaining ask was the SHA, named here; its re-review is owed at this head.

`ff886d61782026ff71b53217d36b33bdc613253c` is the orchestrator's recarry of main into the previous head (a roster conflict resolved structurally, a coordinator.py rename conflict keeping both intents, a re-anchored const.py citation, and a re-recorded guard_pins closure). It is not a clean merge of the live head and main (parent 1 and parent 2 do not merge cleanly; a resolution goes through prepr), so prepr checked this head.

`ff886d61782026ff71b53217d36b33bdc613253c` re-keys 4 `## Unpinned sites` line(s) the main merge moved from `1b08999995b1e7d5c882e56cfe86b269c4329b5e`, each to the line at this head with identical text and kind (`ci_predict.py --rekey-body`): custom_components/heatpump_optimizer/coordinator.py:5093 BOOLOP -> custom_components/heatpump_optimizer/coordinator.py:5075 BOOLOP; custom_components/heatpump_optimizer/coordinator.py:5093 GUARD_OFF -> custom_components/heatpump_optimizer/coordinator.py:5075 GUARD_OFF; custom_components/heatpump_optimizer/coordinator.py:5100 BOOLOP -> custom_components/heatpump_optimizer/coordinator.py:5082 BOOLOP; custom_components/heatpump_optimizer/coordinator.py:5100 GUARD_OFF -> custom_components/heatpump_optimizer/coordinator.py:5082 GUARD_OFF.

`cd900939e60aebcdf176ba536f2124992a34748d`, five commits on the reviewed head `7e9fea6acb929bf8eecd279096d99fafb208ac56`, merge base `3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f` (`git merge-base origin/main HEAD`; `origin/main` is `6fe5170cd`):

- `34f78bb5a` the fix, the three checks and the first two mutant rows;
- `e5472964f` the R10-COP-GATE carry for the flow-lift residual;
- `4fc760104` the two ledger pins the fix moved, dropped by hand (a stale pin is a predicted red `mutation-autofix` never repairs);
- `ec7af675c` the span-close floor folded into the assignment the fold already had, so the architecture score does not move;
- `cd900939e` the four mutant rows the two edited lines' operators need. This commit touches `dev/audit/harnesses/r10_heat_meter_mutants.py` only, so every production measurement below was taken at `ec7af675c` and applies to this head unchanged.

`git merge-tree --write-tree origin/main HEAD` exits 0 at this head, so no merge of `origin/main` was made and no resolution inside the reviewed code head is described.

## Mutation proof

The in-tree table (`python3 dev/audit/harnesses/r10_heat_meter_mutants.py -j 4`, each mutant one exact replacement in its own `git archive` copy, `tests/features.py` in full) at this head. The null row is a comment-only edit; it fails one check, #363's `recorded_at`, in every `git archive` copy because the copy carries no git history, so a mutant is killed on the checks it fails *beyond* the null.

```
NULL      N0 null control (a comment): 1 of 4497 FEATURE CHECKS FAILED; 0 beyond the null
KILLED    S the no-power refusal drops the counter exemption: 4 of 4497 FEATURE CHECKS FAILED; 3 beyond the null
      FAIL a heat counter with the electric counter and no power entity folds its span's COP as heat over electricity; ...
      FAIL null control on that install: heat equal to the model's COP times the electricity reproduces the model ...
      FAIL on that install the duty floor is judged at the span close on its mean draw and ask ...
KILLED    T the span close's duty floor dropped on a counter install: 2 of 4497 FEATURE CHECKS FAILED; 1 beyond the null
      FAIL on that install the duty floor is judged at the span close on its mean draw and ask ...
STALE     U the counter exemption's operator turned into or: no summary (rc=1) 'TypeError: unsupported operand type(s) for *: 'NoneType' and 'float''
STALE     V the no-power refusal removed: no summary (rc=1) 'ConfigEntryNotReady: Error updating data: float() argument must be a string or a real number, not 'NoneType''
STALE     W the per-cycle duty floor's operator turned into or: no summary (rc=1) 'UnboundLocalError: cannot access local variable 'refusal' where it is not associated with a value'
KILLED    X the per-cycle duty floor removed: 5 of 4497 FEATURE CHECKS FAILED; 4 beyond the null
      FAIL a folded COP interval clears the refusal
      FAIL a refused COP interval names its guard and the floor in the diagnostics
      FAIL idle and standby draws under the modulation floor still teach nothing
      FAIL with no modulation floor configured the nameplate floor still applies
3 survivor(s) of 6 mutant(s); the null fails ['and the path that proceeds still stamps a resolvable recorded_at (#363)']
```

`STALE` in that table is the harness's own rule (no closing summary line = instrument error, printed with the traceback tail), not a survivor: U, V and W abort `tests/features.py` during setup inside the mutated line, and `tests/mutation_table.py` counts an uncaught exception as one failing check (`failing_count`'s `n + int(_TRACEBACK in run.stderr)`, which `killed` compares against a green baseline), so all three are kills by that instrument. The harness prints `3 survivor(s)` because it counts its own STALE rows; I did not change its rule to make the number read better.

The table's other thirteen rows (the design's ten targets, the precedence row and the three carries') mutate `heat_energy.py`, `flow_meter.py`, `const.py` and `snapshots.py`. This round changes none of those files and none of those checks, so their round-3 result stands and was not re-run.

## Null control

Every quantified claim carries one, named where it is measured:

- the three new checks each carry their own null in their text: heat equal to the model's COP times the electricity holds the model and the scale at 1.0; the same install at 2.0 kW folds where the 0.5 kW span refuses; the duty-floor row names its 2.0 kW arm as the control;
- the fix's discriminator, `probe_counter_only.py` (sha1 `a89a3702c47e02545d4bb64587f496bb8c761e04`, this seat's): N1 measures that the reviewer's probe arm is a *counter-less* install, where the no-power refusal is the right answer at every head, and N2 is the null on a coordinator with neither counter nor power, which refuses at both ends;
- the flow-lift probe carries two: the same plan with no mode entity folds, and an all-space window folds under both readings;
- the mutation table's archive null above;
- the architecture score's null is that no metric moves: `coordinator_multiassigned_attrs` falls by the one attribute the design moved, and nothing rises.

## Figures

All at head `ec7af675c` against merge base `3b4180dcc680` unless stated. Logs are this seat's; every command is quoted so it can be re-run.

- `PYTHONPATH=tests/hastub PYTHONHASHSEED=0 python3 tests/features.py` -- `ALL 4497 FEATURE CHECKS PASSED`, 0 failed. The same file at the reviewed head `7e9fea6ac`, in a pristine worktree of that head carrying only the new `tests/features.py`: `3 of 4497 FEATURE CHECKS FAILED`, the three this round adds, each reading `samples 0` with refusals `['no_measured_power', 'no_measured_power', 'no_measured_power']`. Red then green on the same three checks.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`: `max_class_loc 8181 <= 8181`, `class_excess_loc 18076 <= 18076`, `coordinator_attrs 142`, `coordinator_multiassigned_attrs 109`, `seam_cut_total 423`, `max_method_loc 373`. No row moved this round: the class's only edit is net zero lines (the docstring's power clause reflowed, a three-line head comment trimmed to two, the tail comment removed) and the span-close edit is outside the class.
- `python3 tools/audit/archscore/score.py --diff 3b4180dcc680 HEAD` -- `Architecture score: dS +0.0131 IMPROVES`, `coordinator_multiassigned_attrs 110 -> 109 +0.0131`. The design's move of the day-health flag onto the snapshot ring. A first cut of the fix held the span's duty-floor refusal in a local, which the counters read as `coord_footprint 2421 -> 2422` (`dS +0.0125 WORSENS`, an inadmissible vector); `ec7af675c` folds it into the assignment it already had, one statement instead of two, and the vector is the reviewed head's again.
- `python3 tools/pr/ci_predict.py --base 3b4180dcc680` -- `no closures, fast, wave-script or instrument red predicted`; `4 unpinned site(s) the diff adds`, each listed under `## Unpinned sites`. The fix's first cut also produced two `STALE PIN` rows against the ledger (`GUARD_OFF ca278eff` on the no-power refusal, `GUARD_OFF c31691cd` on the per-cycle floor); `4fc760104` deletes both files, which is the repair the tool names, and the re-run reports no ledger red.
- The round-3 reviewer's harness, `rev_heat_meter.py` (17 checks, its own instrument, driven through the production `close_span`): `17 check(s), 0 failed` at `7e9fea6ac` and `17 check(s), 0 failed` at `ec7af675c`. At the merge base it cannot run: `ImportError: cannot import name 'heat_energy' from 'heatpump_optimizer'`, because that module is added by this PR, so the harness has no both-ends arm and none is claimed.
- The round-3 reviewer's probe, `probe_no_power_cop.py`: `4 check(s), 0 failed` at `7e9fea6ac` **and** `4 check(s), 0 failed` at `ec7af675c`, and the reason it reads the same at both heads is measured, not assumed. Its P1 drives `_fold_measured_cop` on a stub carrying `_measured_power = None` and nothing else; the counter is read through `heat_energy.meter_of(self)`, and that stub's meter has `counter False`. So its arm is a counter-*less* install, where `no_measured_power` is the correct answer at every head. I built `probe_counter_only.py` rather than edit the reviewer's instrument: on a real coordinator with both counters configured and no power entity (`meter counter True`, `_measured_power None`) the same call returns `no_measured_power` at `7e9fea6ac` and `span_open` at `ec7af675c`, and both nulls hold at both ends (`3 check(s), 0 failed` each).
- `probe_fold_flow_lift.py` (sha1 `ae265a5eae99c36f54b6c27d845dfc3efe9d6461`, this seat's, the review's Finding 2): `5 check(s), 0 failed` at `ec7af675c`. C1 and C1b: a plan commanding space with the live mode hot water hands `_commanded_split()` `(0.0, 0.0)` and `(0.0, 1.0)`, and `_fold_flow_lift` folds nothing. C2, its null: the same plan with no mode entity folds one sample. C3, the residual: a switch back to heat inside the window (0.45 h hot water, 0.05 h space) leaves the plan split `(2.0, 0.0)` and folds one sample while `heat_energy.meter_of(coord).attribution(split)` reports `observed True`, `dhw_share 0.900` against `_COP_CURVE_SHARE` 0.15. C4, its null: an all-space window folds under both readings. The conversion is a departure from this group's approved design (out-of-scope list, "these concern the plan's ask"), so it is carried.
- The scoped gate, `NODE_OPTIONS=--max-old-space-size=8192 GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at `8c4bec5c2` -- `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`, `4 TEST SCRIPT(S) FAILED` in `5116s` on `python 3.14.7 (darwin)` / `Apple M1` / `numpy 2.4.6`, against `524c1896b`: `tests/typing_ruler.py` `2 of 10` ruler checks and `1 of 12` source checks (the two `arg-type` errors under `tests / typing` above); `tests/optimality.py` `1 of 84`, the recorded claim `one|summer_negative|shoulder` reading `claimed but gap 0.0000% is at or below the bar -- the claim closed and should be removed`, the golden-drift rule's canonical-environment cell; `tests/stress.py` and `tests/harness_headers.py` were refused by the gate lease (`gate_lock: flock-wrap refused, fix-2854-conflict holds no lease: no live gate lease to renew`) when the 30-minute lease lapsed inside this 85-minute run -- both are lease-class, and `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` standalone. Every other script in the run is green at this head, including the two that were red before the merge: `tests/entities.py` `ALL 2467 ENTITY CHECKS PASSED` and `node tests/card.mjs` `ALL CARD CHECKS PASSED` (both failed at `ec7af675c`, so the merge to this head is their repair); `features` ALL 4506, `closure` 117, `manual_plan` 132, `block_duty` 46, `doc_claims`, `config_flow_steps`, `structure` STRUCTURE RATCHET PASSED, `open_meteo`, `solar_alignment`, `guard_pins`, `debug_collect` 136, `finite_boundary` 108, `layout`, `deployment_shape`, `wood_advisor`, `md_tables`, `env_drift --all` `NO STALE FIXTURE` (56 fixtures), `arch_score` 255 and `arch_score_head` 18, `validate` NO ISSUES, `edge` ALL EDGE CASES PASS, `backtest` 25, `boost_drift_replay` 46, `plan_view`, `frontend`.
- `governance / wave-script`: the job restores the checker from the base `524c1896b` and reported it red at `69d4bb2be9`, whose tree predated #2871's roster rows. `node tools/policy/check-wave-script.mjs` at `8c4bec5c2` reports `224 passed, 0 failed` (the checker this branch does not modify), so the merge is the repair.
- `tests / typing`, reproduced off the Linux-only lock: the CI census at `69d4bb2be9` reads `errors 2`, `by_code {arg-type: 2}`, `by_module {coordinator.py: 2}` on mypy 2.3.1 / homeassistant-stubs 2026.9.3. The same pair, resolved for macOS (`mypy 2.3.1`, `homeassistant-stubs 2026.9.3`), run as `python -m mypy --strict --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental --python-version 3.14 custom_components/heatpump_optimizer`, reports the same 2 errors at `8c4bec5c2` (`coordinator.py:5109`, `:5122`, both `[arg-type]`). The two are the counter exemption's narrowing loss; `## Red checks` records the repair the fixer owes.
- Seams (fixer step 8), `git grep -n "_commanded_split()\|dhw_share\|space_share" ec7af675c -- custom_components/heatpump_optimizer/coordinator.py`, all fourteen lines, each with its disposition:

| line | enclosing function | disposition |
|---|---|---|
| 885 | `_fold_flow_lift` | out of scope by the design ("these concern the plan's ask"); the residual measured above is carried to R10-COP-GATE |
| 919 | `_interval_measured_heat_kw` | converted here: asks `heat_energy.attribution` (and so #2753's replay and `replay_freeze`'s lift, which it is handed) |
| 1016 | `_propagated_slab` | out of scope by the design (`draw_range.space_draw_kw`: electric replay without a heat meter, a behaviour no finding names) |
| 1091 | `_async_learn_heat_span` | by design: the span's `close_span` is handed the plan split, and the attribution governs inside `close_span` |
| 1188 | `_settle_interval_diag` | converted here: the diagnosis triple's shares come from the attribution |
| 4782 | `_commanded_power` | out of scope by the design (the plan's ask) |
| 4803, 4833, 4840 | `_interval_space_power` | out of scope by the design (electric replay without a heat meter) |
| 5063 | `_cop_reference_curve` | converted here: asks the attribution |
| 9855 | `_record_accuracy` (`draw_range.fold`) | out of scope by the design (the draw evidence, which belongs to R10-COP-GATE) |
| 10209, 10212, 10266 | `_accumulate_energy` | converted here: the energy ledger's split is the attribution's |

## Architecture score

Architecture score: dS +0.0131

- `coordinator_multiassigned_attrs` 110 -> 109: the design's day-health flag moved onto the snapshot ring (round 1 of this branch; not this round). This round adds no coordinator statement and no attribute.

## Unpinned sites

The four sites `tools/pr/ci_predict.py --base 3b4180dcc680` listed, each driven in the in-tree table above; `mutation-autofix` pinned all four at `69d4bb2be9` (`_fold_measured_cop`'s two guards, `BOOLOP` and `GUARD_OFF` each), which this head merges. `ci_predict.py --base 524c1896b` now reports no unpinned site.

- `custom_components/heatpump_optimizer/coordinator.py:5075 BOOLOP` -- row U, the exemption's `and` turned into `or`: the suite aborts in setup with `TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'`, one failing check under the rule above
- `custom_components/heatpump_optimizer/coordinator.py:5075 GUARD_OFF` -- row V, the no-power refusal off: `ConfigEntryNotReady: Error updating data: float() argument must be a string or a real number, not 'NoneType'`, one failing check under the rule above
- `custom_components/heatpump_optimizer/coordinator.py:5082 BOOLOP` -- row W, the floor's `and` turned into `or`: `UnboundLocalError: cannot access local variable 'refusal' where it is not associated with a value`, one failing check under the rule above
- `custom_components/heatpump_optimizer/coordinator.py:5082 GUARD_OFF` -- row X, the per-cycle floor off: four checks fail (`a folded COP interval clears the refusal`, `a refused COP interval names its guard and the floor in the diagnostics`, `idle and standby draws under the modulation floor still teach nothing`, `with no modulation floor configured the nameplate floor still applies`)

## Red checks

Two CI checks stand red on commits this branch pushed, and both are named here. `governance / wave-script` was red at `69d4bb2be9`: the job restores the checker from the pull request's base (`524c1896b`, which carries #2871's roster rows) and runs it over the head's tree, which at that commit predated #2871 because the branch had merged only to `4f3c73020`. It is a merge-drift red, not a branch defect: at `8c4bec5c2`, which carries #2871's rows, the same checker (`node tools/policy/check-wave-script.mjs`, 224 checks) passes 0 failed. The cheaper detector is the wave-script lane itself: it is unscoped and runs on every pull request, so the standing cost is unchanged. `tests / typing` was red at `69d4bb2be9` with two real `arg-type` errors in `coordinator.py` (`5109`, `5122`): this branch moved the no-power refusal behind `and not counter` in `_fold_measured_cop`, so mypy no longer narrowed `_measured_power` at the ratio and at the `_fold_cop_evidence` call, although the counter early-return above makes both unreachable without a power reading. It is not repaired in this merge head: the repair is a narrowing change at those two sites, and any such change moves the two ledger pins `CLAMP_DROP 2a1bdb6a` and `RETURN_DEL c0033b3e` and adds two unpinned sites, which is the fixer's mutation proof rather than a conflict resolution; it is reported here so the fixer owns it. The detector is the typing lane itself, already run on every pull request at the recorded pair, so no cheaper one exists and the standing cost is unchanged. The branch's earlier concluded reds stay answered: `tests / mutation` at `91d78cbca` by the checks this branch adds, `gate` as their aggregate, `pr-contract` by naming `prelude`, `prelude` as a queue-wait refusal with its twin green on the same head, and `tests / closures` by `closures-autofix` after `ci_predict.py` named the scripts. `ci_predict.py` predicted two `STALE PIN` reds on the fix's first cut and none after `4fc760104`.

## Forward-carry

- **R10-COP-GATE** carry 11, in its brief on `origin/main` (`dev/programme/rosters/wave-r10-groups.json`): render `span_open` (`COP_REFUSED_SPAN_OPEN`) as a span still open, never a refusal, and `counter_reset`, `counter_rollover`, `counter_resolution`, `span_too_long` (`heat_energy.SPAN_REFUSED_*`) and `unaligned_meters` as their own codes. Control: a counter install whose span folds shows its COP as measured while every cycle in between reads `span_open`. Carry: R10-COP-GATE
- **R10-UX-HEALTH** carry 16, in its brief on `origin/main`: a Health string for `span_open` (waiting for the span, not a fault) and for each span refusal code. Control: the Health panel on a counter install mid-span renders the string, never the raw code. Carry: R10-UX-HEALTH
- **R10-REPLAY-REAL-DAY** carry 4 (D15 lead L9), in its brief on `origin/main`: read `unhealthy_input` from each weekly learner snapshot in the next live bundle, name the input that marked each unhealthy snapshot, and change outdoor's 180 min on-change limit only on that evidence. Controls: a week with every input reporting names none (null); a week with one input silent all day names that input. Carry: R10-REPLAY-REAL-DAY
- **R10-COP-GATE** carry 12, added by this branch's own roster edit (`e5472964f`), so it lands with this PR and not after it: the flow-bias learner's duty gate at `coordinator.py:885` reads the commanded split, and the measurement in `## Figures` shows the review's case does not fire while a switch-back window does (one sample folds with the dwell hot-water-dominant, both nulls in the carry). The control the conversion owes: that window folds nothing once the gate reads `heat_energy.meter_of(coord).attribution(...)`, while both nulls still fold. `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` reports 0 errors and 0 warnings at this head: this branch's `const.py` insertions moved `R10-IMMERSION-LATCH`'s line-pinned citation, re-anchored from `const.py:1149` to `const.py:1156` (`IMMERSION_FACTOR`'s line at this head), and nothing in the edited entry is reported. Carry: R10-COP-GATE

## Friction

none




