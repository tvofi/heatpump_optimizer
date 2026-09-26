"""L4 lead (raised by D4-s1) for D4-s2 / D4.M2 -- setup-diagram text is English on a Swedish install.

Metric (one line): en_identical = published setup strings that are byte-identical between an
  `en` and an `sv` install, over three seams: (a) the config/options flow's setup_overview page,
  counted per non-empty, non-fence line of the RENDERED description (the translation's own template with the
  flow's `setup_summary` placeholder filled in, exactly as the frontend substitutes it); (b) the
  slot labels `describe_setup` publishes as the plan sensors' `setup_topology` attribute, which the
  card prints verbatim; (c) the `sensor_advisor` row labels. Count key: the strings production
  delivers (flow placeholders, describe_setup / rank_sensor_advisor return values).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D4/leads/l4_setup_labels.py [--perturb]
Perturbation (--perturb): an in-memory stand-in for the honest fix -- topology's slot-label table
  and the summary's fixed headings are passed through a Swedish table when the language is `sv`
  (the way narrative.render already picks TEMPLATES[language]). Expected: en_identical -> 0 on (b)
  and (c), and (a) down to the non-text lines (entity ids, box glyphs).
Null control: narrative.render, the other language-bearing text on the same plan sensors, driven
  with the same sample reason under `en` and `sv`: 0 identical lines.
Expected: en_identical_total=41 (22 page lines of 23, 16 of 16 slots, 3 of 3 advisor rows), null 0;
  --perturb 0. Exact. Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: config_flow:_setup_overview_form, topology:describe_setup, topology:render_text_summary,
  topology:rank_sensor_advisor, narrative:render.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import config_flow, narrative, topology  # noqa: E402
from profiles import house  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
TR = {lang: json.load(open(f"{PKG}/translations/{lang}.json", encoding="utf-8"))
      for lang in ("en", "sv")}
CONFIG = dict(house(two_zone=True), indoor_temp_entity="sensor.livingroom",
              outdoor_temp_entity="sensor.outside", buffer_tank_temp_entity="sensor.tank",
              dhw_enabled=True)
PERTURB = "--perturb" in sys.argv
LANG = {"v": "en"}

if PERTURB:
    # A stand-in for a localised backend: every English literal the three seams publish gets
    # a Swedish rendering when the active language is sv. Mechanical ("[sv] " + text), because
    # what the count keys on is whether the published string follows the language at all.
    _orig_desc, _orig_sum, _orig_adv = (topology.describe_setup, topology.render_text_summary,
                                        topology.rank_sensor_advisor)

    def _tr(s):
        return s if LANG["v"] == "en" else "[sv] " + s

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


class _Flow:
    def async_show_form(self, **kw):
        return kw


def seams(lang):
    LANG["v"] = lang
    form = config_flow._setup_overview_form(_Flow(), CONFIG)
    template = TR[lang]["options"]["step"]["setup_overview"]["description"]
    page = template.format(**form["description_placeholders"])
    labels = [s["label"] for s in topology.describe_setup(dict(CONFIG))["slots"]]
    adv = topology.rank_sensor_advisor(dict(CONFIG), hp_kw=()) or {}
    adv_labels = [r["label"] for r in adv.get("candidates", [])]
    narr = narrative.render([{"reason": "cheap_price", "kwh": 1.2, "sek": 0.5, "hours": 2,
                              "start": "02:00", "end": "04:00", "price": 0.3}], lang, "SEK")
    return page, labels, adv_labels, narr


def main():
    t0, th0 = time.process_time(), time.thread_time()
    en, sv = seams("en"), seams("sv")
    en_lines = {ln for ln in en[0].split("\n") if ln.strip() and ln.strip() != "```"}
    sv_lines = [ln for ln in sv[0].split("\n") if ln.strip() and ln.strip() != "```"]
    same_page = [ln for ln in sv_lines if ln in en_lines]
    same_slots = sum(a == b for a, b in zip(en[1], sv[1]))
    same_adv = sum(a == b for a, b in zip(en[2], sv[2]))
    same_narr = sum(a == b for a, b in zip(en[3], sv[3]))
    for ln in same_page[:12]:
        print(f"SV_PAGE_LINE_IDENTICAL_TO_EN {ln!r}")
    print(f"SV_SLOT_LABELS {sv[1]}")
    print(f"SV_ADVISOR_LABELS {sv[2]}")
    print(f"NARRATIVE en={en[3]} sv={sv[3]}")
    print(f"RESULT flow_page_lines_sv={len(sv_lines)} count")
    print(f"RESULT flow_page_lines_identical_to_en={len(same_page)} count")
    print(f"RESULT slot_labels_identical_to_en={same_slots} of {len(sv[1])}")
    print(f"RESULT advisor_labels_identical_to_en={same_adv} of {len(sv[2])}")
    print(f"RESULT en_identical_total={len(same_page) + same_slots + same_adv} count")
    print(f"RESULT null_narrative_lines_identical_to_en={same_narr} of {len(sv[3])}")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
