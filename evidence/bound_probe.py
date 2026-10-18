"""Reviewer-built: attacks on the WAITING bound. usage: bound_probe.py <checkout> <scratchdir>"""
import importlib.util, json, sys, datetime, pathlib
root, tmp = sys.argv[1], pathlib.Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("ot", f"{root}/tools/audit/seat/orchestrator_tick.py")
ot = importlib.util.module_from_spec(spec); sys.modules["ot"] = ot; spec.loader.exec_module(ot)
def tick(checkout): return ot.Tick("o/r", str(checkout), gh=ot.Stub(), git=ot.Stub(), proc=ot.Stub(), now=ot.NOW)
def ago(m): return (ot.NOW - datetime.timedelta(minutes=m)).isoformat().replace("+00:00", "Z")
def co(val):
    d = tmp / f"co-{val!r}".replace("/", "_"); (d / "tests").mkdir(parents=True, exist_ok=True)
    (d / "tests" / "ci_budgets.json").write_text(val if isinstance(val, str) else json.dumps(val)); return d
t = tick(root); med = t.critical_median(); print(f"RESULT live median at checkout: {med}")
cases = [
 ("queued run, started_at null", root, {"c": {"status": "queued", "started_at": None}}),
 ("queued run, started_at missing", root, {"c": {"status": "queued"}}),
 ("in flight 100 min (< 2x median)", root, {"c": {"status": "in_progress", "started_at": ago(100)}}),
 ("in flight 115 min (> 2x median, legit slow sibling)", root, {"c": {"status": "in_progress", "started_at": ago(115)}}),
 ("stale low median 10 -> 30 min sibling", co({"critical_path_minutes": 10}), {"c": {"status": "in_progress", "started_at": ago(30)}}),
 ("stale high median 600 -> 10 h sibling", co({"critical_path_minutes": 600}), {"c": {"status": "in_progress", "started_at": ago(600)}}),
 ("median 0", co({"critical_path_minutes": 0}), {"c": {"status": "in_progress", "started_at": ago(5)}}),
 ("median as string '54'", co({"critical_path_minutes": "54"}), {"c": {"status": "in_progress", "started_at": ago(5)}}),
 ("budgets JSON is a list", co("[1]"), {"c": {"status": "in_progress", "started_at": ago(5)}}),
]
for label, c, latest in cases:
    try: w, a = tick(c).split_absent(["closures"], latest); out = "WAITING" if w else "ABSENT"
    except Exception as e: out = f"RAISES {type(e).__name__}: {str(e)[:60]}"
    print(f"RESULT {label}: {out}")
# ETA lane reader equivalence: old inline expression vs critical_median, truthiness
def old(c):
    try: return json.loads((pathlib.Path(c) / ot.CI_BUDGETS).read_text()).get("critical_path_minutes")
    except (OSError, ValueError): return None
for v in [{"critical_path_minutes": 54.8}, {"critical_path_minutes": 0}, {}, "not json", {"critical_path_minutes": None}]:
    c = co(v)
    try: n = tick(c).critical_median()
    except Exception as e: n = f"raises {type(e).__name__}"
    try: o = old(c)
    except Exception as e: o = f"raises {type(e).__name__}"
    print(f"RESULT ETA reader {v!r}: old={o!r} (unreadable={not o if not isinstance(o,str) else o}) new={n!r} (unreadable={not n if not isinstance(n,str) else n})")
