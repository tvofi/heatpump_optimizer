import subprocess, sys, re, importlib.util, os, collections
ref = sys.argv[1]; R = "/home/user/heatpump_optimizer"
os.chdir(os.path.expanduser("~/wt")); sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
spec = importlib.util.spec_from_file_location("dc", "tests/doc_claims.py"); dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
def show(p):
    r = subprocess.run(["git", "-C", R, "show", f"{ref}:{p}"], capture_output=True, text=True); return r.stdout if r.returncode == 0 else None
BODY = r"(?i)\b(originally|formerly|releas\w*|newer|older|earlier|previous\w*|since|any ?more|legacy|old|silently|upgrad\w*|renamed|deprecated|introduced|historic\w*|used to|no longer|changed|replaced|moved|dropped|was|were|had)\b"
WIDE = r"(?i)\b(formerly|became|began|begun|initially|reverted|anymore|changelog|nowadays|switched to|instead of the|no more|went|v\d[\w.]*|#\d{2,}|\d+\.\d+\.\d+|introduced|deprecated|until v\d|as of|starting with|from v\d)\b"
mode = sys.argv[2]; pat = re.compile(BODY if mode == "body" else WIDE)
cnt = collections.Counter(); n = 0
for p in dc.USER_PAGES:
    t = show(p)
    if t is None: continue
    s = dc.stateless_text(t) if mode != "raw" else t
    lines = s.splitlines()
    for m in pat.finditer(s):
        ln = s.count("\n", 0, m.start()) + 1; w = m.group(1).lower(); cnt[w] += 1; n += 1
        print(f"{p}:{ln}:\t{w}\t{lines[ln-1].strip()[:150]}")
print(f"RESULT census_hits={n} mode={mode} ref={ref}")
print("RESULT by_term", dict(sorted(cnt.items(), key=lambda x: -x[1])))
