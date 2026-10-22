#!/usr/bin/env python3
"""R10-ARCH-DOCS-FIRST mutation proof: each mutant of the doc-wiring and coffee-button arms, or of the production docs,
applied in place to a checkout, tests/doc_claims.py run, its FAIL lines listed, the file restored.

    python3 dev/audit/harnesses/r10_arch_docs_first_mutants.py <checkout root>

Run it in a scratch worktree (git worktree add --detach <dir> HEAD): it rewrites files while it runs.
M0 is the null control: no mutation, no FAIL line.
"""
import pathlib, subprocess, sys, os
root = pathlib.Path(sys.argv[1])
DC = "tests/doc_claims.py"
M = [
 ("M0 null (no mutation)", DC, None, None),
 ("M1 (a) path resolution never fires", DC, "if tok not in tree and tok.rstrip(\"/\") + \"/\" not in dirs and not marked:", "if False:"),
 ("M2 (a) marker exemption dropped", DC, "if tok not in tree and tok.rstrip(\"/\") + \"/\" not in dirs and not marked:", "if tok not in tree and tok.rstrip(\"/\") + \"/\" not in dirs:"),
 ("M3 (b) unknown group passes", DC, "out.append(f\"{name}: [{kind}: {g}] names no group in the roster\")", "pass"),
 ("M4 (b) malformed marker passes", DC, "            if not g:\n                out.append(f\"{name}: malformed marker", "            if not g:\n                continue\n                out.append(f\"{name}: malformed marker"),
 ("M5 (c) refuses a done group", DC, "                    notes.append(f\"{name}: [{kind}: {g}] names a done group", "                    out.append(f\"{name}: [{kind}: {g}] names a done group"),
 ("M6 N1 roster read unconditionally", DC, "    if groups:\n        stages = roster()", "    stages = roster()\n    if groups:"),
 ("M7 (d) declared-node rule off", DC, "if n == 1 and t not in shaped]", "if False]"),
 ("M8 (d) diagram type unchecked", DC, "            if kind not in _DIAGRAMS:", "            if False:"),
 ("M9 (d) sequence participants unchecked", DC, "            if who not in declared:", "            if False:"),
 ("M10 (e) hex colour unchecked", DC, "                if _HEX.search(body):", "                if False:"),
 ("M11 (e) init unchecked", DC, "                if \"%%{init\" in body:", "                if False:"),
 ("M12 button: README arm off", DC, "    if not m:\n        out.append(\"README.md: no button", "    if False:\n        out.append(\"README.md: no button"),
 ("M13 button: index footer arm off", DC, "    if not (foot and _COFFEE_A.search(foot.group(0))):\n        out.append(\"docs/index.html", "    if False:\n        out.append(\"docs/index.html"),
 ("M14 button: built footer arm off", DC, "        if not (foot and _COFFEE_A.search(foot.group(0))):\n            out.append(f\"{page}", "        if False:\n            out.append(f\"{page}"),
 ("M15 button: SVG token compare off", DC, "if not want or not got or got.group(1).strip().lower() != want.lower():", "if False:"),
 ("P1 production: button gone from build_docs.mjs footer", "tools/site/build_docs.mjs", "<a class=\"bmc\" href=\"https://buymeacoffee.com/rpgshcwb2tp\">", "<a class=\"bmc\" href=\"#\">"),
 ("P2 production: button gone from docs/index.html footer", "docs/index.html", "<a class=\"bmc\" href=\"https://buymeacoffee.com/rpgshcwb2tp\">", "<a class=\"bmc\" href=\"#\">"),
 ("P3 production: button gone from README top", "README.md", "[![Buy me a coffee](docs/img/brand/coffee.svg)](https://buymeacoffee.com/rpgshcwb2tp)\n", ""),
 ("P4 production: a marker dropped from dev/README.md", "dev/README.md", "- `.github/workflows/gate-sweep.yml`, which re-runs a stale `gate` at a pull request's live head [target: R10-CI-LAYOUT-P2]", "- `.github/workflows/gate-sweep.yml`, which re-runs a stale `gate` at a pull request's live head"),
]
env = dict(os.environ, PYTHONPATH="tests/hastub:tests:custom_components")
for name, f, old, new in M:
    p = root / f
    orig = p.read_text()
    if old is not None:
        assert orig.count(old) >= 1, (name, old)
        p.write_text(orig.replace(old, new, 1))
    try:
        r = subprocess.run([sys.executable, DC], cwd=root, env=env, capture_output=True, text=True)
        fails = [l.strip()[5:].split("  [")[0] for l in r.stdout.splitlines() if l.strip().startswith("FAIL ")]
        print(f"== {name}: rc={r.returncode}, {len(fails)} FAIL")
        if r.returncode and not fails:
            print("     CRASH " + (r.stderr.strip().splitlines() or ["(no stderr)"])[-1])
        for x in fails:
            print(f"     FAIL {x}")
    finally:
        p.write_text(orig)
