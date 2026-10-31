"""Class P2 sweep probes: one probe per F1 seam dispositioned `instance` beyond the findings.

Each probe asks one question of a seam and of the owner of the same fact, on the same
input, and FAILS when the two answers differ. The owner of "the plan runs this step" is
thermal_model.planned_draw_runs (MIN_RUNNING_DRAW_KW = 0.1 kW on space+DHW). The input is
the D8-s1-01 step: 0.07 kW asked, which the owner declares off.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py [--perturb]

--perturb swaps every copy's literal for the owner's value on a temp copy of the package
(the null arm): every probe must then pass. Prints RESULT probes_failed=<n>.
"""
from __future__ import annotations

import ast
import shutil
import sys
import tempfile
from pathlib import Path


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
KW = 0.07  # the D8-s1-01 step: between the copies' 0.05 and the owner's 0.1

# (file, exact old text, owner-valued text) for the --perturb null arm
FIXES = [
    ("optimizer.py", "    n_steps: int,\n    threshold: float = 0.05,\n    *,",
     "    n_steps: int,\n    threshold: float = MIN_RUNNING_DRAW_KW,\n    *,"),
    ("optimizer.py", "    n_steps: int,\n    threshold: float = 0.05,\n    idle:",
     "    n_steps: int,\n    threshold: float = MIN_RUNNING_DRAW_KW,\n    idle:"),
    ("freq_control.py", "if not np.isfinite(target_kw) or target_kw <= 0.05:\n            return None",
     "if not np.isfinite(target_kw) or target_kw <= 0.1:\n            return None"),
    ("freq_control.py", "if not np.isfinite(target_kw) or target_kw <= 0.05:\n            return False",
     "if not np.isfinite(target_kw) or target_kw <= 0.1:\n            return False"),
    ("coordinator.py", "heating = float(self._current_action.get(\"power\", 0.0)) > 0.05",
     "heating = float(self._current_action.get(\"power\", 0.0)) > 0.1"),
    ("coordinator.py", "self._commanded_power() > 0.05 and reported >= hz_min",
     "self._commanded_power() > 0.1 and reported >= hz_min"),
]


def _expr_in(pkg: Path, fname: str, func: str, needle: str) -> str:
    """The source of the first expression in `func` whose text contains `needle`."""
    tree = ast.parse((pkg / fname).read_text())
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name == func:
            for n in ast.walk(fn):
                if isinstance(n, (ast.Compare, ast.BoolOp)) and needle in ast.unparse(n):
                    return ast.unparse(n)
    raise LookupError((fname, func, needle))


def run(pkg: Path) -> list[tuple[str, bool, str]]:
    import numpy as np
    sys.path.insert(0, str(pkg.parent))
    for m in [m for m in sys.modules if m.startswith("heatpump_optimizer")]:
        del sys.modules[m]
    from heatpump_optimizer import freq_control, optimizer, thermal_model

    owner = thermal_model.planned_draw_runs(KW, 0.0)  # bool: does the plan run this step
    out = []

    # 1-2: the idle-reason classifiers; a running reason is "not idle"
    sp = optimizer.classify_space_steps(
        np.array([KW]), np.array([1.0]), np.array([21.0, 21.0]), np.array([19.0]),
        np.array([1.0]), None, 1)
    idle_codes = {v for k, v in vars(optimizer).items() if k.startswith("REASON_IDLE")}
    seam = sp[0] not in idle_codes
    out.append(("optimizer.classify_space_steps", seam == owner, f"reason={sp[0]} owner_runs={owner}"))
    dh = optimizer.classify_dhw_steps(np.array([KW]), np.array([True]), np.array([50.0]), None, 1)
    seam = dh[0] not in idle_codes
    out.append(("optimizer.classify_dhw_steps", seam == owner, f"reason={dh[0]} owner_runs={owner}"))

    # 3-4: the frequency map, with evidence at every decile
    fm = freq_control.FrequencyMap()
    for _ in range(freq_control.FREQ_MIN_SAMPLES + 1):
        for hz in range(30, 91, 5):
            fm.observe(float(hz), 0.06 + 0.001 * hz, 30.0, 90.0)
    rec = fm.recommend(KW, 30.0, 90.0)
    out.append(("freq_control.FrequencyMap.recommend", (rec is not None) == owner,
                f"recommend={rec} owner_runs={owner}"))
    fm2 = freq_control.FrequencyMap()
    for _ in range(freq_control.FREQ_MIN_SAMPLES + 1):
        fm2.observe(30.0, 0.06, 30.0, 90.0)
    # the gate under test: past it, the method answers about evidence; before it, False
    gate = _expr_in(pkg, "freq_control.py", "evidence_exhausted", "target_kw <=")
    passes_gate = not eval(gate, {"np": np}, {"target_kw": KW})  # noqa: S307 - own source
    out.append(("freq_control.FrequencyMap.evidence_exhausted", passes_gate == owner,
                f"gate '{gate}' passes={passes_gate} owner_runs={owner}"))

    # 5-6: coordinator predicates, evaluated from their own source on the D8 action
    class _Self:
        _current_action = {"power": KW, "dhw_power": 0.0, "heat_pump_on": owner}

        def _commanded_power(self):
            return KW

    e5 = _expr_in(pkg, "coordinator.py", "_async_learn_buffer_cooling", "_current_action.get('power'")
    v5 = bool(eval(e5, {}, {"self": _Self()}))  # noqa: S307 - own source
    out.append(("coordinator._async_learn_buffer_cooling", v5 == owner,
                f"'{e5}' -> heating={v5} owner_runs={owner}"))
    e6 = _expr_in(pkg, "coordinator.py", "_observe_frequency", "_commanded_power() >")
    v6 = bool(eval(e6, {}, {"self": _Self(), "reported": 45.0, "hz_min": 30.0}))  # noqa: S307
    out.append(("coordinator._observe_frequency", v6 == owner,
                f"'{e6}' -> watch_active={v6} owner_runs={owner}"))
    return out


def main(argv):
    pkg = REPO / "custom_components" / "heatpump_optimizer"
    if "--perturb" in argv:
        tmp = Path(tempfile.mkdtemp())
        dst = tmp / "custom_components" / "heatpump_optimizer"
        shutil.copytree(pkg, dst, ignore=shutil.ignore_patterns("__pycache__"))
        for fname, old, new in FIXES:
            f = dst / fname
            src = f.read_text()
            assert src.count(old) == 1, (fname, old, src.count(old))
            f.write_text(src.replace(old, new))
        pkg = dst
    rows = run(pkg)
    for name, ok, why in rows:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {why}")
    print(f"RESULT probes_failed={sum(not ok for _, ok, _ in rows)} count")
    print(f"RESULT probes_total={len(rows)} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
