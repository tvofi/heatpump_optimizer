# Review packet #3734
head: e9ad13fa58e02965bb5eb772b19535c09c9523c6
base: e893cd3d1ebd1ec3bb56756ce902144a370fe821

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=136821089758 success
budget-raise-gate / budget-raise-gate id=136821092445 success
cancel-superseded id=136821098832 skipped
codeql id=136615740276 skipped
codeql / Analyze (actions) id=136821085275 success
codeql / Analyze (javascript-typescript) id=136821074960 success
codeql / Analyze (python) id=136821061421 in_progress
gate id=136624510662 failure
governance id=136615740207 skipped
governance / env-matrix id=136821088043 success
governance / instrument-self-tests id=136821099658 success
governance / policy-docs id=136821101388 success
governance / record id=136821062376 skipped
governance / wave-script id=136821092250 success
hassfest id=136615740025 skipped
hassfest / hassfest id=136821098136 success
kernel-points id=136821096132 skipped
pr-contract / pr-contract id=136620400573 success
prelude id=136821093810 success
refresh id=136821077702 skipped
sweep-self id=136631508451 skipped
tests id=136615741084 skipped
tests / arch-instrument id=136821063236 success
tests / briefs id=136821091185 success
tests / browser id=136821063260 success
tests / ci-ratchet id=136821064408 skipped
tests / claims-autofix id=136821063817 skipped
tests / closure-scope id=136821063209 success
tests / closures id=136821063846 success
tests / closures-autofix id=136821063987 skipped
tests / coverage id=136821063271 success
tests / coverage-ratchet id=136821064149 success
tests / fast (3.14) id=136821063561 success
tests / graders-head-copy id=136821064332 skipped
tests / lane-proofs id=136821064494 skipped
tests / mutation id=136821096980 success
tests / mutation-autofix id=136821063572 skipped
tests / mutation-pins id=136821063011 skipped
tests / nightly-ha id=136821062790 skipped
tests / nightly-status id=136821100075 skipped
tests / replay id=136821063781 skipped
tests / typing id=136821101364 success
validate id=136615741469 skipped
validate / validate-hacs id=136821074089 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at e9ad13fa58e02965bb5eb772b19535c09c9523c6 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item ed976865: dismissed:the absence is recorded under Figures, and the round-end triage reads it there.
NOTE body item d3bb5061: dismissed:answered by the orchestrator's inbox ruling, line 1 of refs/heads/inbox/r11-seam-inputs-guards.
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  unverified EXPORT=$(mktemp -d); git archive 819aa2e354b4e5baaf824b8568fd72bea8168a75 dev/audit/rounds/round11 | tar -x -C $EXPORT
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py
             the path `$EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only temperature_roundtrip
             the path `$EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/s3/parsers_fuzz.py --arm pump
             the path `$EXPORT/dev/audit/rounds/round11/D1/s3/parsers_fuzz.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D1/leads/plausible_upper.py
             the path `$EXPORT/dev/audit/rounds/round11/D1/leads/plausible_upper.py` is a template or an expansion, not a literal
  unverified PYTHONPATH=tests/hastub:tests python3 $EXPORT/dev/audit/rounds/round11/D1/s2/config_fuzz.py --versions N
             the path `$EXPORT/dev/audit/rounds/round11/D1/s2/config_fuzz.py` is a template or an expansion, not a literal
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head

FIGURES: 7 resolved, 7 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
new file mode 100644
index 0000000000..2161ad64c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.ab300483.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:async_migrate_entry GUARD_OFF ab300483",
+  "killed_by": "tests/entities.py",
+  "old": "        if repairs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.CMP_BOUND.6bfd271f.json b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.CMP_BOUND.6bfd271f.json
new file mode 100644
index 0000000000..4dc323f737
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.CMP_BOUND.6bfd271f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_interval_minutes CMP_BOUND 6bfd271f",
+  "killed_by": "tests/entities.py",
+  "old": "    if minutes is None or not 0.0 < minutes <= _MAX_PLAN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if minutes is None or not 0.0 <= minutes <= _MAX_PLAN_MINUTES:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.GUARD_OFF.6bfd271f.json b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.GUARD_OFF.6bfd271f.json
new file mode 100644
index 0000000000..9866c220cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.GUARD_OFF.6bfd271f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_interval_minutes GUARD_OFF 6bfd271f",
+  "killed_by": "tests/entities.py",
+  "old": "    if minutes is None or not 0.0 < minutes <= _MAX_PLAN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
new file mode 100644
index 0000000000..8ef22ec1ad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_interval_minutes.RETURN_DEL.3410ce8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_interval_minutes RETURN_DEL 3410ce8b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return minutes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.CMP_BOUND.ca4768b4.json b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.CMP_BOUND.ca4768b4.json
new file mode 100644
index 0000000000..ea49048d7e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.CMP_BOUND.ca4768b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_lead_minutes CMP_BOUND ca4768b4",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    if minutes is None or not 0.0 <= minutes <= _MAX_PLAN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if minutes is None or not 0.0 < minutes <= _MAX_PLAN_MINUTES:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.GUARD_OFF.ca4768b4.json b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.GUARD_OFF.ca4768b4.json
new file mode 100644
index 0000000000..858115e98e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.GUARD_OFF.ca4768b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_lead_minutes GUARD_OFF ca4768b4",
+  "killed_by": "tests/entities.py",
+  "old": "    if minutes is None or not 0.0 <= minutes <= _MAX_PLAN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.RETURN_DEL.3410ce8b.json b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.RETURN_DEL.3410ce8b.json
new file mode 100644
index 0000000000..d9087563c0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/_lead_minutes.RETURN_DEL.3410ce8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:_lead_minutes RETURN_DEL 3410ce8b",
+  "killed_by": "tests/features.py",
+  "old": "    return minutes",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
new file mode 100644
index 0000000000..13f963296c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.6aa9ea3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF 6aa9ea3a",
+  "killed_by": "tests/features.py",
+  "old": "        if not isinstance(entity_id, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
new file mode 100644
index 0000000000..c5754e5738
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/parse_bool.RETURN_DEL.3434dfb6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:parse_bool RETURN_DEL 3434dfb6",
+  "killed_by": "tests/features.py",
+  "old": "    return None if number is None else number != 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
new file mode 100644
index 0000000000..620f1267b2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.30aea580.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 30aea580",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    kept = [i for i, t in enumerate(times) if t >= floor]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`kept = [i for i, t in enumerate(times) if t > floor]`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
new file mode 100644
index 0000000000..4a1284b11b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.CMP_BOUND.4d7eb319.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block CMP_BOUND 4d7eb319",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if len(kept) < 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(kept) <= 2:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.4d7eb319.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.4d7eb319.json
new file mode 100644
index 0000000000..e884adff30
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.4d7eb319.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block GUARD_OFF 4d7eb319",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if len(kept) < 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Review scope: delta (later round over the reviewed head 98cb43e750457b41ae6feb9a0c56cf1d6728e201)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 98cb43e750457b41ae6feb9a0c56cf1d6728e201
Fix review: blocked 98cb43e750457b41ae6feb9a0c56cf1d6728e201 mutation-vacuous: open_meteo.py _parse_block len(kept) < 2 loosened to < 1 survives every _parse_block caller and is not equivalent

bus-nonce: 9067c8bbf58c0d6c4f2d781b8a9243f8

## Block

- Round 3 of this PR (round 2 blocked at 40328a85, `class-open: wood_fuel.lighting_window`). Review scope: full. The packet rendered with no `--reviewed-head`.
- Survivor: `custom_components/heatpump_optimizer/open_meteo.py:256`, the line this PR adds, `if len(kept) < 2:` mutated to `if len(kept) < 1:`. Under the mutant these all stay green: `tests/open_meteo.py` (`ALL OPEN-METEO CHECKS PASSED`), `tests/solar_alignment.py` (`ALL SOLAR ALIGNMENT CHECKS PASSED`), and features.py's block `P1/P2/N-min-gap ... feed parsers`, which is the only other `_parse_block` caller (`ALL 7 FEATURES BLOCK PASSED`). See `ev/m12_closure_runs.txt`. I did not run the other 20 scripts in open_meteo.py's measured closure. None of them calls `_parse_block` (scout locate over `tests/` and `tools/`).
- The body says round 1's reviewer dismissed this mutant (round 1's M14) "as equivalent under `mean_over`'s coverage rule". It is not equivalent: `ev/m12_probe.txt` (driver `ev/m12_probe.py`, run on a `git archive` of the head):
  - Block `{"time": ["0001-01-01T00:00", "2026-08-21T00:00"], "shortwave_radiation": [1.0, 100.0]}`.
  - At the head, the block parses to an empty series. `mean_over` reads `None` for 23:00-00:00, 23:30-00:00 and 22:00-01:00.
  - Under the mutant, it parses to a one-sample series `(2026-08-21 00:00, 100.0)` with `resolution 739848 days, 0:00:00`. Its span `(t - resolution, t]` reaches back to year 1. `mean_over` then reads `100.0` for all three windows.
  - The guard is what refuses a lone survivor whose resolution was inferred from a gap to the dropped stamp. That case always has a span back to year 1: with two stamps and one dropped, the single gap is at least the survivor's distance from year 1.
- The finder's harness does not separate the mutant. `parsers_fuzz.py --arm openmeteo` reads `openmeteo_year1_solve_failures=0` at the head and also under the mutant (`ev/finder_openmeteo_mb_head_m12.txt`). This survivor is therefore a test gap, not a regression of D1-s3-03's metric.
- Remedy, owed by the fixer: a `tests/open_meteo.py` check that the two-stamp block above parses to no samples (or that `mean_over` reads `None` over a window it would otherwise claim), with its null control. The rest of the review holds, and a re-review is the delta.

## Findings

- Residual: features.py's P8 block (`R.section("P8 — a price or temperature entity's unit is read at the seam (#1513)")`) does not run alone under `tools/audit/seat/features_block.py`, even with the `_r9f41_const` prelude: `NameError: name '_Coord' is not defined` after the D7-s3-01 check. The D7-s3-01 check reads `ok` at the head and `FAIL` under its mutant before the NameError, so the proof stands, but the block cannot be run whole. Carry: dismissed: a seat-instrument convenience, `--emit-prelude` derives the missing prelude; nothing in this PR's code or tests depends on it.
- Note: paperwork: the body's `## Unpinned sites` row for `entry_config.py:52` still names `_MAX_INTERVAL_MINUTES`, which the repair renamed `_MAX_PLAN_MINUTES`. Carry: dismissed: a stale name in the body, settled by the fixer's next body edit on this PR.

## Evidence

- Head reviewed: 98cb43e750457b41ae6feb9a0c56cf1d6728e201 (`ev/HEAD.txt`). Merge base: ae0ed64af898d8923ac35afe6e9c031ac1e6b111.
- `git merge-tree --write-tree origin/main 98cb43e7...` rc=0, no conflict (`ev/merge-tree.txt`).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, `tests/golden/`, `tests/*budgets.json`: three-dot diff empty (`ev/untouched.txt`).
- Mutation proof, one at a time, worktree at the head, with `git status --porcelain` empty after each (`ev/mutants_*.log`, driver `ev/mutant_driver.py`). Killed:
  - M1, `parse_bool` back to `float(token) != 0.0`: `FAIL parse_bool reads no non-finite number as a flag (D1-s3-01)`.
  - M2, `_begin`'s `isinstance(entity_id, str)` guard deleted: the block dies with `TypeError: cannot use 'dict' as a dict key`.
  - M3, `kept` = every index: `FAIL a stamp with no representable span is dropped, and the block still averages`.
  - M4, `repairs = {}`: `FAIL an old entry's non-numbers under numeric options are repaired, with one warning naming them`.
  - M6, `_attach_windows` reading the raw option with `max(0.0, finite_float(...))`: `FAIL a stored lead outside [0, a day] is the default 60 min`.
  - M7, `_interval_minutes`'s range guard dropped: `FAIL an optimization interval outside (0, a day] parses as the default`.
  - M8, `temperature_from_c` multiplying by the factor: `FAIL temperature_from_c inverts every unit row the reader converts (D7-s3-01)`.
  - M9, `plausible_c` one-sided: `FAIL every plausible window refuses a reading one degree past either end (D1-s2-51)`.
  - M11, `repaired_numbers` keeping keys mapped to None: `FAIL an old entry's non-numbers ... repaired`.
  - M13, the lead floor made strict: `FAIL a lead inside [0, a day] is its own`.
  - M5, `_lead_minutes` dropped from `_DEFAULTED_NUMBERS`: `FAIL every option whose parse defaults text it cannot read is repaired by the migration [unrepaired: ['wood_lighting_lead_minutes']]`.
  - M10, `number_repairs`'s bool branch dropped: `FAIL an old entry's non-numbers ... repaired` (`cop_scale: True` left stored).
  - M14, the `mixing_valve_target` declaration deleted: the same check (`mixing_valve_target: 'abc'` left stored).
- Survivor: M12 (above).
- The finder's harnesses, from the plan export 819aa2e3 (`parsers_fuzz.py` sha1 74da66cd7b0beac627cb2a636e6c0364c1ddc019), merge base then head (`ev/finder_*.txt`). Each matches the body:
  - `pump_nonfinite_flag_true`: 10 then 0. `pump_nonfinite_freeze_fault`: 5 then 0. `pump_null_control_zero_flag_true`: 0 then 0.
  - `openmeteo_year1_solve_failures`: 3 then 0. `openmeteo_healthy_solve_failures`: 0 then 0.
  - `config_fuzz.py --versions 2`: `build_fail` 11 then 0, `permanent_cycle_fail` 14 then 0. `--versions 5`: 5 then 0 and 17 then 0. I re-ran v2 and v5 only; v1, v3, v4 and v6 were not re-run.
- Body figure "47 fields" re-derived: the selection by parse behaviour returns 47 fields, with parses exactly `_interval_minutes`, `_lead_minutes`, `_nonzero_number` and `finite_float`. It equals the `_DEFAULTED_NUMBERS`-declared set (difference empty).
- Class step: every production reader of `optimization_interval` and `wood_lighting_lead_minutes` reads the parsed `EntryConfig` field (`coordinator.py`, `supply_hold.py:101`, `__init__.py:179`, `early_cutoff.py:172`, `heat_curve.py:348`, `wood_fuel.py:560`). `sysid.py:1359` reads the constant default. No raw reader is left. I found no seam beyond the body's dispositions.
- Step 16: no new path skips an actuator write.
- CI, live classify on this head, polled every ~60 s since 22:49 UTC: still WAIT at the verdict, last line `WAIT 98cb43e750457b41ae6feb9a0c56cf1d6728e201 pending: gate red: none` (`ev/classify_poll.log`). The block above is on tests, not CI. The digest's `tests / mutation` red is in the `owed-reds` set and is answered in the body's `## Red checks`; I checked that it was answered, not the answer.

