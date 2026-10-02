"""Reviewer's own instrument (not the finder's, not the fixer's): check every
value in tests/golden/coord_*.json `data` against payload.Payload at runtime.
JSON loses datetime (str accepted for datetime, noted) and tuple (list)."""
import json, sys, types, typing, datetime, glob, importlib.util, collections
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("payload", f"{root}/custom_components/heatpump_optimizer/payload.py")
m = importlib.util.module_from_spec(spec); sys.modules["payload"] = m; spec.loader.exec_module(m)
P = m.Payload
problems = collections.defaultdict(set); notes = collections.defaultdict(set)
def is_td(t): return isinstance(t, type) and typing.is_typeddict(t)
def check(v, t, path, fx):
    o = typing.get_origin(t); a = typing.get_args(t)
    if t is object: return
    if o in (typing.Union, types.UnionType):
        errs = []
        for alt in a:
            sub = collections.defaultdict(set)
            if _ok(v, alt, path, fx): return
        problems[path].add(f"{fx}: {type(v).__name__}={str(v)[:60]} not in {t}"); return
    if t is type(None):
        if v is not None: problems[path].add(f"{fx}: expected None got {type(v).__name__}")
        return
    if v is None:
        problems[path].add(f"{fx}: None but declared {getattr(t,'__name__',t)}"); return
    if is_td(t):
        if not isinstance(v, dict): problems[path].add(f"{fx}: {type(v).__name__} not dict for {t.__name__}"); return
        hints = typing.get_type_hints(t)
        for k, vv in v.items():
            if k not in hints: problems[f"{path}.{k}"].add(f"{fx}: key not declared in {t.__name__}"); continue
            check(vv, hints[k], f"{path}.{k}", fx)
        return
    if t is datetime.datetime:
        if isinstance(v, str): notes[path].add("str (JSON-serialised datetime)"); return
        if not isinstance(v, datetime.datetime): problems[path].add(f"{fx}: {type(v).__name__} for datetime")
        return
    if t is float:
        if isinstance(v, bool) or not isinstance(v, (int, float)): problems[path].add(f"{fx}: {type(v).__name__}={str(v)[:40]} for float")
        return
    if t is int:
        if isinstance(v, bool) or not isinstance(v, int): problems[path].add(f"{fx}: {type(v).__name__}={str(v)[:40]} for int")
        return
    if t in (str, bool):
        if type(v) is not t: problems[path].add(f"{fx}: {type(v).__name__}={str(v)[:40]} for {t.__name__}")
        return
    if o is list:
        if not isinstance(v, list): problems[path].add(f"{fx}: {type(v).__name__} for list"); return
        for i, x in enumerate(v): check(x, a[0], path + "[]", fx)
        return
    if o is dict:
        if not isinstance(v, dict): problems[path].add(f"{fx}: {type(v).__name__} for dict"); return
        for k, x in v.items(): check(x, a[1], path + "{}", fx)
        return
    problems[path].add(f"{fx}: unhandled type {t}")
def _ok(v, t, path, fx):
    before = sum(len(s) for s in problems.values())
    snap = {k: set(s) for k, s in problems.items()}
    check(v, t, path, fx)
    after = sum(len(s) for s in problems.values())
    if after != before:
        problems.clear(); problems.update({k: s for k, s in snap.items()}); return False
    return True
hints = typing.get_type_hints(P)
missing = collections.defaultdict(list); allnone = collections.Counter(); seen = collections.Counter()
for f in sorted(glob.glob(f"{root}/tests/golden/coord_*.json")):
    fx = f.split("coord_")[1][:-5]
    d = json.load(open(f))["data"]
    for k, v in d.items():
        if k not in hints: missing[k].append(fx); continue
        seen[k] += 1
        if v is None: allnone[k] += 1
        check(v, hints[k], k, fx)
print("RESULT payload_keys", len(hints))
print("RESULT golden_keys_missing_from_Payload", len(missing), dict(missing))
print("RESULT payload_keys_absent_from_all_goldens", sorted(set(hints) - set(seen)))
print("RESULT keys_None_in_every_golden_they_appear", sum(1 for k in seen if allnone[k] == seen[k]))
print("RESULT type_mismatch_paths", len(problems))
for p in sorted(problems): print("  MISMATCH", p, sorted(problems[p]))
for p in sorted(notes): print("  NOTE", p, sorted(notes[p]))
