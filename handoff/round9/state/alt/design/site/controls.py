#!/usr/bin/env python3
"""Planted-error controls for check_site.py: each variant of the page (or of the doc side) must turn it red."""
import os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("HPO_REPO", "/home/user/heatpump_optimizer")  # a checkout holding ref 5dfa6684
PAGE = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()

def run(text, *extra):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(text)
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_site.py"), f.name, "--repo", REPO, *extra], capture_output=True, text=True)
    os.unlink(f.name)
    return r.returncode, [l for l in r.stdout.splitlines() if l.startswith("FAIL")]

def once(s, a, b):
    assert s.count(a) >= 1, a
    return s.replace(a, b, 1)

CASES = [
    ("wrong number in a tile", once(PAGE, '<span class="v">20<small>', '<span class="v">48<small>'), ()),
    ("reworded quoted claim", once(PAGE, "for up to 20 hours and the optimizer", "for up to 48 hours and the optimizer"), ()),
    ("dead heading slug", once(PAGE, 'data-src="README.md#known-limitations"', 'data-src="README.md#known-limitation"'), ()),
    ("dropped feature", once(PAGE, "<h3 data-feature>Shows its work.</h3>", "<h3>Shows its work.</h3>"), ()),
    ("extra docs entry", once(PAGE, '<a class="doc" data-doc="DISCLAIMER.md"', '<a class="doc" data-doc="docs/HANDOVER.md" href="#">x</a><a class="doc" data-doc="DISCLAIMER.md"'), ()),
    ("docs row removed", re.sub(r'<a class="doc" data-doc="docs/ecl110.md".*?</a>', "", PAGE, flags=re.S), ()),
    ("number outside any claim", once(PAGE, '<div class="wrap">\n<section', '<div class="wrap"><p>Saves 40 % a year</p>\n<section'), ()),
    ("version literal", once(PAGE, "installs with HACS</span>", "installs with HACS v6.7.12</span>"), ()),
    ("image not in the tree", once(PAGE, 'data-repo="docs/setup/03-menu.png"', 'data-repo="docs/setup/03-menus.png"'), ()),
    ("link to a sub-page the docs build does not produce", once(PAGE, 'href="ecl110.html"', 'href="tuning.html"'), ()),
    ("external script", once(PAGE, "</head>", '<script src="https://cdn.example.com/x.js"></script></head>'), ()),
    ("fonts from a third party (impl profile)", once(PAGE, "</head>", '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit"></head>'), ("--profile", "impl")),
    ("font url() to a third party in CSS", once(PAGE, "url(fonts/outfit-latin-600-normal.woff2)", "url(https://fonts.gstatic.com/s/outfit/x.woff2)"), ()),
    ("doc side moved: README says 12 hours, page still 20", PAGE, ("--repo", "DOCREPO", "--ref", "HEAD")),
]
def doc_repo():
    """A throwaway repo holding the reader corpus at 5dfa6684 with one README figure changed: the page is unchanged,
    so red here proves the fact side is read from the documents, not carried."""
    d = tempfile.mkdtemp()
    src = REPO
    files = subprocess.run(["git", "-C", src, "ls-tree", "-r", "--name-only", "5dfa6684", "--", "README.md", "DISCLAIMER.md", "VERSION", "docs"], capture_output=True, text=True).stdout.split()
    for f in files:
        os.makedirs(os.path.join(d, os.path.dirname(f)), exist_ok=True)
        with open(os.path.join(d, f), "wb") as o:
            o.write(subprocess.run(["git", "-C", src, "show", f"5dfa6684:{f}"], capture_output=True).stdout)
    r = os.path.join(d, "README.md"); t = open(r).read()
    assert "for up to 20 hours" in t
    open(r, "w").write(t.replace("for up to 20 hours", "for up to 12 hours", 1))
    for c in (["init", "-q"], ["add", "-A"], ["-c", "user.email=x@x", "-c", "user.name=x", "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", d, *c], check=True)
    return d
DOCREPO = doc_repo()
old = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h", "-S", "**Fits your Home Assistant.**", "5dfa6684", "--", "README.md"], capture_output=True, text=True).stdout.strip()
ok = True
base = run(PAGE)
print(f"baseline: exit {base[0]}, {len(base[1])} FAIL line(s)")
ok &= base[0] == 0
for name, text, extra in CASES:
    extra = tuple(DOCREPO if e == "DOCREPO" else e for e in extra)
    code, fails = run(text, *extra)
    red = code == 1 and fails
    ok &= bool(red)
    print(f"{'RED ' if red else 'MISS'} {name}: {fails[0][5:120] if fails else 'no failure'}" + (f" (+{len(fails)-1} more)" if len(fails) > 1 else ""))
os.remove if False else None
missing = run(PAGE.replace("data-src", "data-xsrc"))
print(f"{'RED ' if missing[0] else 'MISS'} anchor, zero claims: {missing[1][-1][5:] if missing[1] else ''}")
ok &= missing[0] == 1
code = subprocess.run([sys.executable, os.path.join(HERE, "check_site.py"), "/nonexistent.html"], capture_output=True, text=True)
print(f"{'RED ' if code.returncode else 'MISS'} anchor, no page: {code.stdout.splitlines()[-2][5:]}")
ok &= code.returncode == 1
print("RESULT:", "every control red, baseline green" if ok else "A CONTROL DID NOT MEASURE")
sys.exit(0 if ok else 1)
