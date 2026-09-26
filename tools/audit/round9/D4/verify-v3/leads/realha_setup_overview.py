"""V3 leads sub-seat, round 9: D4-s2-81 (setup overview / setup diagram text is
English on a Swedish install) driven through REAL Home Assistant -- the real
options FlowManager, the real ``helpers.translation`` loader and a real
``hass.config.language``, not a JSON file read directly (as the lead harness
did) and not tests/hastub.

METRIC (one line): of the setup_overview page's RENDERED description -- the
real translation catalogue's own Swedish template (``helpers.translation
.async_get_translations``, exactly what the frontend receives) with the real
``OptionsFlow.async_step_setup_overview``'s ``description_placeholders``
substituted in -- how many non-empty lines are byte-identical to the same
page rendered under an English install; separately, whether the Swedish
template text itself (the part production actually localises) is genuinely
Swedish, to rule out a translation file that is itself untranslated.

RUN (from repo root; NOT PYTHONPATH=tests/hastub):
  PYTHONPATH=<scratch numpy/scipy dir> /home/claude/havenv/bin/python \
    tools/audit/round9/D4/verify-v3/leads/realha_setup_overview.py [--perturb]

Perturbation (--perturb): topology.describe_setup / render_text_summary /
  rank_sensor_advisor wrapped in memory to pass every literal they publish
  through a Swedish table when hass.config.language == "sv" -- mirroring the
  lead harness's own perturbation, but here applied around the REAL
  OptionsFlow rather than by calling the functions directly. Expected:
  identical-line count on the rendered page drops to (at most) the
  language-invariant lines (the Swedish template's own fixed prose and any
  entity ids / box-drawing glyphs).

EXPECTED at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact):
  real_template_is_swedish=1 (the sv translation catalogue's fixed prose
    around {setup_summary} is genuinely Swedish, read through the real loader)
  real_identical_lines_sv_en=<n> (>0: the {setup_summary} body inside the
    real rendered page is English regardless of hass.config.language)
  --perturb: real_identical_lines_sv_en drops (summary body no longer English)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence, 96b89163).
Machine: G2-leads verify-v3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import shutil
import sys
import tempfile
import time
from unittest import mock

REPO = os.getcwd()
assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"

import abc as _abc  # noqa: E402
import typing as _typing  # noqa: E402
if not hasattr(_typing, "ByteString"):
    class _ByteString(_abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    _typing.ByteString = _ByteString

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import area_registry as ar  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers import floor_registry as fr  # noqa: E402
from homeassistant.helpers import label_registry as lr  # noqa: E402
from homeassistant.helpers import translation  # noqa: E402

assert "hastub" not in homeassistant.__file__, homeassistant.__file__
PERTURB = "--perturb" in sys.argv
DOMAIN = "heatpump_optimizer"


async def make_hass(tmp, language="en"):
    hass = core.HomeAssistant(tmp)
    hass.config.skip_pip = True
    hass.config.language = language
    await hass.config.async_set_time_zone("Europe/Stockholm")
    loader.async_setup(hass)
    for reg in (ar, fr, lr, dr, er):
        await reg.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    # Environment shim, not a production change: the manifest's 'http'
    # dependency needs hass.auth and a web server, neither of which a flow
    # touches; mark it loaded so the real FlowManager proceeds (mirrors
    # tools/audit/round9/D12/verify-v3/realha_flows.py's mechanics).
    hass.config.components.add("http")
    return hass


def add_entry(hass, data=None, options=None, title="HPO"):
    entry = config_entries.ConfigEntry(
        data=data or {}, discovery_keys={}, domain=DOMAIN, minor_version=1,
        options=options or {}, source="user", subentries_data=None, title=title,
        unique_id=None, version=1,
    )
    hass.config_entries._entries[entry.entry_id] = entry
    return entry


CONFIG = {
    "name": "HPO", "price_source": "entity", "price_entity": "sensor.nordpool",
    "weather_entity": "weather.home", "indoor_temp_entity": "sensor.livingroom",
    "outdoor_temp_entity": "sensor.outside", "buffer_tank_temp_entity": "sensor.tank",
    "dhw_enabled": True, "two_zone_enabled": True,
}


async def overview_page(hass, entry):
    """The real OptionsFlow, driven to the setup_overview page, exactly as
    the frontend would reach it: init > (menu hops as needed) > setup_overview."""
    mgr = hass.config_entries.options
    res = await mgr.async_init(entry.entry_id)
    flow = mgr._progress[res["flow_id"]]
    result = await flow.async_step_setup_overview()
    mgr.async_abort(res["flow_id"])
    return result


async def rendered_description(hass, lang, entry):
    tr = await translation.async_get_translations(hass, lang, "options", {DOMAIN})
    template = tr[f"component.{DOMAIN}.options.step.setup_overview.description"]
    hass.config.language = lang
    result = await overview_page(hass, entry)
    ph = result["description_placeholders"]
    rendered = template
    for k, v in ph.items():
        rendered = rendered.replace("{" + k + "}", str(v))
    return template, rendered, ph


async def main():
    tmp = tempfile.mkdtemp(prefix="realha_d4v3_")
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(tmp, "custom_components"))
    sys.path.insert(0, tmp)
    from custom_components.heatpump_optimizer import topology  # noqa: E402

    if PERTURB:
        _orig_desc, _orig_sum, _orig_adv = (
            topology.describe_setup, topology.render_text_summary, topology.rank_sensor_advisor)
        _lang_box = {"v": "en"}

        def _tr(s):
            return s if _lang_box["v"] == "en" else "[sv] " + s

        def describe_setup(config):
            out = _orig_desc(config)
            for slot in out.get("slots", []):
                slot["label"] = _tr(slot["label"])
            return out

        def render_text_summary(setup):
            return "\n".join(_tr(ln) if ln.strip() and ln.strip() != "```" else ln
                              for ln in _orig_sum(setup).split("\n"))

        def rank_sensor_advisor(config, *, hp_kw=()):
            out = _orig_adv(config, hp_kw=hp_kw)
            for row in (out or {}).get("candidates", []):
                row["label"] = _tr(row["label"])
            return out

        topology.describe_setup = describe_setup
        topology.render_text_summary = render_text_summary
        topology.rank_sensor_advisor = rank_sensor_advisor

        import custom_components.heatpump_optimizer.config_flow as cf  # noqa: E402
        cf.topology.describe_setup = describe_setup
        cf.topology.render_text_summary = render_text_summary

    hass = await make_hass(tmp, "en")
    entry = add_entry(hass, data=dict(CONFIG))

    tmpl_en, rendered_en, _ = await rendered_description(hass, "en", entry)

    if PERTURB:
        _lang_box["v"] = "sv"
    tmpl_sv, rendered_sv, ph_sv = await rendered_description(hass, "sv", entry)

    print(f"# real sv template head: {tmpl_sv.splitlines()[0]!r}")
    print(f"# real en rendered head: {rendered_en.splitlines()[0]!r}")
    print(f"# real sv rendered head: {rendered_sv.splitlines()[0]!r}")

    # Is the sv translation catalogue's own fixed prose (the part around
    # {setup_summary}, excluding it) genuinely Swedish, through the real loader?
    fixed_sv = tmpl_sv.replace("{setup_summary}", "")
    fixed_en = tmpl_en.replace("{setup_summary}", "")
    swedish_markers = ("ditt", "är", "givare", "anläggning", "utifrån")
    is_swedish = fixed_sv != fixed_en and any(m in fixed_sv for m in swedish_markers)
    print(f"RESULT real_template_is_swedish={int(is_swedish)} flag")

    en_lines = {ln for ln in rendered_en.split("\n") if ln.strip() and ln.strip() != "```"}
    sv_lines = [ln for ln in rendered_sv.split("\n") if ln.strip() and ln.strip() != "```"]
    same = [ln for ln in sv_lines if ln in en_lines]
    for ln in same[:15]:
        print(f"SV_RENDERED_LINE_IDENTICAL_TO_EN {ln!r}")
    print(f"RESULT real_rendered_lines_sv={len(sv_lines)} count")
    print(f"RESULT real_identical_lines_sv_en={len(same)} count")

    # setup_topology attribute (describe_setup slot labels), and the sensor
    # advisor, as production actually calls them (not the template layer).
    if PERTURB:
        _lang_box["v"] = "en"
    slots_en = [s["label"] for s in topology.describe_setup(dict(CONFIG))["slots"]]
    hass.config.language = "sv"
    if PERTURB:
        _lang_box["v"] = "sv"
    slots_sv = [s["label"] for s in topology.describe_setup(dict(CONFIG))["slots"]]
    same_slots = sum(a == b for a, b in zip(slots_en, slots_sv))
    print(f"RESULT real_slot_labels_identical_to_en={same_slots} of {len(slots_sv)}")
    print(f"RESULT ha_version={HA_VERSION}")

    await hass.async_stop(force=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    t0, tt0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={(pc / tc) if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
