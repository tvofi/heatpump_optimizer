import glob, json
D = "dev/audit/rounds/round11/D5/s2"
SHA = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
DOCS = ("README.md docs/CONTRIBUTING.md docs/architecture.md docs/automations.md docs/configuration.md "
        "docs/dashboard-card.md docs/ecl110.md docs/how-it-works.md docs/setup.md")
SCRIPTS = ("docs/img/card/make_card_figures.mjs docs/img/model/make_card_weekly_figure.mjs "
           "docs/img/model/make_model_figures.py docs/img/readme/make_readme_figures.py "
           "docs/img/readme/render.mjs docs/img/readme/render_mermaid.mjs")
findings = [json.load(open(p)) for p in sorted(glob.glob(f"{D}/findings/D5-s2-*.json"))]
H = lambda n: f"{D}/{n}"
report = {
 "dimension": "D5",
 "baseline_sha": SHA,
 "report_path": f"{D}/REPORT.md",
 "exposure": ("Read README.md and docs/*.md (D5 brief): how-it-works.md in full, configuration.md prose and tables, "
              "architecture.md prose, the README 'How it works' section, ecl110.md's options and 'What the integration sends', "
              "CONTRIBUTING.md's opening; comments citing earlier ids met as context only (R9-UI-4, #558 C1/C2/C3, D4-01, R4-D4-01, "
              "D1-s5-51, R10-README-GRAPHICS, R9-WEB-4, #1413 in tests/closure.py and doc_claims.py). The wall-removed "
              "dev/archive/backlog.md (linked from how-it-works.md:1454) was not looked for."),
 "coverage": [
  {"step": "D5.M2",
   "enumerator": f"python3 tools/audit/text_ledger.py outline {DOCS} | awk -F'\\t' '$3==\"heading\"||$3==\"link\"'",
   "universe": 382, "examined": 382, "not_reached": [],
   "redispatched": [{"item": "C3", "state": "examined"}],
   "evidence": ("structure.py over all 382 rows (207 headings: depth/order/multiple h1; 175 links: 142 internal file+anchor by "
                "GitHub's slug rule, 33 external fetched with --net, all < 400), plus paragraph-hash repeats, fenced-block repeats, "
                "orphan documents, stale HA/Python versions and the README/configuration menu twin. C3: the code/JS cells in this "
                "seat's cells are the six docs/img generators; outline prints no rows for them, and their structure (header usage "
                "lines, the paths and commands they name) was checked by comments.py; production code/JS cells belong to D5-s3/s4.")},
  {"step": "D5.M3",
   "enumerator": f"python3 tools/audit/text_ledger.py units --dim D6 {DOCS}",
   "universe": 3265, "examined": 3265,
   "not_reached": [],
   "redispatched": [{"item": "C1", "state": "examined"}, {"item": "C2", "state": "examined"}, {"item": "C4", "state": "examined"}],
   "evidence": ("All 3265 units examined (first pass: how-it-works.md 583, configuration.md 1037, architecture.md 84; re-run on the orchestrator's order: the 1561 units left). Arms on all: content.py (579 backticked symbol mentions in 315 units, 0 stale), basis.py. Mechanism trace: defaults.py (57 stated numbers vs ThermalParameters/const/module constants, 7 drifted, incl. 21 Pump duty control numbers traced to pump_arbiter.py/duty_switch.py/boost.py), defaults_table.py (108 table defaults, 79 ranges), cycling.py, dhw_enable.py, menu_order.py, and executed spot traces per document: README (ring of 8 snapshots, 20 h manual window, comfort 21/19.5 and 07-22, 31 set_thermal_parameters fields, 15 services, 12 K slab-seed bound), dashboard-card.md (900x380 view, 48 h history in 12 h chunks, hours 1-168, 0.05 kW running threshold, plan stale 3 intervals/90 min, 24-month receipts, silent slider 0.6-1, 10 series keys), setup.md (menu order, wood top probe 5 K, pre-fill offer), automations.md (5 events by name, economy 1.5 K/15 degC floor, plan stale), ecl110.md (options registry, offset/persistent bands, 12 writes/day, 60 min dwell, 90 s grace, 2x1440/interval guard, the Luxtronik curve deltas 1.15/1.25/1.35 K recomputed), CONTRIBUTING.md (branch rule, review comment and adoption shape in bus.sh adopt, agent words in AGENT_DECLARED). C1: this row is the denominator round 10 lacked; C2: how-it-works and configuration mechanism paragraphs traced, Pump duty control numbers included; C4: every docstring in this seat's cells rowed in the M4 ledger by an executed check.")},
  {"step": "D5.M4",
   "enumerator": f"python3 tools/audit/text_ledger.py units --dim D5 {DOCS} {SCRIPTS}",
   "universe": 75, "examined": 75, "not_reached": [],
   "redispatched": [{"item": "C5", "state": "examined"}],
   "evidence": ("comments.py writes work/m4_ledger.tsv: 75 rows, 56 claims (54 true, 2 false), 19 no-claim; text_ledger check: "
                "unrowed=0 orphan=0 malformed=0; --plant fails structurally for this seat (finding D5-s2-07), passes "
                "(plant_refused=1, rc 0) with a D5-suffix file first. C5: cited_numbers.py automates the cited-number-vs-adjacent-"
                "literal check (10 cited, 3 without an adjacent literal, each true by its comments.py check); the README/docs M4 "
                "cell ran (the 9 documents are one `file` unit each under D5); www/*.js is D5-s4's cell, handed over as a lead.")}],
 "unfinished": [],
 "findings": findings,
 "non_findings": [
  {"claim": "Pump duty control (configuration.md 683-966): 21 stated numbers equal the arbiter's constants (flow ceiling 55, hold 35, gates 25/30, return spread 5 K, lift 5 K, feedback 5 min/0.2 K per min/3 min/10 %/0.3 K, stop window 3 min, 5 switches, 14-day half-life, two days, rails 90/30 min, boost 2 h, retry 5 min, tank rise 0.5)", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/defaults.py", "value": "21 ok; the one BAD there is the echo grace (D5-s2-08)"},
  {"claim": "ecl110.md offset entity and persistent-parameter defaults and ranges equal the registry; the loop guard is 2x1440/interval; the write grace is 90 s; the Luxtronik curve example recomputes to 1.15/1.25/1.35 K", "command": "PYTHONPATH=tests/hastub:custom_components python3 -c 'import heatpump_optimizer.config_flow as cf ...'; grep -n HELD_GRACE_S custom_components/heatpump_optimizer/heat_curve.py", "value": "3.0 K (0.5-5) x2, 12 (0-48), 60 min (15-360); 90.0 s; [1.15, 1.25, 1.35]"},
  {"claim": "automations.md: the five event names, economy widening 1.5 K with a 15 degC floor, plan stale after three cycles (90 min floor)", "command": "grep -n EVENT_ custom_components/heatpump_optimizer/notifier.py; grep -n ECONOMY_ custom_components/heatpump_optimizer/const.py", "value": "5 events; 1.5 / 15.0; 'older than three solve cycles (min 90 min)'"},
  {"claim": "README and dashboard-card numbers: 8 snapshots kept, 20 h manual window, 21/19.5 degC and 07-22, 31 set_thermal_parameters fields, 900x380 chart, 48 h history in 12 h chunks, hours 1-168, 24 receipts, silent slider 0.6-1", "command": "grep RING_SIZE snapshots.py; MANUAL_PLAN_WINDOW_HOURS; VIEW_W/VIEW_H, HISTORY_SPAN_MS/CHUNK_MS in the card; KEEP_MONTHS ledger.py", "value": "all equal"},
  {"claim": "setup.md wood probes: top-only bulk read 5 degC colder, bottom-only gives none", "command": "sed -n 42,57p custom_components/heatpump_optimizer/external_heat.py", "value": "top - 5.0; None without top"},
  {"claim": "CONTRIBUTING.md review shape (VERDICT.md + ev/, comment first line + review-commit) and refused agent words match bus.sh adopt and AGENT_DECLARED", "command": "sed -n 355,425p tools/audit/seat/bus.sh; sed -n 100,102p tools/policy/budget_raise_gate.py", "value": "match"},
  {"claim": "No heading skips a level and no document has a second h1 (207 headings)", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py", "value": "heading_skip=0 heading_multi_h1=0"},
  {"claim": "Every internal link and anchor resolves (142 internal links; planted control: 2 dead anchors counted)", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py [--plant]", "value": "link_file_missing=0 link_anchor_missing=0 (plant: 2)"},
  {"claim": "Every external link answers below HTTP 400", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py --net", "value": "external_checked=33 external_bad=0"},
  {"claim": "No stale Home Assistant or Python version in the reader docs (HA floor 2025.2.0 = hacs.json; Python 3.13 in badge, README and architecture.md)", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py; grep -noE 'v?[0-9]+\\.[0-9]+\\.[0-9]+' README.md docs/*.md", "value": "stale_ha_version=0"},
  {"claim": "Every backticked code symbol, path, entity id and service the reader docs name exists in the code corpus", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/content.py [--plant]", "value": "symbol_mentions=579 stale_symbols=2, both deliberate negatives (direct_radiation named as not used; luxtronik_shi an external integration's name); plant +1"},
  {"claim": "configuration.md options-page defaults and ranges agree with config_flow._OPTION_FIELDS except the legionella interval", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/defaults_table.py", "value": "rows_comparable=108 default_mismatches=1 (legionella, in D5-s2-08); rows_with_range=79 range_mismatches=0"},
  {"claim": "50 other stated mechanism numbers match the shipped values", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/defaults.py", "value": "pairs=57 mismatches=7 (all in D5-s2-08)"},
  {"claim": "Services paragraph of configuration.md: 15 services, 10 take entry_id, required only on factory_reset, 5 act on every entry", "command": "python3 -c \"import yaml;d=yaml.safe_load(open('custom_components/heatpump_optimizer/services.yaml'))...\"", "value": "15 / 10 / ['factory_reset'] / 5"},
  {"claim": "how-it-works 'What the tests actually prove' thresholds match tests/rolling.py", "command": "grep -n -E '< 3\\.0|1\\.6|0\\.15|0\\.12|0\\.05|> 10' tests/rolling.py", "value": "3.0 dh, 1.6x, >10 samples, +0.05, <=TRUE_ERROR+0.15, std<0.05, |drift-1|<0.12 all present"},
  {"claim": "ecl110.md options table matches the registry (topics empty, qos 1 of 0-2, retain off, displace -20/+20 within -30..0/0..30, PID 1.5 h within 0.25-6); heat_pump_on threshold 0.1 kW", "command": "PYTHONPATH=tests/hastub:custom_components python3 -c 'import heatpump_optimizer.config_flow as cf ...'", "value": "all equal; MIN_RUNNING_DRAW_KW=0.1"},
  {"claim": "CONTRIBUTING.md branch-name rule (letters, digits, . _ - /, <=100 chars, leading alnum, not main) equals tools/pr/outside.py:HEAD_REF", "command": "grep -n HEAD_REF tools/pr/outside.py", "value": "[A-Za-z0-9][A-Za-z0-9._/-]{0,99}"},
  {"claim": "dashboard-card.md documents all 10 SERIES_DEFS keys under series:", "command": "sed -n 1061,1072p docs/dashboard-card.md; grep -n '^    key:' card SERIES_DEFS", "value": "10 = 10"},
  {"claim": "dashboard-card.md 'House heat loss in W/K' row reads the effective basis (heat_loss_w_per_k = house_heat_loss_effective x 1000)", "command": "sed -n 2054,2062p custom_components/heatpump_optimizer/sensor.py", "value": "effective basis; the gap is only the identification figure's (D5-s2-03)"},
  {"claim": "54 of 56 claim-bearing comment units in the docs/img generators are true of their code by executed checks (closure classification, card source, ThermalModel runs, contrast ratios 6.48/5.12, 2026-01-16 a Friday, parse_windows split 2, plan payload 0.07 degC above the minimum)", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py --plandata $TMPDIR/plandata.json", "value": "true=54 false=2 (D5-s2-04, D5-s2-05)"},
  {"claim": "No comment in render.mjs, render_mermaid.mjs or make_readme_figures.py fails C1 or C5; render_mermaid's run-block 69-word hit is command lines, not prose", "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/comments.py", "value": "false 0, long_sentences 0 for those three files"},
  {"claim": "C4 (history over reason): no comment unit in the cells is more than half history", "command": "work/m4_ledger.tsv read unit by unit", "value": "0 units; the longest history clause (make_card_weekly_figure.mjs header's 'older picture') is one sentence of seven"}],
 "harnesses": [H("structure.py"), H("content.py"), H("basis.py"), H("defaults.py"), H("defaults_table.py"), H("cycling.py"),
               H("dhw_enable.py"), H("comments.py"), H("plant.py"), H("cited_numbers.py"), H("menu_order.py")],
 "leads": [
  {"owner_seat": "D5-s4", "file": "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", "symbol": "comment units", "what": "Round 10 carry C5: www/*.js comments not scanned for named symbols; this seat's cells hold none of it."},
  {"owner_seat": "D5-s8", "file": "tests/card_drift.mjs", "symbol": "header comment (lines 20-33)", "what": "Says 'docs/ is INERT in tests/closure.py, so a card change selects no script that reads them'; closure.INERT_EXCEPT now lists docs/img/card PNGs (card-plan-chart.png, plan-light.png, ...) that tests/doc_claims.py reads, so the sentence is true only of the two SVG figures; check against closure.is_inert."},
  {"owner_seat": "D6-s1", "file": "README.md", "symbol": "line 927-962 page table vs docs/configuration.md 337-365", "what": "Three drifted twins need a truth verdict: Fuse and peak guards (silent mode), Heat curve control (controller time constant), Sensors and entities ('Tibber token' vs 'Price source')."},
  {"owner_seat": "D6-s1", "file": "README.md", "symbol": "'How it works' prose, line ~880", "what": "'The prices come from Tibber' omits the price-sensor source configuration.md:13 documents (price_source / price_entity)."},
  {"owner_seat": "D6-s1", "file": "docs/how-it-works.md", "symbol": "lines 622, 1004, 827-831, 303-305", "what": "Sentence-level truth for D5-s2-08/09/10/11: legionella interval 7 vs 10 days, input age 60 vs 360 min, configuration.md:900 echo grace 60 vs 20 s, the smooth start term, the DHW presence rule, setup.md:131 menu order."},
  {"owner_seat": "D5-s1", "file": "docs/CONTRIBUTING.md", "symbol": "inbound links", "what": "Developer reader path: the contributor guide is linked from no reader document (D5-s2-02); reachable only via GitHub's sidebar."},
  {"owner_seat": "D5-s6", "file": "tools/audit/text_ledger.py", "symbol": "run_check --plant", "what": "Instrument defect D5-s2-07 sits in this seat's cell; its fix should also add a self-test arm with a .md first file under --dim D5."}]
}
json.dump(report, open(f"{D}/REPORT.json", "w"), indent=1)
print(len(findings), "findings;", sum(len(c["not_reached"]) for c in report["coverage"]), "not_reached groups")
