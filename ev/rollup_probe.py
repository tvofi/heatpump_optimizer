import sys, importlib.util
sys.path.insert(0, "/home/user/heatpump_optimizer/tools/audit/seat")
spec = importlib.util.spec_from_file_location("mt", sys.argv[1]); mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)
e = lambda st, at, run="COMPLETED": {"name": "gate", "status": run, "conclusion": st, "completedAt": at}
cases = {
 "#3445 shape: 4 FAILURE newest 09:29, SUCCESS 09:23 last": [e("FAILURE","2026-11-11T09:10:00Z"),e("FAILURE","2026-11-11T09:29:14Z"),e("SUCCESS","2026-11-11T09:23:45Z")],
 "P567 #3405 shape: deferral FAILUREs older, code SUCCESS newest": [e("FAILURE","2026-11-11T01:10:00Z"),e("FAILURE","2026-11-11T01:20:00Z"),e("SUCCESS","2026-11-11T01:30:49Z")],
 "same, reversed": [e("SUCCESS","2026-11-11T01:30:49Z"),e("FAILURE","2026-11-11T01:20:00Z"),e("FAILURE","2026-11-11T01:10:00Z")],
 "StatusContext no stamps: FAILURE then SUCCESS": [{"context":"gate","state":"FAILURE"},{"context":"gate","state":"SUCCESS"}],
 "EXPECTED status context": [{"context":"gate","state":"EXPECTED"}],
 "zero-time unfinished + SUCCESS": [e("SUCCESS","2026-11-11T09:00:00Z"),{"name":"gate","status":"IN_PROGRESS","conclusion":"","completedAt":"0001-01-01T00:00:00Z","startedAt":"2026-11-11T10:00:00Z"}],
}
for k,v in cases.items(): print(f"{k}: {mt.rollup_states(v)}")
print("POLICY_RED:", mt.POLICY_RED)
