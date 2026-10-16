import subprocess, sys, collections
sys.path.insert(0, "tools/audit/seat")
import ref_privacy as rp
host = rp.Identity.of_host()
for rev in sys.argv[1:]:
    out = subprocess.run(["git","--git-dir",rev.split("::")[0],"log",rev.split("::")[1],"--format=%an <%ae> %cn <%ce>"],capture_output=True,text=True).stdout.splitlines()
    c = collections.Counter(k for l in out for k in rp.leaks(l, host))
    hostish = sum(1 for l in out if ".local>" in l)
    print(f"{rev.split('::')[1]}: {len(out)} commits; author/committer lines by leak class: {dict(c)}; '.local' host emails: {hostish}")
