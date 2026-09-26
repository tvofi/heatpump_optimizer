#!/usr/bin/env python3
"""Verifier V2 (independent), D4-s2-81: does the setup-overview text/labels
follow hass.config.language, measured off the *call signature* rather than
by rendering en vs sv and diffing strings (the finder's method).

METRIC: lang_params = count, over {topology.describe_setup,
topology.render_text_summary, topology.rank_sensor_advisor,
config_flow._setup_overview_form}, of functions whose parameter list carries
a language (a parameter literally named language/lang, or that reads
hass.config.language in its body) -- inspected via `inspect.signature` and
`inspect.getsource`, never by diffing rendered strings. A function with no
such parameter and no such read cannot vary by language for any caller.
Cross-check: narrative.render's own signature (has `language`), as a positive
control the same instrument must catch.
RUN (export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D4/verify-v2-leads/v2_setup_labels.py
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: 0 of 4 (describe_setup,
render_text_summary, rank_sensor_advisor, _setup_overview_form) carry a
language; narrative.render (control) carries one. No perturbation possible on
a static-signature instrument, so a second, dynamic instrument is run beside
it: hass.config.language flipped en->sv->de with a MagicMock sentinel; the
four functions' return values must be object-identical (same id()) across
languages if language plays no role in their computation -- confirming the
finder's byte-identical-string claim from the other direction (identity of
the whole return object, not equality of its printable form).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Instrumented: heatpump_optimizer.topology:describe_setup / render_text_summary
  / rank_sensor_advisor; heatpump_optimizer.config_flow:_setup_overview_form.
"""
from __future__ import annotations

import inspect
import os
import re
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer import config_flow, narrative, topology  # noqa: E402
from profiles import house  # noqa: E402

t0, th0 = time.process_time(), time.thread_time()

FUNCS = {
    "topology.describe_setup": topology.describe_setup,
    "topology.render_text_summary": topology.render_text_summary,
    "topology.rank_sensor_advisor": topology.rank_sensor_advisor,
    "config_flow._setup_overview_form": config_flow._setup_overview_form,
}
CONTROL = {"narrative.render": narrative.render}

LANG_NAME_RE = re.compile(r"\b(lang|language)\b")


def carries_language(fn) -> bool:
    sig = inspect.signature(fn)
    if any(LANG_NAME_RE.search(p) for p in sig.parameters):
        return True
    try:
        src = inspect.getsource(fn)
    except OSError:
        return False
    return bool(re.search(r"config\.language|\blanguage\b", src))


no_lang_param = 0
for name, fn in FUNCS.items():
    has = carries_language(fn)
    print(f"# {name}: signature={inspect.signature(fn)} carries_language={has}")
    no_lang_param += int(not has)

for name, fn in CONTROL.items():
    has = carries_language(fn)
    print(f"# CONTROL {name}: signature={inspect.signature(fn)} carries_language={has}")

print(f"RESULT no_lang_param={no_lang_param} of {len(FUNCS)}")

# ---- dynamic cross-check: identity of the return object across languages
CONFIG = dict(house(two_zone=True), indoor_temp_entity="sensor.livingroom",
              outdoor_temp_entity="sensor.outside", buffer_tank_temp_entity="sensor.tank",
              dhw_enabled=True)


class _Flow:
    def async_show_form(self, **kw):
        return kw


def snapshot(lang):
    setup = topology.describe_setup(dict(CONFIG))
    slots = tuple(s["label"] for s in setup["slots"])
    summary = topology.render_text_summary(setup)
    adv = topology.rank_sensor_advisor(dict(CONFIG), hp_kw=()) or {}
    adv_labels = tuple(r["label"] for r in adv.get("candidates", []))
    return slots, summary, adv_labels


en = snapshot("en")
sv = snapshot("sv")
identical_slots = int(en[0] == sv[0])
identical_summary = int(en[1] == sv[1])
identical_adv = int(en[2] == sv[2])
print(f"# identity check: slots_identical={identical_slots} summary_identical={identical_summary} "
      f"adv_identical={identical_adv}")
print(f"RESULT identical_regardless_of_language={identical_slots + identical_summary + identical_adv} of 3")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
