#!/usr/bin/env python3
"""D6-s4 ledger: row every D6 unit of the seat's cells, with an executed check per checked claim.

Metric: per unit of `tools/audit/text_ledger.py units --dim D6` over the two cell files, a
ledger row; RESULT counts of claims checked true / false and claims left NOT CHECKED.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s4/ledger.py
      (writes dev/audit/rounds/round11/D6/s4/LEDGER.tsv; then
       python3 tools/audit/text_ledger.py check --dim D6 dev/audit/rounds/round11/D6/s4/LEDGER.tsv
         --plant <the two files> refuses a skipped unit)
Expected at baseline 92d38ecb: units=3913, false=4 (two sv.json units of the persistent
heat-curve write budget, the card's sv stale-pill title, and its sv fragment pair is one
unit), counts exact.
Classification: a unit under 6 words with no digit is a label (no-claim); a unit a check
below matches is a checked claim; every other unit is a claim rowed NOT CHECKED
(verdict `unverifiable`, the next round's not_reached), never silently true.
Checks execute production: const/module attributes imported live, the card through
card_probe.mjs (production `L`, `setConfig`, the stale constants) and the persistent
heat-curve arm through persistent_budget.py (production `_write_persistent_target`).
Perturbation: --perturb sets const.ECONOMY_MIN_TEMP_WIDENING to 2.0 in memory; the
"1,5 K" sv rows flip true->false (false goes up by their count).
Machine: B13 finder box (linux x86_64); counts are load-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, subprocess, sys, time
from pathlib import Path

sys.path[:0] = [".", "tools/audit"]
import text_ledger  # noqa: E402
from custom_components.heatpump_optimizer import const as C  # noqa: E402
from custom_components.heatpump_optimizer import (  # noqa: E402
    coordinator, driving_grade, optimizer, pump_arbiter, slab_seed, slot_drivers, snapshots)

HERE = Path(__file__).parent
SV = "custom_components/heatpump_optimizer/translations/sv.json"
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
if "--perturb" in sys.argv:
    C.ECONOMY_MIN_TEMP_WIDENING = 2.0

t0p, t0t = time.process_time(), time.thread_time()
probe = json.loads([l for l in subprocess.run(["node", str(HERE / "card_probe.mjs")], capture_output=True,
                    text=True, check=True).stdout.splitlines() if l.startswith("JSON ")][-1][5:])
budget = dict(re.findall(r"RESULT (plan_writes_B\d+)=(\d+)", subprocess.run(
    [sys.executable, str(HERE / "persistent_budget.py")], capture_output=True, text=True, check=True).stdout))
OPT_H = optimizer.OptimizationConfig().horizon_hours


def eq(expr, got, want):
    return (got == want, f"{expr}={got!r}")


# (where, substring, check) -- where: "sv" or "card:<key>"; check() -> (holds, result text)
CHECKS = [
    ("sv", "planerar 24 timmar framåt", lambda: eq("OptimizationConfig().horizon_hours", OPT_H, 24.0)),
    ("sv", "optimeringens horisont på 24 timmar", lambda: eq("OptimizationConfig().horizon_hours", OPT_H, 24.0)),
    ("sv", "kommande 24 timmarna", lambda: eq("OptimizationConfig().horizon_hours", OPT_H, 24.0)),
    ("sv", "Ekonomi sänker den med ytterligare 1,5 K", lambda: eq("const.ECONOMY_MIN_TEMP_WIDENING", C.ECONOMY_MIN_TEMP_WIDENING, 1.5)),
    ("sv", "öppet fönster med 1 K", lambda: eq("const.OPEN_WINDOW_RELAX_C", C.OPEN_WINDOW_RELAX_C, 1.0)),
    ("sv", "rymmer minst 100 liter", lambda: eq("const.BUFFER_STORE_MIN_VOLUME", C.BUFFER_STORE_MIN_VOLUME, 100.0)),
    ("sv", "ackumulatortank på minst 100 L", lambda: eq("const.BUFFER_STORE_MIN_VOLUME", C.BUFFER_STORE_MIN_VOLUME, 100.0)),
    ("sv", "standardvärdet 35 liter", lambda: eq("const.DEFAULT_BUFFER_TANK_VOLUME", C.DEFAULT_BUFFER_TANK_VOLUME, 35.0)),
    ("sv", "Med 3 L tappvatten eller mindre", lambda: eq("const.COMBI_LEGIONELLA_POTABLE_LIMIT_L", C.COMBI_LEGIONELLA_POTABLE_LIMIT_L, 3.0)),
    ("sv", "begränsat till 0,8 °C", lambda: eq("const.CONFIDENCE_MARGIN_CAP_C", C.CONFIDENCE_MARGIN_CAP_C, 0.8)),
    ("sv", "minst 60 % av märkeffekten", lambda: eq("const.CAPACITY_FLOOR_FRACTION", C.CAPACITY_FLOOR_FRACTION, 0.6)),
    ("sv", "ett lägre värde höjs till 0,6", lambda: eq("const.CAPACITY_FLOOR_FRACTION", C.CAPACITY_FLOOR_FRACTION, 0.6)),
    ("sv", "tvåtimmarsfönster", lambda: eq("(OUTAGE_RECOVERY_HOURS, OUTAGE_DHW_DELAY_MINUTES)",
                                         (C.OUTAGE_RECOVERY_HOURS, C.OUTAGE_DHW_DELAY_MINUTES), (2.0, 45.0))),
    ("sv", "mer än 12 K över rummet ignoreras", lambda: eq("slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K", slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K, 12.0)),
    ("sv", "ackumulatortankens temperatur plus 2", lambda: eq("const.WOOD_TANK_MIN_MARGIN", C.WOOD_TANK_MIN_MARGIN, 2.0)),
    ("sv", "minst 5 °C under börvärdet", lambda: eq("const.DHW_MIN_TEMP_SETPOINT_MARGIN", C.DHW_MIN_TEMP_SETPOINT_MARGIN, 5.0)),
    ("sv", "0,75 är svenska byggreglernas riktvärde", lambda: eq("const.DEFAULT_THERMAL_BRIDGE_FRSI", C.DEFAULT_THERMAL_BRIDGE_FRSI, 0.75)),
    ("sv", "kommande 20 timmarna", lambda: eq("const.MANUAL_PLAN_WINDOW_HOURS", C.MANUAL_PLAN_WINDOW_HOURS, 20)),
    ("sv", "Standard är 20 timmar framåt", lambda: eq("const.MANUAL_PLAN_WINDOW_HOURS", C.MANUAL_PLAN_WINDOW_HOURS, 20)),
    ("sv", "Efter 5 minuters starthållning", lambda: eq("pump_arbiter.FEEDBACK_START_HOLD.total_seconds()/60",
                                                       pump_arbiter.FEEDBACK_START_HOLD.total_seconds() / 60, 5.0)),
    ("sv", "55 °C passar ett framledningsmål", lambda: eq("const.DEFAULT_FLOW_HEAT_C", C.DEFAULT_FLOW_HEAT_C, 55.0)),
    ("sv", "(högst 70 °C)", lambda: eq("const.FLOW_HEAT_C_MAX", C.FLOW_HEAT_C_MAX, 70.0)),
    ("sv", "5 K passar en styrenhet", lambda: eq("const.DEFAULT_FLOW_MIN_LIFT_K", C.DEFAULT_FLOW_MIN_LIFT_K, 5.0)),
    ("sv", "hållit den temperaturen i 20 minuter", lambda: eq("const.DHW_LEGIONELLA_HOLD_MINUTES", C.DHW_LEGIONELLA_HOLD_MINUTES, 20.0)),
    ("sv", "12 (sex förskjutningar med återgång)", lambda: eq("const.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY",
                                                              C.DEFAULT_HEAT_CURVE_PERSISTENT_WRITES_PER_DAY, 12)),
    ("sv", "0 eller 1 skriver ingenting", lambda: eq("persistent_budget.py plan_writes_B1", int(budget["plan_writes_B1"]), 0)),
    ("sv", "en hålls alltid kvar för den", lambda: eq("persistent_budget.py plan_writes_B12 (one kept back: <=11)",
                                                      int(budget["plan_writes_B12"]), 11)),
    ("sv", "3 K är en uppskattning", lambda: eq("(DEFAULT_HEAT_CURVE_OFFSET_BAND_K, DEFAULT_HEAT_CURVE_PERSISTENT_BAND_K)",
                                               (C.DEFAULT_HEAT_CURVE_OFFSET_BAND_K, C.DEFAULT_HEAT_CURVE_PERSISTENT_BAND_K), (3.0, 3.0))),
    ("sv", "60 minuter är ungefär tre svarstider", lambda: eq("const.DEFAULT_HEAT_CURVE_PERSISTENT_MIN_DWELL_MINUTES",
                                                             C.DEFAULT_HEAT_CURVE_PERSISTENT_MIN_DWELL_MINUTES, 60)),
    ("sv", "mätt vid 45 °C i ett 20-gradigt rum", lambda: eq("(DHW_COOLING_REFERENCE_TANK_TEMP, _AMBIENT_TEMP)",
                                                            (C.DHW_COOLING_REFERENCE_TANK_TEMP, C.DHW_COOLING_REFERENCE_AMBIENT_TEMP), (45.0, 20.0))),
    ("sv", "vid 45 °C i beredaren och 20 °C omgivning", lambda: eq("(DHW_COOLING_REFERENCE_TANK_TEMP, _AMBIENT_TEMP)",
                                                                  (C.DHW_COOLING_REFERENCE_TANK_TEMP, C.DHW_COOLING_REFERENCE_AMBIENT_TEMP), (45.0, 20.0))),
    ("sv", "veckokopian", lambda: eq("snapshots.SNAPSHOT_INTERVAL_DAYS", snapshots.SNAPSHOT_INTERVAL_DAYS, 7.0)),
    ("sv", "nästa veckovisa ögonblicksbild", lambda: eq("snapshots.SNAPSHOT_INTERVAL_DAYS", snapshots.SNAPSHOT_INTERVAL_DAYS, 7.0)),
    ("card:health.cop_reason_tracking_gate", "", lambda: eq("const.COP_TRACKING_ERROR_GATE", C.COP_TRACKING_ERROR_GATE, 0.3)),
    ("card:score.part_operation", "", lambda: eq("(driving_grade.FULL_SAVING, REFERENCE)",
                                                (driving_grade.FULL_SAVING, driving_grade.REFERENCE), (0.2, 0.0))),
    ("card:score.part_machine", "", lambda: eq("(const.COP_BASELINE_MIN_SAMPLES, SCORE_REFERENCE['machine'])",
                                              (C.COP_BASELINE_MIN_SAMPLES, coordinator.SCORE_REFERENCE["machine"]), (20, 100.0))),
    ("card:score.part_envelope", "", lambda: eq("coordinator.SCORE_REFERENCE['envelope']", coordinator.SCORE_REFERENCE["envelope"], 50.0)),
    ("card:whynow.explain_forecast", "", lambda: eq("slot_drivers.FORECAST_LOOKAHEAD_H", slot_drivers.FORECAST_LOOKAHEAD_H, 8.0)),
    ("card:errors.cfg_hours", "", lambda: eq("setConfig accepts hours {0.9,1,168,169}", probe["hours"],
                                            {"0.9": False, "1": True, "168": True, "169": False})),
    ("card:status.stale_title", "", lambda: eq("card (PLAN_STALE_INTERVALS, PLAN_STALE_FLOOR_MIN) vs coordinator",
                                              (probe["stale"]["intervals"], probe["stale"]["floor"]),
                                              (coordinator.PLAN_STALE_INTERVALS, coordinator.PLAN_STALE_FLOOR_MINUTES))),
]

strings = probe["strings"]
LANG_LINES = []  # (first line, lang) of each dictionary in STRINGS, from the source
src_lines = Path(CARD).read_text(encoding="utf-8").splitlines()
for n, line in enumerate(src_lines, 1):
    m = re.match(r"^  (en|sv|de): \{$", line)
    if m:
        LANG_LINES.append((n, m.group(1)))
DICT_END = next(n for n, l in enumerate(src_lines, 1) if n > LANG_LINES[-1][0] and l == "};")
norm = lambda s: " ".join(s.split())


def card_key(line, text):
    if not LANG_LINES or line < LANG_LINES[0][0] or line > DICT_END:
        return None, None
    lang = [lg for n, lg in LANG_LINES if n <= line][-1]
    frag = norm(text)
    for key, val in strings[lang].items():
        if frag and frag in norm(val):
            return lang, key
    return lang, None


units = text_ledger.enumerate_units(".", [SV, CARD], "D6")
rows, tally = [], {"checked_true": 0, "checked_false": 0, "not_checked": 0, "no_claim": 0}
for uid, line, kind, text in units:
    t = norm(text)
    path = uid.split("#")[0]
    hits = []
    lang = key = None
    if path == CARD:
        lang, key = card_key(line, text)
    for where, sub, fn in CHECKS:
        if where == "sv" and path == SV and sub in t:
            hits.append(fn())
        elif where.startswith("card:") and key == where[5:] and re.search(r"\d", t):
            hits.append(fn())
    if key is not None and ("{" in t):
        left = probe["unresolved"].get(f"{lang}/{key}")
        hits.append((not left, f"production L({key}) under {lang} leaves {left or 'no'} literal token"))
    if hits:
        ok = all(h[0] for h in hits)
        res = "; ".join(h[1] for h in hits)
        truth = "" if ok else "the executed value contradicts the sentence (see REPORT.md finding)"
        rows.append([uid, str(line), "claim", "ledger.py CHECKS", res, "true" if ok else "false", truth])
        tally["checked_true" if ok else "checked_false"] += 1
    elif len(t.split()) < 6 and not re.search(r"\d", t):
        rows.append([uid, str(line), "no-claim", "", "", "-", ""])
        tally["no_claim"] += 1
    else:
        rows.append([uid, str(line), "claim", "none executed", "NOT CHECKED", "unverifiable",
                     "NOT CHECKED this round: behavioural or numeric prose with no executed check; not_reached"])
        tally["not_checked"] += 1

out = HERE / ("LEDGER.perturbed.tsv" if "--perturb" in sys.argv else "LEDGER.tsv")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\t".join(text_ledger.HEADER) + "\n")
    for r in rows:
        fh.write("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) + "\n")
print(f"RESULT units={len(units)} count")
for k, v in tally.items():
    print(f"RESULT {k}={v} count")
for r in rows:
    if r[5] == "false":
        print(f"   false {r[0]} line {r[1]}: {r[4]}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
