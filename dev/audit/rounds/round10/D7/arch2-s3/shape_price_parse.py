"""Shape: 'a price reading in major currency per kWh' -- every entry point, driven on shared probes.

Entry points (the seam rule, printed): package functions that call ``normalize_price_per_kwh`` or
``price_per_kwh``, or that read a ``total``/``value``/``price`` row key into a float
(``price_model._raw_value``'s callers). Driven, on the same (raw, unit) probe:

* series   ``price_model.prices_from_entity_attributes({unit, raw_today: [{start, value: raw}]})``
           -> the row's ``total`` (vat 1, surcharge 0)
* scalar   ``coordinator._entity_price(hass, entity)`` over a FakeHass state (raw, unit) -- the
           export-price and grid-fee path
* tibber   ``price_model.prices_from_tibber_payload`` with ``total: raw`` (Tibber publishes no unit;
           driven only on unit-less probes)

Metric: disagreeing_probes = probes on which the driven entry points do not return the same float
(bit for bit, float.hex) or the same refusal; ulp_only = the subset whose two answers differ by at
most 4 ulps (a spelling difference: the series scales ``value * normalize(1.0, unit)``, the scalar
``normalize(value, unit)``). Key: the value each production entry point returns.

Perturbation: --perturb rebinds ``price_model.normalize_price_per_kwh`` in this process to a copy
that ignores the minor-unit rule (öre read as SEK); the öre probes must then disagree by 100x
(``disagreeing_probes`` rises, ``ulp_only`` does not).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/shape_price_parse.py [--root DIR] [--perturb]

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
RAWS = ["1.5", "123.4", "37.77", "0.1", "-0.3", "1e-3", "nan", "inf", "1e400", "abc", " 2.25 "] + [
    f"{(i * 7919) % 100000 / 100:.2f}" for i in range(1, 121)]  # 120 seeded two-decimal prices
UNITS = [None, "", "SEK/kWh", "öre/kWh", "EUR/MWh", "c/kWh", "€/kWh", "SEK", "kWh", "SEK/Wh"]


def seams(pkg: Path) -> list[str]:
    out = []
    for p in sorted(pkg.glob("*.py")):
        for fn in ast.walk(ast.parse(p.read_text())):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if fn.name in ("normalize_price_per_kwh", "price_per_kwh"):
                continue
            names = {c.func.id for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
            if names & {"normalize_price_per_kwh", "price_per_kwh", "_raw_value"}:
                out.append(f"{p.stem}.{fn.name}:{fn.lineno}  calls {sorted(names & {'normalize_price_per_kwh', 'price_per_kwh', '_raw_value'})}")
    return out


def ulps(a: float, b: float) -> float:
    if a == b:
        return 0.0
    return abs(a - b) / max(math.ulp(a), math.ulp(b))


def main() -> int:
    root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else REPO
    perturb = "--perturb" in sys.argv
    sys.path.insert(0, str(REPO / "tests"))
    from harness import FakeHass, FakeState
    sys.path.insert(0, str(root / "custom_components"))  # after harness, which inserts the CWD's
    pm = importlib.import_module("heatpump_optimizer.price_model")
    coord = importlib.import_module("heatpump_optimizer.coordinator")
    print(f"RESULT measured_tree={Path(pm.__file__).parents[2]}")
    rows = seams(root / "custom_components" / "heatpump_optimizer")
    print(f"RESULT entry_points={len(rows)} count")
    for r in rows:
        print("   ", r)
    if perturb:
        real = pm.normalize_price_per_kwh

        def no_minor(value, unit):
            if unit and str(unit).strip().lower().startswith("öre"):
                return value * 1.0
            return real(value, unit)
        pm.normalize_price_per_kwh = no_minor

    def series(raw, unit):
        attrs = {"raw_today": [{"start": "2026-01-15T00:00:00+01:00", "value": raw}]}
        if unit is not None:
            attrs["unit_of_measurement"] = unit
        got = pm.prices_from_entity_attributes(attrs)
        return None if isinstance(got, str) else got[0]["total"]

    def scalar(raw, unit):
        hass = FakeHass({"sensor.price": FakeState(raw, unit=unit)})
        return coord._entity_price(hass, "sensor.price")

    def tibber(raw, unit):
        payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
            "today": [{"total": raw, "startsAt": "2026-01-15T00:00:00+01:00"}]}}}]}}}
        got = pm.prices_from_tibber_payload(payload)
        return None if isinstance(got, str) or not got else got[0]["total"]

    dis, ulp_only, n = [], [], 0
    for unit in UNITS:
        for raw in RAWS:
            n += 1
            ans = {"series": series(raw, unit), "scalar": scalar(raw, unit)}
            if unit in (None, ""):
                ans["tibber"] = tibber(raw, unit)
            keys = {("None" if v is None else float(v).hex()) for v in ans.values()}
            if len(keys) > 1:
                vals = [v for v in ans.values() if v is not None]
                label = f"{raw!r}@{unit!r}"
                if len(vals) == len(ans) and all(ulps(vals[0], v) <= 4 for v in vals[1:]):
                    ulp_only.append(label)
                dis.append(label)
                print(f"  DISAGREE {label}: {ans}")
    print(f"RESULT probes={n} count")
    print(f"RESULT disagreeing_probes={len(dis)} count")
    print(f"RESULT ulp_only={len(ulp_only)} count")
    print(f"RESULT disagreeing_non_ulp={len(dis) - len(ulp_only)} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
