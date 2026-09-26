#!/usr/bin/env python3
"""D7 verify-v3 (D7-s1-01): the reverse of the finder's move. Outline a
coordinator method into a module-level ``_name(coord, ...)`` called as
``_name(self, ...)`` and measure what tests/structure.py:measure() charges.

Metric (one line): over every eligible coordinator method (sync, undecorated,
referenced in coordinator.py only as ``self.<name>(``, no ``super``), the count
whose outlining LOWERS sum(cut_*)+cross_seam_edges, and the summed fall.
Count key: structure.measure()['metrics'] on the transformed copy minus the
untouched copy (the production seam is the ratchet; the harness only moves
text between two shapes that execute identically).
Also prints the seam census: module-level functions package-wide whose first
parameter is ``coord`` and their ``coord.<attr>`` loads (none priced).

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/verify-v3/outline_reward.py [--limit N]
Null control: a method whose body crosses no seam outlines at delta 0
(outline_neutral); the perturbation is the finder's own reverse arm
(helper_escape.py inlines, this outlines) -- the two must move in opposite directions.
Expected at 1936d5ca + round-9 evidence (exact counts): census 52/92,
eligible 108, rewarded 83, neutral 24, rose 1, total_fall 513.
Machine: cloud container linux x86_64 (4 cores, shared). Writes only under tempfile.mkdtemp().
"""
from __future__ import annotations
import os
for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")
import argparse, ast, json, re, shutil, sys, tempfile, time  # noqa: E401,E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import structure  # noqa: E402

PKG = Path("custom_components/heatpump_optimizer")
CLS = structure.COORDINATOR_CLASS_NAME


def copy_tree(dst: Path) -> None:
    shutil.copytree(ROOT / PKG, dst / PKG)
    (dst / "tests").mkdir(parents=True)
    shutil.copy(ROOT / "tests" / "seam_map.json", dst / "tests" / "seam_map.json")


def measure_at(root: Path) -> dict:
    structure.REPO_ROOT = root
    structure.PACKAGE_DIR = root / PKG
    structure.SEAM_MAP_FILE = root / "tests" / "seam_map.json"
    return structure.measure()["metrics"]


def cut(m: dict) -> int:
    return sum(v for k, v in m.items() if k.startswith("cut_") or k == "cross_seam_edges")


def eligible(src: str) -> list[str]:
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLS)
    out = []
    for m in cls.body:
        if not isinstance(m, ast.FunctionDef) or m.decorator_list or m.name.startswith("__"):
            continue
        if not m.args.args or m.args.args[0].arg != "self":
            continue
        body = ast.get_source_segment(src, m) or ""
        if "super(" in body or "__class__" in body:
            continue
        uses = len(re.findall(rf"(?<![\w]){re.escape(m.name)}(?!\w)", src))
        calls = len(re.findall(rf"self\.{re.escape(m.name)}\(", src))
        if calls and uses == calls + 1:  # the def plus call sites only
            out.append(m.name)
    return out


def outline(root: Path, name: str) -> None:
    path = root / PKG / "coordinator.py"
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLS)
    fn = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == name)
    body = lines[fn.lineno - 1:fn.end_lineno]
    body = [re.sub(r"\bself\b", "coord", ln) for ln in body]
    body = [ln[4:] if ln.startswith("    ") else ln for ln in body]
    rest = lines[:fn.lineno - 1] + lines[fn.end_lineno:]
    text = "".join(rest).rstrip("\n") + "\n\n\n" + "".join(body)
    text = re.sub(rf"self\.{re.escape(name)}\(\)", f"{name}(self)", text)
    text = re.sub(rf"self\.{re.escape(name)}\(", f"{name}(self, ", text)
    ast.parse(text)
    path.write_text(text)
    sf = root / "tests" / "seam_map.json"
    doc = json.loads(sf.read_text())
    doc["seams"].pop(name, None)
    sf.write_text(json.dumps(doc))


def census() -> tuple[int, int]:
    fns = refs = 0
    for f in sorted((ROOT / PKG).glob("*.py")):
        for d in ast.parse(f.read_text()).body:
            if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)) and d.args.args \
                    and d.args.args[0].arg == "coord":
                fns += 1
                refs += sum(1 for m in ast.walk(d) if isinstance(m, ast.Attribute)
                            and isinstance(m.value, ast.Name) and m.value.id == "coord"
                            and m.attr != "_ctx")
    return fns, refs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    fns, refs = census()
    print(f"RESULT census_coord_param_functions={fns} count")
    print(f"RESULT census_coord_attr_loads={refs} count")
    tmp = Path(tempfile.mkdtemp(prefix="d7v3_outline_"))
    try:
        base = tmp / "base"
        copy_tree(base)
        m0 = measure_at(base)
        names = eligible((base / PKG / "coordinator.py").read_text())
        if a.limit:
            names = names[: a.limit]
        rewarded = fall = neutral = rose = errs = 0
        for n in names:
            cell = tmp / f"c_{n}"
            copy_tree(cell)
            try:
                outline(cell, n)
                m = measure_at(cell)
            except Exception as e:  # noqa: BLE001
                errs += 1
                print(f"  cell {n}: error {type(e).__name__}")
                shutil.rmtree(cell, ignore_errors=True)
                continue
            d = cut(m) - cut(m0)
            print(f"  cell {n}: cut_delta={d:+d}")
            if d < 0:
                rewarded += 1
                fall += -d
            elif d == 0:
                neutral += 1
            else:
                rose += 1
            shutil.rmtree(cell, ignore_errors=True)
        print(f"RESULT eligible_methods={len(names)} count")
        print(f"RESULT outline_rewarded={rewarded} count")
        print(f"RESULT outline_neutral={neutral} count")
        print(f"RESULT outline_rose={rose} count")
        print(f"RESULT outline_errors={errs} count")
        print(f"RESULT outline_total_fall={fall} count")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "n/a")
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
