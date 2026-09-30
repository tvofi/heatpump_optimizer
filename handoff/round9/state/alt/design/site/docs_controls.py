#!/usr/bin/env python3
"""Planted-error controls for docs_build.mjs: each changed corpus must turn the build red; the unchanged one stays green.

    python3 docs_controls.py CORPUS TREE.txt      (CORPUS holds README.md, DISCLAIMER.md and docs/ at the ref)
"""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS, TREE = sys.argv[1], sys.argv[2]

def build(corpus, tree=TREE):
    out = tempfile.mkdtemp()
    r = subprocess.run(["node", os.path.join(HERE, "docs_build.mjs"), "--root", corpus, "--tree", tree, "--out", out], capture_output=True, text=True)
    shutil.rmtree(out)
    return r.returncode, [l for l in r.stdout.splitlines() if l.startswith("FAIL")]

def variant(path, old, new):
    d = tempfile.mkdtemp()
    shutil.copytree(CORPUS, d, dirs_exist_ok=True)
    f = os.path.join(d, path)
    t = open(f, encoding="utf-8").read()
    assert old in t, (path, old)
    open(f, "w", encoding="utf-8").write(t.replace(old, new, 1))
    return d

CASES = [
    ("cross-page anchor to a heading that does not exist", variant("docs/how-it-works.md", "This is the long version.", "This is the long version ([see](configuration.md#no-such-heading)).")),
    ("same-page anchor to a heading that does not exist", variant("docs/setup.md", "This page is the journey.", "This page is the [journey](#no-such-heading).")),
    ("image that is not in the tree", variant("docs/setup.md", "setup/01-first-screen.png", "setup/01-first-screens.png")),
    ("relative link to an untracked file", variant("docs/automations.md", "\n\n", "\n\nSee [the script](../tools/nope.py).\n\n")),
    ("README row for a file that does not exist", variant("README.md", "| [docs/ecl110.md](docs/ecl110.md)", "| [docs/new-page.md](docs/new-page.md) | A page nobody wrote |\n| [docs/ecl110.md](docs/ecl110.md)")),
    ("EXCLUDE entry the README no longer lists", variant("README.md", "| [docs/backlog.md](docs/backlog.md)", "| [docs/backlog-archive.md](docs/backlog-archive.md)")),
    ("heading renamed under an inbound link", variant("docs/configuration.md", "\n## Services\n", "\n## Service calls\n")),
    ("anchor: no Documentation table", variant("README.md", "## Documentation\n", "## Further reading\n")),
]
ok = True
code, fails = build(CORPUS)
print(f"baseline: exit {code}, {len(fails)} FAIL line(s)")
ok &= code == 0
for name, corpus in CASES:
    code, fails = build(corpus)
    shutil.rmtree(corpus)
    red = code == 1 and fails
    ok &= bool(red)
    print(f"{'RED ' if red else 'MISS'} {name}: {fails[0][5:130] if fails else 'no failure'}" + (f" (+{len(fails)-1} more)" if len(fails) > 1 else ""))
print("RESULT:", "every control red, baseline green" if ok else "A CONTROL DID NOT MEASURE")
sys.exit(0 if ok else 1)
