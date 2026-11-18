"""D6-s2 harness: every settings-table row in the docs against the real config flow.

Metric: count of documented settings-table rows (Setting | Default | Range/Choices)
whose default, min, max or step disagrees with the schema the real config flow
renders for the field of that label (tests/golden.py:capture_config_flow, which
drives heatpump_optimizer.config_flow's initial and options flows through FakeHass).
Key of the count: the value the production schema delivers (voluptuous default()
or suggested_value, NumberSelector config min/max/step), never the doc cell alone.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/config_tables.py
    add --perturb to patch each mismatching production field to its documented
    value in memory (config_flow._OPTION_FIELDS rows / module constants), which
    must drive RESULT config_rows_false to (or toward) zero.
Expected: see REPORT.md (exact; a count, contention-immune).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd() (measures the tree it is run from).
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))

_t0p, _t0t = time.process_time(), time.thread_time()

import golden  # noqa: E402

DOCS = ["docs/configuration.md", "docs/ecl110.md", "docs/automations.md",
        "docs/how-it-works.md", "docs/setup.md", "docs/dashboard-card.md",
        "docs/architecture.md"]

STRINGS = json.loads((ROOT / "custom_components/heatpump_optimizer/strings.json").read_text())


def norm(s):
    s = re.sub(r"\s*\((?:optional|recommended[^)]*|learned|kw/°c|kwh/°c|kw|writes[^)]*|nord pool[^)]*)\)\s*$", "", s, flags=re.I)
    s = re.sub(r"[`*]", "", s).lower()
    s = s.replace("’", "'").replace("–", "-")
    return re.sub(r"[^a-z0-9%/°]+", " ", s).strip()


def label_index():
    """norm(label) -> set of (flow, step, key)."""
    idx = {}

    def walk(flow, step, node):
        for key, lab in (node.get("data") or {}).items():
            idx.setdefault(norm(lab), set()).add((flow, step, key))
        for sec in (node.get("sections") or {}).values():
            walk(flow, step, sec)

    for flow in ("config", "options"):
        for step, node in STRINGS[flow]["step"].items():
            walk(flow, step, node)
    return idx


def flatten(fields, out):
    for key, m in fields.items():
        if "fields" in m:
            flatten(m["fields"], out)
        else:
            out[key] = m
    return out


def schema_index(pages):
    """(flow, step) -> {key: marker}."""
    idx = {}
    for step, fields in pages.items():
        if step.startswith("_"):
            continue
        idx[("options", step)] = flatten(fields, {})
    import heatpump_optimizer.config_flow as cf
    row_default = {}
    for row in cf._OPTION_FIELDS:
        if isinstance(row.default, (bool, int, float, str)) or row.default is None:
            row_default.setdefault(row.key, repr(row.default))
    for step, fields in pages["_seeded"].items():
        seeded = flatten(fields, {})
        base = idx.get(("options", step), {})
        for key, m in seeded.items():
            if key in base:
                continue
            # A field reached only by seeding: its seeded default is the seed,
            # not a default; take the registry row's plain default instead.
            base[key] = {**m, "default": row_default.get(key)}
        idx[("options", step)] = base
    for step, fields in pages["_initial"].items():
        if "menu" in fields:
            continue
        idx[("config", step)] = flatten(fields, {})
    return idx


def tables(path):
    """Yield (line, header, cells) for each body row of each table with a Default column."""
    lines = (ROOT / path).read_text().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|$", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip("|").split("|")]
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                cells = [c.strip() for c in lines[j].strip("|").split("|")]
                if "Default" in header:
                    yield j + 1, header, cells
                j += 1
            i = j
        else:
            i += 1


NUM = r"-?\d{1,3}(?: \d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?"

#: Doc labels that paraphrase the UI label (or name several fields): mapped to
#: the option key(s) by reading strings.json, not by value.
ALIASES = {
    "Weekend daytime / night comfort": ("weekend_comfort_temp_day", "weekend_comfort_temp_night"),
    "Holiday daytime / night comfort": ("holiday_comfort_temp_day", "holiday_comfort_temp_night"),
    "Tank heat loss": ("dhw_cooling_rate",),
    "Upper / lower floor thermal mass": ("upper_floor_thermal_mass", "lower_floor_thermal_mass"),
    "Upper / lower floor heat loss": ("upper_floor_heat_loss", "lower_floor_heat_loss"),
    "Inter-zone transfer": ("inter_zone_heat_transfer",),
    "Radiator power fraction": ("radiator_power_fraction",),
}


def fnum(s):
    try:
        return float(str(s).replace(" ", "").strip("'\""))
    except (TypeError, ValueError, AttributeError):
        return None


def check_row(path, line, header, cells, labels, schemas):
    row = dict(zip(header, cells))
    setting = row.get("Setting", cells[0])
    cands = set(labels.get(norm(setting), set()))
    bare = setting.strip("` ")
    if re.fullmatch(r"[a-z0-9_]+", bare):
        cands |= {(f, st, k) for (f, st), fields in schemas.items() for k in fields if k == bare}
    for alias in ALIASES.get(setting, ()):
        cands |= {(f, st, k) for (f, st), fields in schemas.items() for k in fields if k == alias}
    hits = []
    for flow, step, key in sorted(cands):
        m = schemas.get((flow, step), {}).get(key)
        if m is not None:
            hits.append((flow, step, key, m))
    rec = {"src": f"{path}:{line}", "setting": setting, "default_doc": row.get("Default"),
           "range_doc": row.get("Range") or row.get("Choices / range") or row.get("Choices")}
    if not hits:
        rec["verdict"] = "unmatched"
        return rec
    problems = []
    dd = row.get("Default", "")
    dnum = re.match(rf"^\s*({NUM})(?!\s*[–-]\s*\d)", dd.replace("`", "").replace("−", "-").replace("+", ""))
    rng = rec["range_doc"] or ""
    rm = re.match(rf"^\s*({NUM})\s*[–-]\s*({NUM})", rng)
    sm = re.search(rf"({NUM}) steps?", rng)
    seen = []
    compared = []
    alias = ALIASES.get(setting, ())
    parts = [x.strip() for x in dd.split(" / ")] if alias and " / " in dd else None
    for flow, step, key, m in hits:
        cfg = m.get("config") or {}
        if parts and key in alias and len(parts) == len(alias):
            dd_k = parts[alias.index(key)]
            if not re.search(r"[a-zA-Z°]", dd_k):
                dd_k += " " + parts[-1].split(" ", 1)[-1] if " " in parts[-1] else ""
            dnum = re.match(rf"^\s*({NUM})", dd_k)
        got_def = m.get("default")
        seen.append(f"{flow}/{step}/{key} default={got_def} min={cfg.get('min')} max={cfg.get('max')} step={cfg.get('step')}")
        prob = compare_default(dd, dnum, got_def, m, key)
        compared.append(_COMPARED.pop() if _COMPARED else False)
        if prob:
            problems.append(f"{flow}/{step}/{key}: default doc {prob}")
        if (rm and "min" in cfg) or (sm and "step" in cfg):
            compared.append(True)
        if rm and "min" in cfg:
            if abs(fnum(rm.group(1)) - fnum(cfg["min"])) > 1e-9 or abs(fnum(rm.group(2)) - fnum(cfg["max"])) > 1e-9:
                problems.append(f"{flow}/{step}/{key}: range doc {rm.group(1)}-{rm.group(2)} vs code {cfg['min']}-{cfg['max']}")
        if sm and "step" in cfg and abs(fnum(sm.group(1)) - fnum(cfg["step"])) > 1e-9:
            problems.append(f"{flow}/{step}/{key}: step doc {sm.group(1)} vs code {cfg['step']}")
    rec["code"] = seen
    rec["verdict"] = "false" if problems else ("true" if any(compared) else "unchecked")
    rec["problems"] = problems
    return rec


def select_label(m, value):
    cfg = m.get("config") or {}
    tk = (cfg.get("translation_key") or "").strip("'")
    opts = STRINGS.get("selector", {}).get(tk, {}).get("options", {})
    return opts.get(str(value).strip("'"))


_COMPARED = []


def compare_default(dd, dnum, got_def, m, key):
    """None when the documented default agrees with the delivered one, else a description."""
    _COMPARED.clear()
    _COMPARED.append(True)
    r = _compare_default(dd, dnum, got_def, m, key)
    return r


def _compare_default(dd, dnum, got_def, m, key):
    d = norm(dd)
    got = None if got_def is None else str(got_def).strip("'")
    if m.get("selector") == "SelectSelector" and got is not None:
        lab = select_label(m, got)
        if lab is not None:
            ok = d in (norm(lab), norm(got)) or norm(lab).startswith(d)
            return None if ok else f"'{dd}' vs code {got} ('{lab}')"
    if d in ("on", "off") and got in ("True", "False"):
        return None if (d == "on") == (got == "True") else f"'{dd}' vs code {got}"
    if d in ("none", "empty", "") or d.startswith("none") or d.startswith("empty"):
        return None if got in (None, "''", "", "None") else f"'{dd}' vs code {got}"
    tick = re.fullmatch(r"`([^`]*)`", dd.strip())
    if tick and got is not None:
        return None if tick.group(1) == got else f"'{dd}' vs code {got}"
    if dnum and fnum(got) is not None:
        want = fnum(dnum.group(1))
        if re.search(r"\bhours?\b", dd) and key.endswith("_minutes"):
            want *= 60
        return None if abs(want - fnum(got)) <= 1e-9 else f"{dnum.group(1)} vs code {got_def}"
    _COMPARED[:] = [False]
    return None


PERTURB_ROWS = {}  # filled by --perturb: key -> dict(default=..., min=..., max=..., step=...)


def apply_perturbation(recs):
    """Patch production rows to the documented values, in memory, then re-capture."""
    from unittest import mock
    import heatpump_optimizer.config_flow as cf
    wanted = {}
    for r in recs:
        for p in r.get("problems", []):
            m = re.match(r"^(\w+)/(\w+)/(\w+): (default|range|step) doc (\S+) vs", p)
            if m:
                wanted.setdefault(m.group(3), {})[m.group(4)] = m.group(5)
    rows = list(cf._OPTION_FIELDS)
    for i, row in enumerate(rows):
        if row.key not in wanted:
            continue
        w = wanted[row.key]
        new = row
        if "default" in w and not callable(getattr(row.default, "of", None)) and isinstance(row.default, (int, float)):
            new = new._replace(default=float(w["default"]))
        widget = new.widget
        if hasattr(widget, "config") and ("range" in w or "step" in w):
            cfg = dict(widget.config)
            if "range" in w:
                lo, hi = w["range"].split("-") if w["range"].count("-") == 1 else (None, None)
                if lo is not None:
                    cfg["min"], cfg["max"] = float(lo), float(hi)
            if "step" in w:
                cfg["step"] = float(w["step"])
            new = new._replace(widget=type(widget)(type(widget.config)(**cfg)) if hasattr(type(widget), "__init__") else widget)
        rows[i] = new
    return mock.patch.object(cf, "_OPTION_FIELDS", tuple(rows)), wanted


def run():
    pages = golden.capture_config_flow()
    labels = label_index()
    schemas = schema_index(pages)
    recs = []
    for path in DOCS:
        if not (ROOT / path).exists():
            continue
        for line, header, cells in tables(path):
            recs.append(check_row(path, line, header, cells, labels, schemas))
    return pages, recs


def main():
    pages, recs = run()
    if "--perturb" in sys.argv:
        patcher, wanted = apply_perturbation(recs)
        with patcher:
            pages, recs = run()
        print(f"# perturbation applied to {len(wanted)} option-flow keys: {sorted(wanted)}")
    for r in recs:
        print(f"{r['verdict']:9s} {r['src']:32s} {r['setting'][:48]:48s} "
              + ("; ".join(r.get("problems", [])) if r["verdict"] == "false" else ""))
    # structural claims of configuration.md
    menu = pages["_menu"]
    print("RESULT option_pages=%d count" % sum(1 for k in pages if not k.startswith("_")))
    print("RESULT first_menu_pages=%d count" % sum(1 for k, _ in menu["init"] if k != "advanced"))
    print("RESULT advanced_menu_pages=%d count" % len(menu["advanced"]))
    n = len(recs)
    print(f"RESULT config_rows_total={n} count")
    print(f"RESULT config_rows_matched={sum(r['verdict'] != 'unmatched' for r in recs)} count")
    print(f"RESULT config_rows_true={sum(r['verdict'] == 'true' for r in recs)} count")
    print(f"RESULT config_rows_false={sum(r['verdict'] == 'false' for r in recs)} count")
    print(f"RESULT config_rows_unchecked={sum(r['verdict'] == 'unchecked' for r in recs)} count")
    print(f"RESULT config_rows_unmatched={sum(r['verdict'] == 'unmatched' for r in recs)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")
    out = os.environ.get("D6_TABLE_JSON")
    if out:
        Path(out).write_text(json.dumps(recs, indent=1))


if __name__ == "__main__":
    main()
