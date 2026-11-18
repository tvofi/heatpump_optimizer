#!/usr/bin/env python3
"""Read decision 0018's `operation` and `generality` terms: count a ledger row only on a witness this read produced.

Usage: python3 -I tools/audit/product_reads.py operation --ledger TSV [--repo DIR] [--jobs N]
       python3 -I tools/audit/product_reads.py generality --ledger TSV [--pairs-out TSV] [--repo DIR] [--jobs N]
       python3 -I tools/audit/product_reads.py --self-test
  operation    universe `enumerate.py d16-writes --cells`; a row is `<cell>\t<script>::<check>`. Each cited
               script runs unedited under the launcher, twice as it is, then once per cited (site, cell state)
               with the payload written from that site perturbed, only in arbitration passes whose recorded
               state is the cell's. A row is `moved` (the check turns FAIL or its detail changes, after a
               write from the site in a pass of the cell's state) or `reached` (a hold site: `log_held` called
               from it in a pass of the cell's state before the ok check); both count. The state is read from
               the plan the coordinator held at `pump_arbiter.apply` entry, by plain indexing (STATE_TOKENS);
               a token with no entry prints `state not recorded`. Each moved write is compared with the plan:
               an indoor set-point against `optimal_setpoints[k]` (`target=plan` or `target=differs`).
  generality   universe `enumerate.py d12-cells --pairs`; a row is `<level cell>\t<source>\t<script>::<check>`.
               `reached`: a recorded configuration (a FakeEntry's data and options, or a tests/profiles.py
               profile argument) carried the level before the ok check. `witnessed`, counted: the read's own
               run with only that level's observable switched, in that configuration, to the next level of
               the axis turns the check FAIL or changes its detail. A pair counts when both its level rows are
               witnessed in one configuration of one script; --pairs-out writes those rows in the three-column
               format `enumerate.py d12-cells --pairs --ledger` reads. A bundle or install-report row is never
               re-run with a level switched, so it is printed and never counted.
Every check whose outcome or detail differs between the two unchanged runs is `nondeterministic` and never counted.
Stdout: every universe item with its verdict, the per-site and unlisted-writer lines, then
`RESULT read=<term> universe=N examined=n ...`; exit 0. A missing or empty universe or ledger source, or a
ledger row naming no item, exits 2 with no RESULT line.
Null control: --self-test plants a fake tree (package, harness, scripts) with each control the design names and
reads every verdict; it prints `SELF-TEST passed (N arms)` or names the failing arm and exits 1.
"""
import argparse, ast, collections, concurrent.futures, contextlib, importlib.abc, io, itertools, json, os, runpy, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enumerate as census  # noqa: E402  (tools/audit/enumerate.py, the universes and their refusals)

PKG = census.PKG
RUN_TIMEOUT_S = 900
# A cell token -> what it observes, every comparison against the plan's or the test's own values. A token
# printed by `d16-writes --cells` with no entry here prints `state not recorded` and never counts.
PLAN_STATES = ("idle", "dhw-only", "both", "partial", "full", "min-cold-tank")
# The duty mode each `d16-writes --cells` state runs under (enumerate.STATES, one row per state).
DUTY_OF = dict(census.STATES)
# Option axes -> the const.py names of the configuration keys that carry the level; profile axes -> the
# tests/profiles.py function whose `profile` argument carries it; binary CONF_*_ENTITY axes read the key's
# presence. An axis in none of these prints `no witness` per level (no observable in the stub: language,
# units, Home Assistant versions, operation mode).
OPTION_KEYS = {"layout": ("CONF_TOPOLOGY_LAYOUT",), "pump_duty_mode": ("CONF_PUMP_DUTY_MODE",),
               "compressor_modulation": ("CONF_COMPRESSOR_MODULATION",), "heat_curve_target_kind": ("CONF_HEAT_CURVE_TARGET_KIND",),
               "mixing_valve_mode": ("CONF_MIXING_VALVE_MODE",), "valve_write_target": ("CONF_MIXING_VALVE_WRITE_TARGET_KIND",),
               "combi_tank": ("CONF_DHW_COMBI_TANK_TYPE",), "two_zone_mode": ("CONF_TWO_ZONE_MODE",),
               "space_setpoint_unit": ("CONF_SPACE_SETPOINT_UNIT",), "wood_type": ("CONF_WOOD_TYPE",), "wood_packing": ("CONF_WOOD_PACKING",),
               "price_source": ("CONF_PRICE_SOURCE",), "solar_source": ("CONF_SOLAR_FORECAST_SOURCE",), "grid_fee_mode": ("CONF_GRID_FEE_MODE",),
               "structure": ("CONF_BUILDING_STRUCTURE",), "foundation": ("CONF_BUILDING_FOUNDATION",), "era": ("CONF_BUILDING_ERA",),
               "emitter": ("CONF_UPPER_EMITTER", "CONF_LOWER_EMITTER")}
PROFILE_AXES = {"price_shape": "prices", "climate": "weather"}
RERUN_SOURCES = ("simulation", "property-test")
UNHELD_ENTITY = "sensor.product_reads_unheld"
HOLD_MODULES = ("pump_arbiter", "off_restore", "coordinator", "inputs", "heat_curve")


class Refuse(Exception):
    pass


# ---------------------------------------------------------------- the launcher (runs inside one child process)

def _site(frame, repo):
    return f"{os.path.relpath(frame.f_code.co_filename, repo)}:{frame.f_lineno}"


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _perturb(data):
    """Numbers offset, strings replaced: a check comparing the payload sees a different one."""
    return {k: (v + 7.0 if _num(v) else f"{v}~perturbed" if isinstance(v, str) and k != "entity_id" else v) for k, v in data.items()}


def plan_state(plan, cfg, now, defaults):
    """The pass's state from the plan's own arrays by plain indexing, never a pump_arbiter call. k is the
    largest i with timestamps[i] <= now < the next stamp (the last step lasts as long as the one before it)."""
    get = (lambda key, d=None: cfg.get(key, d)) if hasattr(cfg, "get") else (lambda key, d=None: d)
    st = {"duty": get(defaults["duty_key"], defaults["duty_default"]), "plan": plan is not None, "k": None, "plan_state": None, "setpoint": None}
    ts = list(getattr(plan, "timestamps", None) or [])
    for i, t in enumerate(ts):  # a one-step plan's step has no length (ts[-1] is itself), so no k
        end = ts[i + 1] if i + 1 < len(ts) else t + (t - ts[i - 1])
        if t <= now < end:
            st["k"] = i
    k = st["k"]
    if k is None:
        return st
    at = lambda name: (lambda a: float(a[k]) if a is not None and k < len(a) else None)(getattr(plan, name, None))
    s, d, f, p = at("power_schedule"), at("dhw_power_schedule") or 0.0, getattr(plan, "duty_floor_kw", None), get(defaults["max_key"])
    st["setpoint"] = at("optimal_setpoints")
    if s is None:
        return st
    if s == 0 and d == 0:
        st["plan_state"] = "idle"
    elif s == 0:
        st["plan_state"] = "dhw-only"
    elif d > 0:
        st["plan_state"] = "both"
    elif _num(p) and s == float(p):
        st["plan_state"] = "full"
    elif _num(f) and s == float(f):
        st["plan_state"] = "min-cold-tank"
    elif _num(p) and 0 < s < float(p):
        st["plan_state"] = "partial"
    return st


def token_holds(tok, ps, write):
    """True / False against a recorded pass state (and the write, for a write site), or None: not recorded."""
    if ps is None:
        return False
    # every token is a row of census.STATES: it holds only under the duty mode that row names
    if tok in DUTY_OF and ps["duty"] != DUTY_OF[tok]:
        return False
    first = ps["plan"] and ps["ordinal"] == 0 and not (write or {}).get("unavailable")
    if tok in PLAN_STATES:
        return first and ps["plan_state"] == tok
    if tok in ("observe", "off"):
        return first
    if tok == "baseline":
        return ps["plan"] and ps["k"] is None
    if tok == "restart":
        return ps["ordinal"] > 0
    if tok == "unavailable":
        return None if write is None else bool(write.get("unavailable"))
    return None


class _Hook(importlib.abc.MetaPathFinder):
    """Patch a module's namespace the moment it finishes executing, before any `from x import y` binds."""

    def __init__(self, patches):
        self.patches = patches

    def find_spec(self, name, path, target=None):
        short = name.rsplit(".", 1)[-1]
        if short not in self.patches or (short != "profiles" and "heatpump_optimizer" not in name):
            return None
        for f in sys.meta_path:
            spec = f.find_spec(name, path, target) if f is not self and hasattr(f, "find_spec") else None
            if spec and spec.loader and hasattr(spec.loader, "exec_module"):
                real, patch = spec.loader.exec_module, self.patches[short]
                spec.loader.exec_module = lambda m, real=real, patch=patch: (real(m), patch(m))
                return spec
        return None


def launch(spec):
    """Run one test script under the recorders and write what they saw to spec['out']."""
    repo = Path(spec["repo"]).resolve()
    os.chdir(repo)
    # As `python3 <script>` would: the script's directory first, never this one's (tools/audit shadows names).
    sys.path[:] = [str((repo / spec["script"]).parent), str(repo / "tests")] + [x for x in sys.path[1:] if x != str(Path(__file__).resolve().parent)]
    rec = {"checks": [], "writes": [], "holds": [], "passes": [], "configs": [], "error": None}
    seq, open_passes, ordinals, hasses = itertools.count(), [], {}, []
    pert, switch = spec.get("perturb"), spec.get("switch")
    defaults = spec["defaults"]
    import harness

    real_check = harness.Results.check

    def check(self, name, condition, detail=""):
        rec["checks"].append([next(seq), name, bool(condition), str(detail)])
        return real_check(self, name, condition, detail)

    real_call = harness.FakeServices.async_call

    def call(self, domain, service, data=None, **kw):  # a plain function, so the frame is the caller's (n1)
        site = _site(sys._getframe(1), repo)
        pi = open_passes[-1] if open_passes else None
        ps, hass = (rec["passes"][pi]["state"], hasses[pi]) if pi is not None else (None, None)
        ent = (data or {}).get("entity_id") if isinstance(data, dict) else None
        st = hass.states.get(ent) if hass is not None and isinstance(ent, str) else None
        w = {"seq": next(seq), "site": site, "pass": pi, "service": f"{domain}.{service}",
             "unavailable": (getattr(st, "state", None) == "unavailable") if st is not None else None,
             "payload": {k: v for k, v in (data or {}).items() if _num(v) or isinstance(v, str)} if isinstance(data, dict) else {}}
        if (pert and site == pert["site"] and isinstance(data, dict)
                and all(token_holds(t, ps, w) for t in pert["tokens"])):
            data = _perturb(data)
        rec["writes"].append(w)
        return real_call(self, domain, service, data, **kw)

    real_entry = harness.FakeEntry.__init__

    def entry(self, data=None, options=None, *a, **kw):
        data, options = dict(data or {}), dict(options or {})
        if switch and switch["ordinal"] == len(rec["configs"]):
            for k in switch["keys"]:
                if switch["to"] is None:  # present -> absent
                    data.pop(k, None), options.pop(k, None)
                elif switch["from"] is None:  # absent -> present, an entity no state holds
                    data[k] = switch["to"]
                else:  # one option level -> the next, wherever the level sits
                    for d in (data, options):
                        if d.get(k) == switch["from"]:
                            d[k] = switch["to"]
        merged = {**data, **options}
        rec["configs"].append({"seq": next(seq), "kind": "entry", "values": {k: (v if isinstance(v, str) else None) for k, v in merged.items()
                                                                              if v not in (None, "")}})
        real_entry(self, data, options, *a, **kw)

    harness.Results.check, harness.FakeServices.async_call, harness.FakeEntry.__init__ = check, call, entry

    def ordinal(coord):
        """The coordinator's place among those built (else first seen) on its entry object: a reload builds a
        second coordinator on the same entry. The entry is held, so its id is never reused."""
        e = getattr(coord, "entry", None)
        seen = ordinals.setdefault(id(e), (e, []))[1]
        if not any(c is coord for c in seen):
            seen.append(coord)
        return next(i for i, c in enumerate(seen) if c is coord)

    def patch_arbiter(m):
        real_apply = m.apply

        async def apply(coord, now=None, *a, **kw):
            t = now
            if t is None:
                from homeassistant.util import dt as dt_util
                t = dt_util.now()
            # The plan and configuration as the coordinator holds them, read off its attributes: an extra
            # arbiter_inputs() call would read entities through InputReader, whose log_held this read records.
            plan, cfg = getattr(coord, "_optimization_result", None), None
            with contextlib.suppress(Exception):
                cfg = coord.effective_config
            if not hasattr(cfg, "get"):
                cfg = getattr(coord, "_config", None) or {}
            ps = plan_state(plan, cfg, t, defaults)
            ps["ordinal"] = ordinal(coord)
            rec["passes"].append({"state": ps})
            hasses.append(getattr(coord, "hass", None))
            open_passes.append(len(rec["passes"]) - 1)
            try:
                return await real_apply(coord, now, *a, **kw)
            finally:
                open_passes.pop()

        m.apply = apply
        patch_holds(m)

    def patch_holds(m):
        real = getattr(m, "log_held", None)
        if real is None:
            return

        def held(*a, **kw):
            rec["holds"].append({"seq": next(seq), "site": _site(sys._getframe(1), repo), "pass": open_passes[-1] if open_passes else None})
            return real(*a, **kw)

        m.log_held = held

    def patch_coordinator(m):
        patch_holds(m)
        cls = getattr(m, "HeatPumpOptimizerCoordinator", None)
        if cls is not None:
            real_init = cls.__init__

            def init(self, *a, **kw):
                real_init(self, *a, **kw)
                ordinal(self)  # built on its entry: the ordinal is the construction order, not the first pass

            cls.__init__ = init

    def patch_profiles(m):
        for fn in ("prices", "weather"):
            real = getattr(m, fn, None)
            if real is None:
                continue

            def wrapped(profile, *a, _real=real, _fn=fn, **kw):
                n = len(rec["configs"])
                if switch and switch["ordinal"] == n:
                    profile = switch["to"]
                rec["configs"].append({"seq": next(seq), "kind": _fn, "values": {"profile": profile}})
                return _real(profile, *a, **kw)

            setattr(m, fn, wrapped)

    patches = {mod: patch_holds for mod in HOLD_MODULES}
    patches.update(pump_arbiter=patch_arbiter, coordinator=patch_coordinator, profiles=patch_profiles)
    sys.meta_path.insert(0, _Hook(patches))
    sys.argv = [spec["script"]]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(spec["script"], run_name="__main__")
    except SystemExit:
        pass
    except BaseException as e:  # noqa: BLE001 - recorded: checks after the raise never ran
        rec["error"] = f"{type(e).__name__}: {e}"
    Path(spec["out"]).write_text(json.dumps(rec, default=str))


# ---------------------------------------------------------------- the parent: universes, runs, verdicts

def const_values(repo):
    tree = census.parse(Path(repo) / PKG / "const.py")
    out = {}
    for n in tree.body:
        tgt = n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else getattr(n, "target", None)
        val = getattr(n, "value", None)
        if isinstance(tgt, ast.Name) and isinstance(val, ast.Constant):
            out[tgt.id] = val.value
    return out


def defaults_of(repo):
    c = const_values(repo)
    return {"duty_key": c.get("CONF_PUMP_DUTY_MODE", "pump_duty_mode"), "duty_default": c.get("DEFAULT_PUMP_DUTY_MODE"),
            "max_key": c.get("CONF_HEAT_PUMP_MAX_POWER", "heat_pump_max_power")}


def universe(repo, name, **kw):
    with contextlib.redirect_stderr(io.StringIO()):
        items = census.run(name, repo, **kw)
    return [l.split("\t")[0] for l in items]


def read_ledger(path, items, three):
    rows = []
    text = Path(path).read_text()
    for i, l in enumerate(text.splitlines(), 1):
        if not l.strip() or l.startswith("#"):
            continue
        c = [x.strip() for x in l.split("\t")]
        if len(c) != 2 + three or "::" not in c[-1] or (three and c[1] not in census.SOURCES):
            raise Refuse(f"{path}:{i}: a row is the item, " + ("its source, " if three else "") + "and `<script>::<check>`, tab-separated")
        if c[0] not in items:
            raise Refuse(f"{path}:{i}: {c[0]!r} is no item of this universe as printed")
        script, _, chk = c[-1].partition("::")
        rows.append({"item": c[0], "source": c[1] if three else None, "script": script, "check": chk})
    if not rows:
        raise Refuse(f"{path}: no ledger row: a read with nothing cited examines nothing")
    return rows


def run_script(repo, script, defaults, **extra):
    with tempfile.TemporaryDirectory() as d:
        spec = {"repo": str(repo), "script": script, "defaults": defaults, "out": str(Path(d) / "rec.json"), **extra}
        env = {**os.environ, "PYTHONPATH": str(Path(repo).resolve() / "tests" / "hastub")}
        try:
            subprocess.run([sys.executable, str(Path(__file__).resolve()), "_launch", json.dumps(spec)], cwd=repo, env=env,
                           capture_output=True, text=True, timeout=RUN_TIMEOUT_S)
            rec = json.loads(Path(spec["out"]).read_text())
        except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError) as e:
            rec = {"checks": [], "writes": [], "holds": [], "passes": [], "configs": [], "error": f"launcher: {e}"}
    keyed, n = {}, collections.Counter()
    for s, name, ok, detail in rec["checks"]:
        n[name] += 1
        keyed[name if n[name] == 1 else f"{name} #{n[name]}"] = {"seq": s, "ok": ok, "detail": detail}
    rec["by_check"] = keyed
    return rec


def moved(base, other, key):
    """Called only on a check that passed at the head: each read prints `FAIL at the head` first."""
    a, b = base["by_check"].get(key), other["by_check"].get(key)
    return a is not None and b is not None and (not b["ok"] or b["detail"] != a["detail"])


class Runs:
    """Every script run the reads need, each made once, in parallel."""

    def __init__(self, repo, jobs):
        self.repo, self.defaults, self.jobs, self.cache = Path(repo), defaults_of(repo), jobs, {}

    def get(self, wanted):
        todo = [w for w in dict.fromkeys(wanted) if w not in self.cache]
        with concurrent.futures.ThreadPoolExecutor(max(1, self.jobs)) as ex:
            futs = {w: ex.submit(run_script, self.repo, w[0], self.defaults, **dict(json.loads(w[1]))) for w in todo}
            for w, f in futs.items():
                self.cache[w] = f.result()

    def __getitem__(self, w):
        return self.cache[w]


def key(script, run=0, **extra):
    return (script, json.dumps(sorted(extra.items())), run)


def baseline(runs, script):
    a, b = runs[key(script, 0)], runs[key(script, 1)]
    nondet = {k for k in set(a["by_check"]) | set(b["by_check"])
              if (a["by_check"].get(k) or {}).get("ok") != (b["by_check"].get(k) or {}).get("ok")
              or (a["by_check"].get(k) or {}).get("detail") != (b["by_check"].get(k) or {}).get("detail")}
    return a, nondet


def read_operation(repo, ledger, jobs):
    items = universe(repo, "d16-writes", cells=True)
    rows = read_ledger(ledger, set(items), False)
    sites = {l.split(" ")[1] for l in universe(repo, "d16-writes")}
    for r in rows:
        head, *toks = [x.strip() for x in r["item"].split("|")]
        r["kind"], r["site"], r["tokens"] = head.split(" ")[0], head.split(" ")[1], toks
    runs = Runs(repo, jobs)
    scripts = sorted({r["script"] for r in rows})
    want = [key(s, i) for s in scripts for i in (0, 1)]
    want += [key(r["script"], perturb={"site": r["site"], "tokens": r["tokens"]}) for r in rows if r["kind"] == "write"]
    runs.get(want)
    verdicts, out = collections.defaultdict(list), []
    for r in rows:
        base, nondet = baseline(runs, r["script"])
        c = base["by_check"].get(r["check"])
        evs = base["writes"] if r["kind"] == "write" else base["holds"]
        at_site = [e for e in evs if e["site"] == r["site"] and (c is None or e["seq"] < c["seq"])]
        states = [(e, base["passes"][e["pass"]]["state"] if e["pass"] is not None else None) for e in at_site]
        match = [e for e, ps in states if all(token_holds(t, ps, e if r["kind"] == "write" else None) for t in r["tokens"])]
        unrec = [t for t in r["tokens"] if any(token_holds(t, ps, e if r["kind"] == "write" else None) is None for e, ps in states if ps)]
        if c is None:
            v = f"not witnessed: unknown check{' (' + base['error'] + ')' if base['error'] else ''}"
        elif not c["ok"]:
            v = "not witnessed: FAIL at the head"
        elif r["check"] in nondet:
            v = "not witnessed: nondeterministic"
        elif not at_site:
            v = "not witnessed: site never reached before the check"
        elif unrec:
            v = f"not witnessed: state not recorded ({', '.join(sorted(set(unrec)))})"
        elif not match:
            got = sorted({_state_text(ps, e) for e, ps in states})
            v = f"not witnessed: state differs (recorded {'; '.join(got)})"
        elif r["kind"] == "hold":
            v = "reached"
        elif not moved(base, runs[key(r["script"], perturb={"site": r["site"], "tokens": r["tokens"]})], r["check"]):
            v = "not witnessed: the check does not move"
        else:
            v = "moved\t" + _target(match[-1], base["passes"][match[-1]["pass"]]["state"])
        verdicts[r["item"]].append(f"{r['script']}::{r['check']}\t{v}")
    for it in items:
        out += [f"{it}\t{v}" for v in verdicts.get(it, ["not run"])]
    counted = {it for it, vs in verdicts.items() if any("\tmoved" in v or v.endswith("\treached") for v in vs)}
    n_moved = sum(v.split("\t")[1] == "moved" for vs in verdicts.values() for v in vs)
    n_reached = sum(v.endswith("\treached") for vs in verdicts.values() for v in vs)
    seen_out, unlisted = collections.Counter(), collections.Counter()
    for s in scripts:
        rec = runs[key(s, 0)]
        for e in rec["writes"] + rec["holds"]:
            if e["pass"] is None and e["site"] in sites:
                seen_out[e["site"]] += 1
        for e in rec["writes"]:
            if e["site"].startswith(PKG + "/") and e["site"] not in sites:
                unlisted[e["site"]] += 1
        no_cfg = sum(1 for e in rec["writes"] if e["pass"] is None)
        out.append(f"script {s}\tchecks={len(rec['by_check'])}\twrites outside every pass={no_cfg}" + (f"\terror={rec['error']}" if rec["error"] else ""))
    out += [f"outside every pass {site}\t{n} (never witnessable: no plan)" for site, n in sorted(seen_out.items())]
    out += [f"unlisted writer {site}\t{n}" for site, n in sorted(unlisted.items())]
    out.append(f"RESULT read=operation universe={len(items)} examined={len(counted)} moved={n_moved} reached={n_reached}")
    return out


def _state_text(ps, e):
    if ps is None:
        return "outside every pass"
    return (f"duty={ps['duty']} plan={ps['plan_state'] or ('none' if not ps['plan'] else 'k=none' if ps['k'] is None else 'unread')} "
            f"ordinal={ps['ordinal']}" + (f" unavailable={e.get('unavailable')}" if e and "unavailable" in e else ""))


def _target(w, ps):
    sent = w["payload"].get("temperature") if w["service"].endswith(".set_temperature") else None
    if sent is None or ps["setpoint"] is None:
        return "target=no plan value"
    return "target=plan" if float(sent) == ps["setpoint"] else f"target=differs plan={ps['setpoint']} sent={sent}"


def observables(repo, axes):
    """{axis: ('keys', (key, ...)) | ('presence', key) | ('profile', fn)} or a `no witness` reason."""
    c = const_values(repo)
    out = {}
    for a in axes:
        if a in PROFILE_AXES:
            out[a] = ("profile", PROFILE_AXES[a])
        elif a in OPTION_KEYS:
            ks = [c.get(n) for n in OPTION_KEYS[a]]
            out[a] = ("keys", tuple(ks)) if all(isinstance(k, str) for k in ks) else f"no witness: {', '.join(OPTION_KEYS[a])} not in const.py"
        elif a.startswith("CONF_") and axes[a] == ["absent", "present"]:
            out[a] = ("presence", c[a]) if isinstance(c.get(a), str) else f"no witness: {a} not in const.py"
        else:
            out[a] = "no witness: no observable in the stub"
    return out


def carried(cfg, obs, level):
    kind, what = obs
    v = cfg["values"]
    if kind == "profile":
        return cfg["kind"] == what and v.get("profile") == level
    if cfg["kind"] != "entry":
        return False
    if kind == "presence":
        return (what in v) == (level == "present")
    return any(v.get(k) == level for k in what)


def switch_of(obs, axis_levels, level, ordinal):
    kind, what = obs
    nxt = axis_levels[(axis_levels.index(level) + 1) % len(axis_levels)]
    if kind == "presence":
        return {"ordinal": ordinal, "keys": [what], "from": None if level == "absent" else level,
                "to": UNHELD_ENTITY if level == "absent" else None}
    return {"ordinal": ordinal, "keys": list(what) if kind == "keys" else [], "from": level, "to": nxt}


def read_generality(repo, ledger, jobs, pairs_out=None):
    with contextlib.redirect_stderr(io.StringIO()):
        axes, _ = census.population_axes(Path(repo))
    items = universe(repo, "d12-cells", pairs=True)
    levels = [l for l in items if l.startswith("level ")]
    rows = read_ledger(ledger, set(levels), True)
    obs = observables(repo, axes)
    runs = Runs(repo, jobs)
    scripts = sorted({r["script"] for r in rows if r["source"] in RERUN_SOURCES})
    runs.get([key(s, i) for s in scripts for i in (0, 1)])
    plan = []
    for r in rows:
        r["axis"], _, r["level"] = r["item"][len("level "):].partition("=")
        o = obs.get(r["axis"])
        r["ordinal"] = None
        if r["source"] in RERUN_SOURCES and isinstance(o, tuple):
            base, _ = baseline(runs, r["script"])
            c = base["by_check"].get(r["check"])
            before = [i for i, cfg in enumerate(base["configs"]) if c and cfg["seq"] < c["seq"] and carried(cfg, o, r["level"])]
            if before:
                r["ordinal"] = before[-1]
                r["switch"] = switch_of(o, axes[r["axis"]], r["level"], r["ordinal"])
                plan.append(key(r["script"], switch=r["switch"]))
    runs.get(plan)
    verdicts, witnessed = collections.defaultdict(list), collections.defaultdict(set)
    for r in rows:
        o = obs.get(r["axis"])
        if not isinstance(o, tuple):
            v = o
        elif r["source"] not in RERUN_SOURCES:
            v = f"not witnessed: source {r['source']} is never re-run with a level switched"
        else:
            base, nondet = baseline(runs, r["script"])
            c = base["by_check"].get(r["check"])
            if c is None:
                v = "not witnessed: unknown check" + (f" ({base['error']})" if base["error"] else "")
            elif not c["ok"]:
                v = "not witnessed: FAIL at the head"
            elif r["check"] in nondet:
                v = "not witnessed: nondeterministic"
            elif r["ordinal"] is None:
                v = "not witnessed: no recorded configuration carried the level before the check"
            elif not moved(base, runs[key(r["script"], switch=r["switch"])], r["check"]):
                v = f"reached (configuration {r['ordinal']}): the check does not move with the level switched"
            else:
                v = f"witnessed (configuration {r['ordinal']})"
                witnessed[(r["script"], r["ordinal"])].add((r["axis"], r["level"], r["check"]))
        verdicts[r["item"]].append(f"{r['source']}\t{r['script']}::{r['check']}\t{v}")
    pair_rows = {}
    for (script, _o), lv in witnessed.items():
        for (a, x, ca), (b, y, _cb) in itertools.combinations(sorted(lv), 2):
            if a != b:
                pair_rows.setdefault(f"pair {a}={x} & {b}={y}", f"simulation\t{script}::{ca}")
    out = []
    for it in items:
        if it in pair_rows:
            out.append(f"{it}\t{pair_rows[it]}\twitnessed (both levels, one configuration)")
        else:
            out += [f"{it}\t{v}" for v in verdicts.get(it, ["not run"])]
    if pairs_out:
        Path(pairs_out).write_text("".join(f"{p}\t{t}\n" for p, t in sorted(pair_rows.items())))
    lv_counted = {it for it, vs in verdicts.items() if any("\twitnessed" in v for v in vs)}
    reached = {it for it, vs in verdicts.items() if any("\treached" in v for v in vs)} - lv_counted
    for s in scripts:
        rec = runs[key(s, 0)]
        out.append(f"script {s}\tchecks={len(rec['by_check'])}\tconfigurations={len(rec['configs'])}"
                   f"\tchecks with no recorded configuration={sum(1 for c in rec['by_check'].values() if not any(f['seq'] < c['seq'] for f in rec['configs']))}"
                   + (f"\terror={rec['error']}" if rec["error"] else ""))
    out.append(f"RESULT read=generality universe={len(items)} examined={len(lv_counted) + len(pair_rows)} "
               f"levels={len(lv_counted)} pairs={len(pair_rows)} reached-only={len(reached)}")
    return out


# ---------------------------------------------------------------- self-test

FAKE_HARNESS = '''
class Results:
    def __init__(self, title):
        self.failures = 0
    def check(self, name, condition, detail=""):
        self.failures += not condition
        return bool(condition)
class FakeServices:
    def __init__(self):
        self.calls = []
    async def async_call(self, domain, service, data=None, **kw):
        self.calls.append((domain, service, data))
class FakeState:
    def __init__(self, state):
        self.state = state
class FakeStates(dict):
    pass
class FakeHass:
    def __init__(self, states=None):
        self.services, self.states = FakeServices(), FakeStates(states or {})
class FakeEntry:
    def __init__(self, data=None, options=None, *, entry_id="e"):
        self.data, self.options, self.entry_id = dict(data or {}), dict(options or {}), entry_id
'''
FAKE_ARBITER = '''from .log_latch import log_held
from . import off_restore
async def apply(coord, now=None):
    p = coord._optimization_result
    if coord.hold:
        log_held("held") if coord.hold is True else off_restore.arm() if coord.hold == "restore" else coord.held()
        return
    await coord.hass.services.async_call("climate", "set_temperature", {"entity_id": "climate.x", "temperature": p.optimal_setpoints[0] + coord.offset})
    if coord.extra:
        await coord.hass.services.async_call("number", "set_value", {"entity_id": "number.y", "value": 3.0})
        svc = coord.hass.services
        await svc.async_call("switch", "turn_on", {"entity_id": "switch.z"})
async def direct(hass):
    await hass.services.async_call("light", "turn_on", {"entity_id": "light.q"})
'''
FAKE_COORDINATOR = '''from .log_latch import log_held
class HeatPumpOptimizerCoordinator:
    def __init__(self, hass, entry, plan):
        self.hass, self.entry, self._optimization_result = hass, entry, plan
        self.hold, self.offset, self.extra, self._config = False, 0.0, False, {}
    @property
    def effective_config(self):
        return {"pump_duty_mode": "control"}
    def held(self):
        return log_held("coordinator")
'''
FAKE_SCRIPT = '''import asyncio, os, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from types import SimpleNamespace as NS
from harness import FakeEntry, FakeHass, FakeState, Results
from heatpump_optimizer import pump_arbiter, off_restore
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Real
import profiles
T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
def plan():
    return NS(timestamps=[T0, T0 + timedelta(minutes=15)], power_schedule=[0.0, 0.0],
              dhw_power_schedule=[0.0, 0.0], optimal_setpoints=[21.0, 21.0], duty_floor_kw=None)
def hass(device="heat"):
    return FakeHass({"climate.x": FakeState(device)})
def coord(hold=False, entry=None, device="heat", offset=0.0, extra=False):
    return NS(hass=hass(device), hold=hold, _config={"pump_duty_mode": "control"}, entry=entry or NS(), offset=offset, extra=extra,
              _optimization_result=plan())
def sent(c, field="temperature"):
    return [d[field] for _d, _s, d in c.hass.services.calls if field in d]
r = Results("fake")
first = coord(); asyncio.run(pump_arbiter.apply(first, T0))
r.check("payload", sent(first) == [21.0], str(sent(first)))
r.check("constant", True)
held = coord(hold=True); asyncio.run(pump_arbiter.apply(held, T0))
r.check("held", True)
restored = coord(hold="restore"); asyncio.run(pump_arbiter.apply(restored, T0))
r.check("restored", True)
again = coord(entry=first.entry); asyncio.run(pump_arbiter.apply(again, T0))
r.check("restart-payload", sent(again) == [21.0], str(sent(again)))
gone = coord(device="unavailable"); asyncio.run(pump_arbiter.apply(gone, T0))
r.check("unavailable-payload", sent(gone) == [21.0])
e = FakeEntry({"a_entity": "sensor.a", "mode": "m1"}, {"b_entity": "sensor.b"})
r.check("has-a", "a_entity" in e.data)
r.check("has-b", "b_entity" in e.options)
r.check("mode-is-m1", e.data.get("mode") == "m1")
r.check("mode-detail", True, str(e.data.get("mode")))
r.check("mode-steady", True, str(e.data.get("a_entity")))
r.check("const-after-config", True)
r.check("counter", True, str(os.getpid()))
e2 = FakeEntry({"mode": "m2"})
r.check("mode-is-m2", e2.data.get("mode") == "m2")
r.check("price", profiles.prices("p1", 0) == "p1")
two = coord(extra=True); asyncio.run(pump_arbiter.apply(two, T0))
r.check("other-payload", sent(two, "value") == [3.0], str(sent(two, "value")))
off = coord(offset=1.0); asyncio.run(pump_arbiter.apply(off, T0))
r.check("differs-payload", sent(off) == [22.0], str(sent(off)))
r.check("differs-detail", True, str(sent(off)))
r.check("steady-detail", True, str(sent(held)))
late = coord(); asyncio.run(pump_arbiter.apply(late))
r.check("now-none-payload", sent(late) == [21.0], str(sent(late)))
ent = NS()
ra, rb = Real(hass(), ent, plan()), Real(hass(), ent, plan())
asyncio.run(pump_arbiter.apply(rb, T0))
r.check("built-second-payload", sent(rb) == [21.0], str(sent(rb)))
rc = Real(hass(), NS(), plan()); rc.hold = "coordinator"; asyncio.run(pump_arbiter.apply(rc, T0))
r.check("coordinator-held", True)
asyncio.run(pump_arbiter.direct(FakeHass()))
r.check("direct-hold", off_restore.arm() == "restore")
r.check("always-fails", False)
r.check("argv", sys.argv == ["tests/fake_script.py"], str(sys.argv))
r.check("check-returns", r.check("inner", True) is True)
e3 = FakeEntry({})
profiles.prices("p2", 0)
r.check("no-c", "c_entity" not in e3.data)
e4 = FakeEntry({"mode": "m1", "mode2": "m2"})
r.check("e4-m1", e4.data.get("mode") == "m1")
r.check("e4-m2", e4.data.get("mode2") == "m2")
pp, ww = profiles.prices("p1", 0), profiles.weather("p1", 0)
r.check("price-late", pp == "p1")
r.check("weather-late", ww == "p1")
raise RuntimeError("planted")
'''


def plant(root):
    P = root / PKG
    for d in ("tests/hastub/homeassistant/util", "dev/audit/config", "blueprints", f"{PKG}/www"):
        (root / d).mkdir(parents=True, exist_ok=True)
    w = lambda p, t: (root / p).write_text(t)
    w(f"{PKG}/__init__.py", "")
    w(f"{PKG}/const.py", "PUMP_DUTY_MODES = ('off', 'observe', 'control')\nCONF_PUMP_DUTY_MODE = 'pump_duty_mode'\nDEFAULT_PUMP_DUTY_MODE = 'off'\n"
      "CONF_A_ENTITY = 'a_entity'\nCONF_B_ENTITY = 'b_entity'\nCONF_C_ENTITY = 'c_entity'\nMODES = ('m1', 'm2')\nGRID = ('g1', 'g2')\n"
      "CONF_GRID = 'grid'\nCONF_MODE = 'mode'\nCONF_MODE2 = 'mode2'\n")
    w(f"{PKG}/config_flow.py", "X = (CONF_A_ENTITY, CONF_B_ENTITY, CONF_C_ENTITY)\n")
    w(f"{PKG}/log_latch.py", "def log_held(key):\n    return key\n")
    w(f"{PKG}/off_restore.py", "from .log_latch import log_held\ndef arm():\n    return log_held('restore')\n")
    w(f"{PKG}/pump_arbiter.py", FAKE_ARBITER)
    w(f"{PKG}/coordinator.py", FAKE_COORDINATOR)
    w("tests/dies.py", "import os\nos._exit(3)\n")
    w(f"{PKG}/www/card.js", "")
    w("tests/harness.py", FAKE_HARNESS)
    w("tests/profiles.py", "def prices(profile, s):\n    if profile == 'p1':\n        pass\n    elif profile == 'p2':\n        pass\n    return profile\n"
      "def weather(profile, s):\n    if profile == 'p1':\n        pass\n    elif profile == 'w2':\n        pass\n    return profile\n")
    w("tests/fake_script.py", FAKE_SCRIPT)
    for p in ("tests/hastub/homeassistant/__init__.py", "tests/hastub/homeassistant/util/__init__.py"):
        w(p, "")
    w("tests/hastub/homeassistant/util/dt.py", "import datetime\ndef now():\n    return datetime.datetime.now(datetime.timezone.utc)\n")
    w(census.OBJECTIVE, json.dumps({"population": [
        {"axis": "mode", "kind": "tuple", "file": f"{PKG}/const.py", "symbol": "MODES"},
        {"axis": "grid", "kind": "tuple", "file": f"{PKG}/const.py", "symbol": "GRID"},
        {"axis": "optional_entity", "kind": "name", "file": f"{PKG}/config_flow.py", "pattern": "CONF_[A-Z0-9_]+_ENTITY", "binary": True},
        {"axis": "price_shape", "kind": "compare", "file": "tests/profiles.py", "function": "prices", "argument": "profile"},
        {"axis": "climate", "kind": "compare", "file": "tests/profiles.py", "function": "weather", "argument": "profile"}]}))


def self_test():
    arms, fails = 0, []

    def arm(name, got, want):
        nonlocal arms
        arms += 1
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    S = "tests/fake_script.py::"
    A = f"{PKG}/pump_arbiter.py"
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        plant(root)
        global OPTION_KEYS
        saved, OPTION_KEYS = OPTION_KEYS, {"mode": ("CONF_MODE", "CONF_MODE2"), "grid": ("CONF_GRID",)}
        try:
            cells = universe(root, "d16-writes", cells=True)
            W, W2, WD = f"write {A}:8 apply domain=climate", f"write {A}:10 apply domain=number", f"write {A}:14 direct domain=light"
            H = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {A}"))
            arm("the fake write sites are the arbiter's three `.services.async_call` lines, not the aliased fourth",
                sorted({c.split(" |")[0] for c in cells if c.startswith("write ")}), sorted([W, W2, WD]))
            R = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {PKG}/off_restore.py"))
            HC = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {PKG}/coordinator.py"))
            led = root / "op.tsv"
            ops = [(f"{W} | idle", "payload"), (f"{W} | idle", "constant"),
                   (f"{W} | idle", "restart-payload"), (f"{W} | restart", "payload"),
                   (f"{W} | upgrade", "payload"), (f"{H} | idle", "held"),
                   (f"{W} | off", "payload"), (f"{W} | restart", "restart-payload"),
                   (f"{W} | idle", "nosuch"), (f"{W} | unavailable", "unavailable-payload"),
                   (f"{W} | idle", "unavailable-payload"), (f"{W} | idle", "counter"),
                   (f"{R} | idle", "restored"), (f"{W} | idle", "other-payload"),
                   (f"{W2} | idle", "other-payload"), (f"{H} | off", "held"),
                   (f"{W} | idle", "differs-payload"), (f"{W} | baseline", "now-none-payload"),
                   (f"{W} | restart", "built-second-payload"), (f"{HC} | idle", "coordinator-held"),
                   (f"{WD} | idle", "direct-hold"), (f"{W} | idle", "always-fails"),
                   (f"{W} | idle", "differs-detail"), (f"{W} | idle", "steady-detail")]
            led.write_text("# a comment and a blank line are skipped\n\n" + "".join(f"{c}\t{S}{k}\n" for c, k in ops)
                           + f"{W} | idle\ttests/dies.py::x\n")
            out = read_operation(root, led, 4)
            base = run_script(root, "tests/fake_script.py", defaults_of(root))
            full = {tuple(l.split("\t")[:2]): "\t".join(l.split("\t")[2:]) for l in out if "\t" in l and "::" in l}
            got = {k: x.split("\t")[0] for k, x in full.items()}
            v = lambda i: got[(ops[i][0], S + ops[i][1])]
            arm("null: a check comparing the payload, its running cell: moved", v(0), "moved")
            arm("null: the target half reads the plan's set-point", next(l for l in out if l.startswith(ops[0][0]) and S + "payload" in l).endswith("target=plan"), True)
            arm("planted (i): a constant-condition check does not move", v(1), "not witnessed: the check does not move")
            arm("planted v2-1: a check on the restart write, a running write before it, cited for running: perturbing running passes only",
                v(2), "not witnessed: the check does not move")
            arm("planted (iii): a first-coordinator check cited for restart: state differs", v(3).startswith("not witnessed: state differs"), True)
            arm("planted (iv): a token with no table entry", v(4), "not witnessed: state not recorded (upgrade)")
            arm("null: a hold under the per-module log_held patch is reached", v(5), "reached")
            arm("planted: another duty mode differs", v(6).startswith("not witnessed: state differs"), True)
            arm("null: a second coordinator on one entry is restart, and moves", v(7), "moved")
            arm("planted: an unknown check, the script's own raise printed with it", v(8), "not witnessed: unknown check (RuntimeError: planted)")
            arm("null: a write to an unavailable entity, its unavailable cell: moved", v(9), "moved")
            arm("planted: the unavailable write's check cited for running: only running passes perturbed, it does not move",
                v(10), "not witnessed: the check does not move")
            arm("planted: a check whose detail embeds a counter is never moved", v(11), "not witnessed: nondeterministic")
            arm("null: a hold in a second importing module (off_restore) is reached", v(12), "reached")
            arm("planted: a check moved only by a second site's write, cited for the first site: only the cited site is perturbed",
                v(13), "not witnessed: the check does not move")
            arm("null: the second site's own check moves; a write with no set-point reads no plan value", full[(ops[14][0], S + ops[14][1])],
                "moved\ttarget=no plan value")
            arm("planted: a hold whose recorded state differs is not reached", v(15).startswith("not witnessed: state differs (recorded duty=control"), True)
            arm("planted: a set-point the plan does not hold", full[(ops[16][0], S + ops[16][1])], "moved\ttarget=differs plan=21.0 sent=22.0")
            arm("null: a pass with no `now` reads the clock: past the plan, it is baseline", v(17), "moved")
            arm("null: the real coordinator class built second on one entry and applied first is restart (construction order)", v(18), "moved")
            arm("null: a hold in the coordinator module is reached", v(19), "reached")
            arm("planted: a write outside every pass", v(20), "not witnessed: state differs (recorded outside every pass)")
            arm("planted: a FAIL at the head", v(21), "not witnessed: FAIL at the head")
            arm("null: a check that stays ok while only its detail moves under the perturbed payload: moved", full[(ops[22][0], S + ops[22][1])],
                "moved\ttarget=differs plan=21.0 sent=22.0")
            arm("planted: a check that stays ok with a detail the perturbed site does not reach does not move", v(23),
                "not witnessed: the check does not move")
            arm("planted: a launcher that dies before writing its record",
                got[(f"{W} | idle", "tests/dies.py::x")].startswith("not witnessed: unknown check (launcher: "), True)
            n_checks = len(base["by_check"])
            arm("per-script, outside-every-pass and unlisted-writer lines", [l for l in out if not l.startswith(("write ", "hold ", "RESULT"))],
                ["script tests/dies.py\tchecks=0\twrites outside every pass=0\terror=launcher: " + next(
                    l for l in out if l.startswith("script tests/dies.py")).split("error=launcher: ")[1],
                 f"script tests/fake_script.py\tchecks={n_checks}\twrites outside every pass=1\terror=RuntimeError: planted",
                 f"outside every pass {R.split(' ')[1]}\t1 (never witnessable: no plan)",
                 f"outside every pass {A}:14\t1 (never witnessable: no plan)", f"unlisted writer {A}:12\t1"])
            arm("RESULT counts distinct cells", out[-1], f"RESULT read=operation universe={len(cells)} examined=8 moved=8 reached=3")
            arm("planted (ii): a site never reached", _never_reached(root, S), "not witnessed: site never reached before the check")
            arm("null: no site perturbed turns no check but the planted FAIL (the recorders keep each return value and argv)",
                sorted(k for k, c in base["by_check"].items() if not c["ok"]), ["always-fails"])
            only_latch = _only_latch(root)
            arm("planted r1: log_held patched only in log_latch reaches nothing", only_latch, 0)
            for name, plan, cfg, want in _plan_cases():
                arm(f"plan state: {name}", plan_state(plan, cfg, _T0, {"duty_key": "pump_duty_mode", "duty_default": "off", "max_key": "max"})["plan_state"], want)
            ps = {"duty": "control", "plan": True, "k": None, "plan_state": None, "ordinal": 0}
            arm("token: baseline is a plan held and no step covering now", (token_holds("baseline", ps, None), token_holds("baseline", {**ps, "k": 0}, None)), (True, False))
            arm("token: an unknown token is not recorded", token_holds("boost-partial", ps, None), None)
            arm("token: a write outside every pass holds no token", token_holds("idle", None, None), False)
            arm("token: a plan-state token reads the recorded plan state", (token_holds("idle", {**ps, "plan_state": "idle"}, None),
                token_holds("both", {**ps, "plan_state": "idle"}, None)), (True, False))
            # generality
            gl = root / "gen.tsv"
            gen = [("level CONF_A_ENTITY=present", "has-a"), ("level CONF_B_ENTITY=present", "has-b"),
                   ("level mode=m1", "const-after-config"), ("level mode=m1", "mode-is-m1"), ("level grid=g1", "has-a"),
                   ("level mode=m2", "mode-is-m2"), ("level CONF_C_ENTITY=absent", "counter"), ("level price_shape=p1", "price"),
                   ("level mode=m1", "has-a", "bundle"), ("level mode=m2", "mode-is-m1"), ("level CONF_C_ENTITY=absent", "no-c"),
                   ("level mode=m1", "e4-m1"), ("level mode=m2", "e4-m2"), ("level mode=m1", "nosuch"), ("level mode=m1", "always-fails"),
                   ("level mode=m1", "mode-detail"), ("level mode=m1", "mode-steady"), ("level price_shape=p1", "price-late"),
                   ("level climate=p1", "weather-late")]
            gl.write_text("# a comment\n\n" + "".join(f"{g[0]}\t{g[2] if len(g) > 2 else 'simulation'}\t{S}{g[1]}\n" for g in gen))
            po = root / "pairs.tsv"
            gout = read_generality(root, gl, 4, pairs_out=po)
            gg = {}
            for l in gout:
                c = l.split("\t")
                if len(c) >= 4 and "::" in c[2]:
                    gg[(c[0], c[2].split("::")[1], c[1])] = c[3]
            g = lambda i: gg[(gen[i][0], gen[i][1], gen[i][2] if len(gen[i]) > 2 else "simulation")]
            arm("null: a check on a key's presence, its level switched: witnessed", g(0), "witnessed (configuration 0)")
            arm("null: a second level in the same configuration: witnessed", g(1), "witnessed (configuration 0)")
            arm("planted (i): a constant check after a configuration carrying the level: reached, not witnessed",
                g(2), "reached (configuration 0): the check does not move with the level switched")
            arm("null: an option level switched to the next level: witnessed", g(3), "witnessed (configuration 0)")
            arm("planted (ii): a level no recorded configuration carried", g(4), "not witnessed: no recorded configuration carried the level before the check")
            arm("planted (iv): a check whose detail embeds a counter", g(6), "not witnessed: nondeterministic")
            arm("null: a profile argument switched: witnessed", g(7).startswith("witnessed"), True)
            arm("planted: a configuration built after the check carries nothing for it", g(9),
                "not witnessed: no recorded configuration carried the level before the check")
            arm("a bundle row is never counted", g(8), "not witnessed: source bundle is never re-run with a level switched")
            arm("null: an absent level gains its key: witnessed; a profile configuration after it carries no entry level", g(10), "witnessed (configuration 3)")
            arm("null: two keys of one axis carry two levels in one configuration", (g(11), g(12)), ("witnessed (configuration 5)",) * 2)
            arm("planted: an unknown check", g(13), "not witnessed: unknown check (RuntimeError: planted)")
            arm("planted: a FAIL at the head", g(14), "not witnessed: FAIL at the head")
            arm("null: a check that stays ok while only its detail moves with the level switched: witnessed", g(15), "witnessed (configuration 0)")
            arm("planted: a check that stays ok with a detail the switched level does not reach: reached", g(16),
                "reached (configuration 0): the check does not move with the level switched")
            arm("null: a price level whose prices() configuration precedes a weather() one sharing the level name: carried by its own kind",
                g(17), "witnessed (configuration 6)")
            arm("null: the weather() configuration carries the climate level of that name", g(18), "witnessed (configuration 7)")
            arm("a witnessed pair prints its pair row in the universe listing", sorted(l for l in gout if l.startswith("pair ") and l.endswith("one configuration)")),
                [f"pair CONF_A_ENTITY=present & CONF_B_ENTITY=present\tsimulation\t{S}has-a\twitnessed (both levels, one configuration)",
                 f"pair CONF_A_ENTITY=present & mode=m1\tsimulation\t{S}has-a\twitnessed (both levels, one configuration)",
                 f"pair CONF_B_ENTITY=present & mode=m1\tsimulation\t{S}has-b\twitnessed (both levels, one configuration)"])
            arm("generality per-script line", [l for l in gout if l.startswith("script ")],
                [f"script tests/fake_script.py\tchecks={n_checks}\tconfigurations=8\tchecks with no recorded configuration=6\terror=RuntimeError: planted"])
            pairs = po.read_text().splitlines()
            arm("null: two levels witnessed in one configuration make their pairs; planted (iii): m2 in ordinal 1 pairs with nothing;"
                " planted: two levels of one axis in one configuration are no pair",
                sorted(p.split("\t")[0] for p in pairs),
                ["pair CONF_A_ENTITY=present & CONF_B_ENTITY=present", "pair CONF_A_ENTITY=present & mode=m1", "pair CONF_B_ENTITY=present & mode=m1"])
            arm("planted (i): no pair through the constant check", any("const-after-config" in p for p in pairs), False)
            arm("the pair rows are a ledger enumerate.py d12-cells --pairs accepts",
                len([l for l in census.run("d12-cells", root, pairs=True, ledger=str(po)) if not l.endswith("\tnot run")]), 3)
            OPTION_KEYS = {"mode": ("CONF_MODE",)}
            arm("an axis with no table entry prints no witness",
                next(l for l in read_generality(root, gl, 4) if l.startswith("level grid=g1\t")).endswith("no witness: no observable in the stub"), True)
            OPTION_KEYS = {"mode": ("CONF_MODE", "CONF_MODE2"), "grid": ("CONF_GRID",)}
            arm("generality RESULT", gout[-1], f"RESULT read=generality universe={len(universe(root, 'd12-cells', pairs=True))} examined=10 levels=7 pairs=3 reached-only=0")
            # refusals
            for name, fn in (("operation", lambda: read_operation(root, led, 1)), ("generality", lambda: read_generality(root, gl, 1))):
                arm(f"{name}: a ledger row naming no item exits 2, citing its line",
                    _refused(name, root, "# c\nnosuch\tx::y\n" if name == "operation" else "# c\nnosuch\tsimulation\tx::y\n", "x.tsv:2: 'nosuch'"), True)
                arm(f"{name}: an empty ledger exits 2", _exit(name, root, "# nothing\n")[0], 2)
            item = f"{W} | idle"
            for name, text in (("operation", f"{item}\tsimulation\t{S}payload\n"), ("operation", f"{item}\t{S}payload\textra\n"),
                               ("operation", f"{item}\ttests/fake_script.py payload\n"), ("generality", f"level mode=m1\t{S}payload\n"),
                               ("generality", f"level mode=m1\tsimulation\ttests/fake_script.py payload\n"),
                               ("generality", f"level mode=m1\tguesswork\t{S}payload\n")):
                arm(f"{name}: a malformed row exits 2: {text.strip()!r}", _refused(name, root, text, "x.tsv:1: a row is"), True)
            arm("operation: a read that prints its RESULT exits 0", _exit("operation", root, f"{W} | idle\t{S}payload\n")[0],
                "RESULT printed, exit 0")
            (root / PKG / "pump_arbiter.py").write_text("x = 1\n")
            (root / PKG / "log_latch.py").write_text("")
            (root / PKG / "off_restore.py").write_text("")
            arm("operation: an emptied universe source exits 2", _exit("operation", root, f"{W} | idle\t{S}payload\n")[0], 2)
            (root / census.OBJECTIVE).unlink()
            arm("generality: an emptied universe source exits 2", _exit("generality", root, f"level mode=m1\tsimulation\t{S}payload\n")[0], 2)
            arm("a read with no --ledger exits 2 before reading", _usage_exit(["operation", "--repo", str(root)]), 2)
        finally:
            OPTION_KEYS = saved
    if fails:
        print("SELF-TEST FAILED\n  " + "\n  ".join(fails))
        return 1
    print(f"SELF-TEST passed ({arms} arms)")
    return 0


def _plan_cases():
    from datetime import datetime, timedelta, timezone
    from types import SimpleNamespace as NS
    mk = lambda s, d, f=None, n=2: NS(timestamps=[_T0 + timedelta(minutes=15 * i) for i in range(n)], power_schedule=[s] * n,
                                     dhw_power_schedule=[d] * n, optimal_setpoints=[20.0] * n, duty_floor_kw=f)
    cfg = {"max": 4.0}
    return [("idle", mk(0.0, 0.0), cfg, "idle"), ("dhw-only", mk(0.0, 1.0), cfg, "dhw-only"), ("both", mk(2.0, 1.0), cfg, "both"),
            ("full", mk(4.0, 0.0), cfg, "full"), ("min-cold-tank", mk(1.0, 0.0, 1.0), cfg, "min-cold-tank"),
            ("partial", mk(0.5, 0.0, 1.0), cfg, "partial"), ("a one-step plan has no k", mk(2.0, 0.0, n=1), cfg, None),
            ("no configured maximum reads no partial", mk(2.0, 0.0), {}, None),
            ("now past the plan has no k", NS(timestamps=[_T0 - timedelta(hours=2), _T0 - timedelta(hours=1, minutes=45)],
                                              power_schedule=[2.0, 2.0]), cfg, None),
            ("no power schedule reads no state", NS(timestamps=[_T0, _T0 + timedelta(minutes=15)]), cfg, None),
            ("dhw past its end reads 0", NS(timestamps=[_T0 - timedelta(minutes=15), _T0], power_schedule=[0.5, 0.5],
                                            dhw_power_schedule=[1.0], duty_floor_kw=None), cfg, "partial")]


_T0 = __import__("datetime").datetime(2026, 1, 1, tzinfo=__import__("datetime").timezone.utc)


def _never_reached(root, S):
    p = root / PKG / "pump_arbiter.py"
    keep = p.read_text()
    p.write_text(keep + "async def unused(hass):\n    await hass.services.async_call('a', 'b', {})\n")
    try:
        cell = next(c for c in universe(root, "d16-writes", cells=True) if " unused domain=a | idle" in c)
        led = root / "never.tsv"
        led.write_text(f"{cell}\t{S}payload\n")
        return next(l.split("\t")[2] for l in read_operation(root, led, 2) if l.startswith(cell + "\t"))
    finally:
        p.write_text(keep)


def _only_latch(root):
    """The control for the per-module patch: a recorder wrapping log_latch.log_held once the package is imported
    (the obvious recorder) sees no hold, because pump_arbiter bound the name at its own import."""
    probe = root / "tests" / "latch_probe.py"
    probe.write_text("import sys\nsys.path.insert(0, 'custom_components')\nfrom heatpump_optimizer import pump_arbiter, log_latch, coordinator\nn = []\n"
                     "real = log_latch.log_held\nlog_latch.log_held = lambda *a: n.append(a) or real(*a)\n"
                     "sys.argv = ['tests/fake_script.py']\nimport runpy, io, contextlib\n"
                     "with contextlib.redirect_stdout(io.StringIO()), contextlib.suppress(RuntimeError):\n"
                     "    runpy.run_path('tests/fake_script.py', run_name='__main__')\nprint(len(n))\n")
    env = {**os.environ, "PYTHONPATH": str(root / "tests" / "hastub")}
    r = subprocess.run([sys.executable, str(probe)], cwd=root, env=env, capture_output=True, text=True)
    probe.unlink()
    return int(r.stdout.strip() or -1)


def _refused(name, root, text, message):
    rc, err = _exit(name, root, text)
    return rc == 2 and err.startswith(message)


def _usage_exit(argv):
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            return f"returned {main(argv)}"
    except SystemExit as stop:
        return stop.code


def _exit(name, root, text):
    led = root / "x.tsv"
    led.write_text(text)
    with contextlib.redirect_stdout(io.StringIO()) as o, contextlib.redirect_stderr(io.StringIO()) as e:
        rc = main([name, "--repo", str(root), "--ledger", str(led), "--jobs", "1"])
    return (rc, e.getvalue().replace(f"REFUSE: {root}/", "")) if "RESULT" not in o.getvalue() else (f"RESULT printed, exit {rc}", "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("read", nargs="?", choices=("operation", "generality", "_launch"))
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ledger")
    ap.add_argument("--pairs-out")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.read == "_launch":
        launch(json.loads(a.spec))
        return 0
    if not a.read or not a.ledger:
        ap.error("a read and --ledger are required")
    try:
        out = read_operation(a.repo, a.ledger, a.jobs) if a.read == "operation" else read_generality(a.repo, a.ledger, a.jobs, a.pairs_out)
    except (Refuse, census.Refuse, OSError, SyntaxError, json.JSONDecodeError) as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
