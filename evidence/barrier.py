import sys; sys.path.insert(0, "tests")
import replay
rs = replay.kernel_checks()
for n, ok, d in rs: print("ok  " if ok else "FAIL", n[:110])
print(f"BARRIER {sum(1 for _,o,_ in rs if o)} of {len(rs)}")
