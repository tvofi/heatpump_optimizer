import sys, types, importlib.util
spec = importlib.util.spec_from_file_location("ot", "tools/audit/seat/orchestrator_tick.py")
ot = importlib.util.module_from_spec(spec); sys.modules["ot"] = ot; spec.loader.exec_module(ot)
cls = next(c for c in vars(ot).values() if isinstance(c, type) and hasattr(c, "relay_owed"))
log = sys.argv[1]
s = types.SimpleNamespace(relay_log=log, out=[])
s.line = lambda S, t, flag=False: s.out.append(t)
s.unreadable = lambda *a: s.out.append("UNREADABLE")
cls.relay_owed(s, "S")
print(len(s.out)); [print(" ", x) for x in s.out]
