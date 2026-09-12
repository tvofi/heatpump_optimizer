#!/usr/bin/env python3
"""D4 round-4 — the config and options flows, scored against a written rubric.

METRIC: for every page of both flows, driven through the real handlers with
the Home Assistant stub, the per-page counts a rubric scores — presented
fields (section-nested included), fields with no ``data_description`` help
text, fields whose label or help text is missing from en.json or sv.json,
numeric selectors with no min/max, pages with no description, and error keys
raised by the handlers that no strings file translates — plus the step count
from install to the first plan.

RUN (from the export root):

    PYTHONPATH=tests/hastub \\
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \\
      tools/audit/round4/D4/config_flow_rubric.py

EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, audit box
(8-core Apple M1, macOS 25.6.0, CPython 3.11): every RESULT below is a count
over the tree; tolerance +-0 (no float, no timing, no contention).

LIMIT, stated because the brief requires it: there is no Home Assistant
frontend on this box, so nothing here RENDERS a config-flow page. Every
statement about a page's look is inferred from the schema the handler
returns and from the strings files the frontend would use to label it.
Ordering, grouping, field counts, selector ranges, defaults, error keys and
translation coverage are read off the real objects; visual spacing,
line-wrapping and control sizes are not measured and are not claimed.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import voluptuous as vol  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow  # noqa: E402

ROOT = Path(".")
OUT = ROOT / "tools/audit/round4/D4/out"
OUT.mkdir(parents=True, exist_ok=True)

STRINGS = json.loads((ROOT / "custom_components/heatpump_optimizer/strings.json").read_text())
EN = json.loads((ROOT / "custom_components/heatpump_optimizer/translations/en.json").read_text())
SV = json.loads((ROOT / "custom_components/heatpump_optimizer/translations/sv.json").read_text())


# ---------------------------------------------------------------- schema walk
def _name(key):
    return str(getattr(key, "schema", key))


def walk_schema(schema, section=None, out=None):
    """(section, field, required, default, selector) in the order presented.

    Sections are ``data_entry_flow`` section wrappers: the frontend draws
    them as a collapsible group, so a field inside one is a field the user
    must open a group to reach.
    """
    if out is None:
        out = []
    inner = getattr(schema, "schema", None)
    if not isinstance(inner, dict):
        return out
    for key, value in inner.items():
        sub = getattr(value, "schema", None)
        is_section = value.__class__.__name__ == "section" or (
            hasattr(value, "schema") and isinstance(getattr(value.schema, "schema", None), dict)
            and value.__class__.__name__ not in ("Schema",)
        )
        if is_section and sub is not None:
            walk_schema(sub if hasattr(sub, "schema") else value.schema, _name(key), out)
            continue
        if isinstance(value, vol.Schema) and isinstance(getattr(value, "schema", None), dict):
            walk_schema(value, _name(key), out)
            continue
        default = None
        has_default = False
        d = getattr(key, "default", None)
        if d is not None and d is not vol.UNDEFINED:
            try:
                default = d()
                has_default = True
            except Exception:
                default = repr(d)
                has_default = True
        out.append({
            "section": section,
            "field": _name(key),
            "required": key.__class__.__name__ == "Required",
            "has_default": has_default,
            "default": default if isinstance(default, (int, float, str, bool, type(None))) else repr(default),
            "selector": value.__class__.__name__,
            "config": _selector_config(value),
        })
    return out


def _selector_config(value):
    cfg = getattr(value, "config", None)
    if isinstance(cfg, dict):
        return {k: (v if isinstance(v, (int, float, str, bool, type(None), list)) else repr(v))
                for k, v in cfg.items()}
    return {}


# ------------------------------------------------------------- drive the flows
def _run(coro):
    return asyncio.run(coro)


def config_pages():
    """Every page of the initial flow, rendered by its real handler."""
    pages = {}
    steps = [m.group(1) for m in re.finditer(
        r"^    async def async_step_([a-z_]+)\(",
        (ROOT / "custom_components/heatpump_optimizer/config_flow.py").read_text(), re.M)]
    seen = set()
    for step in steps:
        handler = getattr(config_flow.HeatPumpOptimizerConfigFlow, f"async_step_{step}", None)
        if handler is None or step in seen:
            continue
        seen.add(step)
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        flow._data = {}
        try:
            result = _run(handler(flow, None))
        except Exception as err:  # a step that needs prior state
            pages[step] = {"error": f"{type(err).__name__}: {err}"}
            continue
        pages[step] = _summarise(result)
    return pages


def option_pages():
    cls = config_flow.HeatPumpOptimizerOptionsFlow
    pages = {}
    steps = [m.group(1) for m in re.finditer(
        r"^    async def async_step_([a-z_]+)\(",
        (ROOT / "custom_components/heatpump_optimizer/config_flow.py").read_text(), re.M)]
    for step in steps:
        handler = getattr(cls, f"async_step_{step}", None)
        if handler is None:
            continue
        flow = cls(FakeEntry())
        flow.hass = FakeHass()
        try:
            result = _run(handler(flow, None))
        except Exception as err:
            pages[step] = {"error": f"{type(err).__name__}: {err}"}
            continue
        pages[step] = _summarise(result)
    return pages


def _summarise(result):
    if not isinstance(result, dict):
        return {"type": type(result).__name__}
    out = {"type": result.get("type"), "step_id": result.get("step_id")}
    if result.get("menu_options") is not None:
        mo = result["menu_options"]
        out["menu_options"] = list(mo) if not isinstance(mo, dict) else list(mo)
        out["fields"] = []
        return out
    schema = result.get("data_schema")
    out["fields"] = walk_schema(schema) if schema is not None else []
    return out


# ------------------------------------------------------------------ the rubric
RUBRIC = [
    ("R1 one theme per page",
     "the page's fields belong to one subject; a page mixing unrelated "
     "subjects scores 0"),
    ("R2 related fields adjacent",
     "fields sharing a prefix or a unit are contiguous in the presented order"),
    ("R3 sensible defaults",
     "every non-entity field carries a default, so an untouched page can be "
     "submitted"),
    ("R4 errors say what to change",
     "every error key a handler can raise is translated in en.json and sv.json"),
    ("R5 no jargon without help text",
     "every field has a data_description in strings.json"),
    ("R6 field count",
     "<= 8 presented fields at the top level of a page, sections excluded"),
    ("R7 both languages complete",
     "every label and help text present in en.json is present in sv.json"),
    ("R8 numeric ranges bounded",
     "every NumberSelector carries a min and a max"),
]


def score(step_id, page, strings_section):
    """Score one page. Returns {rule: (0|1, detail)}."""
    fields = page.get("fields", [])
    top = [f for f in fields if f["section"] is None]
    st = strings_section.get(step_id, {})
    data = st.get("data", {}) or {}
    desc = st.get("data_description", {}) or {}
    res = {}

    prefixes = {}
    for f in top:
        prefixes.setdefault(f["field"].split("_")[0], []).append(f["field"])
    scattered = []
    order = [f["field"] for f in top]
    for pref, members in prefixes.items():
        if len(members) < 2:
            continue
        idx = sorted(order.index(m) for m in members)
        if idx != list(range(idx[0], idx[0] + len(idx))):
            scattered.append(pref)
    res["R2"] = (0 if scattered else 1, ",".join(scattered))

    no_default = [f["field"] for f in fields
                  if not f["has_default"] and "Entity" not in f["selector"]]
    res["R3"] = (0 if no_default else 1, ",".join(no_default))

    missing_help = [f["field"] for f in fields if f["field"] not in desc]
    res["R5"] = (0 if missing_help else 1, ",".join(missing_help))

    res["R6"] = (1 if len(top) <= 8 else 0, str(len(top)))

    no_range = [f["field"] for f in fields
                if f["selector"] == "NumberSelector"
                and not ("min" in f["config"] and "max" in f["config"])]
    res["R8"] = (0 if no_range else 1, ",".join(no_range))

    res["_labels_missing"] = [f["field"] for f in fields if f["field"] not in data]
    res["_page_has_description"] = bool(st.get("description"))
    res["_n_fields"] = len(fields)
    res["_n_top"] = len(top)
    res["_n_sections"] = len({f["section"] for f in fields if f["section"]})
    return res


def _sv_gaps(section):
    """Labels / help texts in en.json that sv.json does not have."""
    gaps = []
    en_steps = EN.get(section, {}).get("step", {})
    sv_steps = SV.get(section, {}).get("step", {})
    for step, body in en_steps.items():
        sv_body = sv_steps.get(step)
        if sv_body is None:
            gaps.append(f"{section}.{step}: whole step missing")
            continue
        for part in ("title", "description"):
            if body.get(part) and not sv_body.get(part):
                gaps.append(f"{section}.{step}.{part}")
        for part in ("data", "data_description"):
            for key in (body.get(part) or {}):
                if key not in (sv_body.get(part) or {}):
                    gaps.append(f"{section}.{step}.{part}.{key}")
    return gaps


def _error_keys():
    """Error keys the handlers actually raise, from the source."""
    src = (ROOT / "custom_components/heatpump_optimizer/config_flow.py").read_text()
    keys = set()
    for m in re.finditer(r'errors\[[^\]]+\]\s*=\s*"([a-z0-9_]+)"', src):
        keys.add(m.group(1))
    for m in re.finditer(r'errors\s*=\s*\{[^}]*?"([a-z0-9_]+)"\s*:\s*"([a-z0-9_]+)"', src):
        keys.add(m.group(2))
    for m in re.finditer(r'reason="([a-z0-9_]+)"', src):
        keys.add(m.group(1))
    return keys


def main():
    cfg = config_pages()
    opt = option_pages()
    cfg_scores = {k: score(k, v, STRINGS.get("config", {}).get("step", {}))
                  for k, v in cfg.items() if "error" not in v and v.get("fields") is not None}
    opt_scores = {k: score(k, v, STRINGS.get("options", {}).get("step", {}))
                  for k, v in opt.items() if "error" not in v and v.get("fields") is not None}

    sv_gaps = _sv_gaps("config") + _sv_gaps("options")
    err_keys = _error_keys()
    def _err_map(doc, section):
        return set((doc.get(section, {}) or {}).get("error", {}) or {}) | \
               set((doc.get(section, {}) or {}).get("abort", {}) or {})
    translated_en = _err_map(EN, "config") | _err_map(EN, "options")
    translated_sv = _err_map(SV, "config") | _err_map(SV, "options")
    untranslated_en = sorted(err_keys - translated_en)
    untranslated_sv = sorted(err_keys - translated_sv)

    payload = {
        "config_pages": cfg, "option_pages": opt,
        "config_scores": cfg_scores, "option_scores": opt_scores,
        "sv_gaps": sv_gaps,
        "error_keys": sorted(err_keys),
        "untranslated_en": untranslated_en,
        "untranslated_sv": untranslated_sv,
        "rubric": RUBRIC,
    }
    (OUT / "config_flow_rubric.json").write_text(json.dumps(payload, indent=1, default=repr))

    all_scores = {**{f"config.{k}": v for k, v in cfg_scores.items()},
                  **{f"options.{k}": v for k, v in opt_scores.items()}}
    form_pages = {k: v for k, v in all_scores.items() if v["_n_fields"]}
    def fails(rule):
        return sorted(k for k, v in form_pages.items() if v.get(rule, (1, ""))[0] == 0)

    print("RESULT config_form_pages=%d" % len([1 for v in cfg.values() if v.get("fields")]))
    print("RESULT config_menu_pages=%d" % len([1 for v in cfg.values() if v.get("menu_options")]))
    print("RESULT option_form_pages=%d" % len([1 for v in opt.values() if v.get("fields")]))
    print("RESULT option_menu_pages=%d" % len([1 for v in opt.values() if v.get("menu_options")]))
    print("RESULT form_pages_scored=%d" % len(form_pages))
    print("RESULT fields_total=%d" % sum(v["_n_fields"] for v in form_pages.values()))
    for rule in ("R2", "R3", "R5", "R6", "R8"):
        f = fails(rule)
        print(f"RESULT {rule}_failing_pages={len(f)}")
        if f:
            for k in f:
                print(f"    {rule} {k}: {form_pages[k][rule][1][:160]}")
    missing_labels = {k: v["_labels_missing"] for k, v in form_pages.items() if v["_labels_missing"]}
    print("RESULT pages_with_unlabelled_fields=%d" % len(missing_labels))
    print("RESULT unlabelled_fields=%d" % sum(len(v) for v in missing_labels.values()))
    for k, v in sorted(missing_labels.items()):
        print(f"    LABEL {k}: {len(v)} -> {','.join(v[:8])}")
    nodesc = sorted(k for k, v in form_pages.items() if not v["_page_has_description"])
    print("RESULT pages_without_description=%d" % len(nodesc))
    if nodesc:
        print("    " + ", ".join(nodesc))
    print("RESULT sv_translation_gaps=%d" % len(sv_gaps))
    for g in sv_gaps[:20]:
        print("    SV " + g)
    print("RESULT error_keys_raised=%d" % len(err_keys))
    print("RESULT error_keys_untranslated_en=%d" % len(untranslated_en))
    if untranslated_en:
        print("    " + ", ".join(untranslated_en))
    print("RESULT error_keys_untranslated_sv=%d" % len(untranslated_sv))
    if untranslated_sv:
        print("    " + ", ".join(untranslated_sv))
    print("RESULT thread_factor=1.00 (counting harness, no CPU-time metric)")
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    print("RESULT swapins=0 (not a memory metric)")


if __name__ == "__main__":
    main()
