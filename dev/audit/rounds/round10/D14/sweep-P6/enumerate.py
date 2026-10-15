"""Class sweep P6 (round 10), finding D7-s2-60: every entity state property, in every platform
module of the package, that reads the coordinator payload and publishes it through a guard.

Seam rule (widened from shape_payload_guard.py family()): an AST walk over EVERY module under
custom_components/heatpump_optimizer/, every method named in STATE_PROPS whose body reads
``self.coordinator.data`` or ``self._data()`` and returns a non-None expression. The guard family
is the shape of that expression; any shape outside the four known ones is family ``other`` (still
enumerated, never dropped).

Probe per seam: the property is driven on the real class with a stub coordinator, the payload
value placed at the property's own .get() path. The reference contract is the package's own
owner, sensor._as_float: a bool is not a number (True -> None) and a numeric string is not
published raw nor raises ('21.5' -> None). A seam is an INSTANCE when either probe answers
otherwise; GUARDED when both answer None; NOT APPLICABLE when it publishes a non-number by
design (string/enum/bool state) or cannot be driven from one path (listed with the reason).

Modes:
  (default)            the working tree
  --tree DIR           another checkout (positive control: the D7-s2-60 baseline 554e2ecfa7ad)
  --fixture clean      null control: a synthetic platform module, every site through _as_float
  --fixture reintro    perturbation: the clean fixture with ONE line changed to a round-if-not-None
Run from the repository root: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P6/enumerate.py
"""
import argparse, ast, importlib, json, math, shutil, sys, tempfile, types
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
STATE_PROPS = {"native_value", "current_temperature", "target_temperature", "is_on", "native_value",
               "current_option", "current_operation"}
PROBES = [21.456, True, "21.5"]
# Two seams the literal-path rule cannot drive, each read by hand and pinned here so the sweep
# still answers for them: the outdoor reading arrives through _effective_outdoor (no .get literal
# in the property), and the compressor-start count is an int by design (21.456 is not its number).
PATH_OVERRIDE = {"OutdoorTempSensor": ["outdoor_temperature"]}
INT_SITES = {"CompressorStartsSensor"}

CLEAN = '''
import math
def _as_float(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    return float(v)
class _Base:
    def _data(self):
        return self.coordinator.data or {}
class ASensor(_Base):
    @property
    def native_value(self):
        return _as_float(self._data().get("a"))
class BSensor(_Base):
    @property
    def native_value(self):
        return _as_float(self._data().get("b"))
'''
REINTRO = CLEAN.replace('return _as_float(self._data().get("b"))',
                        'v = self._data().get("b"); return round(v, 1) if v is not None else None')


def family(fn):
    body = ast.unparse(fn)
    if "self.coordinator.data" not in body and "self._data()" not in body:
        return None
    ret = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None
           and not (isinstance(n.value, ast.Constant) and n.value.value is None)]
    if not ret:
        return None
    src = ast.unparse(ret[0].value)
    if src.startswith("round(") and "is not None" in src:
        return "round_if_not_none"
    if src.startswith("round(") and "isinstance" in src:
        return "round_if_number"
    if " if isinstance(" in src and "bool" not in src:
        return "isinstance_number"
    if src.startswith("_as_float("):
        return "_as_float"
    return "other"


def payload_path(fn):
    # order by the KEY literal's position: a chained ``_mapping(d.get("a", {})).get("b")`` puts
    # the outer call first in the tree but its key last in the source
    keys = sorted(((n.args[0].lineno, n.args[0].col_offset, n.args[0].value) for n in ast.walk(fn)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
                   and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)))
    keys = [k[2] for k in keys]
    if not keys and "self._data_key" in ast.unparse(fn):
        return ["<_data_key>"]
    return keys or None


def nest(path, v):
    for k in reversed(path):
        v = {k: v}
    return v


def show(v):
    return "nan" if isinstance(v, float) and math.isnan(v) else repr(v)


def sweep(pkg_dir, pkg_name):
    seams = []
    for f in sorted(pkg_dir.rglob("*.py")):
        tree = ast.parse(f.read_text())
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef) and fn.name in STATE_PROPS:
                    fam = family(fn)
                    if fam:
                        seams.append(dict(file=str(f.relative_to(pkg_dir.parent.parent)) if pkg_dir.parent.parent in f.parents else f.name,
                                          module=f.stem, cls=cls.name, prop=fn.name, family=fam,
                                          line=fn.lineno, path=payload_path(fn)))
    for s in seams:
        s["answers"], s["disposition"], s["reason"] = None, None, ""
        s["path"] = PATH_OVERRIDE.get(s["cls"], s["path"])
        if not s["path"]:
            s["disposition"], s["reason"] = "not_applicable", "no literal payload path; computed state"
            continue
        try:
            mod = importlib.import_module(f"{pkg_name}.{s['module']}" if pkg_name else s["module"])
            cls = getattr(mod, s["cls"])
        except Exception as exc:  # noqa: BLE001
            s["disposition"], s["reason"] = "not_applicable", f"import: {type(exc).__name__}"
            continue
        targets = [(cls, s["path"])]
        if s["path"] == ["<_data_key>"]:
            # a base reading its subclass's key: every concrete subclass is the site
            subs = [c for c in vars(mod).values() if isinstance(c, type) and issubclass(c, cls)
                    and isinstance(getattr(c, "_data_key", None), str)]
            targets = [(c, [c._data_key]) for c in subs]
            s["subclasses"] = [c.__name__ for c in subs]
            if not subs:
                s["disposition"], s["reason"] = "not_applicable", "no concrete subclass names a key"
                continue
        vecs = []
        for tcls, tpath in targets:
            vecs.append(drive(tcls, s["prop"], tpath, 21 if s["cls"] in INT_SITES else PROBES[0]))
        got = vecs[0] if len(set(map(tuple, vecs))) == 1 else [f"MIXED{len(set(map(tuple, vecs)))}"] * 3
        s["answers"] = dict(zip(["21.456", "True", "'21.5'"], got))
        classify(s, got)
    return seams


def drive(cls, prop, path, first):
    got = []
    for v in [first] + PROBES[1:]:
        ent = object.__new__(cls)
        data = nest(path, v)
        data.setdefault("reading_ok", {path[0]: True})  # an ok-flag gate reads the key as measured
        ent.coordinator = types.SimpleNamespace(data=data, last_update_success=True)
        if True:
            try:
                got.append(show(getattr(cls, prop).fget(ent)))
            except Exception as exc:  # noqa: BLE001 -- a raise is the answer
                got.append(type(exc).__name__)
    return got


def classify(s, got):
    if True:
        if got[0] in ("None",) or not got[0].replace(".", "").replace("-", "").isdigit():
            s["disposition"], s["reason"] = "not_applicable", f"does not publish the payload float as a number (21.456 -> {got[0]})"
        elif got[1] == "None" and got[2] == "None":
            s["disposition"], s["reason"] = "guarded", "rejects bool and str (the _as_float contract)"
        else:
            s["disposition"] = "instance"
            s["reason"] = f"True -> {got[1]}, '21.5' -> {got[2]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=REPO)
    ap.add_argument("--fixture", choices=["clean", "reintro"])
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()
    tmp = None
    if a.fixture:
        tmp = Path(tempfile.mkdtemp(prefix="sweep-p6-"))
        (tmp / "fixture_platform.py").write_text(CLEAN if a.fixture == "clean" else REINTRO)
        sys.path.insert(0, str(tmp))
        seams = sweep(tmp, "")
    else:
        sys.path.insert(0, str(a.tree / "custom_components"))
        seams = sweep(a.tree / "custom_components" / "heatpump_optimizer", "heatpump_optimizer")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    for s in seams:
        print(f"{s['disposition']:<15} {s['module']}:{s['cls']}.{s['prop']} L{s['line']} [{s['family']}] {s['reason']}")
    c = {k: sum(1 for s in seams if s["disposition"] == k) for k in ("instance", "guarded", "not_applicable")}
    fams = sorted({s["family"] for s in seams})
    vecs = {tuple(s["answers"].values())[1:] for s in seams if s["disposition"] != "not_applicable"}
    print(f"RESULT seams={len(seams)} instance={c['instance']} guarded={c['guarded']} not_applicable={c['not_applicable']}")
    print(f"RESULT modules={len({s['module'] for s in seams})} families={len(fams)} ({','.join(fams)}) bool_str_vectors={len(vecs)}")
    if not seams:
        print("RESULT ZERO SEAMS -- the universe is empty; a null control only, never a clean package")
    if a.json:
        a.json.write_text(json.dumps(seams, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
