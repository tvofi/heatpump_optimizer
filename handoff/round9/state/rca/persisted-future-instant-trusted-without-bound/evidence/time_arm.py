import sys, time, io, contextlib
sys.argv=["x"]; sys.path.insert(0,"tests")
import finite_boundary as fb
disk = fb._healthy_payloads()
by_name = {k.replace(fb.const.DOMAIN + "_" + fb.ENTRY_ID + "_", ""): (k, v) for k, v in disk.items()}
ts=[]
for i in range(5):
    s=time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()): fb._instant_arm(by_name)
    ts.append(time.perf_counter()-s)
print("arm seconds", [round(x,2) for x in ts], "median", sorted(ts)[2])
