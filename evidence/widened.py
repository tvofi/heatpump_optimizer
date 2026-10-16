# REVIEWER'S OWN widened reader: the arm's _sp_literals with the binding forms
# and read methods the body's rule claims ("every binding ... and read site")
# but the code does not follow -- For targets, walrus, function-parameter
# defaults, class attributes, and the .open() read method. Used only to ask
# whether any of those seams is LIVE (a cited program opens a path that does
# not resolve through one).
import ast as _a

def _binds_w(tree):
    out = {}
    for k, v in _sp_bindings(tree).items():
        out.setdefault(k, []).extend(v)
    for n in _a.walk(tree):
        if isinstance(n, _a.For) and isinstance(n.target, _a.Name) and isinstance(n.iter, (_a.Tuple, _a.List)):
            out.setdefault(n.target.id, []).extend(n.iter.elts)
        elif isinstance(n, _a.NamedExpr) and isinstance(n.target, _a.Name):
            out.setdefault(n.target.id, []).append(n.value)
        elif isinstance(n, (_a.FunctionDef, _a.AsyncFunctionDef)):
            for d in list(n.args.defaults) + [d for d in n.args.kw_defaults if d is not None] + \
                     [n.args.vararg, n.args.kwarg]:
                if isinstance(d, _a.arg):
                    continue
                for nm in [a.arg for a in n.args.args if a.annotation is not None][:0]:
                    pass
            for a, d in zip(n.args.args[-len(n.args.defaults):] if n.args.defaults else [], n.args.defaults):
                out.setdefault(a.arg, []).append(d)
            for a, d in zip(n.args.kwonlyargs, n.args.kw_defaults):
                if d is not None: out.setdefault(a.arg, []).append(d)
        elif isinstance(n, _a.ClassDef):
            for st in n.body:
                if isinstance(st, _a.Assign):
                    for t in st.targets:
                        for nm in _sp_bind_names(t):
                            out.setdefault(nm, []).append(st.value)
    return out

def _literals_w(src, opened=True):
    tree = _a.parse(src)
    docs = {id(n.body[0].value) for n in _a.walk(tree)
            if isinstance(n, (_a.Module, _a.ClassDef, _a.FunctionDef, _a.AsyncFunctionDef))
            and n.body and isinstance(n.body[0], _a.Expr) and isinstance(n.body[0].value, _a.Constant)}
    binds = _binds_w(tree)
    fstr = {id(c) for j in _a.walk(tree) if isinstance(j, _a.JoinedStr)
            for c in j.values if isinstance(c, _a.Constant)}
    via, opens = {}, set()
    for n in _a.walk(tree):
        if not isinstance(n, _a.Call): continue
        name = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
        if name in ("locate", "canon") and n.args and isinstance(n.args[0], _a.Constant):
            via[id(n.args[0])] = _layout_locate if name == "locate" else _layout_canon
        if name in _SP_OPENS:
            for arg in [*n.args, *(k.value for k in n.keywords)]:
                for cc in _sp_reach(arg, binds):
                    if isinstance(cc, _a.Constant): opens.add(id(cc))
        if name in {"read_text", "read_bytes", "open", "readlines", "iterdir", "glob", "rglob"} \
                and isinstance(n.func, _a.Attribute):
            for cc in _sp_reach(n.func.value, binds):
                if isinstance(cc, _a.Constant): opens.add(id(cc))
    out = []
    for n in _a.walk(tree):
        if not (isinstance(n, _a.Constant) and isinstance(n.value, str) and id(n) not in docs
                and (not opened or id(n) in opens)): continue
        v = n.value[1:] if id(n) in fstr and n.value.startswith("/") else n.value
        if re.fullmatch(r"[\w.-]+(?:/[\w.-]+)+/?", v) and v.split("/")[0] in _SP_TOPS:
            out.append((n.lineno, v, via.get(id(n), lambda x: x)(v)))
    return out

print("=== LIVE-SEAM TEST over the cited programs at this head")
live = 0
for p in sorted({*_SP_CITED, *(_sp_p for _sp_p, _ in _SP_REMEASURES)}):
    if not p.endswith(".py") or not Path(p).is_file(): continue
    src = Path(p).read_text()
    arm = {(l, v) for l, v, _ in _sp_literals(src)}
    wid = {(l, v, g) for l, v, g in _literals_w(src)}
    new = [t for t in wid if (t[0], t[1]) not in arm]
    bad = [t for t in new if not Path(t[2].rstrip("/")).exists()]
    if new:
        print(f"  {p}: arm={len(arm)} widened={len(wid)} widened-only={len(new)} UNRESOLVING={len(bad)}")
        for t in bad: print("      LIVE FAULT", t)
        for t in new[:6]:
            if t not in bad: print("      (widened-only, resolves)", t)
        live += len(bad)
print("LIVE_FAULTS", live)
print("COVERAGE cited=%d examined=%d" % (len(_SP_CITED), sum(1 for p in _SP_CITED if p.endswith('.py') and Path(p).is_file())))
print("COVERAGE names", sorted(_SP_CITED))
# positive control: the widening must find a fault the arm misses when one exists
_pc = "ZZ_" + "_".join(["x"]*4)  # a literal the arm would hold
_ctrl_src = 'import os\nfrom pathlib import Path\n_P = Path(".") / "dev/nope_xyz/file.py"\n_X = _P.open()\n'
print("POSITIVE CONTROL arm_reads=%s widened_reads=%s" % (
    [v for _, v, _ in _sp_literals(_ctrl_src)], [v for _, v, _ in _literals_w(_ctrl_src)]))
