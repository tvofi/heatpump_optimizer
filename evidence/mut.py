#!/usr/bin/env python3
"""Reviewer's mutant driver (reviewer-built): apply one textual mutant, run a block runner, restore."""
import pathlib
import subprocess
import sys

WT = pathlib.Path("~/hpo-seats/r10s6/rev-3866-local/wt")
CC = WT / "custom_components/heatpump_optimizer"
M7 = ("pump_arbiter.py", "    if (limit := _space_limit_c(inp)) is not None:\n        caps.append(limit)",
      "    if False:\n        caps.append(None)")
M8 = ("pump_arbiter.py", "_space_limit_c(inp) or math.inf)", "math.inf)")
MUTS = {
    "O-M1 min->max": [("flow_limit.py", "HighLimit(min(kept)", "HighLimit(max(kept)")],
    "O-M2 >= strict": [("flow_limit.py", "value is not None and value >= lowest_c", "value is not None and value > lowest_c")],
    "O-M3 dropped voids other": [("flow_limit.py", "return HighLimit(min(kept) if kept else None",
                                  "return HighLimit(min(kept) if kept and not dropped else None")],
    "O-M4 floor off": [("flow_limit.py", "FLOW_LIMIT_C_MIN <= value <= FLOW_HEAT_C_MAX", "value <= FLOW_HEAT_C_MAX")],
    "O-M5 ceiling off": [("flow_limit.py", "FLOW_LIMIT_C_MIN <= value <= FLOW_HEAT_C_MAX", "FLOW_LIMIT_C_MIN <= value")],
    "O-M6 indoor reads": [("pump_arbiter.py", 'if _grid(inp, "space_setpoint") is None or not _flow_unit(inp.config):',
                           'if _grid(inp, "space_setpoint") is None:')],
    "O-M7 boost_ceiling cap GUARD_OFF": [M7],
    "O-M8 map top ignores limit": [M8],
    "O-M7+M8": [M7, M8],
    "O-M9 hold ignores limit": [("pump_arbiter.py", "_gate_floor_c(inp.config), hi=_space_limit_c(inp))",
                                 "_gate_floor_c(inp.config))")],
    "O-M10 feedback ignores limit": [("pump_arbiter.py", "(rec.cut_hi_c, _space_limit_c(inp))", "(rec.cut_hi_c, None)")],
    "O-M11 sensor bypasses crossed-pair rule": [("pump_arbiter.py", "        _setpoint_limits_c(inp)[1],\n",
        "        float(inp.hass.states.get(inp.config['space_setpoint_high_limit_entity']).state) if inp.config.get('space_setpoint_high_limit_entity') and inp.hass.states.get(inp.config['space_setpoint_high_limit_entity']).state.replace('.','').isdigit() else None,\n")],
    "O-M12 option never read": [("flow_limit.py", "    value = finite_float(stored)\n", "    value = None\n")],
    "C-M1 max clamp off": [("inputs.py", "    if high is not None:\n        sent = min(", "    if False and high is not None:\n        sent = min(")],
    "C-M2 min clamp off": [("inputs.py", "    if low is not None:\n        sent = max(", "    if False and low is not None:\n        sent = max(")],
    "C-M3 max rounds nearest": [("inputs.py", '_on_step(high, step, "down")', '_on_step(high, step, "nearest")')],
    "C-M4 min rounds nearest": [("inputs.py", '_on_step(low, step, "up")', '_on_step(low, step, "nearest")')],
    "C-M5 number keys every domain": [("inputs.py",
        'low_key, high_key = _RANGE_KEYS.get(entity_id.split(".", 1)[0], _NUMBER_RANGE_KEYS)\n    return finite_float',
        'low_key, high_key = _NUMBER_RANGE_KEYS\n    return finite_float')],
}


def main() -> None:
    name, runner, out = sys.argv[1], sys.argv[2], sys.argv[3]
    saved: dict[pathlib.Path, str] = {}
    try:
        for f, old, new in MUTS[name]:
            p = CC / f
            saved.setdefault(p, p.read_text())
            cur = p.read_text()
            n = cur.count(old)
            if n != 1:
                raise SystemExit(f"MUTANT {name}: anchor count {n} in {f}")
            p.write_text(cur.replace(old, new))
        r = subprocess.run(["bash", runner], cwd=WT, capture_output=True, text=True)
        txt = r.stdout + r.stderr
        pathlib.Path(out).write_text(txt)
        fails = [l for l in txt.splitlines() if l.strip().startswith("FAIL")]
        summ = [l for l in txt.splitlines() if "BLOCK" in l]
        print(f"MUTANT {name}: rc={r.returncode} failed={len(fails)} {summ[-1] if summ else ''}")
        for l in fails:
            print("   ", l.strip()[:170])
    finally:
        for p, s in saved.items():
            p.write_text(s)


if __name__ == "__main__":
    main()
