import sys, re, importlib.util, pathlib
# Distinguishing inputs for the three non-probe survivors at the head; each run against the head
# module and against the mutated module (the same one-line replacement the head driver applies).
src = pathlib.Path("tools/audit/carry_audit.py").read_text()
sys.path.insert(0, str(pathlib.Path("tools/audit").resolve()))
MUT = {
    "quoted_lookbehind": ('(?<![\\w"])"[^"\\n]*"(?!\\w)', '"[^"\\n]*"(?!\\w)'),
    "quoted_lookahead": ('(?<![\\w"])"[^"\\n]*"(?!\\w)', '(?<![\\w"])"[^"\\n]*"'),
    "mdlink_url_any": ('\\]\\([^)\\s]*\\)")', '\\]\\([^)]*\\)")'),
}
PROBES = {
    "quoted_lookbehind": 'x. the 5" pipe. Carry: R10-LIVE and 6" too.',
    "quoted_lookahead": 'x. said "q. Carry: R10-LIVE "x" too.',
    "mdlink_url_any": "x. Carry: [#100](a b)",
}
def load(text, name):
    # beside carry_audit.py, so its own path setup (relative to __file__) resolves; removed after load
    p = pathlib.Path("tools/audit") / f"_probe_{name}.py"; p.write_text(text)
    try:
        spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m); return m
    finally:
        p.unlink()
head = load(src, "ca_head")
for k, (a, b) in MUT.items():
    assert src.count(a) == 1, k
    mut = load(src.replace(a, b), "ca_" + k)
    t = PROBES[k]
    segs = lambda m: m.carry_segments(t, shaped=True)
    print(f"{k}: probe {t!r}")
    print(f"  head   segments={segs(head)}")
    print(f"  mutant segments={segs(mut)}")
    print(f"  {'DISTINGUISHED' if segs(head) != segs(mut) else 'NOT distinguished'}")
