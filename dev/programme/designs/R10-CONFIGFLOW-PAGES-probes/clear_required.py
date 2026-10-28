"""Spike: clearing the price entity under price_source=entity -- saved or refused?"""
import asyncio, sys
from pathlib import Path
root = next(c for c in Path(__file__).resolve().parents if (c / "custom_components/heatpump_optimizer/manifest.json").is_file())
sys.path[:0] = [str(root / "tests"), str(root / "custom_components")]
from harness import FakeEntry, FakeHass
from heatpump_optimizer import config_flow as cf, const as c
async def run():
    entry = FakeEntry(data={c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY, c.CONF_PRICE_ENTITY: "sensor.price"})
    flow = cf.HeatPumpOptimizerOptionsFlow(entry); flow.hass = FakeHass()
    res = await flow.async_step_entities({c.CONF_PRICE_SOURCE: c.PRICE_SOURCE_ENTITY})
    saved = {**entry.data, **(entry.options or {})}
    print(f"RESULT type={res.get('type')} errors={res.get('errors')} stored_price_entity={saved.get(c.CONF_PRICE_ENTITY)!r}")
asyncio.run(run())
