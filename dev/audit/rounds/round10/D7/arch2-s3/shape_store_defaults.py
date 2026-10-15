"""Shape: 'a stored numeric field read back with a default' -- every from_dict, driven on shared probes.

Census (AST, printed): every ``from_dict`` classmethod in the package, with the number-parsing calls
it makes (``float``/``int`` bare, a ``try``, an ``isfinite`` guard, or a shared helper).

Driven: one representative numeric scalar field per learner whose ``from_dict`` takes a mapping and
round-trips through ``as_dict`` (the field list below names it), on the same probes for that field:
missing, None, "abc", "nan", "inf", -1, a list, and a valid value. Each answer is the field's value on
the loaded object, the class default (``from_dict({})``) marked ``default``, or the exception name --
a raise from a ``from_dict`` is a learner reset on load (``coordinator``'s loaders catch it and
start empty), so it is an answer, not a harness error.

Metric: policy classes = the distinct (probe -> answer-kind) signatures across the driven learners,
where answer-kind is one of default / raise / kept-nonfinite / kept / clamped. One policy across the
learners is one owner; each extra class is a learner whose store-load disagrees.
Key: the attribute value each production ``from_dict`` returns.

Perturbation: --perturb loads every probe through ``as_dict()`` of a default object with the field
replaced, i.e. the round-trip arm, where a learner must read its own write back: kinds collapse to
``kept`` on the valid probe for every learner (policy classes for the valid probe -> 1).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/shape_store_defaults.py [--root DIR]

Counts only; contention-immune. Writes nothing.
"""
import ast
import importlib
import math
import sys
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
HELPERS = {"float", "int", "isfinite", "_as_float", "_finite", "finite_float", "_optional_float", "_as_num",
           "_number", "_optional_number", "_count", "_samples", "_stored_float", "_force_float"}
PROBES = [("missing", None), ("None", None), ("abc", "abc"), ("nan", "nan"), ("inf", float("inf")),
          ("neg", -1.0), ("list", [1.0]), ("valid", 3.25)]


def census(pkg: Path) -> list[str]:
    out = []
    for p in sorted(pkg.glob("*.py")):
        tree = ast.parse(p.read_text())
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "from_dict":
                    used = {}
                    for c in ast.walk(fn):
                        if isinstance(c, ast.Call):
                            f = c.func
                            nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "?")
                            if nm in HELPERS:
                                used[nm] = used.get(nm, 0) + 1
                    has_try = any(isinstance(n, ast.Try) for n in ast.walk(fn))
                    out.append(f"{p.stem}.{cls.name}.from_dict:{fn.lineno} try={int(has_try)} {used}")
    return out


def kind(value, default, probe_value):
    if isinstance(value, str) and value.startswith("raise:"):
        return "raise"
    if isinstance(value, float) and not math.isfinite(value):
        return "kept-nonfinite"
    if value == default:
        return "default"
    if probe_value is not None and isinstance(probe_value, (int, float)) and value == probe_value:
        return "kept"
    return f"other({value!r})"


def main() -> int:
    root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else REPO
    sys.path.insert(0, str(root / "custom_components"))
    rows = census(root / "custom_components" / "heatpump_optimizer")
    print(f"RESULT from_dict_implementations={len(rows)} count")
    for r in rows:
        print("   ", r)
    # (module, class, field-in-dict, attribute-on-object) -- one scalar per learner, chosen from as_dict()
    targets = []
    for mod, cls in (("tariff", "PeakTracker"), ("wear", "StartCounter"), ("curve_learning", "CurveLearner"),
                     ("flow_lift", "FlowCurveBias"), ("ledger", "MonthlyLedger"), ("price_model", "PriceShapeModel"),
                     ("dhw_draws", "DrawStats"), ("defrost", "DefrostDerate"), ("freq_control", "FrequencyMap"),
                     ("snapshots", "SnapshotRing"), ("accuracy", "AccuracyTracker")):
        try:
            C = getattr(importlib.import_module(f"heatpump_optimizer.{mod}"), cls)
            base = C.from_dict({})
            stored = base.as_dict()
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {mod}.{cls}: {type(exc).__name__}: {exc}")
            continue
        scalar = [(k, v) for k, v in stored.items()
                  if isinstance(v, (int, float)) and not isinstance(v, bool) and hasattr(base, k)]
        if not scalar:
            print(f"  skip {mod}.{cls}: no scalar numeric field round-trips by name ({sorted(stored)[:6]})")
            continue
        targets.append((mod, cls, C, base, stored, scalar[0][0]))
    sigs = {}
    for mod, cls, C, base, stored, field in targets:
        default = getattr(base, field)
        sig = []
        for label, pv in PROBES:
            data = dict(stored)
            if label == "missing":
                data.pop(field, None)
            else:
                data[field] = pv
            try:
                got = getattr(C.from_dict(data), field)
            except Exception as exc:  # noqa: BLE001 -- a raise is a reset on load
                got = f"raise:{type(exc).__name__}"
            sig.append(f"{label}={kind(got, default, pv)}")
        sigs.setdefault(" ".join(sig), []).append(f"{mod}.{cls}.{field}")
    print(f"RESULT driven_learners={len(targets)} count")
    for s, who in sigs.items():
        print(f"  [{len(who)}] {s}\n        {', '.join(who)}")
    print(f"RESULT policy_classes={len(sigs)} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
