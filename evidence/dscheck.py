import importlib.util, sys
spec = importlib.util.spec_from_file_location("g", sys.argv[1]); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
MEAS = "Architecture score: dS +0.0000 NULL"
for f in sys.argv[2:]:
    b = open(f).read()
    print(f.split('/')[-1], "justification:", g.justification(b)[0], "| justified(measured):", g.justified(b, lambda: MEAS), "| check_body(raises):", g.check_body(b, ["x: 1 -> 2"], lambda: MEAS)[0], "| check_body(no raise):", g.check_body(b, [], lambda: MEAS)[0])
