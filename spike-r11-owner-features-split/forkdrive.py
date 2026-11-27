"""Spike (design ref only, never merges): R11-OWNER-FEATURES-SPLIT's fork-server mutation drive.

    cd <base tree>; OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=tests/hastub:tests \
      SPIKE=<swap_run dir> python3 forkdrive.py LINES.json PARTS.json SCRIPT OUT.jsonl \
      [--rows FILE | --n N --seed S] [--workers W] [--null K]

One server process runs SCRIPT span by span under swap_run.Swapper (each part sees only its own
state copy, so a FAIL under a part's span is that part's alone). Before span s it forks one child
per selected row whose first reaching span (lines.json, source order) is s. The child replaces
the code of every live function of the row's module whose code the mutant changes (a gc scan for
functions whose __code__ has that qualname and file), then runs the rest of the script with
fail-fast: the first failed check or raised span ends it, attributed to its span and part.
A row on a module-level line, or whose patch finds no live function or changes free variables,
is refused (printed, not driven): the file-edit drive owns it. `--null K` adds K identity
children (patch nothing) at seeded spans: each must run to the end with no FAIL.
CPU-s is the child's own ru_utime + ru_stime from wait4.
"""
import ast
import json
import marshal
import os
import random
import sys
import types
import gc
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), os.environ["SPIKE"]]
import case_select as cs  # noqa: E402
import mutation_table as mt  # noqa: E402
import swap_run  # noqa: E402
import linereach  # noqa: E402


def _codes(code, out):
    out[code.co_qualname] = code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            _codes(c, out)
    return out


def _sig(code):
    return marshal.dumps(code.replace(co_consts=tuple(
        ("<code>", c.co_qualname) if isinstance(c, types.CodeType) else c for c in code.co_consts)))


def rows_for(lines_path, parts, script):
    rec = json.load(open(lines_path))
    by_line = {}
    for sid, v in rec["lines"].items():
        for x in v:
            by_line.setdefault(tuple(x), set()).add(sid)
    src = open(script, encoding="utf-8").read()
    _, _, spans, _ = cs.split(src, ast.parse(src))
    order = {s.id: i for i, s in enumerate(spans)}
    out, srcc, flc = [], {}, {}
    for p in sorted(Path("tests/mutation_ledger/killed_by").rglob("*.json")):
        row = json.load(open(p))
        if row.get("killed_by") != "tests/features.py":
            continue
        f = row["anchor"].split(":")[0]
        base = os.path.basename(f)
        if f not in srcc:
            srcc[f] = open(f, encoding="utf-8").read().split("\n")
            flc[f] = linereach._func_lines(f)
        cand = [i + 1 for i, t in enumerate(srcc[f]) if t.rstrip("\n") == row["old"]]
        module_level = any(ln not in flc[f] for ln in cand)
        reach = set()
        for ln in cand:
            reach |= by_line.get((base, ln), set())
        first = min((order[s] for s in reach if s in order), default=None)
        out.append({"anchor": row["anchor"], "file": f, "module_level": module_level,
                    "reach_parts": sorted({parts[s] for s in reach if s in parts}),
                    "reach": sorted(reach),
                    "first": first})
    return out, spans


_mut = {}
MC = {}
REAPED = [0.0]


def mutant_codes(anchor, f):
    """{qualname: new code} for every function whose code the mutant changes."""
    if f not in _mut:
        s = (ROOT / f).read_text()
        _mut[f] = (s, {m["anchor"]: m for m in mt.anchor_sites(s, list(mt.candidates(ROOT / f, mt.RATCHETED, s)))})
    s, by = _mut[f]
    m = by.get(anchor)
    if m is None:
        return None
    lines = s.splitlines(True)
    lines[m["line"] - 1] = m["new"] + "\n"
    path = str((ROOT / f).resolve())
    a = _codes(compile(s, path, "exec"), {})
    b = _codes(compile("".join(lines), path, "exec"), {})
    return path, {q: b[q] for q in b if q in a and q != "<module>" and _sig(a[q]) != _sig(b[q])}


def mutant_source(anchor, f):
    mutant_codes(anchor, f)
    s, by = _mut[f]
    m = by.get(anchor)
    if m is None:
        return None
    lines = s.splitlines(True)
    lines[m["line"] - 1] = m["new"] + "\n"
    return str((ROOT / f).resolve()), "".join(lines).encode()


def hook(path, data):
    """Serve the mutated source for one file to the import system (no disk edit, no .pyc)."""
    import importlib.machinery as im
    if any(getattr(m, "__file__", None) and os.path.realpath(m.__file__) == path for m in list(sys.modules.values())):
        return "module already imported"

    class L(im.SourceFileLoader):
        def get_data(self, p):
            if os.path.realpath(p) == path:
                return data
            if p.endswith(".pyc") and os.path.basename(path)[:-3] + "." in os.path.basename(p):
                raise OSError("mutant: no bytecode cache")
            return super().get_data(p)

    class F:
        @staticmethod
        def find_spec(name, target_path=None, target=None):
            spec = im.PathFinder.find_spec(name, target_path)
            if spec is not None and spec.origin and os.path.realpath(spec.origin) == path:
                spec.loader = L(name, spec.origin)
            return spec
    sys.meta_path.insert(0, F)
    return None


def _ps_seconds(t):
    sec = 0.0
    for part in t.strip().split(":"):
        sec = sec * 60 + float(part)
    return sec


def group_cpu(pgid, skip):
    """CPU-s of the live processes in process group `pgid` other than `skip` (solve workers)."""
    import subprocess
    out = subprocess.run(["ps", "-axo", "pgid=,pid=,time="], capture_output=True, text=True).stdout
    tot = 0.0
    for ln in out.splitlines():
        f = ln.split()
        if len(f) == 3 and f[0] == str(pgid) and f[1] != str(skip):
            tot += _ps_seconds(f[2])
    return tot


def patch(path, changed):
    live = [o for o in gc.get_objects() if isinstance(o, types.FunctionType)
            and o.__code__.co_filename == path and o.__code__.co_qualname in changed]
    hit = {o.__code__.co_qualname for o in live}
    if not hit:
        return "no live function"
    for o in live:
        new = changed[o.__code__.co_qualname]
        if new.co_freevars != o.__code__.co_freevars:
            return "free variables change"
        o.__code__ = new
    return None


def main():
    a = sys.argv[1:]
    lines_path, parts_path, script, out_path = a[:4]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d  # noqa: E731
    workers = int(opt("--workers", 4))
    parts = json.load(open(parts_path))
    rows, spans = rows_for(lines_path, parts, script)
    pool = [r for r in rows if r["reach_parts"]]
    if "--rows" in a:
        want = [l.strip() for l in open(opt("--rows", "")) if l.strip()]
        idx = {r["anchor"]: r for r in rows}
        sample = [idx[w] for w in want if w in idx]
    else:
        sample = random.Random(int(opt("--seed", 11))).sample(pool, int(opt("--n", 40)))
    PLAN = "--plan" in a
    needs = {sid: set(v.get("needs", [])) for sid, v in cs.entry(cs.load(), "tests/features.py")["spans"].items()}

    def closure(reach):
        out, todo = set(), list(reach)
        while todo:
            x = todo.pop()
            if x not in out:
                out.add(x)
                todo += list(needs.get(x, ()))
        return out
    twin = int(opt("--twin", 0))
    nulls = random.Random(int(opt("--seed", 11)) + 1).sample(range(len(spans)), int(opt("--null", 0)))
    outf = open(out_path, "a")
    at = {}
    for r in sample:
        if r["first"] is None:
            outf.write(json.dumps({**r, "refused": "no reach"}) + "\n")
            continue
        if r["module_level"]:
            outf.write(json.dumps({"anchor": r["anchor"], "refused": "module-level line: moddrive.py"}) + "\n")
            continue
        at.setdefault(r["first"], []).append(r)
    for rs in at.values():
        for r in rs:
            MC[r["anchor"]] = mutant_source(r["anchor"], r["file"]) if r["module_level"] else mutant_codes(r["anchor"], r["file"])
    if twin:
        for k, (i, rs) in enumerate(sorted(at.items())):
            for r in list(rs):
                if hash(r["anchor"]) % twin == 0 and not r.get("null"):
                    rs.append({"anchor": "TWIN " + r["anchor"], "null": True, "first": i, "reach": r["reach"]})
    for i in nulls:
        at.setdefault(i, []).append({"anchor": f"NULL@{i}", "null": True, "first": i})
    outf.flush()
    print(f"@@ROWS sample {len(sample)} forked {sum(len(v) for v in at.values())} at {len(at)} spans", flush=True)

    src = open(script, encoding="utf-8").read()
    tree = ast.parse(src)
    header, _, spans, tail = cs.split(src, tree)
    flags = cs._flags(header)
    import builtins
    path = os.path.abspath(script)
    module = types.ModuleType("__main__")
    module.__file__ = path
    module.__builtins__ = builtins
    sys.modules["__main__"] = module
    sys.argv[0] = path
    sys.path.insert(0, os.path.dirname(path))
    ns = module.__dict__
    sw = swap_run.Swapper(parts)
    live = {}  # pid -> (row, t0, span index)
    devnull = os.open(os.devnull, os.O_WRONLY)

    def reap(block):
        while live:
            pid, status, ru = os.wait4(-1, 0 if block else os.WNOHANG)
            if pid == 0:
                return
            r, t0, si = live.pop(pid)
            REAPED[0] += ru.ru_utime + ru.ru_stime
            res_path = f"{out_path}.{pid}.res"
            res = json.load(open(res_path)) if os.path.exists(res_path) else {}
            if os.path.exists(res_path):
                os.unlink(res_path)
            outf.write(json.dumps({"anchor": r["anchor"], "null": r.get("null", False),
                                   "reach_parts": r.get("reach_parts"), "fork_span": si,
                                   "cpu_s": round(ru.ru_utime + ru.ru_stime, 2),
                                   "wall_s": round(time.time() - t0, 1), "exit": os.waitstatus_to_exitcode(status),
                                   **res}) + "\n")
            outf.flush()
            print(f"@@DONE {r['anchor']} {res.get('verdict')} {res.get('part')} cpu={ru.ru_utime + ru.ru_stime:.1f}", flush=True)
            if not block:
                continue
            return

    def child(r, si):
        os.setsid()  # own process group: every solve worker it spawns is counted and stopped with it
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        # the persistent solve worker's pipes are the server's: a child spawns its own
        for m in list(sys.modules.values()):
            if getattr(m, "__name__", "").endswith(".coordinator") and hasattr(m, "_PROCESS_WORKER"):
                m._PROCESS_WORKER = None
                for st in [sw.fresh, *sw.slots.values()]:
                    if st and m.__name__ in st["mods"]:
                        st["mods"][m.__name__]["_PROCESS_WORKER"] = None
        res_path = f"{out_path}.{os.getpid()}.res"
        state = {"span": spans[si].id if si >= 0 else "header"}

        plan = closure(r.get("reach", ())) if PLAN and r.get("reach") else None

        def done(verdict, detail=""):
            alive = group_cpu(os.getpid(), os.getpid())
            for m in list(sys.modules.values()):
                if getattr(m, "__name__", "").endswith(".coordinator") and hasattr(m, "_shutdown_process_pool"):
                    try:
                        m._shutdown_process_pool()
                    except Exception:  # noqa: BLE001
                        pass
            import resource; _rc = resource.getrusage(resource.RUSAGE_CHILDREN); json.dump({"worker_cpu_s": round(_rc.ru_utime + _rc.ru_stime + alive, 2), "verdict": verdict, "span": state["span"], "part": parts.get(state["span"], "header"),
                       "detail": detail[:200]}, open(res_path, "w"))
            import signal
            sys.stdout.flush()
            os.killpg(os.getpid(), signal.SIGKILL)  # stops any worker still alive, and this child
            os._exit(0)
        if not r.get("null"):
            mc = MC.get(r["anchor"])
            if mc is None:
                done("refused", "no mutant regenerated")
            why = hook(*mc) if r["module_level"] else patch(*mc)
            if why:
                done("refused", why)
        import harness
        orig = harness.Results.check

        def check(self, name, condition, detail=""):
            ok = orig(self, name, condition, detail)
            if not ok:
                done("killed", name)
            return ok
        harness.Results.check = check
        try:
            if si < 0:
                state["span"] = "header"
                exec(cs._code(header, path, flags), ns)
            for s in spans[max(si, 0):]:
                if plan is not None and s.id not in plan:
                    continue
                state["span"] = s.id
                sw.begin(s.id, s.stmts, ns)
                try:
                    exec(cs._code(s.stmts, path, flags), ns)
                except SystemExit:
                    raise
                except BaseException as e:  # noqa: BLE001
                    done("killed", f"raised {type(e).__name__}: {e}")
            state["span"] = "tail"
            exec(cs._code(tail, path, flags), ns)
        except SystemExit as e:
            if e.code not in (0, None):
                done("killed", f"exit {e.code}")
        done("survived")

    import threading
    sw.begin("header", header, ns)
    for r in at.get(-1, []):
        while len(live) >= workers:
            reap(True)
        sys.stdout.flush()
        pid = os.fork()
        if pid == 0:
            child(r, -1)
        live[pid] = (r, time.time(), -1)
    exec(cs._code(header, path, flags), ns)
    for si, s in enumerate(spans):
        sw.begin(s.id, s.stmts, ns)
        for r in at.get(si, []):
            while len(live) >= workers:
                reap(True)
            sys.stdout.flush()
            nthreads = threading.active_count()
            pid = os.fork()
            if pid == 0:
                child(r, si)
            live[pid] = (r, time.time(), si)
            if nthreads > 1:
                print(f"@@THREADS {nthreads} at fork {si}", flush=True)
        reap(False)
        t = time.process_time()
        try:
            exec(cs._code(s.stmts, path, flags), ns)
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL @raised {type(e).__name__}: {str(e)[:120]}", flush=True)
    while live:
        reap(True)
    import resource
    _s, _c = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    srv = (_s.ru_utime + _s.ru_stime + group_cpu(os.getpgid(0), os.getpid())
           + max(0.0, _c.ru_utime + _c.ru_stime - REAPED[0]))  # the server's own reaped solve workers
    outf.write(json.dumps({"server": True, "cpu_s": round(srv, 2)}) + "\n")
    outf.flush()
    print(f"@@SERVER cpu={srv:.1f} (self + live workers; reaped children excluded: they are the drive's)", flush=True)
    try:
        exec(cs._code(tail, path, flags), ns)
    except SystemExit as e:
        print(f"@@END rc={e.code}", flush=True)
        os._exit(0 if e.code in (0, None) else 1)
    os._exit(0)


if __name__ == "__main__":
    main()
