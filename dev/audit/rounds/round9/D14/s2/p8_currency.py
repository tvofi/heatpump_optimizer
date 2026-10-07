"""D14-s2 / class P8 -- a money figure's currency is decided by the label source, not the number's source.

Metric (one line): money surfaces whose rendered currency token differs from the
  currency the figure is actually denominated in, with no repair issue naming it.
Count key: the token each production surface DELIVERS -- a sensor's
  native_unit_of_measurement, a config-flow widget's unit_of_measurement, the
  card's rendered text -- against the price feed's own declared money code (the
  number's source). Never keyed on an input attribute a fix would rewrite.

Three seam families, one phenomenon:
  A  price feed -> published unit   (coordinator.currency is hass.config.currency;
                                      the feed's declared ISO code is parsed for
                                      its scale and then dropped)
  B  config-flow money widgets      (every other money input resolves the unit
                                      through currency.resolve_currency; the
                                      firewood price hard-codes 'SEK/m³')
  C  card money surfaces            (p8_card.mjs: PlanSource.currency() lets a
                                      card-config currency lead, savingsUnit()
                                      lets the sensor's unit lead)

Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/p8_currency.py
  --seams   prints the static enumeration of every currency-resolution site (seam rule)
Expected (baseline 1936d5ca): A_unflagged_mismatch=8 (12 cells, 8 mismatching,
  0 flagged), exact; A under the perturbation (coordinator.resolve_currency
  returns the feed's code) = 0; A null control (feed code == instance) = 0.
  B_money_widgets_off_instance[EUR]=1 exact, [SEK]=0 (null control).
  C card distinct tokens card_cfg_EUR=2, no_cfg=1, perturbed=1; pre-R7-D4-03
  card (57a6e19f^) off-install surfaces=4 against 3 at baseline.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container B8,
  4 cores, 15 GB, CPython 3.14.0rc2, node v22.22.2. Counts only: no timing.
Instrumented symbols: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator
  (.currency), sensor:CurrentPriceSensor, coordinator:_audit_price_units,
  coordinator:_entity_price, config_flow:_OPTION_FIELDS/_ByHass,
  currency:resolve_currency; card symbols in p8_card.mjs.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, "tests")
_P0, _T0 = time.process_time(), time.thread_time()

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import config_flow, coordinator as coord_mod, sensor as sensor_mod  # noqa: E402
from heatpump_optimizer.const import CONF_PRICE_ENTITY  # noqa: E402

PKG = Path("custom_components/heatpump_optimizer")
ISO = re.compile(r"^[A-Z]{3}$")
SYMBOL_ISO = {"€": "EUR", "£": "GBP", "zł": "PLN"}  # unambiguous symbols only ('kr' and '$' are not)


def feed_code(unit):
    money = str(unit or "").partition("/")[0].strip()
    if ISO.match(money):
        return money
    return SYMBOL_ISO.get(money)


def token_of(unit):
    m = re.match(r"\s*([A-Z]{3})\b", str(unit or ""))
    return m.group(1) if m else None


# --- A: price feed -> published unit -------------------------------------------------
FEED_UNITS = ["SEK/kWh", "EUR/kWh", "NOK/kWh", "DKK/kWh", "EUR/MWh", "€/kWh"]
INSTANCE = ["SEK", "EUR"]


def seam_a(patch_resolver=False):
    cells = mismatch = flagged = unflagged = 0
    rows = []
    for inst in INSTANCE:
        for unit in FEED_UNITS:
            hass = FakeHass({"sensor.price": FakeState("0.10", unit=unit)})
            hass.config.currency = inst
            cfg = {CONF_PRICE_ENTITY: "sensor.price", "price_source": "entity",
                   "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
            code = feed_code(unit)
            ctxm = (mock.patch.object(coord_mod, "resolve_currency", lambda h, _c=code: _c)
                    if patch_resolver else mock.patch.object(coord_mod, "_LOGGER", coord_mod._LOGGER))
            with ctxm:
                c = coord_mod.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
            entry = FakeEntry(data=cfg)
            published = sensor_mod.CurrentPriceSensor(c, entry).native_unit_of_measurement
            value = coord_mod._entity_price(hass, "sensor.price")
            hass.issues = []
            coord_mod._audit_price_units(hass, cfg)
            issue = [i[1] for i in hass.issues if "price" in i[1] or "currency" in i[1]]
            cells += 1
            off = token_of(published) != code
            mismatch += off
            flagged += off and bool(issue)
            unflagged += off and not issue
            rows.append((inst, unit, code, published, value, issue))
    return cells, mismatch, flagged, unflagged, rows


# --- B: config-flow money widgets --------------------------------------------------
MONEY_UNIT = re.compile(r"(?:^|\b)([A-Z]{3})(?:/|\b)")


def seam_b(currency):
    hass = FakeHass({})
    hass.config.currency = currency
    money = off = 0
    rows = []
    for row in config_flow._OPTION_FIELDS:
        w = row.widget.of(hass) if isinstance(row.widget, config_flow._ByHass) else row.widget
        cfg = getattr(w, "config", None)
        unit = cfg.get("unit_of_measurement") if isinstance(cfg, dict) else None
        tok = token_of(unit)
        if not tok or tok in {"COP"}:
            continue
        money += 1
        if tok != currency:
            off += 1
        rows.append((row.step, row.key, unit, tok != currency))
    return money, off, rows


# --- C: the card (Node) --------------------------------------------------------------
def seam_c(tmp):
    plan = Path(tmp) / "plan.json"
    env = dict(os.environ, HPO_PLANDATA=str(plan))
    subprocess.run([sys.executable, "tests/plan_view.py"], env=env, check=True, capture_output=True)
    node = os.environ.get("NODE", "/opt/node22/bin/node")
    out = {}
    runs = [("baseline", None, a) for a in ("card_cfg_EUR", "no_cfg", "perturb_drop_cfg_lead")]
    pre = Path(tmp) / "card_pre_r7.js"
    try:
        pre.write_text(subprocess.run(["git", "show", "57a6e19f^:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"],
                                      capture_output=True, text=True, check=True).stdout)
        runs.append(("pre_R7_D4_03", str(pre), "card_cfg_EUR"))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("NOTE: no .git here, the pre-fix positive control is skipped")
    for label, card, arm in runs:
        cmd = [node, "tools/audit/round9/D14/s2/p8_card.mjs", "--arm", arm] + (["--card", card] if card else [])
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if line.startswith(("RESULT", "SURFACES")):
                print(f"[{label}] {line}")
                m = re.match(r"RESULT (\w+)\[([^\]]+)\]=(\d+)", line)
                if m:
                    out[(label, m.group(1), m.group(2))] = int(m.group(3))
        if res.returncode:
            print(res.stderr[-800:])
    return out


# --- seam rule: every currency-resolution site ----------------------------------------
def seams():
    """Static enumeration: every site that decides a money figure's currency."""
    sites = []
    for f in sorted(PKG.glob("*.py")):
        src = f.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", None)) == "resolve_currency":
                sites.append((str(f), node.lineno, "resolve_currency(hass) [instance config]"))
            elif isinstance(node, ast.Attribute) and node.attr == "currency" and not isinstance(node.ctx, ast.Store):
                base = ast.unparse(node.value)
                if base not in {"hass.config", "getattr(hass, 'config', None)"}:
                    sites.append((str(f), node.lineno, f"{base}.currency [frozen at setup]"))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and re.search(r"\b(SEK|EUR|NOK|DKK)(/|\b)", node.value) and "/" in node.value and len(node.value) < 16:
                sites.append((str(f), node.lineno, f"literal {node.value!r}"))
            elif isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", None)) in {"normalize_price_per_kwh", "price_per_kwh"}:
                sites.append((str(f), node.lineno, "price unit parsed; money code discarded"))
    for tf in [PKG / "strings.json", *sorted((PKG / "translations").glob("*.json"))]:
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    yield from walk(v, f"{path}.{k}")
            elif isinstance(o, str):
                yield path, o
        for path, text in walk(json.loads(tf.read_text())):
            if re.search(r"\b(SEK|EUR|NOK|DKK|kr)\b", text) and "{currency}" not in text:
                sites.append((str(tf), 0, f"literal currency in {path}: {text[:70]!r}"))
    card = PKG / "www/heatpump-optimizer-card.js"
    for i, line in enumerate(card.read_text().splitlines(), 1):
        if re.search(r"\bcurrency\(\)|savingsUnit\(|config\.currency|attrRaw\(\"currency\"", line) and not line.strip().startswith(("*", "//")):
            sites.append((str(card), i, line.strip()[:90]))
    return sites


def main():
    if "--seams" in sys.argv:
        s = seams()
        for f, ln, what in s:
            print(f"SEAM {f}:{ln}  {what}")
        print(f"RESULT p8_currency_sites={len(s)} count")
        return
    cells, mis, fl, unfl, rows = seam_a()
    for r in rows:
        print("A", r)
    print(f"RESULT A_cells={cells} count")
    print(f"RESULT A_mismatch={mis} count")
    print(f"RESULT A_flagged_by_repair_issue={fl} count")
    print(f"RESULT A_unflagged_mismatch={unfl} count")
    _, misP, _, unflP, _ = seam_a(patch_resolver=True)
    print(f"RESULT A_unflagged_mismatch[perturbed:resolve_currency->feed code]={unflP} count")
    for cur in ("EUR", "SEK", "NOK"):
        money, off, brow = seam_b(cur)
        for r in brow:
            if r[3]:
                print("B", cur, r)
        print(f"RESULT B_money_widgets[{cur}]={money} count")
        print(f"RESULT B_money_widgets_off_instance[{cur}]={off} count")
    with tempfile.TemporaryDirectory() as tmp:
        seam_c(tmp)
    pc, tc = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 'n/a'}")
    except OSError:
        print("RESULT swapins=n/a")


if __name__ == "__main__":
    main()
