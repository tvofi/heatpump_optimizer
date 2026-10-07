# Reviewer's round-2 probe (my own instrument): other routes onto a red main.
import sys, pathlib
p = pathlib.Path(sys.argv[1]); src = p.read_text()
anchor = '    try:\n        Train("o/r", Path("."), None, "", (), 1, base="fix/x")'
assert src.count(anchor) == 1
probe = '''
    # R2-A: proved pair; main's run on merge 1 goes red (e.g. FULL catches what the scoped proof missed)
    def red1(w):
        w["after_merge"][1] = lambda: w["red"].add(g(w["R"], "rev-parse", "HEAD")[1])
    w = go({1: {"a.txt": "A\\n"}, 2: {"b.txt": "B\\n"}}, cap=1, setup=red1)
    print("R2-A proved pair, red after merge 1: rc=%s merged=%s last=%r" % (w["rc"], sorted(w["merged"]), w["lines"][-1]))
    # R2-B: lone D merge, nothing serial after it; its own run goes red; train reports DONE
    w = go({1: {"a.txt": "A\\n"}}, cap=1, setup=red1)
    print("R2-B lone D, nothing later, red after: rc=%s merged=%s last=%r" % (w["rc"], sorted(w["merged"]), w["lines"][-1]))
    # R2-C: a second batch invoked on that red tip
    def chain(w):
        red1(w)
    import copy
'''
src = src.replace(anchor, probe + anchor)
g = {"__name__": "probe", "__file__": str(p)}
exec(compile(src, str(p), "exec"), g)
sys.exit(g["_self_test"]())
