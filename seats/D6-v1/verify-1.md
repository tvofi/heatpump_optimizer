# D6 verify-1 (round 11)

All findings measured in the planted export copy; each entry lists its tree, load1 and thread_factor. Every vote is verify; details per finding in REPORT.json.

## D6-s1-01 verify severity=low
- metric: doc rows whose executed check contradicts production (default / counted-at-t)
- reproduced: ledger false_rows config doc=3 (287,478,894 sentence); echo contradictions=6 of 8 offsets (5,10,19,21,30,59 s counted); planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: ThermalParameters().dhw_legionella_interval_days=10.0 vs doc 7 (x2); hold() code path has no elapsed-time test (grep), differing reading drops record at +5 s
- attacks: null control: 6 of 8 echo probe offsets contradict, +21..+90 s agree with code; legionella default read from ThermalParameters() = 10.0 and const DEFAULT=10.0; docs lines 287,478 say 7 (line 894 shifted to 901 in this tree); perturbation not run for echo (hold() has no time term, read at pump_arbiter.hold lines 1497-1516). Note hold() ignores ECHO_GRACE_S; only _edited uses 20 s
- reachable: yes: pure code/docs, no stub dependence; class: I5 confirmed; seam_rule_enumerates: True

## D6-s1-02 verify severity=medium
- metric: README ledger rows contradicting tree; learner row = closed-loop heat_loss_scale end and breach K.h
- reproduced: legionella_default false (10 days); learner scale 1.000->0.300, std 0.0101, breach plain 0.00 -> learned 5.42 K.h; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: own check: ThermalParameters().dhw_legionella_interval_days=10.0; learner number is the finder harness only (not independently rerun, 3 min sim)
- attacks: null control learner_left_alone_12pct true (scale 0.979 with plant_error 1.0): loop not broken at 1.0; config pins heat_pump_max_power 4.25 (finder choice, claim names no such cap) so the divergence is under that config only; legionella README line 506 (499 in baseline) reads 'every 7 days' vs 10
- reachable: yes for README claim; the closed loop uses tests/rolling.py, not HA; class: I5 confirmed (learner arm hints a production P-class defect: scale pinned at its 0.300 floor); seam_rule_enumerates: True

## D6-s2-01 verify severity=high
- metric: strings.json sentences contradicted by the production symbol deciding them
- reproduced: false rows=6 (return_gate x2 sentences, station_potable, wood_packing, flow_units, observe_writes); planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: const.FLOW_UNIT_TO_KG_S['L/min']=0.998/3600 (should be /60: 60x low); COMBI_TANK_PRESETS['external_station'].potable_volume_l=150; wood_fuel.WOOD_KWH_M3['birch']=1140/1900
- attacks: perturbations move: wood 1->0, flow 0.01667->1.0, potable 150->0.0, observe 1->0, return gate 30->20. Direction caveat: for wood, flow and potable the sentence is physically right and the code is wrong (const FLOW_UNIT_TO_KG_S['L/min']=WATER_KG_PER_L/3600 equals the L/h row; const.py comment says external_station is 0 l, code 150; birch loose 1900 > packed 1140 while pine/mixed are 0.60). So these are production defects, not only text drift. Observe: _arbitrate falls through to _command for mode!=control (dhw slot is gated by _grid, mode/space slots are not); my real-_arbitrate run errored on stub inputs so observe is verified by code reading plus the finder's stubbed probe only
- reachable: yes: all pure code paths; flow meter read in inputs.py:352 live; class: new (docs-vs-code, with production data defects; nearest I5/P6); seam_rule_enumerates: True

## D6-s2-02 verify severity=low
- metric: cited path absent from tree
- reproduced: gov_paths=2 (perturbation 0); planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: grep for docs/decisions/ outside round evidence: 9 hits in 6 files
- attacks: dev/governance/decisions/0011-app-authored-identity.md exists, docs/decisions/ does not; the same stale prefix appears also in .github/workflows/governance.yml:439,1631 and decisions 0006/0012/0013 (some may be historical references), so the seam is wider than the two rows
- reachable: yes (agent-facing docs); class: I5 confirmed; seam_rule_enumerates: False

## D6-s2-03 verify severity=low
- metric: cited path absent from tree
- reproduced: gov_paths=2; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: grep as s2-02
- attacks: dev/governance/decisions/0010-merge-commits-on-main.md exists, docs/decisions/0010 does not; same wider seam as s2-02
- reachable: yes (agent-facing docs); class: I5 confirmed; seam_rule_enumerates: False

## D6-s3-01 verify severity=low
- metric: description placeholders the text reads minus those the render supplies, config refusal
- reproduced: config_refusal_missing=2, changed_vs_preview=3, options_refusal_missing=0; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: code read: disclaimer() returns two keys only; found/backup_heater_type come from modbus_prefill (line 281)
- attacks: null control options refusal missing=0 (sibling keeps them); config_flow _device_prefill_form passes only device_prefill.disclaimer() (name_matched, matched_sources) plus notes; perturbed run exits 0 unrenderable. Real HA renders unresolved braces literally, no exception, so low consequence
- reachable: yes (real HA description_placeholders); class: P2 confirmed (sibling page keeps them); seam_rule_enumerates: True

## D6-s3-02 verify severity=medium
- metric: loose/packed kWh/m3 per wood type vs 0.60
- reproduced: types_off_claim=1, packed_birch_sek_per_kwh=1.4035; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: own read wood_fuel.WOOD_KWH_M3: birch packed 1140 loose 1900
- attacks: null: pine 900/1500=0.600, mixed 1020/1700=0.600; birch 1900/1140; perturbation swapping birch entries gives 0; packed birch 1.4035 SEK/kWh. Same defect as D6-s2-01 wood row (duplicate of one of its six rows); the fault is the birch data, text is right
- reachable: yes: pricing path live; class: new (data row swapped; docs-vs-code); seam_rule_enumerates: True

## D6-s4-01 verify severity=low
- metric: L() outputs with leftover {name} per language
- reproduced: unresolved_sv=1, stale_title_literal_tokens=1; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: grep: exactly 1 '{minuter}' in the card
- attacks: null control en=0, de=0; perturbation moves sv 1->0; sv string uses {minuter} (www card line 1794) while call site passes {minutes} (9674). Sole offender by the finder's whole-dictionary sweep
- reachable: yes: card reads hass.language sv in real HA; class: I5 confirmed; seam_rule_enumerates: True

## D6-s4-02 verify severity=low
- metric: plan writes a day at budget B vs the sentence '0 or 1 writes nothing, one always kept'
- reproduced: plan_writes B1=1 B2=2 B12=12, total_with_restore B1=2 B2=3 B12=13; planted export copy (audit-r11-px-D6-1), PYTHONPATH=tests/hastub, /opt/hpo/venv-ci python (no $HOME/venv-ci on this box); load1 0.8-2.2, thread_factor 1.00
- independent: formula read: allowed iff count+1<=budget, so B=1 allows 1
- attacks: perturb (+1 -> +2) moves plan_writes 1,2,12 to 0,1,11; the identical sentence is in en.json and strings.json (so en is equally false); restore write goes through _record_write (counted to the day) but is not budget-gated, so a day reaches B+1 (13 at B=12); the guard at heat_curve.py:556 is writes_today+1>budget
- reachable: yes: heat curve persistent write path live; class: I5 confirmed; seam_rule_enumerates: True

