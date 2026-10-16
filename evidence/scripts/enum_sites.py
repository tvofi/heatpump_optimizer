import re, subprocess, sys
sys.path.insert(0, "tools/audit/seat")
import ref_privacy as rp
out = subprocess.run(["git","grep","-nIE",r"push","HEAD","--","."],capture_output=True,text=True).stdout
site_files, broad = {}, {}
BROAD = re.compile(r"""(?x)
   \bgit\b[^\n]*\bpush\b            # git ... push
 | \$\{?\w*(GIT|git)\w*\}?[\"']?\s+push\b   # "$GIT" push
 | ["']push["']                     # list element 'push'
 | \bpush\s+(origin|-[a-z]|--)      # push origin / flags
 | git/refs | createRef | updateRef
""")
for line in out.splitlines():
    _, path, n, text = line.split(":",3)
    if path.endswith(".md") or path.startswith(("dev/audit/rounds/","dev/archive/","custom_components/","tools/policy/vendor/")) or path.endswith(".json") or path.endswith(".log") or path.endswith(".tsv"): continue
    if rp._COMMENT.match(text): continue
    if rp._SITE.search(text): site_files.setdefault(path,[]).append(int(n))
    if BROAD.search(text): broad.setdefault(path,[]).append((int(n),text.strip()[:140]))
print("== files the module's _SITE rule fires on, ANY tree:")
for p in sorted(site_files): print(("IN-REG " if p in rp.PUSHERS else ("in-scope" if rp.scope(p) else "OUT    ")), p, site_files[p][:6])
print("\n== broad rule, files not in PUSHERS:")
for p in sorted(broad):
    if p in rp.PUSHERS: continue
    print(p)
    for n,t in broad[p][:4]: print("   ",n,t)
