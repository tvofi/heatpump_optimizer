"""Shape: 'a power entity's state as kW' -- every implementation, and whether they agree.

ARCH2-s3's copy of ARCH-s2's harness: ``--root`` selects the tree (default the working tree) instead
of a pinned baseline, the seam rule also reads ``_finite`` as a parse (the prototype owner's spelling; a caller that only delegates to it is not an implementation),
``inf``/``-inf`` string states are probed, and the consumer of the quiet-window read,
``quiet_windows.silent_cap_kw``, is driven on each non-finite state (``silent_cap_on_inf``: the
in-window ceiling a silent step carries when the power entity reads inf; p_max 6 kW, fraction 0.5).

Metric: implementations = functions in the package that call ``normalize_power_kw`` on a value
they themselves parsed with ``float(<state>.state)`` (the seam rule, an AST walk; the shared
normaliser itself and functions that only forward an already-parsed reading are not counted).
disagreeing_states = probe (state, unit) pairs on which the DRIVEN implementations do not return
the same kW (or the same refusal). Key: the value each production function returns.

Driven: inputs.InputReader.read_power_kw (through a real InputReader over a FakeHass),
coordinator.HeatPumpOptimizerCoordinator._pv_measured_production (unbound, over a stub self),
quiet_windows._power_entity_kw. Counted but not driven: the coordinator's _on_power_event, whose
parse sits inside the peak guard's throttle and tariff gates.

Perturbation: --sign-blind maps every answer through abs(); the sign-policy disagreement on
negative states must then vanish while the unit/staleness ones remain.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/shape_power_kw.py [--root DIR] [--sign-blind]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: see REPORT.md, tolerance 0.
Machine: the seat's macOS box; counts only. Writes only under a tempfile.mkdtemp root.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import importlib  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
NOW = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
PROBES = [("1500", "W", 0), ("1.5", "kW", 0), ("-0.4", "kW", 0), ("0", "kW", 0), ("unknown", None, 0),
          ("nan", "kW", 0), ("1e400", "kW", 0), ("inf", "kW", 0), ("-inf", "kW", 0), ("2", "hp", 0), ("2", None, 0), ("1.5", "kW", 600)]


def seams(pkg: Path):
    out = []
    for p in sorted(pkg.glob("*.py")):
        for fn in ast.walk(ast.parse(p.read_text())):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name in ("normalize_power_kw",):
                continue
            calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)]
            norm = any(isinstance(c.func, ast.Name) and c.func.id == "normalize_power_kw"
                       for c in calls)
            parse = any(isinstance(c.func, ast.Name) and c.func.id in ("float", "_finite") and c.args
                        and ("state" in ast.unparse(c.args[0])) for c in calls)
            via_read = any(isinstance(c.func, ast.Attribute) and c.func.attr == "read" for c in calls)
            if norm and (parse or via_read):
                out.append(f"{p.stem}.{fn.name}:{fn.lineno}")
    return out


def main() -> int:
    t0, c0 = time.time(), time.process_time()
    sign_blind = "--sign-blind" in sys.argv
    root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else REPO
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    sys.path.insert(0, str(REPO / "tests"))
    from archscore.score import tree_of
    tmp = Path(tempfile.mkdtemp(prefix="arch-s2-pw-"))
    try:
        tree = root
        sys.path.insert(0, str(tree / "custom_components"))
        rows = seams(tree / "custom_components" / "heatpump_optimizer")
        print(f"RESULT implementations={len(rows)} count")
        for r in rows:
            print("  ", r)
        from harness import FakeHass, FakeState  # tests/harness.py's stubs
        # tests/harness.py puts the CWD's custom_components first on import; the tree under
        # test must win, or the probe measures the working tree whatever --root says.
        sys.path.insert(0, str(tree / "custom_components"))
        inputs = importlib.import_module("heatpump_optimizer.inputs")
        coord = importlib.import_module("heatpump_optimizer.coordinator")
        qw = importlib.import_module("heatpump_optimizer.quiet_windows")
        const = importlib.import_module("heatpump_optimizer.const")
        print(f"RESULT measured_tree={Path(inputs.__file__).parents[2]}")

        def st(state, unit, age_min):
            return FakeState(state, last_updated=NOW - timedelta(minutes=age_min), unit=unit)

        def via_reader(state, unit, age):
            hass = FakeHass({"sensor.p": st(state, unit, age)})
            r = inputs.InputReader(hass, {const.CONF_POWER_ENTITY: "sensor.p"}, now=lambda: NOW)
            return r.read_power_kw(const.CONF_POWER_ENTITY).value

        def via_pv(state, unit, age):
            self = types.SimpleNamespace(hass=FakeHass({"sensor.p": st(state, unit, age)}))
            cfg = types.SimpleNamespace(production_entity="sensor.p")
            return coord.HeatPumpOptimizerCoordinator._pv_measured_production(self, cfg)

        def via_quiet(state, unit, age):
            s = st(state, unit, age)
            return qw._power_entity_kw("sensor.p", lambda _id: s)

        table = {}
        for name, fn in (("inputs.InputReader.read_power_kw", via_reader),
                         ("coordinator._pv_measured_production", via_pv),
                         ("quiet_windows._power_entity_kw", via_quiet)):
            row = []
            for state, unit, age in PROBES:
                try:
                    v = fn(state, unit, age)
                    v = None if v is None else round(abs(v) if sign_blind else v, 6)
                    row.append(repr(v))
                except Exception as exc:  # noqa: BLE001 -- a raise is an answer
                    row.append(type(exc).__name__)
            table[name] = row
        w = max(map(len, table))
        print("probe".ljust(w), *[f"{s}{u or ''}@{a}m"[:12].rjust(12) for s, u, a in PROBES])
        for k, v in table.items():
            print(k.ljust(w), *[x[:12].rjust(12) for x in v])
        dis = [f"{s}{u or ''}@{a}m" for i, (s, u, a) in enumerate(PROBES) if len({v[i] for v in table.values()}) > 1]
        print(f"RESULT driven={len(table)} count")
        print(f"RESULT disagreeing_states={len(dis)} count")
        print(f"RESULT disagreeing_state_values={','.join(dis) or '-'}")
        cfg = {const.CONF_POWER_ENTITY: "sensor.p", const.CONF_SILENT_MODE_FRACTION: 0.5}
        for raw in ("inf", "1e400"):
            s_inf = st(raw, "kW", 0)
            cap = qw.silent_cap_kw(cfg, lambda _id: s_inf, 6.0)
            print(f"RESULT silent_cap_on_{raw}={cap} kW")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
