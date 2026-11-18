"""Class P8 probes, round 11. Exit 1 when the seam's unit disagrees with the
canonical one, 0 when it agrees.

Run from the repo root: PYTHONPATH=tests/hastub python3 probe_p8.py <probe> [--null|--planted]
  currency     runs dev/audit/rounds/round11/D14/s1/currency_precedence.py (SEK instance,
               EUR/kWh feed) and fails on money_seams > 0; --null runs it with a SEK feed (0).
               Covers config_flow._money, _fee_placeholders, _grid_fee_errors and,
               with --instance HUF, grid_fee.fee_bound's scale.
  temperature  writes c in {-20, 0, 21.5, 55, 100} degC through inputs.temperature_from_c
               for every unit in const.TEMPERATURE_UNIT_TO_C and reads it back through
               normalize_temperature_c; fails on any disagreement. --planted re-introduces
               D7-s3-01's line (value_c * factor - offset), as the finder's planted copy had it.
"""
import subprocess, sys
sys.path.insert(0, "custom_components")
probe = sys.argv[1]
flags = sys.argv[2:]
if probe == "currency":
    cmd = [sys.executable, "dev/audit/rounds/round11/D14/s1/currency_precedence.py"]
    if "--null" in flags:
        cmd.append("--null")
    if "--instance" in flags:
        cmd += ["--instance", flags[flags.index("--instance") + 1]]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    n = [int(l.split("=")[1].split()[0]) for l in out.splitlines() if l.startswith("RESULT money_seams=")][0]
    print(f"PROBE currency money_seams={n} -> {'FAIL' if n else 'ok'}")
    sys.exit(1 if n else 0)
if probe == "temperature":
    from heatpump_optimizer import inputs
    if "--planted" in flags:
        def planted(value_c, unit):
            spec = inputs.TEMPERATURE_UNIT_TO_C.get(str(unit).strip())
            if spec is None:
                return value_c
            offset, factor = spec
            return value_c * factor - offset
        inputs.temperature_from_c = planted
    bad = 0
    for unit in sorted(inputs.TEMPERATURE_UNIT_TO_C):
        for c in (-20.0, 0.0, 21.5, 55.0, 100.0):
            back = inputs.normalize_temperature_c(inputs.temperature_from_c(c, unit), unit)
            bad += abs(back - c) > 1e-9
    print(f"PROBE temperature roundtrip_disagreements={bad} of 35 -> {'FAIL' if bad else 'ok'}")
    sys.exit(1 if bad else 0)
sys.exit(f"unknown probe {probe}")
