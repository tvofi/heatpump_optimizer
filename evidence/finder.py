# Round-1 finder's check (633e4ec9 ev/stateless-survivors.txt): grep the four passages, then
# stateless_findings from the HEAD's tests/doc_claims.py over a given ref's seven user pages.
import subprocess, sys, re, importlib.util, os
ref = sys.argv[1]; R = "/home/user/heatpump_optimizer"
os.chdir(os.path.expanduser("~/wt")); sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
spec = importlib.util.spec_from_file_location("dc", "tests/doc_claims.py"); dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
def show(p):
    r = subprocess.run(["git", "-C", R, "show", f"{ref}:{p}"], capture_output=True, text=True); return r.stdout if r.returncode == 0 else None
pages = {p: t for p in dc.USER_PAGES if (t := show(p)) is not None}
PASS = [("docs/how-it-works.md", r"Earlier versions added explicit anticipation"), ("docs/how-it-works.md", r"now\s+1\.0\s+rather\s+than\s+1\.05"),
        ("docs/how-it-works.md", r"survives\s+the\s+upgrade"), ("docs/dashboard-card.md", r"Earlier versions sized the dialog"),
        ("docs/dashboard-card.md", r"upgraded\s+from\s+before"), ("docs/dashboard-card.md", r"older\s+than\s+2\.6\.1")]
n = 0
for p, pat in PASS:
    hit = bool(re.search(pat, pages.get(p, ""))); n += hit; print(f"passage {p} /{pat}/ present={hit}")
f = dc.stateless_findings(pages)
print(f"RESULT finder_passages_present={n} ref={ref}")
print(f"RESULT stateless_findings={len(f)} ref={ref}")
for x in f: print("  ", x)
