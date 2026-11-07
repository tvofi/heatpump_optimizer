import sys, importlib.util, pathlib
p = sys.argv[1]
spec = importlib.util.spec_from_file_location("oi", p); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(pathlib.Path(p).parent)); spec.loader.exec_module(m)
import inspect
t = m.Thread(3225, "issue") if len(inspect.signature(m.Thread.__init__).parameters) == 3 else m.Thread(3225)
t.saw("Bankaifan", "2026-11-06T10:00:00Z")
t.mark({"login": "hpo-approver[bot]", "type": "Bot", "at": "2026-11-06T12:00:00Z", "answered": True})
t.mark({"login": sys.argv[2], "type": sys.argv[3], "at": "2026-11-06T14:00:00Z"})
print(f"{sys.argv[2]}/{sys.argv[3]} owed={m.owed(t, {3225: 'R10-COMBI-TANK'}, True)}")
