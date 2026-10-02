"""Reviewer's own diff probe for coordinator.py:_worker_fallback_streak GUARD_OFF c1f18a7a.
Extracts the five worker-fallback functions from coordinator.py AS WRITTEN (ast source
segments), builds head and mutant namespaces, and drives them through every production
entry point over many hass/data shapes and all op sequences of length 1..3."""
import ast, copy, itertools, sys
SRC = sys.argv[1]
FUNCS = ["_note_worker_fallback", "_clear_worker_fallback", "_worker_fallback_streak",
         "_bump_worker_fallback", "_reset_worker_fallback_streak"]
text = open(SRC).read()
tree = ast.parse(text)
segs = {n.name: ast.get_source_segment(text, n) for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name in FUNCS}
assert set(segs) == set(FUNCS), segs.keys()
OLD = "    if not isinstance(bag, dict):\n        return 0"
assert segs["_worker_fallback_streak"].count(OLD) == 1
def build(mutant):
    ns = {}
    class IR:
        class IssueSeverity: WARNING = "warning"
        @staticmethod
        def async_delete_issue(hass, domain, iid):
            getattr(hass, "issues_log", []).append(("del", iid))
    class L:
        def warning(self, *a): pass
    def _create_issue(hass, domain, iid, **k):
        getattr(hass, "issues_log", []).append(("create", iid, k["translation_placeholders"]["cause"]))
    ns.update(Any=object, HomeAssistant=object, BaseException=BaseException, ir=IR, _LOGGER=L(),
              DOMAIN="hpo", _create_issue=_create_issue, _WORKER_FALLBACK_CAUSES={},
              _WORKER_FALLBACK_STREAK="hpo_worker_fallback_streak")
    for f in FUNCS:
        s = segs[f]
        if mutant and f == "_worker_fallback_streak":
            s = s.replace(OLD, "    if False:\n        return 0")
        exec(s, ns)
    return ns
K = "hpo_worker_fallback_streak"
NODATA = object()
SHAPES = [NODATA, None, [], "s", 3, {}, {K: None}, {K: []}, {K: "x"}, {K: 5}, {K: {}},
          {K: {"A": 2}}, {K: {"A": "7"}}, {K: {"A": "junk"}}, {K: {"A": None}}, {K: {None: 1}},
          {"other": 1}, {K: {"B": 3.5}}, {K: {"A": [1]}}]
class Hass: pass
def mk(shape):
    h = Hass(); h.issues_log = []
    if shape is not NODATA: h.data = copy.deepcopy(shape)
    return h
OPS = ["bump", "reset", "clear", "note"]
ENTRIES = ["A", "B", None]
def run(ns, shape, seq):
    ns["_WORKER_FALLBACK_CAUSES"].clear()
    h = mk(shape); out = []
    for op, e in seq:
        try:
            if op == "bump": r = ns["_bump_worker_fallback"](h, e)
            elif op == "reset": r = ns["_reset_worker_fallback_streak"](h, e)
            elif op == "clear": r = ns["_clear_worker_fallback"](h, e)
            else: r = ns["_note_worker_fallback"](h, RuntimeError(f"{e} boom"), e)
            out.append(("ok", r))
        except Exception as x:
            out.append(("exc", type(x).__name__))
    return out, repr(getattr(h, "data", "<none>")), h.issues_log, dict(ns["_WORKER_FALLBACK_CAUSES"])
head, mut = build(False), build(True)
steps = list(itertools.product(OPS, ENTRIES))
n = diff = 0
for L_ in (1, 2, 3):
    for seq in itertools.product(steps, repeat=L_):
        for shape in SHAPES:
            n += 1
            if run(head, shape, seq) != run(mut, shape, seq): diff += 1
print(f"RESULT probe entry-points: {n} cases, {diff} differing")
# control: direct helper call, which no production code makes
cn = cd = 0
for shape in SHAPES:
    for e in ENTRIES:
        cn += 1
        def direct(ns):
            h = mk(shape)
            try: return ("ok", ns["_worker_fallback_streak"](h, e))
            except Exception as x: return ("exc", type(x).__name__)
        if direct(head) != direct(mut): cd += 1
print(f"RESULT control direct-call: {cn} cases, {cd} differing")
