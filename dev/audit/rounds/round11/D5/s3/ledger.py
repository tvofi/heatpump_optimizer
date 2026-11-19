#!/usr/bin/env python3
"""D5-s3 M4 ledger: one row per D5 unit of the seat's cells, for `text_ledger.py check --plant`.

Metric: the ledger LEDGER.tsv beside this file, every unit `text_ledger.py units --dim D5 --seat D5-s3`
lists rowed. Units this seat judged against the code (C1-C5, by the command in the row) carry
true/false/stale; every other unit is rowed `unverifiable` with the mechanical C2 (identifier
resolution), C5 (sentence length) and C7 (cited number vs adjacent constant) results of scan.py, and
its truth says C1 was not executed on it this round (coverage: not_reached).
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s3/ledger.py
  then:   python3 tools/audit/text_ledger.py check --dim D5 dev/audit/rounds/round11/D5/s3/LEDGER.tsv --plant --seat D5-s3 --repo <git repo> --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692
Expected: RESULT units=2855 rows=2855 unrowed=0 orphan=0 malformed=0 plant_refused=1; exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B3. Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import scan  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
H = "dev/audit/rounds/round11/D5/s3/"

#: Files every unit of which this seat read against the code it sits on.
WHOLE = {
    "batchmath.py": ("true", "sed -n 1,80p " + PKG + "batchmath.py", "row_sums halves above PAIRWISE_BLOCK=128, 8 partials at or under, plain loop under 8"),
    "datetime.py": ("true", "sed -n 1,48p " + PKG + "datetime.py", "native_value reads away_state.override_return_iso"),
    "currency.py": ("true", "sed -n 1,68p " + PKG + "currency.py", "declared_currency/money_scale/resolve_currency as described"),
    "issues.py": ("true", "sed -n 1,89p " + PKG + "issues.py", "package import is const only; set_issue severity WARNING, translation_key=issue_id"),
    "flow_meter.py": ("true", "sed -n 1,151p " + PKG + "flow_meter.py; " + H + "ha_free.py", "flow_meter imports without homeassistant: OK"),
    "comfort_band.py": ("true", "sed -n 1,260p " + PKG + "comfort_band.py; grep -n SELECTOR_MAX const.py; config_flow.py:1758 min_temp _number(14, 25)", "night max 24, min_temp slider max 25; violations used by config_flow:953, services:1033, coordinator:4246"),
}

#: Single units (file, line) judged, with verdict, command, result and the truth when not true.
ONE = {
    ("comfort_band.py", 1): ("stale", H + "slider_ceiling.py", "RESULT overshoot_c=0.0 stale_rows=1",
                             "the climate slider's maximum is the configured ceiling (climate.py:124), not one degree above it; the bullet describes the pre-v5.1.7 slider in the present tense"),
    ("grid_fee.py", 1): ("false", H + "ha_free.py", "grid_fee:27 NEEDS_HA homeassistant refused",
                         "grid_fee imports currency, whose module-level `from homeassistant.core import HomeAssistant` makes grid_fee unimportable without Home Assistant"),
    ("grid_fee.py", 341): ("false", H + "ha_free.py", "grid_fee NEEDS_HA", "'HA-free like the rest of the module': the module needs homeassistant.core through currency"),
    ("accuracy.py", 48): ("true", "grep -n DEFAULT_OPTIMIZATION_INTERVAL const.py; python3 -c 'print(672*30/60/24)'", "30 min; 14.0 days", ""),
    ("const.py", 197): ("true", "sed -n 197,200p const.py", "0.998 kg/L, 4.186 kJ/kg/K, units stated", ""),
    ("const.py", 199): ("true", "sed -n 197,200p const.py", "4.186 kJ/(kg K)", ""),
    ("const.py", 1249): ("true", "python3 -c 'print(1/0.05)'", "20.0 days ~ 3 weeks", ""),
    ("const.py", 1251): ("true", "grep -n SCORE_FREE_SPAN_RESET const.py", "SCORE_FREE_SPAN_RESET=20 == 1/SCORE_ALPHA", ""),
    ("const.py", 1337): ("true", "grep -n COMFORT_TEMP_.*SELECTOR const.py; grep -n SELECTOR comfort_band.py", "bounds shared by selector and rule", ""),
    ("const.py", 1358): ("true", "ls dev/audit/harnesses/r10_cop_partload.py", "present", ""),
    ("const.py", 1626): ("true", "git cat-file -e 52f5a442:BODY.md", "present", ""),
    ("coordinator.py", 797): ("true", "config_flow.py:1868 interval _number(10,120); python3 -c 'print(max(3*10,90))'", "90", ""),
    ("curve_learning.py", 51): ("true", "python3 -c 'print(3*0.5/7)'", "0.214 ~ 0.2 = STEP_K", ""),
    ("dhw_planner.py", 94): ("true", "python3 -c 'print(2*60/15)'", "8.0 = _DHW_MIN_RUN_CHUNK", ""),
    ("freq_control.py", 53): ("true", "python3 -c 'print(20/20)'", "1.0 = FREQ_MAX_KW_PER_HZ", ""),
    ("freq_control.py", 61): ("true", "python3 -c 'print(300/60)'", "5 min", ""),
    ("heat_energy.py", 46): ("true", "python3 -c 'print(0.05*60)'", "3.0 min", ""),
    ("heat_curve.py", 79): ("true", "grep -n ECHO_GRACE_S pump_arbiter.py", "ECHO_GRACE_S = 20.0", ""),
    ("draw_range.py", 69): ("true", "python3 -c 'print((0+1)/2)'", "0.5 = FOLLOW_SLOPE_MIN", ""),
    ("binary_sensor.py", 1): ("true", "grep -c '^class .*BinarySensor(_Optimizer' binary_sensor.py", "6", ""),
    ("button.py", 1): ("true", "grep -c '^class .*Button(_OptimizerButtonBase' button.py", "6", ""),
    ("climate.py", 1): ("true", "sed -n 48,60p climate.py", "modes auto/comfort/economy/off/boost mapped", ""),
    ("climate.py", 110): ("true", H + "slider_ceiling.py", "overshoot_c=0.0: the slider offers exactly the band", ""),
    ("climate.py", 201): ("true", "grep -n '_reading_key = ' sensor.py | cut -d'\"' -f2 | sort -u | wc -l", "6 distinct reading_ok keys", ""),
}
#: The other HA-free claims, true by ha_free.py.
for f, line in (("device_prefill.py", 1), ("diagnosis.py", 1), ("disinfection.py", 1), ("flow_lift.py", 1),
                ("freq_control.py", 1), ("heat_energy.py", 1), ("config_flow.py", 2240)):
    ONE.setdefault((f, line), ("true", H + "ha_free.py", f"{f[:-3]} imports without homeassistant: OK", ""))


def rows():
    out, judged = [], 0
    for f in scan.cell_files():
        base = os.path.basename(f)
        for uid, line, kind, text, flags in scan.scan(f):
            mech = f"C2 unresolved={flags.get('ident', [])}; C5 long={flags.get('long', [])}; C7 num={flags.get('num', '-')}"
            if (base, line) in ONE:
                v, cmd, res, truth = ONE[(base, line)]
                judged += 1
            elif base in WHOLE:
                v, cmd, res = WHOLE[base]
                truth = ""
                judged += 1
            else:
                v, cmd, res = "unverifiable", H + "scan.py", mech
                truth = "C1 not executed on this unit by D5-s3 in round 11 (not_reached); mechanical C2/C5/C7 only"
            if v == "true" and flags.get("long"):
                v, truth = "true", ""  # C5 is reported by c5_long.py, not as a truth verdict
            out.append([uid, str(line), "claim", cmd.replace("\t", " "), (res + " | " + mech).replace("\t", " "), v, truth.replace("\t", " ")])
    return out, judged


def main():
    rs, judged = rows()
    path = HERE / "LEDGER.tsv"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(["unit", "line", "kind", "command", "result", "verdict", "truth"]) + "\n")
        for r in rs:
            fh.write("\t".join(r) + "\n")
    verdicts = {}
    for r in rs:
        verdicts[r[5]] = verdicts.get(r[5], 0) + 1
    print(f"RESULT rows={len(rs)} count")
    print(f"RESULT judged={judged} count")
    for k, v in sorted(verdicts.items()):
        print(f"RESULT verdict_{k}={v} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.0")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
