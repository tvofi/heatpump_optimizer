"""Class P2 enumerator, round 11 (D14 method steps 3-4): one fact decided twice.

P2's mechanism: one fact decided twice by divergent predicates, a guard at one seam
missing at its sibling. Each round-11 finding in the class names one fact; each family
below is that finding's seam_rule widened from the files it named to the whole package,
as a static AST rule. A family lists every SITE of its fact; a site whose shape is the
finding's divergent shape is a SEAM (`bad`), its siblings are listed as `ok` with the
guard the rule saw.

  F01 unbounded_reap   `x.wait()` with no timeout on a non-awaited object       D1-s3-04
  F02 reader_settings  `InputReader(...)` without the entry's enabled=/scale=    D1-s2-52
  F03 data_shadow      `async_update_entry(data=...)` leaving options untouched D10-s2-01
  F04 zone_fact        two-zone decided outside ThermalParameters.from_config,  D12-s2-01 D12-s1-01
                       or a mode-dependent field offered/accepted ungated       D17-s1-03 D17-s3-02
  F05 modulation       the on/off declaration read outside declared_modulation, D12-s3-01
                       or the owner mapping on_off to modulating
  F06 setpoint_range   a set-point write whose value no entity range bounds     D12-s3-02
  F07 domain_refuse    a loader that drops a whole row on admitted() False      D15-s1-04
  F08 seeded_zero      setdefault(k, [x, 0]) not incremented to >=1 in place    D15-s1-05
  F09 boost_branch     a return of a `boosted` target function blind to boost  D16-s1-03
  F10 record_trust     an arbiter write gate trusting its record, no live read  D16-s2-03
  F11 computed_eval    a _Computed default evaluated over the pre-save mapping  D17-s1-02
                       while judging a submit
  F12 wood_valve       a writer that stores the wood-tank probes and no valve   D17-s2-03
  F13 run_publish      async_run_optimization() called with no refresh after    D17-s3-01
  F14 flat_windows     a time-dependent DHW window test on the flat union       D17-s3-51
  F15 twin_formula     a batch twin whose inline formula differs from its        D2-s1-01 D2-s1-02 D2-s3-06
                       scalar owner (flow lift, emitter floor, top-k slice)
  F16 small_rules      water heat-capacity literals, naive-instant converters,  D7-s3-04
                       finite-number predicates written more than once
  F17 gap_feature      a sensor-gap row priced without its feature's gate       D8-s1-01
  F18 waiting_key      `_waiting_for` keyed off a value native_value does not   D8-s1-03
                       read

    python3 enumerate_p2.py [--root DIR]     # seams of the tree (default: this repo)
    python3 enumerate_p2.py --control        # positive control: every judged site re-found
    python3 enumerate_p2.py --fixture        # null control: a clean synthetic package -> 0
    python3 enumerate_p2.py --perturb [--only F10_record_trust,...]   # one re-introduction per family, +1 each
    python3 enumerate_p2.py --json           # seams as JSON
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
PKG_REL = Path("custom_components") / "heatpump_optimizer"


def _trees(pkg: Path):
    for f in sorted(pkg.glob("*.py")):
        src = f.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        par = {}
        for node in ast.walk(tree):
            for ch in ast.iter_child_nodes(node):
                par[ch] = node
        yield f.name, src, tree, par


def _fn(node, par):
    """The innermost enclosing function and its qualified name."""
    names, fn, cur = [], None, node
    while cur in par:
        cur = par[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if fn is None and not isinstance(cur, ast.ClassDef):
                fn = cur
            names.append(cur.name)
    return fn, ".".join(reversed(names)) or "<module>"


def _txt(src, node):
    return ast.get_source_segment(src, node) or ""


def _callname(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}


def site(fam, file, node, sym, bad, why):
    return {"family": fam, "file": f"{PKG_REL}/{file}", "line": getattr(node, "lineno", 0),
            "symbol": sym, "bad": bool(bad), "why": why}


# -- families ---------------------------------------------------------------------------

def f01(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "wait":
                if isinstance(par.get(n), ast.Await):
                    continue  # an asyncio wait on the loop, not a process reap
                fn, sym = _fn(n, par)
                bounded = bool(n.args or n.keywords)
                out.append(site("F01_unbounded_reap", file, n, sym, not bounded,
                                "wait(timeout=...)" if bounded else "wait() with no timeout"))
    return out


def f02(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) == "InputReader":
                kws = {k.arg for k in n.keywords}
                fn, sym = _fn(n, par)
                ok = {"enabled", "scale"} <= kws
                out.append(site("F02_reader_settings", file, n, sym, not ok,
                                "entry enabled=/scale=" if ok else f"defaults (kwargs {sorted(k for k in kws if k)})"))
    return out


def f03(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) == "async_update_entry":
                kws = {k.arg for k in n.keywords}
                if "data" not in kws:
                    continue
                fn, sym = _fn(n, par)
                out.append(site("F03_data_shadow", file, n, sym, "options" not in kws,
                                "data= and options= in one write" if "options" in kws else "data= only; options keep any shadowing key"))
    return out


HOUSE_ONLY = {"CONF_HOUSE_THERMAL_MASS", "CONF_HOUSE_HEAT_LOSS_COEFFICIENT"}
ZONE_ONLY = {"CONF_UPPER_FLOOR_THERMAL_MASS", "CONF_LOWER_FLOOR_THERMAL_MASS", "CONF_UPPER_FLOOR_HEAT_LOSS",
             "CONF_LOWER_FLOOR_HEAT_LOSS", "CONF_INTER_ZONE_TRANSFER"}
SVC_MODE_DEP = {"house_heat_loss_coefficient", "house_thermal_mass", "upper_floor_thermal_mass",
                "lower_floor_thermal_mass", "inter_zone_heat_transfer"}


def f04(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            # (a) the owner: a True verdict only on an explicit 'on'
            if isinstance(n, ast.FunctionDef) and n.name == "from_config" and file == "thermal_model.py":
                for i in ast.walk(n):
                    if isinstance(i, ast.If) and any(
                            isinstance(s, ast.Assign) and "two_zone_enabled" in _txt(src, s.targets[0])
                            and isinstance(s.value, ast.Constant) and s.value.value is True for s in i.body):
                        t = i.test
                        ok = (isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], ast.Eq)
                              and "TWO_ZONE_MODE_ON" in _txt(src, t.comparators[0]))
                        out.append(site("F04_zone_fact", file, i, "ThermalParameters.from_config.two_zone_mode", not ok,
                                        "owner: True only on an explicit on; auto reaches the presence rule" if ok
                                        else f"owner: True on `{_txt(src, t)}` (auto bypasses the presence rule)"))
            # (b) raw-mode verdicts elsewhere
            if isinstance(n, ast.Compare) and file != "thermal_model.py" and any(
                    re.search(r"TWO_ZONE_MODE_(ON|OFF|AUTO)\b", _txt(src, c)) for c in n.comparators):
                fn, sym = _fn(n, par)
                stmt = n
                while stmt in par and not isinstance(stmt, ast.stmt):
                    stmt = par[stmt]
                ui = bool(re.search(r"answers\[|suggested_value", _txt(src, stmt)))
                if isinstance(stmt, ast.If):
                    ui = ui or bool(re.search(r"answers\[|suggested_value", "".join(_txt(src, b) for b in stmt.body)))
                out.append(site("F04_zone_fact", file, n, sym, not ui,
                                ("a form answer from the stored override, not a topology verdict: `" if ui
                                 else "raw two_zone_mode decides two-zone: `") + _txt(src, n)[:60] + "`"))
            # (c) options rows of a mode-dependent field
            if isinstance(n, ast.Call) and _callname(n) == "_F" and len(n.args) >= 2 and isinstance(n.args[1], ast.Name):
                key = n.args[1].id
                if key in HOUSE_ONLY:
                    gated = any(k.arg == "when" for k in n.keywords)
                    out.append(site("F04_zone_fact", file, n, f"_OPTION_FIELDS.{key}", not gated,
                                    "when= gates it on the zone mode" if gated else "single-zone field offered in every zone mode"))
            # (d) service fields that move a mode-dependent parameter
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_THERMAL_PARAM_FIELDS" for t in n.targets) \
                    and isinstance(n.value, ast.Dict):
                for k in n.value.keys:
                    if isinstance(k, ast.Constant) and k.value in SVC_MODE_DEP:
                        out.append(site("F04_zone_fact", file, k, f"_THERMAL_PARAM_FIELDS.{k.value}", True,
                                        "service sets a field one zone mode never reads, no mode check"))
            # (e) zone columns decided from the trajectories, not the model's mode
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = _txt(src, n)
                if re.search(r"\.(upper|lower)_temp_trajectory\b", body) and file not in ("thermal_model.py", "optimizer.py"):
                    nested = [c for c in ast.walk(n) if c is not n and isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and re.search(r"\.(upper|lower)_temp_trajectory\b", _txt(src, c))]
                    if nested:
                        continue
                    ok = "two_zone_enabled" in body
                    fn, sym = _fn(n.body[0], par)
                    out.append(site("F04_zone_fact", file, n, sym, not ok,
                                    "reads the model's two_zone_enabled" if ok else "zone columns from trajectory presence"))
    return out


def f05(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr in ("CONF_COMPRESSOR_MODULATION", "CONF_CLAMP_PLANNED_LEVELS") \
                    or isinstance(n, ast.Name) and n.id in ("CONF_COMPRESSOR_MODULATION", "CONF_CLAMP_PLANNED_LEVELS"):
                if file == "const.py":
                    continue
                fn, sym = _fn(n, par)
                if fn is None:
                    continue
                if fn.name == "declared_modulation":
                    continue
                if isinstance(par.get(n), ast.Call) and _callname(par[n]) == "_F":
                    continue  # the options row that stores it
                if isinstance(par.get(n), ast.alias) or isinstance(par.get(n), ast.ImportFrom):
                    continue
                out.append(site("F05_modulation", file, n, sym, True, "modulation declaration read outside declared_modulation"))
            if isinstance(n, ast.FunctionDef) and n.name == "declared_modulation":
                for e in ast.walk(n):
                    if isinstance(e, ast.IfExp) and "COMPRESSOR_MODULATION_ON_OFF" in _txt(src, e.test):
                        ok = isinstance(e.body, ast.Constant) and e.body.value is False
                        out.append(site("F05_modulation", file, e, "declared_modulation.on_off", not ok,
                                        "owner: on_off -> False (not modulating)" if ok else "owner: on_off mapped to modulating"))
    return out


RANGE = re.compile(r"bounded|setpoint_range_c|\bhi_c\b|\blo_c\b|_bounded\(|min_temp|max_temp")


def f06(T):
    out = []
    for file, src, tree, par in T:
        if file == "inputs.py":
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) in ("write_setpoint", "write_setpoint_c", "quantise_setpoint_c"):
                fn, sym = _fn(n, par)
                body = _txt(src, fn) if fn else ""
                if _callname(n) == "quantise_setpoint_c":
                    kws = {k.arg: _txt(src, k.value) for k in n.keywords}
                    ok = "setpoint_range_c" in kws.get("hi_c", "") or "bounded" in body
                    out.append(site("F06_setpoint_range", file, n, sym, not ok,
                                    "hi_c from the entity's own range" if ok else f"hi_c={kws.get('hi_c', 'None')}: a config cap, not the entity's"))
                    continue
                ok = bool(RANGE.search(body))
                out.append(site("F06_setpoint_range", file, n, sym, not ok,
                                "value bounded in the writer" if ok else "value written as handed in; no entity range in the writer"))
    return out


def f07(T):
    out = []
    for file, src, tree, par in T:
        if file == "store.py":
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) == "admitted":
                fn, sym = _fn(n, par)
                # row-level: the refusal returns None / skips the item; field-level: assigns a default
                cur, row = n, False
                while cur in par and not isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cur = par[cur]
                    if isinstance(cur, ast.If) and any(isinstance(s, (ast.Return, ast.Continue)) for s in cur.body):
                        row = True
                        break
                    if isinstance(cur, (ast.comprehension,)):
                        row = True
                        break
                    if isinstance(cur, ast.DictComp) or isinstance(cur, ast.ListComp):
                        row = True
                        break
                out.append(site("F07_domain_refuse", file, n, sym, row,
                                "refusal drops the whole row/record" if row else "refusal skips one field"))
    return out


def f08(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) == "setdefault" and len(n.args) == 2 \
                    and isinstance(n.args[1], ast.List) and len(n.args[1].elts) == 2 \
                    and isinstance(n.args[1].elts[1], ast.Constant) and n.args[1].elts[1].value == 0:
                fn, sym = _fn(n, par)
                ok = False
                for a in ast.walk(fn):
                    if isinstance(a, ast.Assign) and isinstance(a.targets[0], ast.Subscript) \
                            and _txt(src, a.targets[0].slice) == "1" and isinstance(a.value, ast.BinOp) \
                            and isinstance(a.value.right, ast.Constant) and a.value.right.value == 1:
                        ok = True
                out.append(site("F08_seeded_zero", file, n, sym, not ok,
                                "count +1 in place before any save" if ok else "count can stay 0 when stored"))
    return out


def f09(T):
    out = []
    for file, src, tree, par in T:
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
            if "boosted" not in params:
                continue
            tainted = {"boosted"}
            for _ in range(3):
                for a in ast.walk(fn):
                    if isinstance(a, ast.Assign) and _names(a.value) & tainted:
                        for t in a.targets:
                            tainted |= _names(t)
            exits = [i.lineno for i in ast.walk(fn) if isinstance(i, ast.If) and _names(i.test) & tainted
                     and i.body and isinstance(i.body[-1], ast.Return)]
            for r in ast.walk(fn):
                if isinstance(r, ast.Return) and r.value is not None:
                    if any(e < r.lineno for e in exits):
                        out.append(site("F09_boost_branch", file, r, f"{fn.name}:{r.lineno}", False,
                                        "after the function's boost exit"))
                        continue
                    # the branch that holds it
                    cur, guarded = r, False
                    while cur in par and cur is not fn:
                        cur = par[cur]
                        if isinstance(cur, ast.If) and _names(cur.test) & tainted:
                            guarded = True
                    ok = guarded or bool(_names(r.value) & tainted)
                    out.append(site("F09_boost_branch", file, r, f"{fn.name}:{r.lineno}", not ok,
                                    "branch reads the boost" if ok else f"returns `{_txt(src, r.value)[:60]}` blind to the boost"))
    return out


LIVE = re.compile(r"_observed\(|read_setpoint\(|states\.get\(|\breading\b|\bobserved\b|\bhold\(")


def f10(T):
    out = []
    for file, src, tree, par in T:
        if file != "pump_arbiter.py":
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = _txt(src, fn)
            if not re.search(r"\.written\.get\(|\brecorded\b|\brecord\b", body):
                continue
            uses = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and _callname(c) == "_differs"] + \
                   [c for c in ast.walk(fn) if isinstance(c, ast.Compare) and re.search(r"recorded\[0\]|record\[0\]", _txt(src, c))]
            for c in uses:
                args = c.args[1:] if isinstance(c, ast.Call) else [c.left, *c.comparators]
                texts = [_txt(src, a) for a in args]
                if not any(re.search(r"recorded|record\b|record\[|written|\blast\b|before", t) for t in texts):
                    continue
                ok = any(re.search(r"observed|reading|_observed\(|read_setpoint\(|states\.get\(", t) for t in texts)
                out.append(site("F10_record_trust", file, c, f"{fn.name}:{c.lineno}", not ok,
                                "compares the record against a live reading" if ok
                                else f"decides from the record against its own value ({', '.join(texts)[:60]})"))
    return out


def f11(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "of" \
                    and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "default":
                fn, sym = _fn(n, par)
                params = {a.arg for a in fn.args.args + fn.args.kwonlyargs} if fn else set()
                first = _txt(src, n.args[0]) if n.args else ""
                judging_submit = "user_input" in params
                bad = judging_submit and re.fullmatch(r"current|self\._current|options", first) is not None
                out.append(site("F11_computed_eval", file, n, sym, bad,
                                f"evaluated over `{first}`" + (" while judging the submit" if judging_submit else "")))
    return out


def f12(T):
    out = []
    for file, src, tree, par in T:
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            nested = [c for c in ast.walk(fn) if c is not fn and isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if nested:
                continue
            writes = [d for d in ast.walk(fn) if isinstance(d, ast.Dict) and any(
                isinstance(k, ast.Name) and k.id == "CONF_WOOD_FURNACE_ENABLED" for k in d.keys if k is not None)]
            if not writes:
                continue
            body = _txt(src, fn)
            ok = "MIXING_VALVE" in body or "EXTERNAL_HEAT_DETECTION" in body
            fn_, sym = _fn(fn.body[0], par)
            out.append(site("F12_wood_valve", file, writes[0], sym, not ok,
                            "writes the valve / detection the two-tank model needs" if ok else
                            "stores the wood furnace and its probes, no throttling valve"))
    return out


def f13(T):
    out = []
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _callname(n) == "async_run_optimization":
                fn, sym = _fn(n, par)
                if fn is None:
                    continue
                body = _txt(src, fn)
                internal = fn.name in ("_async_update_data", "async_run_optimization")
                ok = internal or bool(re.search(r"async_request_refresh|async_refresh\(|async_set_updated_data", body))
                out.append(site("F13_run_publish", file, n, sym, not ok,
                                "inside the refresh cycle" if internal else "refresh requested after the run" if ok
                                else "solves without the refresh that fetches inputs and publishes"))
    return out


FLAT = re.compile(r"\.(dhw_demand_windows|dhw_windows)\b(?!_)|_dhw_effective_windows\(|get\(\"dhw_windows\"\)")
CLOCK = re.compile(r"\bnow\b|utcnow|\.hour\b|\.minute\b|minute_of|in_window|_in_window|_minutes\(")


def f14(T):
    out = []
    for file, src, tree, par in T:
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            nested = [c for c in ast.walk(fn) if c is not fn and isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if nested:
                continue
            body = _txt(src, fn)
            m = FLAT.search(body)
            if not m or not CLOCK.search(body):
                continue
            if fn.name in ("_dhw_effective_windows", "dhw_demand_windows", "configured_dhw_windows"):
                continue
            ok = "windows_for_day" in body or "_dhw_windows_at" in body or "weekly" in body
            fn_, sym = _fn(fn.body[0], par)
            out.append(site("F14_flat_windows", file, fn, sym, not ok,
                            "per-weekday windows" if ok else f"time test over the flat union (`{m.group(0)}`)"))
    return out


def _ret_expr(fn, src):
    rets = sorted((r for r in ast.walk(fn) if isinstance(r, ast.Return) and r.value is not None), key=lambda r: r.lineno)
    return _txt(src, rets[-1].value) if rets else ""


def f15(T):
    """Batch twins against their scalar owners: the shape each must share."""
    out, by = [], {}
    for file, src, tree, par in T:
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                by[(file, fn.name)] = (fn, src)

    def norm(s):
        return re.sub(r"\s+", "", s)

    checks = []
    # flow lift: the scalar ratio orientation against the batch's
    if ("thermal_model.py", "flow_lift_factor") in by and ("thermal_model.py", "_batch_cop") in by:
        f, s = by[("thermal_model.py", "flow_lift_factor")]
        b, bs = by[("thermal_model.py", "_batch_cop")]
        sc = re.search(r"carnot_(flow|ref)\s*/\s*carnot_(flow|ref)", " ".join(
            _txt(s, r.value) for r in ast.walk(f) if isinstance(r, ast.Return) and r.value is not None))
        bc = re.search(r"carnot_(flow|ref)\s*/\s*carnot_(flow|ref)", _txt(bs, b))
        checks.append(("thermal_model.py", f, "ThermalModel.flow_lift_factor~_batch_cop",
                       sc and bc and sc.group(0).replace(" ", "") == bc.group(0).replace(" ", ""),
                       f"scalar {sc and sc.group(0)} vs batch {bc and bc.group(0)}"))
    # emitter delivery: the scalar floor against the batch's inline np.maximum(0.0, ...)
    if ("mixing_valve.py", "emitter_delivery") in by and ("thermal_model.py", "simulate_trajectory_batch") in by:
        f, s = by[("mixing_valve.py", "emitter_delivery")]
        floored = norm(_ret_expr(f, s)).startswith("max(0.0,")
        b, bs = by[("thermal_model.py", "simulate_trajectory_batch")]
        bfl = "np.maximum(0.0,ua_rad" in norm(_txt(bs, b))
        checks.append(("mixing_valve.py", f, "emitter_delivery~simulate_trajectory_batch", floored == bfl,
                       f"scalar floored={floored} vs batch floored={bfl}"))
    # top-k: the scalar slice against the batch's
    if ("tariff.py", "_exact_topk_sum") in by and ("tariff.py", "_plateau_aware_topk_sum_batch") in by:
        f, s = by[("tariff.py", "_exact_topk_sum")]
        b, bs = by[("tariff.py", "_plateau_aware_topk_sum_batch")]
        sk = "[-k:]" in norm(_ret_expr(f, s))
        bk = "[:,-k:]" in norm(_txt(bs, b))
        checks.append(("tariff.py", f, "_exact_topk_sum~_plateau_aware_topk_sum_batch", sk == bk,
                       f"scalar largest-k={sk} vs batch largest-k={bk}"))
    for file, node, sym, ok, why in checks:
        out.append(site("F15_twin_formula", file, node, sym, not ok, ("same shape: " if ok else "twins disagree: ") + why))
    return out


WATER = re.compile(r"\b4\.18\d*\b|\b0\.00116\d*\b|\b1\.16\d*e-3\b|\b1\.163\b|\b4186\b|\b4187\b")


def f16(T):
    out = []
    owners = {"finite_float"}
    for file, src, tree, par in T:
        for n in ast.walk(tree):
            # water heat capacity written as a literal outside const.py
            if isinstance(n, ast.Constant) and isinstance(n.value, float) and file != "const.py" \
                    and WATER.fullmatch(repr(n.value)):
                fn, sym = _fn(n, par)
                out.append(site("F16_small_rules", file, n, f"{sym}:water={n.value}", True,
                                "a water heat-capacity literal beside const.py's"))
            if isinstance(n, (ast.FunctionDef,)):
                body = _txt(src, n)
                # a naive instant made aware here, not by drift's owner
                if "tzinfo is None" in body and not [c for c in ast.walk(n) if c is not n and isinstance(c, ast.FunctionDef)]:
                    reps = [_txt(src, k.value) for c in ast.walk(n) if isinstance(c, ast.Call) and _callname(c) == "replace"
                            for k in c.keywords if k.arg == "tzinfo" and _txt(src, k.value) != "None"]
                    zone = ("host-local" if re.search(r"\.astimezone\(\s*\)", body) and not reps else
                            "HA default" if any("DEFAULT_TIME_ZONE" in r for r in reps) else
                            "UTC" if reps and all(re.search(r"utc|UTC|naive_zone", r) for r in reps) else
                            "the caller's reference zone" if reps and all(r.endswith(".tzinfo") or r == "tz" for r in reps) else
                            "host-local" if re.search(r"\.astimezone\(\s*\)", body) else
                            "none (refused or kept naive)" if not reps else "mixed")
                    fn_, sym = _fn(n.body[0], par)
                    out.append(site("F16_small_rules", file, n, f"{sym}:naive->{zone}", zone in ("host-local", "HA default", "mixed"),
                                    f"naive instant read as {zone}"))
                if not re.search(r"\btz(info)? is None", body) and re.search(r"naive", body, re.I) \
                        and re.search(r"\.astimezone\(\s*(timezone\.utc|UTC|dt_util\.UTC)?\s*\)", body) \
                        and not [c for c in ast.walk(n) if c is not n and isinstance(c, ast.FunctionDef)]:
                    fn_, sym = _fn(n.body[0], par)
                    out.append(site("F16_small_rules", file, n, f"{sym}:naive->host-local (astimezone)", True,
                                    "a naive instant read as the host's zone by astimezone(), drift._as_utc reads UTC"))
                # a finite-number predicate (a value parser; a selector builder is not one)
                if re.fullmatch(r"finite_float|payload_number|_as_float|numeric|_number|_stored_number|\w*finite\w*", n.name) \
                        and "Selector" not in body and "definite" not in n.name:
                    fn_, sym = _fn(n.body[0], par)
                    if n.name in owners:
                        out.append(site("F16_small_rules", file, n, sym, False, "the owner"))
                        continue
                    shaped = "finite_float(" in body or ("isfinite" in body and "bool" in body)
                    out.append(site("F16_small_rules", file, n, sym, not shaped,
                                    "refuses NaN, inf and bool as finite_float does" if shaped
                                    else "answers `finite number?` without finite_float's NaN/inf/bool refusal"))
    return out


def f17(T):
    out = []
    for file, src, tree, par in T:
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef) and fn.name == "rank_sensor_gaps":
                for t in ast.walk(fn):
                    if isinstance(t, ast.Tuple) and len(t.elts) == 2 and isinstance(t.elts[0], ast.Name) \
                            and t.elts[0].id.startswith("CONF_"):
                        expr = _txt(src, t.elts[1])
                        key = t.elts[0].id
                        feature = {"CONF_DHW_TEMP_ENTITY": "dhw_enabled"}.get(key)
                        ok = feature is None or feature in expr
                        out.append(site("F17_gap_feature", file, t, f"rank_sensor_gaps.{key}", not ok,
                                        "no optional feature behind it" if feature is None else
                                        ("gated on " + feature) if ok else f"priced without {feature}"))
    return out


def f18(T):
    out = []
    for file, src, tree, par in T:
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            meth = {m.name: m for m in cls.body if isinstance(m, (ast.FunctionDef,))}
            if "_waiting_for" not in meth or "native_value" not in meth:
                continue
            w, nv = meth["_waiting_for"], meth["native_value"]
            wt, nt = _txt(src, w), _txt(src, nv)
            if "raise NotImplementedError" in wt:
                continue
            strs = lambda node: {c.value for c in ast.walk(node) if isinstance(c, ast.Constant) and isinstance(c.value, str)}
            shared = strs(w) & strs(nv)
            ok = "self.native_value" in wt or "_payload_number(" in wt or bool(shared)
            out.append(site("F18_waiting_key", file, w, f"{cls.name}._waiting_for", not ok,
                            f"keys on what native_value reads ({sorted(shared)[:3] or 'same accessor'})" if ok
                            else "keys on a value native_value does not read"))
    return out


FAMILIES = [f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13, f14, f15, f16, f17, f18]


def enumerate_all(root: Path):
    T = list(_trees(root / PKG_REL))
    seams = []
    for f in FAMILIES:
        seams += f(T)
    return seams


def counts(seams):
    c = {}
    for s in seams:
        c.setdefault(s["family"], 0)
        c[s["family"]] += s["bad"]
    return c


# -- positive control -------------------------------------------------------------------
# Every judged site, as (finding, family, file, symbol-substring). PLANTED rows are the
# findings whose defect the register tree does not hold (a planted-defect copy, JUDGE.md:14):
# their control re-plants the claim's one-line defect on a temp copy first.
JUDGED = [
    ("D1-s3-04", "F01_unbounded_reap", "coordinator.py", "_run_in_process"),
    ("D1-s2-52", "F02_reader_settings", "coordinator.py", "_indoor_humidity_value"),
    ("D10-s2-01", "F03_data_shadow", "config_flow.py", "_async_save_reconfigure"),
    ("D12-s2-01", "F04_zone_fact", "thermal_model.py", "from_config.two_zone_mode"),
    ("D12-s1-01", "F04_zone_fact", "coordinator.py", "_build_plan_views"),
    ("D17-s1-03", "F04_zone_fact", "config_flow.py", "CONF_HOUSE_THERMAL_MASS"),
    ("D17-s3-02", "F04_zone_fact", "coordinator.py", "_THERMAL_PARAM_FIELDS.house_heat_loss_coefficient"),
    ("D17-s3-02", "F04_zone_fact", "coordinator.py", "_THERMAL_PARAM_FIELDS.house_thermal_mass"),
    ("D12-s3-01", "F05_modulation", "thermal_model.py", "declared_modulation.on_off"),
    ("D12-s3-02", "F06_setpoint_range", "setpoint_check.py", "_dhw"),
    ("D12-s3-02", "F06_setpoint_range", "repairs.py", ""),
    ("D15-s1-04", "F07_domain_refuse", "debugger.py", "_repair"),
    ("D15-s1-05", "F08_seeded_zero", "coordinator.py", "_fold_capacity_envelope"),
    ("D16-s1-03", "F09_boost_branch", "pump_arbiter.py", "_space_target"),
    ("D16-s2-03", "F10_record_trust", "pump_arbiter.py", "_write"),
    ("D17-s1-02", "F11_computed_eval", "config_flow.py", "_omit_unstored_computed"),
    ("D17-s2-03", "F12_wood_valve", "quick_setup.py", ""),
    ("D17-s3-01", "F13_run_publish", "services.py", "handle_run_optimization"),
    ("D17-s3-51", "F14_flat_windows", "coordinator.py", "_dhw_in_demand_window"),
    ("D2-s1-01", "F15_twin_formula", "thermal_model.py", "flow_lift_factor"),
    ("D2-s1-02", "F15_twin_formula", "mixing_valve.py", "emitter_delivery"),
    ("D2-s3-06", "F15_twin_formula", "tariff.py", "_exact_topk_sum"),
    ("D7-s3-04", "F16_small_rules", "sensor.py", "_gap_probe_terms:water"),
    ("D7-s3-04", "F16_small_rules", "open_meteo.py", "_ensure_utc"),
    ("D7-s3-04", "F16_small_rules", "entity.py", "payload_number"),
    ("D7-s3-04", "F16_small_rules", "sensor.py", "_as_float"),
    ("D7-s3-04", "F16_small_rules", "replay_doc.py", "numeric"),
    ("D8-s1-01", "F17_gap_feature", "topology.py", "CONF_DHW_TEMP_ENTITY"),
    ("D8-s1-03", "F18_waiting_key", "sensor.py", "MonthlySavingsSensor"),
]

# The planted findings' one-line defects, rebuilt from each claim (the plant list is held out).
PLANTS = [
    ("D12-s2-01", "thermal_model.py", "if two_zone_mode == const.TWO_ZONE_MODE_ON:",
     "if two_zone_mode != const.TWO_ZONE_MODE_OFF:"),
    ("D12-s3-01", "thermal_model.py", "False if mode == const.COMPRESSOR_MODULATION_ON_OFF",
     "True if mode == const.COMPRESSOR_MODULATION_ON_OFF"),
    ("D2-s1-01", "thermal_model.py", "return max(0.25, carnot_flow / carnot_ref)",
     "return max(0.25, carnot_ref / carnot_flow)"),
    ("D2-s1-02", "mixing_valve.py", "return max(0.0, ua * (mix_temp - zone_temp))",
     "return ua * (mix_temp - zone_temp)"),
    ("D2-s3-06", "tariff.py", "return float(np.sum(np.sort(excess)[-k:]))",
     "return float(np.sum(np.sort(excess)[:k]))"),
]


def _copy(root: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="p2sweep-"))
    shutil.copytree(root / PKG_REL, tmp / PKG_REL)
    return tmp


def _edit(tmp, file, old, new):
    f = tmp / PKG_REL / file
    s = f.read_text()
    assert s.count(old) == 1, f"{file}: {old!r} found {s.count(old)} times"
    f.write_text(s.replace(old, new, 1))


def control(root: Path):
    tmp = _copy(root)
    try:
        for _, file, old, new in PLANTS:
            _edit(tmp, file, old, new)
        seams = enumerate_all(tmp)
    finally:
        shutil.rmtree(tmp)
    missed = 0
    planted = {p[0] for p in PLANTS}
    for fid, fam, file, sym in JUDGED:
        hit = [s for s in seams if s["family"] == fam and s["bad"] and s["file"].endswith("/" + file) and sym in s["symbol"]]
        print(f"CONTROL {fid} {fam} {file}:{sym or '*'} {'found' if hit else 'MISSED'}"
              f"{' (re-planted)' if fid in planted else ''}" + (f" line {hit[0]['line']}" if hit else ""))
        missed += not hit
    print(f"RESULT control_sites={len(JUDGED)}")
    print(f"RESULT missed_sites={missed}")
    return missed


# -- null control -----------------------------------------------------------------------
CLEAN = {
    "manifest.json": "{}",
    "proc.py": "def reap(worker):\n    worker.kill()\n    worker.wait(timeout=5)\n\n\nasync def gate(ev):\n    await ev.wait()\n",
    "reader.py": "def read(hass, cfg):\n    return InputReader(hass, cfg, enabled=cfg.on, scale=cfg.scale)\n",
    "flow.py": ("def save(hass, entry, data, options):\n"
                "    hass.config_entries.async_update_entry(entry, data=data, options=options)\n\n\n"
                "def _omit(user_input, current, merged):\n    return ROW.default.of(merged, None)\n\n\n"
                "_OPTION_FIELDS = (_F('thermal_model', CONF_HOUSE_THERMAL_MASS, 1, 2, when=_single_zone),)\n"),
    "thermal_model.py": ("class ThermalParameters:\n    @classmethod\n    def from_config(cls, config):\n        values = {}\n"
                         "        two_zone_mode = config.get('m')\n"
                         "        if two_zone_mode == const.TWO_ZONE_MODE_ON:\n            values['two_zone_enabled'] = True\n"
                         "        return values\n\n\n"
                         "def declared_modulation(cfg):\n    mode = cfg.get(const.CONF_COMPRESSOR_MODULATION)\n"
                         "    return False if mode == const.COMPRESSOR_MODULATION_ON_OFF else None\n\n\n"
                         "class ThermalModel:\n    def flow_lift_factor(self, o, f):\n        return max(0.25, carnot_flow / carnot_ref)\n\n"
                         "    def _batch_cop(self, x):\n        return np.maximum(0.25, carnot_flow / carnot_ref)\n\n"
                         "    def simulate_trajectory_batch(self, x):\n        q_rad = np.maximum(0.0, ua_rad * (t_mix - T_upper))\n        return q_rad\n"),
    "mixing_valve.py": "def emitter_delivery(*, mix_temp, zone_temp, ua):\n    return max(0.0, ua * (mix_temp - zone_temp))\n",
    "tariff.py": ("def _exact_topk_sum(excess, k):\n    return float(np.sum(np.sort(excess)[-k:]))\n\n\n"
                  "def _plateau_aware_topk_sum_batch(x, k):\n    return row_sums(np.sort(x, axis=1)[:, -k:])\n"),
    "coordinator.py": ("class C:\n    def _thermal(self):\n        return {}\n\n"
                       "    def _build_plan_views(self, result):\n"
                       "        z = self._thermal_params.two_zone_enabled\n        return result.upper_temp_trajectory if z else None\n\n"
                       "    def _fold(self, b, x):\n        e = self.env.setdefault(b, [x, 0])\n        e[1] = e[1] + 1\n\n"
                       "    def _in_window(self, now):\n        return in_window(now, windows_for_day(self.weekly, now.weekday(), self.params.dhw_windows))\n"),
    "setpoints.py": "async def fix(hass, e, v):\n    await write_setpoint_c(hass, e, grid.bounded(v))\n",
    "store_reader.py": "def load(stored):\n    out = {}\n    if not admitted('ledger', stored):\n        out['x'] = None\n    return out\n",
    "pump_arbiter.py": ("def _space_target(inp, duty, now, *, boosted):\n    if boosted:\n        return 1\n    return 2\n\n\n"
                        "def _write(coord, slot, value, held):\n    observed = _observed(coord, slot)\n    recorded = held.written.get(slot)\n"
                        "    if recorded and not _differs(slot, observed, value):\n        return\n"),
    "quick.py": "def derive(a):\n    return {CONF_WOOD_FURNACE_ENABLED: True, CONF_MIXING_VALVE_MODE: 'smart'}\n",
    "services.py": "async def handle_run(coord):\n    await coord.async_run_optimization()\n    await coord.async_request_refresh()\n",
    "values.py": "def finite_float(x):\n    return x\n",
    "topology.py": "def rank_sensor_gaps(config, dhw_enabled):\n    rows = ((CONF_DHW_TEMP_ENTITY, 0.0 if not dhw_enabled else 1.0),)\n    return rows\n",
    "sensor.py": ("class S:\n    @property\n    def _waiting_for(self):\n        return None if self.native_value is not None else 'x'\n\n"
                  "    @property\n    def native_value(self):\n        return 1\n"),
}


def fixture():
    tmp = Path(tempfile.mkdtemp(prefix="p2clean-"))
    try:
        pkg = tmp / PKG_REL
        pkg.mkdir(parents=True)
        for name, text in CLEAN.items():
            (pkg / name).write_text(text)
        seams = enumerate_all(tmp)
    finally:
        shutil.rmtree(tmp)
    c = counts(seams)
    for fam in sorted({f.__name__ for f in FAMILIES}):
        pass
    sites = len(seams)
    total = sum(s["bad"] for s in seams)
    for s in seams:
        if s["bad"]:
            print(f"FIXTURE-HIT {s['family']} {s['file']}:{s['line']} {s['symbol']} -- {s['why']}")
    print(f"RESULT fixture.sites={sites}")
    print(f"RESULT fixture.total={total}")
    return total


# -- perturbation: one one-line re-introduction per family ------------------------------
PERTURB = {
    "F01_unbounded_reap": ("coordinator.py", "worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)", "worker.wait()"),
    "F02_reader_settings": ("coordinator.py", "            enabled=ctx._config.staleness_watchdog_enabled,\n            scale=ctx._config.staleness_max_age_scale,\n        )\n        indoor", None),
    "F03_data_shadow": ("config_flow.py", "entry, data=data, unique_id=identity_update(self.hass, entry, data=data)",
                        "entry, data=data, unique_id=identity_update(self.hass, entry, data=data)"),
    "F04_zone_fact": ("thermal_model.py", "if two_zone_mode == const.TWO_ZONE_MODE_ON:", "if two_zone_mode != const.TWO_ZONE_MODE_OFF:"),
    "F05_modulation": ("thermal_model.py", "False if mode == const.COMPRESSOR_MODULATION_ON_OFF", "True if mode == const.COMPRESSOR_MODULATION_ON_OFF"),
    "F06_setpoint_range": None,
    "F07_domain_refuse": ("snapshots.py", "snap[\"accuracy\"] = None  # out of its declared domain: not evaluable for restore",
                          "continue  # out of its declared domain: not evaluable for restore"),
    "F08_seeded_zero": ("freq_control.py", "entry[1] = count + 1", "entry[1] = count + int(count > 0)"),
    "F09_boost_branch": ("pump_arbiter.py", "boost_c = _boost_ceiling_c(inp) if boosted else None", "boost_c = None"),
    "F10_record_trust": None,
    "F11_computed_eval": None,
    "F12_wood_valve": None,
    "F13_run_publish": ("button.py", "reason = await self.coordinator.async_run_optimization()\n        off_the_action(self, self.coordinator.async_request_refresh())\n",
                        "reason = await self.coordinator.async_run_optimization()\n"),
    "F14_flat_windows": None,
    "F15_twin_formula": ("tariff.py", "return float(np.sum(np.sort(excess)[-k:]))", "return float(np.sum(np.sort(excess)[:k]))"),
    "F16_small_rules": None,
    "F17_gap_feature": None,
    "F18_waiting_key": None,
}


def perturb(root: Path, only=None):
    base = counts(enumerate_all(root))
    bad = 0
    for fam in sorted(f for f in PERTURB if not only or f in only):
        tmp = _copy(root)
        try:
            spec = PERTURB[fam]
            _apply_perturb(tmp, fam, spec)
            after = counts(enumerate_all(tmp))
        finally:
            shutil.rmtree(tmp)
        d = after.get(fam, 0) - base.get(fam, 0)
        ok = d == 1
        bad += not ok
        print(f"PERTURB {fam} {base.get(fam, 0)}->{after.get(fam, 0)} {'+1' if ok else 'NOT +1'}")
    print(f"RESULT perturb_families={len(only) if only else len(PERTURB)}")
    print(f"RESULT perturb_not_plus_one={bad}")
    return bad


def _append(tmp, file, text):
    f = tmp / PKG_REL / file
    f.write_text(f.read_text() + text)


def _apply_perturb(tmp, fam, spec):
    if fam == "F02_reader_settings":
        # the external-heat reader loses the entry settings (5204's shape -> 9178's)
        f = tmp / PKG_REL / "coordinator.py"
        s = f.read_text()
        old = "InputReader(\n            self.hass,\n            ctx._config,\n            enabled=ctx._config.staleness_watchdog_enabled,\n            scale=ctx._config.staleness_max_age_scale,\n        )"
        assert s.count(old) >= 1
        f.write_text(s.replace(old, "InputReader(self.hass, ctx._config)", 1))
    elif fam == "F03_data_shadow":
        _edit(tmp, "config_flow.py", "self.hass.config_entries.async_update_entry(self._entry, unique_id=uid)",
              "self.hass.config_entries.async_update_entry(self._entry, data=dict(self._entry.data), unique_id=uid)")
    elif fam == "F06_setpoint_range":
        _append(tmp, "repairs.py", "\n\nasync def _p2_perturb_write(hass, entity_id, value):\n    await write_setpoint(hass, entity_id, value)\n")
    elif fam == "F10_record_trust":
        _append(tmp, "pump_arbiter.py", "\n\ndef _p2_perturb_gate(held, slot, value):\n    recorded = held.written.get(slot)\n    return recorded and not _differs(slot, recorded[0], value)\n")
    elif fam == "F11_computed_eval":
        _append(tmp, "config_flow.py", "\n\ndef _p2_perturb_omit(user_input, current, hass):\n    return _OPTION_FIELDS[0].default.of(current, hass)\n")
    elif fam == "F12_wood_valve":
        _append(tmp, "quick_setup.py", "\n\ndef _p2_perturb_derive(answers):\n    return {CONF_WOOD_FURNACE_ENABLED: True}\n")
    elif fam == "F14_flat_windows":
        _append(tmp, "boost.py", "\n\ndef _p2_perturb_open(params, now):\n    return in_window(now, params.dhw_demand_windows)\n")
    elif fam == "F16_small_rules":
        _append(tmp, "flow_meter.py", "\n\ndef _p2_perturb_heat(litres, dk):\n    return litres * dk * 0.0011631\n")
    elif fam == "F17_gap_feature":
        _edit(tmp, "topology.py", "        (\n            CONF_OUTDOOR_TEMP_ENTITY,\n            0.0\n",
              "        (\n            CONF_DHW_TEMP_ENTITY,\n            0.0\n")
    elif fam == "F18_waiting_key":
        _append(tmp, "sensor.py", "\n\nclass _P2PerturbSensor:\n    @property\n    def _waiting_for(self):\n        return None if self._rows() else 'month'\n\n"
                "    @property\n    def native_value(self):\n        return self._rows()[0].get('saving')\n")
    else:
        file, old, new = spec
        _edit(tmp, file, old, new)


def main(argv):
    root = REPO
    if "--root" in argv:
        root = Path(argv[argv.index("--root") + 1]).resolve()
    if "--control" in argv:
        return 1 if control(root) else 0
    if "--fixture" in argv:
        return 1 if fixture() else 0
    if "--perturb" in argv:
        only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
        return 1 if perturb(root, only) else 0
    seams = enumerate_all(root)
    if "--json" in argv:
        print(json.dumps(seams, indent=1))
        return 0
    for s in seams:
        print(f"{'SEAM' if s['bad'] else 'ok  '} {s['family']} {s['file']}:{s['line']} {s['symbol']} -- {s['why']}")
    c = counts(seams)
    for fam in sorted(c):
        print(f"RESULT {fam}={c[fam]}")
    print(f"RESULT sites_total={len(seams)}")
    print(f"RESULT seams_total={sum(c.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
