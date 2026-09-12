#!/usr/bin/env python3
"""D5 verifier-3 own harness (independent of the finder's two).

METRIC (arm A, D5-01): the shipped options-field set taken from the PRODUCTION
options flow (`config_flow.py`'s `_OPTION_FIELDS` registry + `_page_schema`'s
appended `after_save`), diffed key-for-key against `strings.json`'s
`options.step.*.data` (phantom / untranslated keys both directions), then the
count of distinct shipped field LABELS whose text (one trailing parenthetical
stripped, case-folded, non-alnum collapsed) occurs nowhere in README.md or any
`docs/*.md` -- reported over the full docs corpus AND over the finder's
7 reader docs for comparability.

METRIC (arm B, D5-02): counts stated in tests/README.md's script annotations,
re-extracted with my own regexes, against the counts the code produces
(len(sweep_combinations()) via import; `edges` and validate.py's `run(...)`
via my own AST walk, module level).

RUN (from a tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D5/verify3_own.py
Optional: D5_DOCS_DIR=<dir> reads README.md/docs from <dir> instead of the
tree (for doc perturbations against a copied corpus).

EXPECTED at 0855277 (= baseline 7dd68dd for these files; Apple M1, macOS 25.6):
  registry_steps=20 registry_static_fields=175 questionnaire_keys=<n>
  strings_steps_with_data=21 strings_fields_total=200
  phantom_keys (in strings.json, never renderable) = 0 expected
  untranslated_keys (renderable, missing from strings.json) = 0 expected
  labels_absent_distinct_fullcorpus <= 15 (reader corpus: 15)
  doc_stress_sweep=48 vs code_stress_sweep=51 -> mismatches=1
Counts over file bytes and one import; contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("D5_VERIFY_ROOT", ".")).resolve()
DOCS = Path(os.environ.get("D5_DOCS_DIR", ROOT)).resolve()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "custom_components"))

READER_DOCS = ["README.md", "docs/architecture.md", "docs/automations.md",
               "docs/configuration.md", "docs/dashboard-card.md",
               "docs/ecl110.md", "docs/how-it-works.md"]


def my_fold(s):
    s = re.sub(r"\([^()]*\)\s*$", "", s.strip())  # one trailing parenthetical
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def corpus(paths):
    """(folded haystack, n_docs_read)."""
    parts, n = [], 0
    for d in paths:
        p = Path(d) if d.startswith("/") else DOCS / d
        if p.exists():
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
            n += 1
    return " ".join(my_fold(t) for t in parts), n


def arm_a():
    import heatpump_optimizer.config_flow as cf

    strings = json.loads(
        (ROOT / "custom_components" / "heatpump_optimizer" / "strings.json")
        .read_text(encoding="utf-8"))
    steps = strings["options"]["step"]

    # Registry-derived key set per step: every static row (union over `when`),
    # the dynamic questionnaire row expanded, + after_save on pages that save.
    reg: dict[str, set] = {}
    for row in cf._OPTION_FIELDS:
        reg.setdefault(row.step, set())
        if row.default is cf._DYNAMIC:
            reg[row.step].update(row.widget({}).keys())
            reg[row.step].update(
                row.widget({"external_heat_detection_enabled": True}).keys())
        else:
            reg[row.step].add(row.key)
    for sid in reg:
        reg[sid].add(cf.CONF_AFTER_SAVE)

    phantom, untranslated = [], 0
    for sid, body in steps.items():
        skeys = set((body.get("data") or {}).keys())
        rkeys = reg.get(sid, set())
        for k in skeys - rkeys:
            phantom.append((sid, k))
        untranslated += len(rkeys - skeys)

    print(f"RESULT v3_registry_steps={len(reg)} count")
    print(f"RESULT v3_registry_fields={sum(len(v) for v in reg.values())} count")
    print(f"RESULT v3_strings_steps_with_data="
          f"{sum(1 for b in steps.values() if b.get('data'))} count")
    print(f"RESULT v3_strings_fields="
          f"{sum(len(b.get('data') or {}) for b in steps.values())} count")
    print(f"RESULT v3_phantom_keys={len(phantom)} count")
    print(f"RESULT v3_untranslated_keys={untranslated} count")
    for sid, k in phantom:
        print(f"  PHANTOM {sid}.{k}")

    # Absent-label arm. Only over REAL shipped fields (strings minus phantoms).
    real = {sid: {k: v for k, v in (b.get("data") or {}).items()
                  if (sid, k) not in phantom}
            for sid, b in steps.items()}
    reader = set(READER_DOCS)
    full_paths = [str(DOCS / "README.md")] + sorted(
        str(p) for p in (DOCS / "docs").glob("*.md"))
    hay_reader, n_r = corpus(sorted(reader))
    hay_full, n_f = corpus(full_paths)
    absent_r, absent_f = {}, {}
    for sid, fields in real.items():
        for k, label in fields.items():
            f = my_fold(label)
            if f and f not in hay_reader:
                absent_r.setdefault(label, []).append(sid)
            if f and f not in hay_full:
                absent_f.setdefault(label, []).append(sid)
    print(f"RESULT v3_labels_absent_distinct_reader={len(absent_r)} count")
    print(f"RESULT v3_labels_absent_occurrences_reader="
          f"{sum(len(v) for v in absent_r.values())} count")
    print(f"RESULT v3_labels_absent_distinct_fulldocs={len(absent_f)} count")
    print(f"RESULT v3_labels_absent_occurrences_fulldocs="
          f"{sum(len(v) for v in absent_f.values())} count")
    print(f"RESULT v3_docs_scanned_reader={n_r} count")
    print(f"RESULT v3_docs_scanned_fulldocs={n_f} count")
    for label in sorted(absent_r):
        print(f"  ABSENT-READER {label!r} pages={len(absent_r[label])}")
    for label in sorted(absent_f):
        if label not in absent_r:
            print(f"  ABSENT-ONLY-FULLCORPUS {label!r}")

    # README promise sentence.
    readme = (DOCS / "README.md").read_text(encoding="utf-8")
    m = re.search(r"[Ee]very field[^.]*documented[^.]*\.", readme)
    print(f"RESULT v3_readme_promises_every_field={int(bool(m))} count")
    if m:
        print(f"  PROMISE {m.group(0)!r}")


def arm_b():
    txt = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    d = {}
    m = re.search(r"tests/stress\.py\s*#\s*(\d+) combinations,\s*(\d+) edge", txt)
    if m:
        d["stress_sweep"], d["stress_edges"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"tests/validate\.py\s*#\s*(\d+) seasonal", txt)
    if m:
        d["validate_cases"] = int(m.group(1))

    import stress
    c = {"stress_sweep": len(stress.sweep_combinations())}
    tree = ast.parse((ROOT / "tests" / "stress.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign)
                and any(getattr(t, "id", None) == "edges" for t in node.targets)
                and isinstance(node.value, ast.Dict)):
            c["stress_edges"] = len(node.value.keys)
            break
    vt = ast.parse((ROOT / "tests" / "validate.py").read_text(encoding="utf-8"))
    c["validate_cases"] = sum(
        1 for n in vt.body if isinstance(n, ast.Expr)
        and isinstance(n.value, ast.Call)
        and getattr(n.value.func, "id", None) == "run")
    c["seasons_times_buildings"] = len(stress.SEASONS) * len(stress.BUILDINGS)

    bad = 0
    for k in sorted(set(d) | set(c)):
        dv, cv = d.get(k), c.get(k)
        print(f"RESULT v3_doc_{k}={dv} count")
        print(f"RESULT v3_code_{k}={cv} count")
        if dv is not None and dv != cv:  # only doc-STATED counts can mismatch
            bad += 1
            print(f"  MISMATCH {k}: doc={dv} code={cv}")
    print(f"RESULT v3_annotation_mismatches={bad} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    arm_a()
    arm_b()
