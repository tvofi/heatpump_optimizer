import sys, time, importlib.util, statistics
root = sys.argv[1]
sys.path[:0] = [root + "/tests/hastub", root + "/custom_components", root + "/tests"]
spec = importlib.util.spec_from_file_location("h", root + "/dev/audit/harnesses/r10_combi_tank.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
h.cycles(wood=True)  # warm
ts = []
for _ in range(15):
    t = time.perf_counter(); h.cycles(wood=True); ts.append(time.perf_counter() - t)
print(f"RESULT bench_{sys.argv[2]}_median_ms={statistics.median(ts)*1e3:.2f} min_ms={min(ts)*1e3:.2f}")
