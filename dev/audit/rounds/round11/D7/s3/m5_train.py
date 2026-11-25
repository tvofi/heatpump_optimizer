#!/usr/bin/env python3
"""D7.M5 (round 11, seat D7-s3): this year's train -- the test that pins each added module,
its doc paragraph and its owner.

Metric (one line): per function of each module the round's enumerator lists, `pinned` when a
tests/ script that enters it reports a failing check it did not report unmutated once the
function raises on entry (its deletion); `swallowed` when every entering script stays green;
`unentered` when no script of the behaviour suite enters it at all; `not_reached` when an
entering script was not driven under the mutant (named, never read as green).

    # the universe (run on the round's checkout; the export has no .git):
    git -C <checkout> diff --name-status --diff-filter=A 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 \
        92d38ecb640bd462f2e19c0814d0f0b7df1ee692 -- 'custom_components/*.py'
    # 1. record which functions each script enters (one run per script; see fn_trace.sh)
    # 2. the table:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py pins --trace DIR
    # 3. the deletion mutants (resumable; --only <module> for one module):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py mutate --trace DIR --out m5_mutants.json
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py report --trace DIR --out m5_mutants.json
    # the redispatched item C2 (the additions since v4 that live in this seat's cells), same method:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py mutate --c2 --trace DIR --out m5_c2_mutants.json
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py report --c2 --trace DIR --out m5_c2_mutants.json
    # null control: a mutant that raises in a function no script enters must kill nothing
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m5_train.py null --trace DIR

Instrumented symbols: every function of the listed modules, hooked at PY_START by
`trace_site/sitecustomize.py` (HPO_FN_MUTATE=<file>:<first line> raises RuntimeError there,
in memory -- no file of the tree is edited). Count key: (module file, qualified name, first
line), read off the production code object, so a fix that adds a failing-on-deletion check
moves `swallowed`/`unentered` down and a relabel of this harness's records cannot.
Perturbation: the deletion itself; `pinned` rows are the ones whose failing-check count rises.
Counts only (no timing). Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64,
Python 3.14.7; expected values in REPORT.md; exact up to the suite's own baseline failures.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import glob
import json
import re
import subprocess
import sys
import tempfile
import time

PKG = os.path.join("custom_components", "heatpump_optimizer")
HERE = os.path.dirname(os.path.abspath(__file__))
# The enumerator's 29 lines at the baseline (the command in the header printed them).
MODULES = ("batchmath debugger dhw_planner draw_range driving_grade duty_legs duty_switch "
           "early_cutoff entry_config flow_meter heat_curve heat_energy issues learner_progress "
           "log_latch notifier off_restore payload plan_slots plan_step price_tiles quiet_windows "
           "replay_doc running_signal runs slab_seed slot_drivers supply_hold whatif").split()


# C2, handed over from round 10: "batched gradient and bounds gate, drift gate, scoped gate, card
# collaborators, stress budgets, weekly windows, topology catalogue, wood and coil variants, DHW
# confidence, Tuya, re-anchor law". The ones whose code is in custom_components/*.py, as
# (group, module, regular expression over the qualified name). The drift gate, the scoped gate,
# the stress budgets (tests/) and the card collaborators (www/) are outside this seat's cells.
C2 = (
    ("batched_gradient_and_bounds_gate", "optimizer", r"_batch_fd_gradient|_fused_value_and_gradient$|_memoized_value_and_gradient$|_bounds_supported_by_batch|_comfort_terms_batch|_cost_terms_batch|_terminal_cost_batch"),
    ("batched_gradient_and_bounds_gate", "thermal_model", r"_batch_cop|simulate_trajectory_batch$"),
    ("batched_gradient_and_bounds_gate", "tariff", r"_batch$"),
    ("weekly_windows", "dhw_schedule", r"day_selector|weekly_windows|day_spec_problem|day_overrides|resolved_day_spec"),
    ("topology_catalogue", "topology", r"."),
    ("wood_and_coil", "wood_fuel", r"."),
    ("wood_and_coil", "thermal_model", r"^wood_share$|_wood_share_vec|dhw_coil_draw_reduction|apply_dhw_coil|dhw_coil_active"),
    ("wood_and_coil", "dhw_planner", r"_dhw_coil_wood_forecast"),
    ("wood_and_coil", "optimizer", r"_sharing_wood_side|_wood_covered_share"),
    ("dhw_confidence", "coordinator", r"_dhw_confidence_band|_confidence_margins"),
    ("tuya_signals_and_prefill", "pump_signals", r"."),
    ("tuya_signals_and_prefill", "device_prefill", r"."),
    ("tuya_signals_and_prefill", "modbus_prefill", r"."),
    ("tuya_signals_and_prefill", "name_match", r"."),
    ("tuya_signals_and_prefill", "prefill_offer", r"."),
    ("re_anchor_law", "coordinator", r"_reanchor_house_heat_loss_scale"),
    ("re_anchor_law", "thermal_model", r"^reanchor_heat_loss$"),
)


def targets(a):
    """[(group, module, function record)]: the step's modules, or C2's symbols with --c2."""
    out = []
    if getattr(a, "c2", False):
        for group, module, pattern in C2:
            rx = re.compile(pattern)
            for f in functions_of(a.root, module):
                if not f["trivial"] and rx.search(f["qual"]) and "<" not in f["qual"]:
                    out.append((group, module, f))
        return out
    for m in MODULES:
        for f in functions_of(a.root, m):
            if not f["trivial"]:
                out.append((m, m, f))
    return out


def functions_of(root, module):
    path = os.path.join(root, PKG, module + ".py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []

    def walk(node, scope):
        for n in ast.iter_child_nodes(node):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = n.body
                if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
                    body = body[1:]
                trivial = all(isinstance(b, ast.Pass) or (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))
                              for b in body)
                out.append({"module": module, "qual": ".".join(scope + [n.name]), "line": n.lineno,
                            "loc": n.end_lineno - n.lineno + 1, "trivial": trivial})
                walk(n, scope + [n.name])
            elif isinstance(n, ast.ClassDef):
                walk(n, scope + [n.name])
            else:
                walk(n, scope)

    walk(tree, [])
    return out


def load_trace(tdir):
    """{(file, first line): {script,...}} and the per-script baseline record."""
    entered = {}
    for f in glob.glob(os.path.join(tdir, "*.json")):
        base = os.path.basename(f)
        if base.startswith("plandata"):
            continue
        script = base.split(".")[0]
        try:
            rows = json.load(open(f))
        except (ValueError, OSError):
            continue
        for rel, _qual, line in rows:
            entered.setdefault((rel, line), set()).add(script)
    seconds = {}
    done = os.path.join(tdir, "_done.txt")
    if os.path.exists(done):
        for ln in open(done):
            m = re.match(r"(\S+) rc=(-?\d+) seconds=(\d+)", ln)
            if m:
                seconds[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return entered, seconds


FAIL = re.compile(r"^\s*(FAIL|FAILED|ERROR)\b")


def fail_set(text):
    """The failing checks a run names: each FAIL line less its bracketed detail, and the last
    line of a traceback (a crash is a failing check too)."""
    out = set()
    lines = text.splitlines()
    for ln in lines:
        if FAIL.match(ln):
            out.add(re.sub(r"\s+\[.*$", "", ln.strip())[:160])
    if "Traceback (most recent call last)" in text:
        tail = [ln for ln in lines if ln.strip()]
        if tail:
            out.add("CRASH " + re.sub(r"0x[0-9a-f]+", "0x", tail[-1].strip())[:160])
    return out


def run_script(root, script, mutate, timeout, base_fail):
    env = dict(os.environ)
    tmp = tempfile.mkdtemp(prefix="d7s3m5.")
    env["PYTHONPATH"] = os.path.join(HERE, "trace_site") + os.pathsep + os.path.join("tests", "hastub")
    env["HPO_PLANDATA"] = os.path.join(tmp, "plandata.json")
    env.pop("HPO_FN_TRACE", None)
    env["PYTHONUNBUFFERED"] = "1"  # a failing check is read the moment it prints
    if mutate:
        env["HPO_FN_MUTATE"] = mutate
    proc = subprocess.Popen([sys.executable, os.path.join("tests", script + ".py")], cwd=root, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    t0 = time.time()
    chunks = []
    killed_early = False
    try:
        for ln in proc.stdout:
            chunks.append(ln)
            if FAIL.match(ln):
                key = re.sub(r"\s+\[.*$", "", ln.strip())[:160]
                if base_fail is not None and key not in base_fail:
                    killed_early = True
                    proc.kill()
                    break
            if time.time() - t0 > timeout:
                proc.kill()
                break
    finally:
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
    text = "".join(chunks)
    timed_out = (time.time() - t0 > timeout) and not killed_early
    return text, proc.returncode, killed_early, timed_out, time.time() - t0


def baseline_fails(tdir, script):
    p = os.path.join(tdir, script + ".log")
    return fail_set(open(p, errors="replace").read()) if os.path.exists(p) else set()


def docs_paragraphs(root, module):
    n = 0
    files = glob.glob(os.path.join(root, "docs", "*.md")) + [os.path.join(root, "README.md")]
    pat = re.compile(r"(?<![A-Za-z0-9_])%s\.py\b" % re.escape(module))
    for f in files:
        try:
            for para in re.split(r"\n\s*\n", open(f, encoding="utf-8").read()):
                if pat.search(para):
                    n += 1
        except OSError:
            pass
    return n


def importers(root, module):
    out = set()
    for f in glob.glob(os.path.join(root, PKG, "*.py")):
        me = os.path.basename(f)[:-3]
        if me == module:
            continue
        for n in ast.walk(ast.parse(open(f, encoding="utf-8").read())):
            if isinstance(n, ast.ImportFrom) and n.level >= 1:
                if n.module == module or (n.module is None and any(a.name == module for a in n.names)):
                    out.add(me)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in (module, "." + module):
                out.add(me + "(lazy)")
    return sorted(out)


def cmd_pins(a):
    entered, seconds = load_trace(a.trace)
    tot = {"functions": 0, "entered": 0}
    for m in MODULES:
        fns = [f for f in functions_of(a.root, m) if not f["trivial"]]
        ent = [f for f in fns if (m + ".py", f["line"]) in entered]
        scripts = set()
        for f in ent:
            scripts |= entered[(m + ".py", f["line"])]
        src = open(os.path.join(a.root, PKG, m + ".py"), encoding="utf-8").read()
        doc = ast.get_docstring(ast.parse(src)) or ""
        imps = importers(a.root, m)
        tot["functions"] += len(fns)
        tot["entered"] += len(ent)
        print("ROW %s functions=%d entered=%d unentered=%d scripts=%d docstring_lines=%d docs_paragraphs=%d importers=%d [%s]" % (
            m, len(fns), len(ent), len(fns) - len(ent), len(scripts), len(doc.splitlines()),
            docs_paragraphs(a.root, m), len(imps), ",".join(imps)))
        for f in fns:
            if (m + ".py", f["line"]) not in entered:
                print("UNENTERED %s.py:%d %s loc=%d" % (m, f["line"], f["qual"], f["loc"]))
    print("RESULT modules=%d modules" % len(MODULES))
    print("RESULT functions=%d functions" % tot["functions"])
    print("RESULT entered=%d functions" % tot["entered"])
    print("RESULT unentered=%d functions" % (tot["functions"] - tot["entered"]))
    tail()
    return 0


def cmd_mutate(a):
    entered, seconds = load_trace(a.trace)
    results = json.load(open(a.out)) if os.path.exists(a.out) else {}
    todo = []
    for group, m, f in targets(a):
        if a.only and group not in a.only.split(","):
            continue
        key = "%s.py:%d:%s" % (m, f["line"], f["qual"])
        scripts = sorted(entered.get((m + ".py", f["line"]), ()), key=lambda s: seconds.get(s, (0, 1e9))[1])
        if not scripts:
            continue
        if key in results:
            driven = {r["script"] for r in results[key]["scripts"] if "skipped" not in r}
            left = [x for x in scripts if x not in driven and seconds.get(x, (0, 1e9))[1] <= a.max_script_seconds]
            if not (a.retry and results[key]["verdict"] != "pinned" and left):
                continue
        todo.append((key, m, f, scripts))
    # cheapest first, so a cut window leaves the expensive tail not reached, by name
    todo.sort(key=lambda t: min(seconds.get(s, (0, 1e9))[1] for s in t[3]))
    deadline = time.time() + a.budget
    base = {}
    for key, m, f, scripts in todo:
        if time.time() > deadline:
            break
        rec = {"scripts": [], "verdict": "swallowed"}
        prior = {r["script"]: r for r in results.get(key, {}).get("scripts", []) if "skipped" not in r}
        for s in scripts:
            if s in prior:
                rec["scripts"].append(prior[s])  # green under the mutant on an earlier pass
                continue
            cost = seconds.get(s, (0, 1e9))[1]
            if cost > a.max_script_seconds:
                rec["scripts"].append({"script": s, "skipped": "over --max-script-seconds"})
                if rec["verdict"] == "swallowed":
                    rec["verdict"] = "not_reached"
                continue
            if s not in base:
                base[s] = baseline_fails(a.trace, s)
            text, rc, early, timed_out, wall = run_script(
                a.root, s, "%s.py:%d" % (m, f["line"]), max(120, 4 * cost + 60), base[s])
            new = sorted(fail_set(text) - base[s])
            hit = "d7s3-deleted" in text
            rec["scripts"].append({"script": s, "rc": rc, "new_failing": new[:3], "n_new": len(new),
                                   "timed_out": timed_out, "sentinel_in_output": hit})
            if new:
                rec["verdict"] = "pinned"
                rec["pinned_by"] = s
                break
            if timed_out:
                rec["verdict"] = "timeout"
        results[key] = rec
        print("%s %s %s" % (rec["verdict"], key, rec.get("pinned_by", "")), flush=True)
        json.dump(results, open(a.out + ".tmp", "w"), indent=0, sort_keys=True)
        os.replace(a.out + ".tmp", a.out)
    return 0


def cmd_report(a):
    entered, seconds = load_trace(a.trace)
    results = json.load(open(a.out)) if os.path.exists(a.out) else {}
    tot = {}
    tg = targets(a)
    groups = []
    for g, _m, _f in tg:
        if g not in groups:
            groups.append(g)
    for grp in groups:
        c = {"functions": 0, "pinned": 0, "swallowed": 0, "unentered": 0, "not_reached": 0, "timeout": 0}
        by = set()
        for g, m, f in tg:
            if g != grp:
                continue
            c["functions"] += 1
            key = "%s.py:%d:%s" % (m, f["line"], f["qual"])
            if (m + ".py", f["line"]) not in entered:
                c["unentered"] += 1
                print("UNENTERED " + key)
            elif key in results:
                v = results[key]["verdict"]
                c[v] = c.get(v, 0) + 1
                if v != "pinned":
                    print("%s %s scripts=%s" % (v.upper(), key, ",".join(s["script"] for s in results[key]["scripts"])))
            else:
                c["not_reached"] += 1
                print("NOT_REACHED " + key)
            if key in results and results[key].get("pinned_by"):
                by.add(results[key]["pinned_by"])
        print("ROW %s functions=%d pinned=%d swallowed=%d unentered=%d not_reached=%d timeout=%d pinned_by=[%s]" % (
            grp, c["functions"], c["pinned"], c["swallowed"], c["unentered"], c["not_reached"], c["timeout"], ",".join(sorted(by))))
        for k, v in c.items():
            tot[k] = tot.get(k, 0) + v
    for k in ("functions", "pinned", "swallowed", "unentered", "not_reached", "timeout"):
        print("RESULT %s=%d functions" % (k, tot.get(k, 0)))
    tail()
    return 0


def cmd_null(a):
    """Null control: the hook armed on a line no function starts at; nothing may die."""
    entered, seconds = load_trace(a.trace)
    n_new = 0
    for s in a.scripts.split(","):
        base = baseline_fails(a.trace, s)
        text, rc, early, timed_out, wall = run_script(a.root, s, "batchmath.py:999999", 3600, base)
        new = fail_set(text) - base
        n_new += len(new)
        print("NULL %s rc=%s new_failing=%d" % (s, rc, len(new)))
    print("RESULT null_new_failing=%d checks" % n_new)
    tail()
    return 0


def tail():
    print("RESULT thread_factor=%.3f ratio" % (time.process_time() / max(time.thread_time(), 1e-9)))
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    try:
        import resource
        print("RESULT swapins=%d count" % resource.getrusage(resource.RUSAGE_SELF).ru_nswap)
    except Exception:
        print("RESULT swapins=0 count")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("pins", "mutate", "report", "null", "list"))
    ap.add_argument("--root", default=".")
    ap.add_argument("--trace")
    ap.add_argument("--out", default=os.path.join(HERE, "m5_mutants.json"))
    ap.add_argument("--only")
    ap.add_argument("--c2", action="store_true")
    ap.add_argument("--retry", action="store_true", help="re-drive not_reached mutants with the scripts skipped before")
    ap.add_argument("--budget", type=float, default=3600.0)
    ap.add_argument("--max-script-seconds", type=float, default=200.0)
    ap.add_argument("--scripts", default="wood_advisor,solar_alignment,debug_collect")
    a = ap.parse_args()
    if a.cmd == "list":
        for m in MODULES:
            print("custom_components/heatpump_optimizer/%s.py" % m)
        return 0
    return {"pins": cmd_pins, "mutate": cmd_mutate, "report": cmd_report, "null": cmd_null}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
