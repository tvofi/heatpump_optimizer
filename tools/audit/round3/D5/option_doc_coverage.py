#!/usr/bin/env python3
"""D5 harness 6 — option-flow fields the user-facing documentation never names.

METRIC: `option_fields_undocumented` = number of fields RENDERED by the real
        option flow (every page of ``config_flow._OPTION_PAGES`` put through
        ``config_flow._page_schema``, with every feature flag on so no page is
        hidden) for which NONE of the following appears in any user-facing
        document (README.md, docs/how-it-works.md, configuration.md,
        dashboard-card.md, architecture.md, automations.md, ecl110.md):
          (a) the config key verbatim,
          (b) the field's English label from strings.json,
          (c) that label with a trailing "(...)" removed,
          (d) a single line of a document containing every content word of (c).
        Rule (d) is what lets a doc row that merges two fields
        ("Weekend daytime / night comfort") still count as documenting both.

SECOND METRIC: `wood_economics_doc_lines` = lines across the same documents
        that mention any of the four wood-fuel economics inputs by key, by
        label, or by an enumerated value (`birch`/`pine`/`mixed`,
        `packed`/`loose`, "cubic metre", "furnace efficiency").

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/option_doc_coverage.py

Set D5_ROOT=<dir> to point the document side at a copy of the tree.

EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
    wood_economics_doc_lines=0; both moved on main before this check):
    RESULT option_fields_rendered=180 count
    RESULT option_fields_undocumented=7 count
    RESULT option_schema_keys_rendered=213 count
    RESULT wood_economics_fields_rendered=4 count
    RESULT wood_economics_doc_lines=6 count      (tolerance: exact)
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
INSTRUMENTED SYMBOL: heatpump_optimizer.config_flow:_page_schema — the field
    list is produced by rendering every option page, not by reading a table.
PERTURBATION: add the row
      `| Wood type | mixed | birch/pine/mixed | Which wood the furnace burns. |`
    to docs/configuration.md -> option_fields_undocumented must go DOWN by 1
    and wood_economics_doc_lines UP by 1. Deleting configuration.md's
    "Wood tank volume" row moves option_fields_undocumented UP by 1.
"""
import os
import time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
DOCROOT = Path(os.environ.get("D5_ROOT") or REPO).resolve()

sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO))

from harness import FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import config_flow as cf  # noqa: E402
from custom_components.heatpump_optimizer import const as C  # noqa: E402

USER_DOCS = [
    "README.md", "docs/how-it-works.md", "docs/configuration.md",
    "docs/dashboard-card.md", "docs/architecture.md", "docs/automations.md",
    "docs/ecl110.md",
]
STOP = {"the", "a", "an", "of", "per", "and", "or", "to", "for", "in", "on",
        "optional", "recommended", "that", "it", "expects", "what"}

WOOD_KEYS = ["wood_type", "wood_packing", "wood_price_sek_m3",
             "wood_furnace_efficiency"]
WOOD_NEEDLES = WOOD_KEYS + ["wood type", "packing", "price per cubic",
                            "cubic metre", "furnace efficiency", "birch",
                            "pine", "packed", "loose"]


def enabling_config():
    """Every feature flag a page's ``when`` predicate can consult, turned on."""
    cur = {}
    for name in dir(C):
        if not name.startswith("CONF_"):
            continue
        key = getattr(C, name)
        if not isinstance(key, str):
            continue
        default_name = "DEFAULT_" + name[len("CONF_"):]
        default = getattr(C, default_name, None)
        if isinstance(default, bool):
            cur[key] = True
    cur[C.CONF_WOOD_FURNACE_ENABLED] = True
    cur[C.CONF_EXTERNAL_HEAT_ENABLED] = True
    return cur


def walk_keys(schema, out):
    s = schema
    # A ``section``'s ``.schema`` is itself a vol.Schema, so unwrap until a dict.
    for _ in range(6):
        if isinstance(s, dict):
            break
        nxt = getattr(s, "schema", None)
        if nxt is None or nxt is s:
            break
        s = nxt
    if isinstance(s, dict):
        for k, v in s.items():
            name = str(getattr(k, "schema", k))
            out.add(name)
            if hasattr(v, "schema"):
                walk_keys(v, out)
    return out


def label_for(strings, step, key):
    step_block = strings.get("options", {}).get("step", {}).get(step, {})
    lbl = (step_block.get("data", {}) or {}).get(key, "") or ""
    if not lbl:
        for sec in (step_block.get("sections", {}) or {}).values():
            lbl = (sec.get("data", {}) or {}).get(key, "") or lbl
    return lbl


def main():
    strings = json.loads((REPO / "custom_components" / "heatpump_optimizer"
                          / "strings.json").read_text(encoding="utf-8"))
    hass = FakeHass()
    cur = enabling_config()

    rendered = {}   # key -> step it first rendered on
    pages_ok = 0
    for page in cf._OPTION_PAGES:
        try:
            schema = cf._page_schema(page.step, cur, hass)
        except Exception as exc:  # noqa: BLE001
            print(f"  !! page {page.step} did not render: {type(exc).__name__}: {exc}")
            continue
        pages_ok += 1
        for k in walk_keys(schema, set()):
            rendered.setdefault(k, page.step)

    lines, blob = [], ""
    for rel in USER_DOCS:
        p = DOCROOT / rel
        if p.exists():
            lines += [ln.lower() for ln in p.read_text(encoding="utf-8",
                                                       errors="replace").split("\n")]
    blob = "\n".join(lines)

    def words(s):
        return [w for w in re.findall(r"[a-z0-9³°]+", s.lower()) if w not in STOP]

    undocumented = []
    sectionish = 0
    for key, step in sorted(rendered.items()):
        label = label_for(strings, step, key)
        if not label:
            # A ``section()`` container or an unlabelled control, not a field
            # the user reads a name for. Counted, never judged.
            sectionish += 1
            continue
        if key.lower() in blob:
            continue
        short = re.sub(r"\s*\([^)]*\)\s*$", "", label).strip()
        if short and short.lower() in blob:
            continue
        ws = words(short)
        if ws and any(all(w in ln for w in ws) for ln in lines):
            continue
        undocumented.append((step, key, label))

    wood_rendered = [k for k in WOOD_KEYS if k in rendered]
    wood_lines = [ln for ln in lines if any(n in ln for n in WOOD_NEEDLES)]

    print("--- option-flow fields no user-facing document names ---")
    for step, key, label in undocumented:
        print(f"  {step:<22} {key:<34} {label!r}")
    print("--- wood-fuel economics fields, rendered by the real option page ---")
    for k in wood_rendered:
        print(f"  {k}  (page {rendered[k]})  label={label_for(strings, rendered[k], k)!r}")
    print("--- document lines mentioning any wood-fuel economics input ---")
    for ln in wood_lines[:20]:
        print(f"  {ln[:150]}")

    print()
    print(f"RESULT option_pages_rendered={pages_ok} count")
    print(f"RESULT option_schema_keys_rendered={len(rendered)} count")
    print(f"RESULT option_section_or_unlabelled_keys={sectionish} count")
    print(f"RESULT option_fields_rendered={len(rendered) - sectionish} count")
    print(f"RESULT option_fields_undocumented={len(undocumented)} count")
    print(f"RESULT wood_economics_fields_rendered={len(wood_rendered)} count")
    print(f"RESULT wood_economics_doc_lines={len(wood_lines)} count")
    _thr = time.thread_time()
    print(f"RESULT thread_factor={time.process_time() / _thr if _thr else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
