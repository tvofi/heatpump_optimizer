"""Reviewer's own mutant driver (not the fixer's): apply, run stamp self-test, restore."""
import subprocess, sys, pathlib
F = pathlib.Path("tools/release/stamp.py"); Y = pathlib.Path(".github/workflows/release.yml")
orig = {F: F.read_text(), Y: Y.read_text()}
def rep(p, a, b):
    s = orig[p]; assert s.count(a) >= 1, (p, a); return {p: s.replace(a, b, 1)}
FETCH = '    sh("git", "fetch", "origin", "--quiet", "--tags")\n'
TAGS = '''    tags = [t for t in sh("git", "tag", "--list").split() if TAG_RE.match(t)]
    remote = [t for t in (l.split("refs/tags/")[1] for l in sh("git", "ls-remote", "--tags", "origin").splitlines()
                            if "refs/tags/v" in l and not l.endswith("^{}")) if TAG_RE.match(t)]
'''
def before_fetch():
    s = orig[F]
    s = s.replace("    base = bump_base(current, tags + remote)\n", "", 1)
    s = s.replace("    # Rule 1: a fetched, clean checkout of origin/main.\n" + FETCH,
                  TAGS + "    base = bump_base(current, tags + remote)\n    # Rule 1: a fetched, clean checkout of origin/main.\n" + FETCH, 1)
    assert s.index("base = bump_base(current, tags + remote)") < s.index(FETCH)
    return {F: s}
M = {
 "bump_base returns VERSION only": rep(F, '    return ".".join(map(str, max([version_tuple(current), *tops])))', '    return current'),
 "bump_base drops TAG_RE filter": rep(F, "tops = [version_tuple(t) for t in tags if TAG_RE.match(t)]", "tops = [version_tuple(t) for t in tags]"),
 "last_stamped_tag = newest tag by date (ignores tree VERSION)": rep(F,
    '    for tag in sorted((t for t in tags if TAG_RE.match(t)), key=version_tuple, reverse=True):\n        if (version_at(tag) or "").strip() == tag[1:]:\n            return tag\n    return None',
    '    rel = [t for t in tags if TAG_RE.match(t)]\n    order = sh("git", "tag", "--list", "v*", "--sort=-creatordate").split()\n    for tag in order:\n        if tag in rel:\n            return tag\n    return None'),
 "last_stamped_tag drops TAG_RE filter": rep(F, "for tag in sorted((t for t in tags if TAG_RE.match(t)), key=version_tuple, reverse=True):",
    "for tag in sorted(tags, key=lambda t: tuple(int(x) for x in t[1:].split('-')[0].split('.')), reverse=True):"),
 "main(): last_tag = newest tag": rep(F, "    last_tag = last_stamped_tag(tags, tag_version)\n",
    '    last_tag = "v" + ".".join(map(str, top)) if top != (0, 0, 0) else None\n'),
 "main(): next from VERSION (base = current)": rep(F, "    base = bump_base(current, tags + remote)\n", "    base = current\n"),
 "main(): bump base computed before the tag fetch": before_fetch(),
 "release.yml: tree step drops VERSION test": rep(Y, 'if [ "v${version}" != "${TAG}" ]; then', 'if false; then'),
 "release.yml: tree step drops manifest test": rep(Y, 'if [ "v${manifest}" != "${TAG}" ]; then', 'if false; then'),
 "release.yml: tree step drops notes test": rep(Y, 'if ! grep -Fqx "## ${TAG}" RELEASE_NOTES.md; then', 'if false; then'),
 "release.yml: tree step grep not exact-line (-Fq)": rep(Y, 'if ! grep -Fqx "## ${TAG}" RELEASE_NOTES.md; then', 'if ! grep -Fq "## ${TAG}" RELEASE_NOTES.md; then'),
 "release.yml: readback attempts=1": rep(Y, "attempts=5", "attempts=1"),
 "release.yml: readback never fails after loop (exit 0)": rep(Y, 'left as a draft, not published" >&2\n          exit 1', 'left as a draft, not published" >&2\n          exit 0'),
 "release.yml: unbounded readback (while true)": rep(Y, 'for attempt in $(seq 1 "${attempts}"); do', 'attempt=0; while attempt=$((attempt+1)); do'),
}
def run():
    p = subprocess.run([sys.executable, "-I", "tools/release/stamp.py", "--self-test"], capture_output=True, text=True, timeout=900)
    out = p.stdout + p.stderr
    fails = [l for l in out.splitlines() if "FAIL" in l]
    tb = [l for l in out.splitlines() if "Error" in l][-1:] 
    return p.returncode, fails, tb
try:
    rc, f, tb = run(); print(f"NULL unmutated: exit {rc}, {len(f)} FAIL")
    for name, edits in M.items():
        for p, s in edits.items(): p.write_text(s)
        try:
            rc, f, tb = run()
        except subprocess.TimeoutExpired:
            rc, f, tb = "TIMEOUT", [], []
        for p in edits: p.write_text(orig[p])
        print(f"MUTANT {name}: exit {rc}, {len(f)} FAIL {'KILLED' if rc not in (0,) else 'SURVIVED'}")
        for l in f[:4]: print("   ", l.strip()[:200])
        for l in tb: print("    tb:", l.strip()[:200])
    rc, f, tb = run(); print(f"NULL restored: exit {rc}, {len(f)} FAIL")
finally:
    for p, s in orig.items(): p.write_text(s)
