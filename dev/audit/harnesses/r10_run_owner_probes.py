"""R10-ARCH-SHAPES-CLASSIFIER: six seams asked "does the plan run this step" against the owner.

The owner of that fact is ``thermal_model.planned_draw_runs`` (the step's whole
ask against ``MIN_RUNNING_DRAW_KW``). D8-s1-01's input is a 0.07 kW step, which
the owner calls off and a 0.05 kW copy calls on. Each probe asks one seam and
the owner the same question on that step and FAILS when the answers differ:

  1-2 optimizer.classify_space_steps / classify_dhw_steps: a running reason
      (not one of the REASON_IDLE codes) on the step;
  3-4 freq_control.FrequencyMap.recommend / evidence_exhausted, with evidence
      at every decile: an answer, or a gate passed, for the step;
  5-6 coordinator._async_learn_buffer_cooling's ``heating`` and
      _observe_frequency's ``watch_active``: the value assigned to that local,
      evaluated from the method's own source on the step's action.

This is round 10's D14 sweep-P2 ``probes_p2.py``, rebuilt where that probe no
longer runs: the coordinator expressions are found by the local they are
assigned to (not by the comparison text the fix replaces), ``defrost_interval``
is bound in the sixth probe's namespace, and ``--perturb`` is the null arm
rebuilt for the tree it runs on.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_run_owner_probes.py [--perturb]

``--perturb`` copies the package to a temp directory and swaps each 0.05 kW
copy (and the classifiers' ``CHANNEL_ACTIVE_KW`` default) for the owner's
value, then probes the copy; every probe must then pass. It applies only to a
tree that still carries the copies (a fixed tree has nothing to swap, and the
run refuses with AssertionError naming the text it did not find).

EXPECTED RESULT (merge base c3a279e32, without and with --perturb; head):
    RESULT probes_failed=6 count   (base)
    RESULT probes_failed=0 count   (base --perturb, head)
"""
from __future__ import annotations

import ast
import shutil
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
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

# (file, exact text, owner-valued text, count) for the --perturb null arm
PERTURB = [
    ("optimizer.py", "    threshold: float = CHANNEL_ACTIVE_KW,\n",
     "    threshold: float = MIN_RUNNING_DRAW_KW,\n", 2),
    ("freq_control.py", "target_kw <= 0.05:", "target_kw <= 0.1:", 2),
    ("coordinator.py", 'self._current_action.get("power", 0.0)) > 0.05',
     'self._current_action.get("power", 0.0)) > 0.1', 1),
    ("coordinator.py", "self._commanded_power() > 0.05 and",
     "self._commanded_power() > 0.1 and", 1),
]


def _assigned(pkg: Path, fname: str, func: str, local: str) -> str:
    """The source of the value `func` assigns to its local `local`."""
    tree = ast.parse((pkg / fname).read_text())
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name == func:
            for n in ast.walk(fn):
                if (isinstance(n, ast.Assign) and len(n.targets) == 1
                        and isinstance(n.targets[0], ast.Name)
                        and n.targets[0].id == local):
                    return ast.unparse(n.value)
    raise LookupError((fname, func, local))


def run(pkg: Path) -> list[tuple[str, bool, str]]:
    import numpy as np
    sys.path.insert(0, str(pkg.parent))
    for m in [m for m in sys.modules if m.startswith("heatpump_optimizer")]:
        del sys.modules[m]
    from heatpump_optimizer import freq_control, optimizer, thermal_model

    owner = thermal_model.planned_draw_runs(KW, 0.0)
    idle = {v for k, v in vars(optimizer).items() if k.startswith("REASON_IDLE")}
    out = []

    sp = optimizer.classify_space_steps(
        np.array([KW]), np.array([1.0]), np.array([21.0, 21.0]), np.array([19.0]),
        np.array([1.0]), None, 1)
    out.append(("optimizer.classify_space_steps", (sp[0] not in idle) == owner,
                f"reason={sp[0]} owner_runs={owner}"))
    dh = optimizer.classify_dhw_steps(np.array([KW]), np.array([True]), np.array([50.0]), None, 1)
    out.append(("optimizer.classify_dhw_steps", (dh[0] not in idle) == owner,
                f"reason={dh[0]} owner_runs={owner}"))

    fm = freq_control.FrequencyMap()
    for _ in range(freq_control.FREQ_MIN_SAMPLES + 1):
        for hz in range(30, 91, 5):
            fm.observe(float(hz), 0.06 + 0.001 * hz, 30.0, 90.0)
    rec = fm.recommend(KW, 30.0, 90.0)
    out.append(("freq_control.FrequencyMap.recommend", (rec is not None) == owner,
                f"recommend={rec} owner_runs={owner}"))
    # evidence_exhausted answers True past its gate when every bucket is below
    # the target: one bucket at 0.06 kW is, so True means the gate let KW through.
    fm2 = freq_control.FrequencyMap()
    for _ in range(freq_control.FREQ_MIN_SAMPLES + 1):
        fm2.observe(30.0, 0.06, 30.0, 90.0)
    ex = fm2.evidence_exhausted(KW, 30.0, 90.0)
    out.append(("freq_control.FrequencyMap.evidence_exhausted", ex == owner,
                f"exhausted={ex} owner_runs={owner}"))

    class _Signals:
        defrosting = False

    class _Self:
        _current_action = {"power": KW, "dhw_power": 0.0}
        _pump_signals = _Signals()

        def _commanded_power(self):
            return KW

    from heatpump_optimizer import coordinator
    names = dict(vars(coordinator))
    e5 = _assigned(pkg, "coordinator.py", "_async_learn_buffer_cooling", "heating")
    v5 = bool(eval(e5, names, {"self": _Self()}))  # noqa: S307 - own source
    out.append(("coordinator._async_learn_buffer_cooling", v5 == owner,
                f"'{e5}' -> heating={v5} owner_runs={owner}"))
    e6 = _assigned(pkg, "coordinator.py", "_observe_frequency", "watch_active")
    v6 = bool(eval(e6, names, {"self": _Self(), "reported": 45.0, "hz_min": 30.0}))  # noqa: S307
    out.append(("coordinator._observe_frequency", v6 == owner,
                f"'{e6}' -> watch_active={v6} owner_runs={owner}"))
    return out


def main(argv):
    pkg = REPO / "custom_components" / "heatpump_optimizer"
    if "--perturb" in argv:
        tmp = Path(tempfile.mkdtemp())
        dst = tmp / "custom_components" / "heatpump_optimizer"
        shutil.copytree(pkg, dst, ignore=shutil.ignore_patterns("__pycache__"))
        for fname, old, new, count in PERTURB:
            f = dst / fname
            src = f.read_text()
            assert src.count(old) == count, (fname, old, src.count(old))
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
