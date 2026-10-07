# Reviewer's probe (not the finder's harness; R9-RO-12 has no finder): does
# `batch` land anything while main's own tip is red? Injects two checks into
# merge_train.py's _batch_self_test (same fake-GitHub world), runs, prints them.
import sys, pathlib
src_path = pathlib.Path(sys.argv[1])
src = src_path.read_text()
anchor = '    try:\n        Train("o/r", Path("."), None, "", (), 1, base="fix/x")'
assert src.count(anchor) == 1
probe = '''
    def redmain(w):  # main goes red AFTER both heads were cut green: one more unit past cap 1
        (w["R"] / "units/u9").write_text("9\\n")
        g(w["R"], "add", "-A"); g(w["R"], "commit", "-qm", "main reddens")
    w = go({1: {"a.txt": "A\\n"}}, cap=1, setup=redmain)
    print("PROBE lone entry, main red: rc=%s merged=%s pushed=%d last=%r" % (w["rc"], sorted(w["merged"]), len(w["pushed"]), w["lines"][-1]))
    check("PROBE-1 a lone entry is NOT merged while main's tip is red", not w["merged"])
    w = go({1: {"a.txt": "A\\n"}, 2: {"b.txt": "B\\n"}}, cap=1, setup=redmain)
    print("PROBE pair, main red: rc=%s merged=%s pushed=%d lines=%r" % (w["rc"], sorted(w["merged"]), len(w["pushed"]), [l for l in w["lines"] if "dropped" in l or " D: " in l]))
    check("PROBE-2 a pair whose proof is red only because main is red merges nothing", not w["merged"])
    # null control: same world, main NOT reddened -> both merge proved
    w = go({1: {"a.txt": "A\\n"}, 2: {"b.txt": "B\\n"}}, cap=1)
    print("PROBE null control, main green: rc=%s merged=%s" % (w["rc"], sorted(w["merged"])))
'''
src = src.replace(anchor, probe + anchor)
g = {"__name__": "probe", "__file__": str(src_path)}
exec(compile(src, str(src_path), "exec"), g)
sys.exit(g["_self_test"]())
