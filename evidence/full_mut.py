import sys, subprocess, pathlib, importlib.util
spec = importlib.util.spec_from_file_location("m", "/home/user/w/mut.py")
src = open("/home/user/w/mut.py").read().split("cmd = sys.argv[1]")[0]
ns = {}; exec(src, ns); M = ns["M"]
i = int(sys.argv[1]); f, a, b, label = M[i]
wt = pathlib.Path(f"/home/user/mw{i}")
subprocess.run(["git", "-C", "/home/user/rev", "worktree", "add", "-q", "--detach", str(wt), "HEAD"], check=True)
p = wt / "custom_components/heatpump_optimizer" / f; s = p.read_text(); assert s.count(a) == 1; p.write_text(s.replace(a, b))
r = subprocess.run("PYTHONPATH=tests/hastub:custom_components:tests python3 tests/features.py", shell=True, cwd=wt, capture_output=True, text=True)
out = (r.stdout + r.stderr).splitlines()
fails = [l for l in out if "FAIL" in l]
verdict = "KILLED  " if r.returncode else "SURVIVED"
open(f"/home/user/w/ev/full_mut_{i}.txt", "w").write(f"{verdict} {f}: {label} | rc {r.returncode} | {len(fails)} FAIL lines\n" + "\n".join(fails[:5]) + "\n" + "\n".join(out[-2:]) + "\n")
subprocess.run(["git", "-C", "/home/user/rev", "worktree", "remove", "--force", str(wt)])
