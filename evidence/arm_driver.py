"""Run the R9-WEB-3 arm of tests/doc_claims.py (module path given) against the real tree and against planted
trees; print one line: failures in-tree, then planted-tree outcomes. Usage: arm_driver.py WT MODULE_FILE"""
import importlib.util, io, contextlib, os, shutil, subprocess, sys, tempfile, pathlib
WT, MOD = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
os.chdir(WT)
for extra in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(WT / extra))
spec = importlib.util.spec_from_file_location("dcm", MOD)
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
    for fn in (m.check_product_page, m.check_docs_subpages, m.check_site_request_controls, m.check_docs_build_controls):
        fn()
in_tree = m.R.failures

def planted(path, old, new, drop=()):
    d = pathlib.Path(tempfile.mkdtemp())
    files = subprocess.run(["git", "ls-files"], cwd=WT, capture_output=True, text=True).stdout.split("\n")
    for f in files:
        if f and f not in drop and (f.startswith(("docs/", "README.md", "DISCLAIMER.md", "tools/site/", ".claude/workflows/vendor/")) ) and (WT / f).is_file():
            (d / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(WT / f, d / f)
    t = (d / path).read_text()
    assert old in t
    (d / path).write_text(t.replace(old, new, 1))
    subprocess.run(["git", "init", "-q"], cwd=d); subprocess.run(["git", "add", "-A"], cwd=d)
    return d

res = []
for name, args in (("anchor", ("docs/setup.md", "This page is the journey.", "This page is the [journey](#no-such-heading).")),
                   ("untracked-link", ("docs/automations.md", "\n\n", "\n\nSee [the script](../tools/nope.py).\n\n"))):
    d = planted(*args)
    m._BUILD_CACHE.pop(str(d), None)
    with contextlib.redirect_stdout(io.StringIO()):
        # the arm's core, run over the planted tree; the build script is the real one
        m.SITE_BUILD = WT / "tools/site/build_docs.mjs"
        b = m.docs_build(d)
    res.append(f"{name}:{'RED' if (b['rc'] != 0 and b['fails']) else 'MISS'}")
    shutil.rmtree(d)
print(f"in_tree_failures={in_tree}", *res)
