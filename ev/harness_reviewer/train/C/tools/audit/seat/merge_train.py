import os, subprocess, sys
d = os.environ["REAP_DIR"]
open(d + "/pids", "a").write("%d\n" % os.getpid())
p = subprocess.Popen(["bash", os.environ["STUB"]])
p.wait()
