"""Class sweep N-structure-blind (R10, D14 steps 3-4).

Lists every seam where a structure/dead-code/type metric measures a proxy
instead of the property it gates, over five seam rules taken from the R10
findings' seam_rule fields:

  A  budget key = max() over a unit table with no threshold-count sibling on
     the same table (a non-max unit grows unpriced)         [D7-s1-01]
  B  liveness decided by a name set rather than a resolved load
     (structure.py name_kept, HA_CONVENTION_NAMES)           [D7-s3-01]
  C  executable package source in a language no dead-code metric reads
                                                             [D7-s3-02]
  D  archscore predicate that string-matches an unparsed annotation
                                                             [D7-s3-52]
  E  archscore census seeded from a static key set, compared with runtime
                                                             [D7-s3-51]

Usage: PYTHONPATH=tests/hastub python3 enumerate.py [--null] [--perturb] [--probes]
Prints one SEAM line per seam and RESULT lines. --null runs rules A-D on a
clean fixture (expect 0). --perturb adds one count-over-threshold key on god_classes to an
in-memory copy of measure() (expect rule A instances 1 -> 0, total 5 -> 4). --probes runs the dynamic
probes for B and E and D (slow; ~3 min).
"""
from __future__ import annotations
import ast, pathlib, re, subprocess, sys, os

ROOT = pathlib.Path(__file__).resolve().parents[6]
PKG = ROOT / "custom_components/heatpump_optimizer"
STRUCT = ROOT / "tests/structure.py"
ARCH = ROOT / "tools/audit/archscore"
R3 = ROOT / "dev/audit/rounds/round10/D7"


def rule_a(src: str):
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "measure")
    d = next(n.value for n in ast.walk(fn) if isinstance(n, ast.Assign)
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "metrics")
    # names produced by table_maxima(monsters, cc_scores)
    tm = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and getattr(n.value.func, "id", "") == "table_maxima":
            for tgt, arg in zip(n.targets[0].elts, n.value.args):
                tm[tgt.id] = arg.id
    uses: dict[str, list[tuple[str, str]]] = {}
    for k, v in zip(d.keys, d.values):
        key = k.value
        if isinstance(v, ast.Name) and v.id in tm:
            uses.setdefault(tm[v.id], []).append((key, "max"))
            continue
        names = {x.id for x in ast.walk(v) if isinstance(x, ast.Name)}
        is_max = isinstance(v, ast.Call) and getattr(v.func, "id", "") == "max"
        for t in names & {"god_classes", "monsters", "cc_scores"}:
            uses.setdefault(t, []).append((key, "max" if is_max else "count"))
    out = []
    for table, ks in sorted(uses.items()):
        counts = [k for k, kind in ks if kind == "count"]
        for k, kind in ks:
            if kind == "max":
                out.append(("A", "tests/structure.py", f"measure:{k}", "instance" if not counts else "guarded",
                            f"table {table}; threshold siblings {counts or 'none'}"))
    return out


def rule_b():
    out = [("B", "tests/structure.py", "dead_members:name_kept", "instance",
            "name-kept members; probe namekept_sentinel.py NOPROD + namekept_receivers.py typed_hits=0")]
    src = STRUCT.read_text()
    names = ast.literal_eval(re.search(r"HA_CONVENTION_NAMES[^=]*=\s*(\{[^}]*\})", src, re.S).group(1))
    plat = re.search(r"PLATFORMS: Final = \[(.*?)\]", (PKG / "const.py").read_text(), re.S).group(1)
    loaded = {p.strip().strip('"') + ".py" for p in plat.split(",") if p.strip()}
    loaded |= {"__init__.py", "config_flow.py", "diagnostics.py", "repairs.py"}
    stray = []
    for p in sorted(PKG.rglob("*.py")):
        for n in ast.parse(p.read_text()).body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names and p.name not in loaded:
                stray.append(f"{p.name}:{n.name}")
    out.append(("B", "tests/structure.py", "HA_CONVENTION_NAMES", "instance" if stray else "guarded",
                f"convention-named defs outside HA-loaded modules: {stray or 0}"))
    return out


def rule_c(pkg=PKG):
    exts = {".js", ".mjs", ".ts", ".cjs"}
    return [("C", str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "dead_top_level_symbols(py only)",
             "instance", "structure.py rglob('*.py'); card_dead_fn.sh static-dead=1 (textWidth)")
            for p in sorted(pkg.rglob("*")) if p.suffix in exts]


def rule_d(files=None):
    files = files or sorted(ARCH.rglob("*.py"))
    out = []
    for f in files:
        tree = ast.parse(f.read_text())
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            args = {a.arg for a in fn.args.args}
            if not ({"ann"} & args):
                continue
            if any(isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "unparse" for c in ast.walk(fn)):
                rel = str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f)
                out.append(["D", rel, fn.name, None, ""])
    for s in out:
        if s[2] == "is_any":
            s[3], s[4] = "instance", "payload_any_spellings.py: Any|None, Optional[Any], 'Any', alias read 0 of 6"
        elif s[2] == "is_coord_annotation":
            # probe: every package Protocol class is a coordinator stand-in only if it ends in Coord
            prot = [n.name for p in PKG.rglob("*.py") for n in ast.walk(ast.parse(p.read_text()))
                    if isinstance(n, ast.ClassDef) and any(getattr(b, "id", "") == "Protocol" for b in n.bases)]
            miss = [n for n in prot if not n.endswith("Coord") and "Coordinator" in n]
            s[3], s[4] = ("instance" if miss else "guarded",
                          f"Protocols {prot}; coordinator stand-ins all end in Coord; misses={miss or 0}")
        else:
            s[3], s[4] = "not applicable", "unparse used for display only"
    return [tuple(s) for s in out]


def rule_e():
    return [("E", "tools/audit/archscore/metrics/untyped_payload_keys.py", "Flow.returned_keys (census seed)",
             "instance", "payload_census_coverage.py blind_keys=10 (AwayView)")]


def null_fixture():
    src = '''
def table_maxima(a, b): return 0, 0
def measure():
    monsters=[]; cc_scores=[]; god_classes=[]
    max_method_loc, max_cc = table_maxima(monsters, cc_scores)
    metrics = {"methods_over_150": len(monsters), "max_method_loc": max_method_loc,
               "max_cc": max_cc, "functions_cc_over_15": len(cc_scores),
               "classes_over_500": len(god_classes),
               "max_class_loc": max((g[0] for g in god_classes), default=0)}
'''
    import tempfile
    a = [s for s in rule_a(src) if s[3] == "instance"]
    with tempfile.TemporaryDirectory() as d:
        dp = pathlib.Path(d)
        (dp / "x.py").write_text("def f(ann):\n    return ann\n")
        c = rule_c(dp)
        dd = [s for s in rule_d([dp / "x.py"]) if s[3] == "instance"]
    return len(a) + len(c) + len(dd)


def main():
    if "--null" in sys.argv:
        print(f"RESULT null_fixture_instances={null_fixture()}")
        return
    src = STRUCT.read_text()
    if "--perturb" in sys.argv:
        # one line: price every god class, not only the largest
        src = src.replace('"methods_over_150": len(monsters),', '"methods_over_150": len(monsters), "god_classes_n": len(god_classes),', 1)
    seams = rule_a(src) + rule_b() + rule_c() + rule_d() + rule_e()
    for s in seams:
        print("SEAM", " | ".join(s))
    print(f"RESULT seams={len(seams)}")
    print(f"RESULT instances={sum(1 for s in seams if s[3] == 'instance')}")
    if "--probes" in sys.argv:
        env = dict(os.environ, PYTHONPATH="tests/hastub")
        for cmd in (["python3", str(R3 / "s3/namekept_sentinel.py")],
                    ["sh", str(R3 / "s3/card_dead_fn.sh")],
                    ["python3", str(R3 / "arch-s3/payload_census_coverage.py")],
                    ["python3", str(R3 / "arch-s3/payload_any_spellings.py")],
                    ["python3", str(R3 / "s1/class_growth.py")]):
            r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
            for l in r.stdout.splitlines():
                if l.startswith(("RESULT", "NOPROD")):
                    print("PROBE", pathlib.Path(cmd[-1]).name, l)


if __name__ == "__main__":
    main()
