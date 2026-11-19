#!/usr/bin/env python3
"""D14-s3 (round 11, nightly-replay axis): P8 -- which surfaces of ONE install
resolve its money currency from the price feed, and which from the instance.

The install: ``tests/replay/synthetic-dhw-only.json`` with its price sensor
declaring HUF (``unit_of_measurement: HUF/kWh``, ``currency: HUF``) on a Home
Assistant instance configured for SEK, replayed one hour through the real
coordinator; then, on a hass holding that same price state and instance
currency, the options flow and the coordinator's fee notice are driven.

Surfaces (each a production call; the value read is what it delivers):
  S1 entity_units      money units the replayed entities publish (sweep)
  S2 mismatch_issue    the ``price_currency`` repair issue's {feed} placeholder
  S3 widget_label      ``config_flow._OPTION_FIELDS['grid_fee_fixed'].widget.of(hass)`` unit
  S4 widget_bound      the same widget accepts a 20 feed-units/kWh fee (stub selector range)
  S5 rules_bound       ``OptionsFlow.async_step_grid_fees({'grid_fee_rules': '= 20'})`` errors
  S6 notice_bound      ``HeatPumpOptimizerCoordinator._fee_series`` raises grid_fee_magnitude for '= 20'
A surface is DIVERGENT when it resolves to the instance (SEK) rather than the
feed (HUF): S1/S2/S3 by the code they name; S4/S5 by refusing a 20 HUF/kWh
fee the HUF bound (fee_bound('HUF') = 500, the money field max 250) admits;
S6 by raising the öre notice on it.

Metric: divergent surfaces out of 6 (count key: each surface's delivered value).
Null control (arm ``huf_instance``): the instance is HUF too -> 0.
Perturbation (``--perturb``): ``config_flow.resolve_currency`` resolves the
feed's declared code first (one line) -> divergent goes down (to 0 on S3-S5).
The repair issue's own text tells the user to enter grid fees in the FEED
currency, so a divergent S4/S5 refuses the action the notice asks for.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/p8_surfaces.py
Expected at 92d38ecb6: huf_feed_sek_instance divergent=3 (S3,S4,S5), huf_instance 0.
Machine: box B7, 4 vCPU. Tolerance: exact.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replaykit  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

FEED = "HUF"
ARMS = {"huf_feed_sek_instance": "SEK", "huf_instance": "HUF"}


def child(tree: Path, arm: str, perturb: bool) -> dict:
    instance = ARMS[arm]
    doc = json.loads((tree / "tests" / "replay" / "synthetic-dhw-only.json").read_text())
    start = datetime.fromisoformat(doc["window"]["start"])
    doc["window"]["end"] = (start + timedelta(hours=1)).isoformat()
    cfg = {**doc["entry"]["data"], **doc["entry"]["options"]}
    price = cfg["price_entity"]
    for row in doc["states"][price]:
        if row[2] is not None:
            row[2] = {**row[2], "unit_of_measurement": f"{FEED}/kWh", "currency": FEED}
    issues: list = []

    def setup(ctx):
        import harness
        from homeassistant.helpers import issue_registry as ir
        harness.FakeConfig.currency = instance
        real = ir.async_create_issue

        def create(hass, domain, issue_id, **kw):
            issues.append((issue_id, kw.get("translation_placeholders") or {}))
            return real(hass, domain, issue_id, **kw)
        ir.async_create_issue = create
        if perturb:
            from heatpump_optimizer import config_flow as cf
            from heatpump_optimizer import currency as cur
            real_resolve = cf.resolve_currency

            def resolve(hass):  # the feed's declared code first, as the entities do
                st = hass.states.get(price)
                attrs = dict(getattr(st, "attributes", {}) or {}) if st else {}
                return cur.declared_currency(attrs.get("unit_of_measurement"), attrs) \
                    or real_resolve(hass)
            cf.resolve_currency = resolve

    out = replaykit.run(tree, doc, 30, setup)
    surfaces: dict[str, object] = {}
    units = sorted({str(r["unit"]) for recs in out["records"] for r in recs
                    if r.get("unit") and re.search(r"\b[A-Z]{3}\b", str(r["unit"]))})
    surfaces["S1_entity_units"] = units
    feed_issue = [p.get("feed") for i, p in issues if i == "price_currency"]
    surfaces["S2_mismatch_issue"] = feed_issue[-1:] or None

    # The options flow and the fee notice, on a hass holding that price state.
    import harness
    from heatpump_optimizer import config_flow as flow
    from heatpump_optimizer import coordinator as cm
    last = doc["states"][price][-1]
    last = [last[0], last[1], next(r[2] for r in reversed(doc["states"][price]) if r[2])]
    hass = harness.FakeHass({price: harness.FakeState(
        last[1], attributes=last[2], last_updated=datetime.now(timezone.utc))})
    row = next(r for r in flow._OPTION_FIELDS if r.key == "grid_fee_fixed")
    widget = row.widget.of(hass)
    surfaces["S3_widget_label"] = widget.config.get("unit_of_measurement")
    try:
        widget(20.0)
        surfaces["S4_widget_bound"] = f"accepts 20 (max {widget.config.get('max')})"
    except ValueError as err:
        surfaces["S4_widget_bound"] = f"refuses 20: {err}"

    class Entry:
        def __init__(self, data):
            self.data, self.options, self.entry_id = data, {}, "e"
            self.title, self.version, self.minor_version = "t", 1, 1
            self.unique_id = None
    opt = flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(Entry({**cfg}))
    opt.hass = hass
    shown = asyncio.run(opt.async_step_grid_fees(None))
    sent = asyncio.run(opt.async_step_grid_fees({"grid_fee_rules": "= 20"}))
    surfaces["S5_rules_bound"] = {
        "placeholder_bound": (shown.get("description_placeholders") or {}).get("fee_bound"),
        "placeholder_currency": (shown.get("description_placeholders") or {}).get("currency"),
        "error": (sent.get("errors") or {}).get("grid_fee_rules")}
    nh = harness.FakeHass({price: harness.FakeState(
        last[1], attributes=last[2], last_updated=datetime.now(timezone.utc))})
    coord = cm.HeatPumpOptimizerCoordinator(nh, Entry({**cfg, "grid_fee_mode": "rules",
                                                       "grid_fee_rules": "= 20"}))
    now = datetime.now(timezone.utc)
    coord._fee_series([now + timedelta(minutes=15 * i) for i in range(4)])
    notice = [i[2].get("translation_placeholders", {}) for i in getattr(nh, "issues", [])
              if i[1] == "grid_fee_magnitude"]
    surfaces["S6_notice_bound"] = {"coordinator_currency": coord.currency,
                                   "raised": notice}
    return {"arm": arm, "instance": instance, "surfaces": surfaces,
            "cycles": out["run"]["cycles"]}


def divergent(d: dict) -> list[str]:
    s = d["surfaces"]
    inst = d["instance"]
    if inst == FEED:
        bad_code = None
    else:
        bad_code = inst
    out = []
    if bad_code and any(bad_code in u for u in s["S1_entity_units"]):
        out.append("S1_entity_units")
    if bad_code and s["S2_mismatch_issue"] and s["S2_mismatch_issue"][0] != FEED:
        out.append("S2_mismatch_issue")
    if bad_code and str(s["S3_widget_label"]).startswith(bad_code):
        out.append("S3_widget_label")
    if str(s["S4_widget_bound"]).startswith("refuses"):
        out.append("S4_widget_bound")
    if s["S5_rules_bound"]["error"]:
        out.append("S5_rules_bound")
    if s["S6_notice_bound"]["raised"]:
        out.append("S6_notice_bound")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=replaykit.ROOT)
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--child", action="store_true")
    a = ap.parse_args()
    tree = a.tree.resolve()
    if a.child:
        replaykit.emit(child(tree, a.arm, a.perturb))
        return 0
    t0 = time.monotonic()
    import concurrent.futures as cf
    arms = [a.arm] if a.arm else list(ARMS)
    extra = ["--perturb"] if a.perturb else []
    with cf.ThreadPoolExecutor(len(arms)) as ex:
        res = dict(zip(arms, ex.map(lambda arm: replaykit.child(
            Path(__file__).resolve(), tree, ["--arm", arm, *extra]), arms)))
    for arm, d in res.items():
        if d is None:
            print(f"RESULT {arm}_ran=0 count")
            continue
        print(f"arm {arm} (feed {FEED}, instance {d['instance']}): cycles={d['cycles']}")
        for k, v in d["surfaces"].items():
            print(f"  {k}: {v}")
        div = divergent(d)
        print(f"  divergent: {div}")
        print(f"RESULT {arm}_divergent_surfaces={len(div)} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    replaykit.tail_results()
    return 0


if __name__ == "__main__":
    sys.exit(main())
