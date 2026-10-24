"""Class N-registry-leak enumerator (round 10, D14 steps 3-4).

Seams: every module-level mutable container in custom_components/heatpump_optimizer
that some function in the package mutates (subscript store, setdefault/add/append/
update/__setitem__).  Static half lists them all with their key kind.  Dynamic half
runs N setup->cycle->unload rounds (debug collection on, boost/arbiter state touched)
and, for every registry still holding a torn coordinator, walks gc referents from
the held value (closures followed, module globals not) and reports whether the
value reaches its own key -- the leak mechanism.

Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/N-registry-leak/registry_leak.py
         [--rounds N] [--clean] [--plant]
  --clean : null control; early_cutoff wiring dropped at shutdown (the one judged
            site repaired in memory) -> expect pins_key 0 on every registry, torn_alive 0.
  --plant : with --clean, re-introduce one line: boost._PLAN_BASES value holds the
            coordinator -> expect boost_plan_bases pins_key 1.. and torn_alive>0.
"""
import ast, asyncio, gc, os, sys, types, weakref
from weakref import WeakKeyDictionary
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.."))
PKG = os.path.join(ROOT, "custom_components/heatpump_optimizer")
sys.path.insert(0, os.path.join(ROOT, "dev/audit/rounds/round10/D1/s1"))
MUT = {"setdefault", "add", "append", "update", "__setitem__", "extend", "insert"}


def static_seams():
    out = []
    for fn in sorted(os.listdir(PKG)):
        if not fn.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(PKG, fn)).read())
        names = {}
        for n in tree.body:
            tgt = n.targets[0] if isinstance(n, ast.Assign) else getattr(n, "target", None)
            val = getattr(n, "value", None)
            if isinstance(tgt, ast.Name) and val is not None and (
                isinstance(val, (ast.Dict, ast.Set, ast.List, ast.DictComp))
                or (isinstance(val, ast.Call) and getattr(val.func, "id", getattr(val.func, "attr", ""))
                    in {"dict", "set", "list", "WeakKeyDictionary", "WeakValueDictionary", "defaultdict", "WeakSet", "OrderedDict", "deque"})):
                names[tgt.id] = (n.lineno, ast.unparse(val)[:40])
        mutated = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store) and isinstance(n.value, ast.Name):
                mutated.add(n.value.id)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in MUT and isinstance(n.func.value, ast.Name):
                mutated.add(n.func.value.id)
        for name, (ln, src) in names.items():
            out.append((fn[:-3], name, ln, src, name in mutated))
    return out


def reaches(start, target, cap=50000):
    seen, todo = {id(start)}, [start]
    while todo and len(seen) < cap:
        o = todo.pop()
        if o is target:
            return True
        if isinstance(o, (types.ModuleType, type)):
            continue
        refs = gc.get_referents(o)
        if isinstance(o, types.FunctionType):
            refs = [r for r in refs if r is not o.__globals__]
        for r in refs:
            if id(r) not in seen:
                seen.add(id(r)); todo.append(r)
    return False


async def dynamic(n, clean, plant):
    import rig
    from harness import FakeEntry, ha_setup_entry, ha_unload_entry
    import importlib
    rig.install_inputs()
    gate = rig.Gate(); gate.install(); gate.release.set()
    Coord = rig.cm.HeatPumpOptimizerCoordinator
    from heatpump_optimizer import early_cutoff, boost, pump_arbiter
    if clean:
        orig = Coord.async_shutdown
        async def shut(self):
            await orig(self)
            held = early_cutoff._STATES.get(self)
            if held is not None:
                held.wiring = None
        Coord.async_shutdown = shut
    hass = rig.make_hass()
    entry = FakeEntry(data=dict(rig.CONFIG), options={"debug_collect": True}) if "options" in FakeEntry.__init__.__code__.co_varnames else FakeEntry(data=dict(rig.CONFIG))
    refs = []
    for _ in range(n):
        assert await ha_setup_entry(rig.integration, hass, entry)
        c = entry.runtime_data
        assert await rig.wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
        boost.held_for(c); pump_arbiter.state_for(c)
        if plant:
            boost._PLAN_BASES[c] = {"pin": c}   # the one-line re-introduction
        await asyncio.sleep(0.05)
        await ha_unload_entry(rig.integration, hass, entry)
        refs.append(weakref.ref(c)); del c
    await asyncio.sleep(0.2)
    hass.created.clear(); gc.collect(); gc.collect()
    print(f"RESULT torn_alive={sum(1 for r in refs if r() is not None)} count")
    for mod, name, ln, src, mutated in static_seams():
        m = importlib.import_module(f"heatpump_optimizer.{mod}")
        reg = getattr(m, name, None)
        torn = [r() for r in refs if r() is not None]
        if isinstance(reg, WeakKeyDictionary):
            pins = sum(1 for c in torn if c in reg and reaches(reg[c], c))
            held = sum(1 for c in torn if c in reg)
        elif mutated:
            pins = sum(1 for c in torn if reaches(reg, c)); held = pins
        else:
            continue
        print(f"RESULT {mod}.{name}_held={held} pins_key={pins} count")
    hass.pool.shutdown(wait=True)


if __name__ == "__main__":
    for s in static_seams():
        if s[4]:
            print(f"SEAM {s[0]}.py:{s[2]} {s[1]} = {s[3]}")
    if "--static" not in sys.argv:
        N = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 3
        asyncio.run(dynamic(N, "--clean" in sys.argv or "--plant" in sys.argv, "--plant" in sys.argv))
