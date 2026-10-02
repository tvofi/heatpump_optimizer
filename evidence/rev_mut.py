"""Reviewer's own mutation/plant harness for site_findings (fix-review, PR 1846). Run from the head worktree root."""
import pathlib, re, sys, types
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
SRC = pathlib.Path("tests/doc_claims.py").read_text()
PAGE = pathlib.Path("docs/index.html").read_text()
ROOT = pathlib.Path(".").resolve()
def load(src):
    m = types.ModuleType("dcm"); m.__file__ = str(ROOT / "tests/doc_claims.py")
    exec(compile(src, "dcm", "exec"), m.__dict__); return m
def once(s, a, b):
    assert a in s, a; return s.replace(a, b, 1)
PLANTS = {
 "num": once(PAGE, 'class="v">20<', 'class="v">21<'),
 "reword": None, "slug": once(PAGE, 'data-src="README.md#known-limitations"', 'data-src="README.md#known-limitationz"'),
 "feat": None,
 "doc+": once(PAGE, '<a class="doc" data-doc="DISCLAIMER.md"', '<a class="doc" data-doc="docs/HANDOVER.md" href="#top">x</a><a class="doc" data-doc="DISCLAIMER.md"'),
 "stray": once(PAGE, '<section', '<p>Cuts the bill 31 percent</p><section'),
 "ver": once(PAGE, '</footer>', '<span data-copy>v1.2</span></footer>') if '</footer>' in PAGE else None,
 "img": once(PAGE, 'data-repo="docs/setup/03-menu.png"', 'data-repo="docs/setup/03-menuX.png"'),
 "alt": re.sub(r'alt="[^"]+"', 'alt=""', PAGE, count=1),
 "link": once(PAGE, 'blob/main/docs/ecl110.md"', 'blob/main/docs/ecl111.md"'),
 "linkslug": once(PAGE, 'blob/main/docs/ecl110.md"', 'blob/main/docs/ecl110.md#no-such-head"'),
 "script": once(PAGE, '</head>', '<script src="https://x.example/a.js"></script></head>'),
 "css": once(PAGE, 'url(site/fonts/outfit-latin-600-normal.woff2)', 'url(https://x.example/f.woff2)'),
 "cssmissing": once(PAGE, 'url(site/fonts/outfit-latin-600-normal.woff2)', 'url(site/fonts/nope.woff2)'),
 "keyq": once(PAGE, 'data-q="30 minutes by default"', 'data-q="45 minutes by default"'),
 "zero": PAGE.replace("data-src=", "data-xx="),
}
# a reworded verbatim quote: pick the first README#what-it-does verbatim element text and change one word
PLANTS["reword"] = once(PAGE, "There is no cooling mode and no cooling plan.", "There is no cooling mode and no heating plan.")
m = re.search(r'<(h3) data-feature>([^<]+)</h3>', PAGE); PLANTS["feat"] = PAGE.replace(m.group(0), f"<h3>{m.group(2)}</h3>", 1)
MUTS = [
 ("key-phrase number", "if n not in have:", "if False:", "num"),
 ("key phrase", 'if _site_norm(e["a"]["data-q"]) not in sec:', "if False:", "keyq"),
 ("verbatim test", "if f not in sec:", "if False:", "reword"),
 ("slug test", "if frag not in secs[path]:", "if False:", "slug"),
 ("feature leads-feats", 'for x in sorted(leads - feats)]', 'for x in sorted(set())]', "feat"),
 ("docs feats-rows", 'for x in sorted(docs - rows)]', 'for x in sorted(set())]', "doc+"),
 ("stray number", "if _SITE_NUM.search(data):", "if False:", "stray"),
 ("version literal", r'm in re.finditer(r"\bv\d+\.\d+(?:\.\d+)?\b", visible)]', r'm in re.finditer(r"(?!)", visible)]', "ver"),
 ("image in tree", "if not rp or not (root / rp).is_file():", "if not rp:", "img"),
 ("alt text", 'if t == "img" and not (a.get("alt") or "").strip():', "if False:", "alt"),
 ("link path", "if not (root / path).is_file():", "if False:", "link"),
 ("link slug", 'elif frag and path.endswith(".md") and frag not in', 'elif False and frag not in', "linkslug"),
 ("external script", 'if t == "script" and a.get("src"):', "if False:", "script"),
 ("css third-party", "if re.match(r\"[a-z][a-z0-9+.-]*:|//\", u, re.I) and not u.startswith(\"data:\"):", "if False:", "css"),
 ("css in tree", "elif not u.startswith((\"data:\", \"#\")) and not (root / \"docs\" / u).is_file():", "elif False:", "cssmissing"),
 ("anchor", "if st[k] == 0:", "if False:", "zero"),
]
base = load(SRC); e0, st0 = base.site_findings(PAGE)
print(f"RESULT null: {len(e0)} findings at head page {st0}")
killed = 0; total = 0
for name, a, b, plant in MUTS:
    total += 1
    if PLANTS.get(plant) is None: print(f"SKIP {name}: no plant"); continue
    red_orig = base.site_findings(PLANTS[plant])[0]
    assert SRC.count(a) == 1, (name, SRC.count(a))
    mut = load(SRC.replace(a, b, 1)); assert mut.site_findings(PAGE)[0] == [] or name, name
    try:
        red_mut = mut.site_findings(PLANTS[plant])[0]; k = bool(red_orig) and len(red_mut) < len(red_orig)
    except Exception as ex:
        red_mut = [("crash", repr(ex))]; k = bool(red_orig)  # an uncaught exception reddens the run: killed
    killed += k
    print(f"{'KILLED' if k else 'SURVIVED'} {name}: plant {plant} red {len(red_orig)} -> mutant {len(red_mut)}  [{red_orig[:1]}]")
print(f"RESULT mutants killed {killed}/{total}")
# message-keyed re-run of the two masked branches (the plant changes both src and data-repo; the CSS check keys on its own message)
P2 = once(PAGE, 'data-repo="docs/setup/03-menu.png"', 'data-repo="docs/setup/03-menuX.png"').replace('src="setup/03-menu.png"', 'src="setup/03-menuX.png"', 1)
for name, a, b, plant, key in [
  ("image in tree (src agrees)", "if not rp or not (root / rp).is_file():", "if not rp:", P2, "not in the tree"),
  ("css third-party (message)", "if re.match(r\"[a-z][a-z0-9+.-]*:|//\", u, re.I) and not u.startswith(\"data:\"):", "if False:", PLANTS["css"], "third-party resource in CSS"),
]:
    o = [m for _, m in base.site_findings(plant)[0] if key in m]
    mm = [m for _, m in load(SRC.replace(a, b, 1)).site_findings(plant)[0] if key in m]
    print(f"{'KILLED' if o and not mm else 'SURVIVED'} {name}: '{key}' {len(o)} -> {len(mm)}")
