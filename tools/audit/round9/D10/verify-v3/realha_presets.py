"""D10 verify-v3 (round 9), D10-s2-01 in REAL Home Assistant core 2026.2.3.

The entry is created by the real config flow (price-entity source) and set up
by the real ConfigEntries; the climate entity's preset_modes are read from the
REAL state machine (hass.states), and each preset is resolved the way the
frontend resolves a state-attribute value, against the translations and icons
real HA serves (homeassistant.helpers.translation.async_get_translations and
homeassistant.helpers.icon.async_get_icons, i.e. what the websocket
frontend/get_translations and frontend/get_icons return):
  1. component.<platform>.entity.climate.<translation_key>.state_attributes.preset_mode.state.<p>
  2. component.climate.entity_component._.state_attributes.preset_mode.state.<p>
  else the raw token is displayed.
Metric (one line each):
  untranslated_<lang>  presets in the state's preset_modes with neither key, for en and sv;
  no_specific_icon     presets with no state icon at either level (they get the
                       climate component's default, mdi:circle-medium);
  hvac_untranslated    hvac_modes with no translation (the sibling attribute).
Perturbation (--perturb): the published preset 'economy' renamed to HA's
standard 'eco' in memory (class attribute and the set-preset map untouched,
read only) -> untranslated_en 2 -> 1.
Expected: baseline untranslated_en=2 untranslated_sv=2 no_specific_icon=2
hvac_untranslated=0; --perturb 1/1/1/0. Exact (counts).

Run:  /home/claude/havenv/bin/python tools/audit/round9/D10/verify-v3/realha_presets.py [--perturb]
      (from the repository root, WITHOUT tests/hastub on PYTHONPATH)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _realha as R  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant import config_entries  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers.icon import async_get_icons  # noqa: E402
from homeassistant.helpers.translation import async_get_translations  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
PERTURB = "--perturb" in sys.argv
CLOCK = R.Clock()

from custom_components.heatpump_optimizer import climate, const  # noqa: E402

if PERTURB:
    # real HA's CachedProperties metaclass turns _attr_* into descriptors, so
    # the list is rebuilt from the module's PRESET_* constants, not read back
    climate.HeatPumpOptimizerClimate._attr_preset_modes = [
        "eco" if p == climate.PRESET_ECONOMY else p
        for p in (climate.PRESET_AUTO, climate.PRESET_COMFORT, climate.PRESET_ECONOMY, climate.PRESET_BOOST)]


async def setup(hass):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    rows = [{"start": (now - timedelta(hours=1) + timedelta(minutes=15 * i)).isoformat(),
             "value": 0.9} for i in range(4 * 49)]
    hass.states.async_set("sensor.price", "0.9", {"raw_today": rows, "unit_of_measurement": "SEK/kWh"})
    hass.states.async_set("weather.home", "sunny")
    mgr = hass.config_entries.flow
    r = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_USER})
    r = await mgr.async_configure(r["flow_id"], {
        "name": "HPO", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.price", const.CONF_WEATHER_ENTITY: "weather.home"})
    r = await mgr.async_configure(r["flow_id"], {})
    for _ in range(6):
        if r["type"] in ("abort", "create_entry"):
            break
        r = await mgr.async_configure(r["flow_id"], {"next_step_id": "finish_now"} if r["type"] == "menu" else {})
    assert r["type"] == "create_entry", r
    await hass.async_block_till_done(wait_background_tasks=True)
    return r["result"]


async def main():
    hass = await R.make_hass()
    entry = await setup(hass)
    assert entry.state is config_entries.ConfigEntryState.LOADED, entry.state
    reg = er.async_get(hass)
    ent = next(e for e in reg.entities.values()
               if e.config_entry_id == entry.entry_id and e.domain == "climate")
    st = hass.states.get(ent.entity_id)
    presets = st.attributes.get("preset_modes") or []
    hvac = st.attributes.get("hvac_modes") or []
    tk = ent.translation_key
    print(f"entity={ent.entity_id} translation_key={tk!r} preset_modes={presets} hvac_modes={hvac} "
          f"state={st.state} preset_mode={st.attributes.get('preset_mode')!r}")
    res = {}
    for lang in ("en", "sv"):
        ent_tr = await async_get_translations(hass, lang, "entity", [R.DOMAIN])
        comp_tr = await async_get_translations(hass, lang, "entity_component", ["climate"])

        def label(attr, v):
            k1 = f"component.{R.DOMAIN}.entity.climate.{tk}.state_attributes.{attr}.state.{v}"
            k2 = f"component.climate.entity_component._.state_attributes.{attr}.state.{v}"
            return ent_tr.get(k1) if tk else None, comp_tr.get(k2)

        miss = [p for p in presets if not any(label("preset_mode", p))]
        shown = {p: (label("preset_mode", p)[0] or label("preset_mode", p)[1] or f"<raw:{p}>") for p in presets}
        res[lang] = miss
        hv = [h for h in hvac if not comp_tr.get(f"component.climate.entity_component._.state.{h}")]
        res[f"hvac_{lang}"] = hv
        print(f"lang={lang} displayed={shown} untranslated={miss} hvac_untranslated={hv}")
    icons = await async_get_icons(hass, "entity_component", ["climate"])
    eicons = await async_get_icons(hass, "entity", [R.DOMAIN])
    comp_pm = icons["climate"]["_"]["state_attributes"]["preset_mode"]
    ent_pm = (((eicons.get(R.DOMAIN) or {}).get("climate") or {}).get(tk or "", {})
              .get("state_attributes", {}).get("preset_mode", {}).get("state", {}))
    noicon = [p for p in presets if p not in comp_pm.get("state", {}) and p not in ent_pm]
    print(f"icons: {[(p, ent_pm.get(p) or comp_pm.get('state', {}).get(p) or 'default:' + comp_pm.get('default', '')) for p in presets]}")
    print(f"MODE {'perturb' if PERTURB else 'baseline'}  ha_version={R.HA_VERSION}")
    print(f"RESULT untranslated_en={len(res['en'])} count ({','.join(res['en'])})")
    print(f"RESULT untranslated_sv={len(res['sv'])} count ({','.join(res['sv'])})")
    print(f"RESULT no_specific_icon={len(noicon)} count ({','.join(noicon)})")
    print(f"RESULT hvac_untranslated={len(res['hvac_en'])} count")
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_stop(force=True)


asyncio.run(main())
R.footer(CLOCK)
