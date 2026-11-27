"""Spike (design ref only, never merges): R11-OWNER-FEATURES-SPLIT's swap run.

    PYTHONPATH=tests/hastub:tests python3 swap_run.py partition            # step A, prints part counts
    PYTHONPATH=tests/hastub:tests python3 swap_run.py run plain|swap|one [--drop FAMILY] > log

Runs tests/features.py through case_select.run, span by span, printing `@@SPAN <id> <part>`
before each span. `plain` swaps nothing; `swap` keeps one copy of every state family per part
and swaps the entering span's part's copy in at each boundary; `one` maps every span to one
part (the null: no boundary ever swaps). `--drop store` leaves the stub store unswapped (the
perturbation). Diff with `diff.py`.
"""
import ast
import copy
import os
import random
import sys
import types

sys.path.insert(0, "tests")
import case_select as cs  # noqa: E402

PKG = "heatpump_optimizer"
SEAMS = {
    "inputs": "inputs pump_signals pump_mode running_signal flow_meter heat_energy open_meteo external_heat "
              "setpoint_check rooms room_history room_record",
    "model": "thermal_model sysid accuracy comfort_learning curve_learning dhw_learning defrost learner_progress "
             "learning_freeze slab_seed drift flow_lift heat_curve presets batchmath",
    "plan": "optimizer tariff price_model price_tiles pv battery grid_fee currency solve_gate plan_slots plan_step "
            "whatif early_cutoff comfort_band comfort_floor quiet_windows silent_mode freq_control duty_ledger "
            "duty_legs duty_switch wear runs driving_grade process_worker",
    "dhw": "dhw_planner dhw_schedule dhw_draws dhw_start disinfection legionella draw_range wood_fuel circulation",
    "actuation": "pump_arbiter mixing_valve supply_hold flow_limit power_guard boost away off_restore "
                 "number_restore slot_drivers pump_schedule manual_plan climate switch datetime",
}
ORDER = ["inputs", "model", "plan", "dhw", "actuation", "surface"]
MOD2SEAM = {m: s for s, ms in SEAMS.items() for m in ms.split()}
EXCLUDED = {"const", "coordinator", "__init__"}


def _prod_module(path: str) -> str | None:
    if path.startswith("custom_components."):
        path = path[len("custom_components."):]
    if not (path == PKG or path.startswith(PKG + ".")):
        return None
    rest = path[len(PKG):].lstrip(".").split(".")
    return rest[0] if rest and rest[0] else "__init__"


def partition(script="tests/features.py"):
    src = open(script, encoding="utf-8").read()
    tree = ast.parse(src)
    _, _, spans, _ = cs.split(src, tree)
    aliases = cs._aliases(tree)
    out = {}
    for s in spans:
        mods = set()
        for top in s.stmts:
            for n in ast.walk(top):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        m = _prod_module(a.name)
                        if m:
                            mods.add(m)
                elif isinstance(n, ast.ImportFrom) and n.module:
                    for a in n.names:
                        m = _prod_module(f"{n.module}.{a.name}")
                        if m:
                            mods.add(m)
                elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in aliases:
                    m = _prod_module(aliases[n.id])
                    if m:
                        mods.add(m)
        mods -= EXCLUDED
        count = {}
        for m in mods:
            seam = MOD2SEAM.get(m, "surface")
            count[seam] = count.get(seam, 0) + 1
        if not count:
            out[s.id] = "cycle"
        else:
            best = max(count.values())
            out[s.id] = next(p for p in ORDER if count.get(p) == best)
    return out


# ------------------------------------------------------------------ the swap
def _repo_modules():
    return {n: m for n, m in cs._repo_modules().items()}


def _main_classes(ns):
    return [v for v in list(ns.values()) if isinstance(v, type) and getattr(v, "__module__", "") == "__main__"]


class Swapper:
    """A case_select recorder stand-in: begin/end at each span boundary."""

    def __init__(self, parts, drop=()):
        self.parts, self.drop = parts, set(drop)
        self.slots = {}
        self.cur = None
        self.fresh = None
        self.swaps = 0

    def _targets(self, ns):
        mods = _repo_modules()
        classes = []
        for m in mods.values():
            for v in list(vars(m).values()):
                if isinstance(v, type) and getattr(v, "__module__", None) == m.__name__:
                    classes.append(v)
        classes += _main_classes(ns)
        return mods, classes

    def _save(self, ns):
        mods, classes = self._targets(ns)
        st = {"mods": {}, "cls": {}, "cont": {}}
        for name, m in mods.items():
            if "store" in self.drop and name.endswith("helpers.storage"):
                continue
            d = dict(vars(m))
            st["mods"][name] = d
            for k, v in d.items():
                if type(v) in (dict, list, set) and not k.startswith("__"):
                    st["cont"][(name, k)] = (v, copy.copy(v))
        for c in classes:
            try:
                st["cls"][c] = dict(vars(c))
            except Exception:  # noqa: BLE001
                pass
        st["random"] = random.getstate()
        np = sys.modules.get("numpy")
        st["np"] = np.random.get_state() if np is not None else None
        st["environ"] = dict(os.environ)
        st["syspath"] = list(sys.path)
        return st

    def _load(self, st, ns):
        for name, d in st["mods"].items():
            m = sys.modules.get(name)
            if m is None:
                continue
            for k in [k for k, v in list(vars(m).items()) if k not in d and not k.startswith("__")
                      and not isinstance(v, types.ModuleType)]:
                try:
                    delattr(m, k)  # an attribute this part never had: a patch that added a name
                except Exception:  # noqa: BLE001
                    pass
            for k, v in d.items():
                if k.startswith("__"):
                    continue
                if vars(m).get(k, _MISSING) is not v:
                    try:
                        setattr(m, k, v)
                    except Exception:  # noqa: BLE001
                        pass
        for (name, k), (obj, saved) in st["cont"].items():
            if type(obj) is dict:
                if obj != saved or list(obj) != list(saved):
                    obj.clear(); obj.update(saved)
            elif type(obj) is list:
                if obj != saved:
                    obj[:] = saved
            elif obj != saved:
                obj.clear(); obj.update(saved)
        for c, d in st["cls"].items():
            for k in [k for k in list(c.__dict__) if k not in d]:
                try:
                    delattr(c, k)
                except Exception:  # noqa: BLE001
                    pass
            for k, v in d.items():
                if k in ("__dict__", "__weakref__", "__doc__", "__module__"):
                    continue
                try:
                    if c.__dict__.get(k, _MISSING) is not v:
                        setattr(c, k, v)
                except Exception:  # noqa: BLE001
                    pass
        random.setstate(st["random"])
        np = sys.modules.get("numpy")
        if np is not None and st["np"] is not None:
            np.random.set_state(st["np"])
        if os.environ != st["environ"]:
            os.environ.clear(); os.environ.update(st["environ"])
        sys.path[:] = st["syspath"]

    def begin(self, sid, stmts, ns):
        part = self.parts.get(sid, "header")
        if sid != "header":
            if self.fresh is None:
                self.fresh = self._save(ns)  # the state the header leaves: every part starts here
            if part != self.cur:
                if self.cur is not None:
                    self.slots[self.cur] = self._save(ns)
                self._load(self.slots.get(part, self.fresh), ns)
                self.swaps += 1
            self.cur = part
        print(f"@@SPAN {sid} {part}", flush=True)

    def end(self, ns):
        pass


_MISSING = object()


def run_contained(script, sw):
    """case_select.run's loop, with a span's raise printed as one FAIL line and the run going on."""
    import builtins, traceback
    path = os.path.abspath(script)
    source = open(path, encoding="utf-8").read()
    tree = ast.parse(source)
    header, _, spans, tail = cs.split(source, tree)
    flags = cs._flags(header)
    module = types.ModuleType("__main__")
    module.__file__ = path
    module.__builtins__ = builtins
    sys.modules["__main__"] = module
    sys.argv[0] = path
    sys.path.insert(0, os.path.dirname(path))
    ns = module.__dict__
    try:
        sw.begin("header", header, ns)
        exec(cs._code(header, path, flags), ns)
        for s in spans:
            sw.begin(s.id, s.stmts, ns)
            try:
                exec(cs._code(s.stmts, path, flags), ns)
            except Exception as e:  # noqa: BLE001
                print(f"  FAIL @raised {type(e).__name__}: {str(e)[:120]}", flush=True)
                traceback.print_exc(limit=2)
        sys.stdout.flush()
        exec(cs._code(tail, path, flags), ns)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return 0


def main(argv):
    if argv[0] == "partition":
        p = partition()
        from collections import Counter
        print(sorted(Counter(p.values()).items(), key=lambda kv: -kv[1]))
        for sid, part in p.items():
            print(f"{part}\t{sid}")
        return 0
    mode = argv[1]
    drop = argv[argv.index("--drop") + 1:argv.index("--drop") + 2] if "--drop" in argv else []
    script = argv[argv.index("--script") + 1] if "--script" in argv else "tests/features.py"
    if "--parts" in argv:
        import json
        parts = json.load(open(argv[argv.index("--parts") + 1]))
    else:
        parts = partition(script)
    if mode == "one":
        parts = {k: "one" for k in parts}
    sw = Swapper(parts, drop)
    if mode == "plain":
        sw._save = lambda ns: None  # noqa: E731
        sw._load = lambda st, ns: None  # noqa: E731
    rc = run_contained(script, sw)
    print(f"@@END rc={rc} swaps={sw.swaps}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
