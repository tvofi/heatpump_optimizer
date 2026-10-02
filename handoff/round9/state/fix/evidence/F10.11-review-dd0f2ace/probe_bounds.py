"""F10.11 review probe: run_bounded's scope and both bounds, from the head tree."""
import os, resource, sys, time
sys.path.insert(0, "tests")
import harness_headers as hh
env = dict(os.environ)
before = resource.getrlimit(resource.RLIMIT_CPU)
t = time.time(); rc_spin = hh.run_bounded([sys.executable, "-c", "while True: pass"], env, 2, 60)[0]; dt = time.time() - t
after = resource.getrlimit(resource.RLIMIT_CPU)
print("parent RLIMIT_CPU before", before, "after", after, "-> child-only:", before == after)
print("spin rc", rc_spin, "wall %.1fs" % dt)
# grandchild inherits the limit (a spinning grandchild is also killed)
rc_gc = hh.run_bounded([sys.executable, "-c",
  "import subprocess,sys; r=subprocess.run([sys.executable,'-c','while True: pass']); print(r.returncode)"], env, 2, 60)
print("grandchild spin: parent rc", rc_gc[0], "grandchild rc", rc_gc[1].strip())
# multithreaded spin: CPU counts across threads (4 threads hit 2 CPU-s in ~0.5 s wall)
t = time.time(); rc_mt = hh.run_bounded([sys.executable, "-c",
  "import threading\ndef f():\n  while True: pass\n[threading.Thread(target=f,daemon=True).start() for _ in range(3)]\nf()"], env, 2, 60)[0]
print("3-thread spin rc", rc_mt, "wall %.1fs" % (time.time() - t), "(GIL-bound python threads: ~1 core)")
print("idle past wall", hh.run_bounded([sys.executable, "-c", "import time; time.sleep(5)"], env, 30, 1))
