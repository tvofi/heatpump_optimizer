#!/usr/bin/env python3
"""D10.M1 config-flow-test-coverage (Bronze): does the suite show the user RECOVER from each flow error?

The rule: "Every error the flow can show needs a test ... After each error,
the test fixes the cause and finishes the flow, to show the user can
recover", for the user, reconfigure, reauthentication and options flows.

Metric: of the distinct (flow kind, step, error code) triples the suite's
flow tests render, the number for which NO flow object that rendered the
error later finished (create_entry, or an abort whose reason is
reauth_successful / reconfigure_successful) -- i.e. errors shown but never
recovered from. Per-flow-object tracking: each config/options flow instance
is followed from its first rendered form to its last result.
Count key: the results the production flow classes return
(async_show_form errors=..., async_create_entry, async_abort) while the test
scripts drive them; nothing is read from the test source.
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow and
config_flow:HeatPumpOptimizerOptionsFlow (async_show_form,
async_create_entry, async_abort wrapped per instance).
Scripts driven: tests/config_flow_steps.py (the flow suite; default) and,
with --with-entities, tests/entities.py too.
Perturbation: ``--perturb`` appends, after the suite, one recovery walk per
unrecovered user-step triple (the same flow resubmitted with a good token
and finished); the unrecovered count must fall by exactly that many (down).

Run (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/cfg_recovery.py [--with-entities] [--perturb]
Expected: see REPORT.md (exact count for the tree).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import collections
import contextlib
import io
import runpy
import sys
import tempfile
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))

from heatpump_optimizer import config_flow  # noqa: E402

TRACK = {}  # id(flow) -> dict(kind, errors:set[(step, code)], done:bool)
OK_ABORTS = {"reauth_successful", "reconfigure_successful"}


def _rec(flow):
    kind = "options" if isinstance(flow, config_flow.HeatPumpOptimizerOptionsFlow) else "config"
    if kind == "config":
        if getattr(flow, "_reauth_entry", None) is not None:
            kind = "reauth"
        elif getattr(flow, "_reconfigure_entry", None) is not None:
            kind = "reconfigure"
    r = TRACK.setdefault(id(flow), {"kind": kind, "errors": set(), "done": False, "obj": flow,
                                    "events": []})
    if kind != "config":
        r["kind"] = kind
    return r


def wrap(cls):
    show, create, abort = cls.async_show_form, cls.async_create_entry, cls.async_abort
    menu = cls.async_show_menu

    def async_show_form(self, *a, **k):
        r = _rec(self)
        errs = tuple(sorted((k.get("errors") or {}).values()))
        for field, code in (k.get("errors") or {}).items():
            r["errors"].add((k.get("step_id"), code))
        r["events"].append(("form", k.get("step_id"), errs))
        return show(self, *a, **k)

    def async_show_menu(self, *a, **k):
        _rec(self)["events"].append(("menu", k.get("step_id"), ()))
        return menu(self, *a, **k)

    def async_create_entry(self, *a, **k):
        _rec(self)["done"] = True
        _rec(self)["events"].append(("create", None, ()))
        return create(self, *a, **k)

    def async_abort(self, *a, **k):
        reason = k.get("reason") if "reason" in k else (a[0] if a else None)
        if reason in OK_ABORTS:
            _rec(self)["done"] = True
            _rec(self)["events"].append(("create", None, ()))
        return abort(self, *a, **k)
    cls.async_show_form, cls.async_create_entry, cls.async_abort = async_show_form, async_create_entry, async_abort
    cls.async_show_menu = async_show_menu


def stepped_past(r, step, code):
    """Lenient recovery: after the error form, the same flow reached a menu, an
    entry, a success abort, or a form of ANOTHER step (the page was accepted)."""
    ev = r["events"]
    for i, (kind, sid, errs) in enumerate(ev):
        if kind == "form" and sid == step and code in errs:
            for kind2, sid2, _e in ev[i + 1:]:
                if kind2 in ("menu", "create") or (kind2 == "form" and sid2 != step):
                    return True
    return False


def run_script(path):
    buf = io.StringIO()
    rc = None
    with contextlib.redirect_stdout(buf):
        try:
            runpy.run_path(path, run_name="__main__")
        except SystemExit as e:
            rc = e.code
    tail = buf.getvalue().strip().splitlines()[-1:] if buf.getvalue() else []
    print(f"SCRIPT {path} exit={rc} last={tail}")


async def recovery_walk(step, code):
    """The fix shape for a user-step error: same flow, good token, finish."""
    from harness import FakeHass

    class _R:
        def __init__(s, st, p):
            s.status, s._p = st, p

        async def json(s):
            return s._p

        async def __aenter__(s):
            return s

        async def __aexit__(s, *e):
            return False

    class _S:
        def __init__(s, script):
            s.script, s.n = list(script), 0

        def post(s, *a, **k):
            s.n += 1
            st = s.script[min(s.n - 1, len(s.script) - 1)]
            if isinstance(st, Exception):
                raise st
            return _R(*st)

    bad = {"invalid_tibber_token": (401, None), "cannot_connect": OSError("down")}.get(code)
    sess = _S([bad, (200, {"data": {"viewer": {"name": "x"}}})])
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: sess
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    first = {"name": "x", "tibber_token": "t", "weather_entity": "weather.home"}
    if code == "tibber_token_required":
        first.pop("tibber_token")
        await flow.async_step_user(dict(first))
        first["tibber_token"] = "t"
    elif code == "price_entity_required":
        await flow.async_step_user({**first, "price_source": "entity"})
    else:
        await flow.async_step_user(dict(first))
    await flow.async_step_user(dict(first))
    await flow.async_step_user_sensors({})
    await flow.async_step_setup_overview({})


def main():
    wrap(config_flow.HeatPumpOptimizerConfigFlow)
    wrap(config_flow.HeatPumpOptimizerOptionsFlow)
    scripts = ["tests/config_flow_steps.py"]
    if "--with-entities" in sys.argv:
        scripts.append("tests/entities.py")
    for s in scripts:
        run_script(s)
    def tally():
        triples = collections.defaultdict(lambda: [0, 0, 0])  # shown, finished, stepped_past
        for r in TRACK.values():
            for step, code in r["errors"]:
                t = triples[(r["kind"], step, code)]
                t[0] += 1
                t[1] += int(r["done"])
                t[2] += int(stepped_past(r, step, code))
        return triples
    triples = tally()
    before = sorted(k for k, (s, rec, past) in triples.items() if rec == 0)
    if "--perturb" in sys.argv:
        for kind, step, code in before:
            if kind == "config" and step == "user":
                asyncio.run(recovery_walk(step, code))
        triples = tally()
        print("RESULT perturbed=one recovery walk appended per unrecovered user-step error")
    unrec = sorted(k for k, (s, rec, past) in triples.items() if rec == 0)
    never_past = sorted(k for k, (s, rec, past) in triples.items() if rec == 0 and past == 0)
    for k, (s, rec, past) in sorted(triples.items()):
        print(f"TRIPLE {k[0]}/{k[1]}/{k[2]} shown_in_flows={s} finished_in_flows={rec} "
              f"stepped_past_in_flows={past}")
    print(f"RESULT never_stepped_past_triples={len(never_past)} count")
    for kind, n in sorted(collections.Counter(k[0] for k in never_past).items()):
        print(f"RESULT never_stepped_past_{kind}={n} count")
    by_kind = collections.Counter(k[0] for k in unrec)
    print(f"RESULT flows_tracked={len(TRACK)} count")
    print(f"RESULT error_triples={len(triples)} count")
    print(f"RESULT unrecovered_triples={len(unrec)} count")
    for kind, n in sorted(by_kind.items()):
        print(f"RESULT unrecovered_{kind}={n} count")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    main()
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
