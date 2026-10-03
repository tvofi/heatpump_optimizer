import sys, os
sys.path.insert(0, "tests"); sys.path.insert(0, "tests/hastub")
import harness_headers as h
names = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
echo = [sys.executable, "-c", f"import os;print(*(os.environ.get(k, '') for k in {names!r}))"]
rc, out, _ = h.run_bounded(echo, {**os.environ, **dict.fromkeys(names, "8")}, 30, 30)
print("RESULT pass=", rc == 0 and out.split() == ["1","1","1"], out.split())
