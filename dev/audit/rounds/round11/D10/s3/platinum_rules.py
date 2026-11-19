#!/usr/bin/env python3
"""D10-s3 platinum-tier rule checks (D10.M1/M2), one check per rule, every cell.

Metric (one line each):
  untyped_requirements      = manifest.json requirements whose INSTALLED
                              distribution ships no py.typed and for which no
                              `types-<name>` / `<name>-stubs` distribution is
                              installed or pinned in tests/requirements-typing.txt
                              (hassfest's strict-typing requirement check, as the
                              rule page states it). Key: the distribution's file
                              list (installed, or the pinned wheel with --pinned).
  untyped_requirements_under_done_row = untyped_requirements while the
                              strict-typing row of quality_scale.yaml reads
                              `done`, else 0 (the row's claim is what fails).
  coordinator_untyped_config_entry = DataUpdateCoordinator subclasses in the
                              integration whose MRO (inside the package) carries
                              no `config_entry` annotation naming the typed
                              entry alias (rule pages strict-typing/runtime-data:
                              `config_entry: MyConfigEntry`). Key: the runtime
                              class's annotations via inspect.get_annotations.
  coordinator_untyped_under_done_row = the above while strict-typing is `done`.
  entry_point_bare          = parameters of the entry points the runtime-data
                              page lists (async_setup_entry/unload/migrate/
                              remove/remove_config_entry_device in __init__,
                              every platform's async_setup_entry, diagnostics
                              functions, async_get_options_flow) that are not
                              annotated with the typed entry alias.
  unshared_http_sessions    = construction sites of aiohttp.ClientSession /
                              httpx.(Async)Client instead of HA's shared session.
  blocking_io_imports       = imports of a blocking network library
                              (requests, urllib.request, http.client, socket,
                              urllib3, pycurl) in the integration.
  platinum_rows_missing     = checklist platinum rules with no row.

Command (from the export root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D10/s3/platinum_rules.py [--perturb X]
Perturbations (in memory only):
  --perturb req      threadpoolctl dropped from the manifest requirements in memory:
                     untyped_requirements 1 -> 0
  --pinned           judge requirements at the typing lock's pinned versions (downloads
                     wheels to a mkdtemp); same expected values
  --perturb row      strict-typing row read as `todo`: both *_under_done_row 1/1 -> 0
  --perturb coord    HeatPumpOptimizerCoordinator gets `config_entry: HeatPumpOptimizerConfigEntry`
                     (class annotation patched): coordinator_untyped_config_entry 1 -> 0
  --perturb session  one `aiohttp.ClientSession()` appended to config_flow.py source in
                     memory: unshared_http_sessions 0 -> 1 (control for the non-finding)
  --perturb entry    sensor.py's async_setup_entry `entry` annotation read as bare
                     ConfigEntry: entry_point_bare 0 -> 1 (control for the non-finding)
Expected at baseline (exact counts, +-0): untyped_requirements=1 (threadpoolctl; scipy is
  covered by scipy-stubs pinned in tests/requirements-typing.txt), untyped_requirements_under_done_row=1, coordinator_untyped_config_entry=1,
  coordinator_untyped_under_done_row=1, entry_point_bare=0, unshared_http_sessions=0,
  blocking_io_imports=0, platinum_rows_missing=0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64 (orchestrator box B3),
  venv-ci python 3.14.7, numpy 2.5.4, scipy 1.18.1, threadpoolctl 3.7.0.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import importlib.metadata as md  # noqa: E402
import inspect  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402

import sys  # noqa: E402

import yaml  # noqa: E402

sys.path.insert(0, os.getcwd())  # repo root, as tests/harness.py does

PKG = pathlib.Path("custom_components/heatpump_optimizer")
ALIAS = "HeatPumpOptimizerConfigEntry"
PLATINUM = ("async-dependency", "inject-websession", "strict-typing")
INIT_ENTRY_POINTS = {"async_setup_entry", "async_unload_entry", "async_migrate_entry",
                     "async_remove_entry", "async_remove_config_entry_device"}
DIAG_FUNCS = {"async_get_config_entry_diagnostics", "async_get_device_diagnostics"}
BLOCKING = {"requests", "urllib.request", "http.client", "socket", "urllib3", "pycurl"}


def files():
    return sorted(p for p in PKG.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def req_name(req):
    return re.split(r"[<>=!~\[; ]", req, maxsplit=1)[0].strip()


def typing_lock():
    """name -> version pinned by the project's own typing toolchain lock."""
    pins = {}
    path = pathlib.Path("tests/requirements-typing.txt")
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s;\\]+)", line)
            if m:
                pins[m.group(1).lower().replace("_", "-")] = m.group(2)
    return pins


def wheel_typed(name, version):
    """Download the pinned wheel to a private temp dir; does it ship py.typed?"""
    import subprocess
    import tempfile
    import zipfile
    d = tempfile.mkdtemp(prefix="d10s3-wheel-")
    subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "-q", "-d", d,
                    f"{name}=={version}"], check=True)
    whl = next(pathlib.Path(d).glob("*.whl"))
    return any(n.endswith("py.typed") for n in zipfile.ZipFile(whl).namelist())


def dist_typed(name, lock, pinned):
    key = name.lower()
    for stub in (f"types-{key}", f"{key}-stubs"):
        if stub in lock:
            return True, f"stub dist {stub}=={lock[stub]} pinned in tests/requirements-typing.txt"
        try:
            md.distribution(stub)
            return True, f"stub dist {stub} installed"
        except md.PackageNotFoundError:
            pass
    if pinned and key in lock:
        ok = wheel_typed(name, lock[key])
        return ok, f"pinned wheel {name}=={lock[key]} ships py.typed={ok}"
    try:
        dist = md.distribution(name)
    except md.PackageNotFoundError:
        return None, "not installed"
    if any(str(f).endswith("py.typed") for f in (dist.files or [])):
        return True, f"installed {dist.version} ships py.typed"
    return False, f"installed {dist.version}: no py.typed, no types-{name}/{name}-stubs installed or pinned"


def ann_src(node):
    return ast.unparse(node) if node is not None else "<none>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["req", "row", "coord", "session", "entry"])
    ap.add_argument("--pinned", action="store_true",
                    help="judge each requirement at the version tests/requirements-typing.txt pins "
                         "(pip download --no-deps into a mkdtemp; needs network)")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()

    qs = yaml.safe_load((PKG / "quality_scale.yaml").read_text())["rules"]
    status = {k: (v if isinstance(v, str) else v["status"]) for k, v in qs.items()}
    if a.perturb == "row":
        status["strict-typing"] = "todo"
    manifest = json.loads((PKG / "manifest.json").read_text())
    reqs = manifest.get("requirements", [])
    if a.perturb == "req":
        reqs = [r for r in reqs if req_name(r) != "threadpoolctl"]

    lock = typing_lock()
    missing = [r for r in PLATINUM if r not in status]
    untyped = []
    for r in reqs:
        ok, why = dist_typed(req_name(r), lock, a.pinned)
        print(f"REQ {req_name(r)} typed={ok} {why}")
        if ok is False:
            untyped.append(req_name(r))

    # --- AST census over every python cell -------------------------------
    entry_bare, sessions, blocking, cells = [], [], [], []
    platforms = {p.stem for p in PKG.glob("*.py")} & {
        "sensor", "switch", "button", "binary_sensor", "climate", "datetime", "number",
        "select", "text", "time", "date", "water_heater", "update", "event"}
    for p in files():
        rel = str(p)
        if p.suffix != ".py":
            reach = {
                "manifest.json": "strict-typing(requirements), async-dependency(requirements)",
                "quality_scale.yaml": "platinum rows",
                "py.typed": "strict-typing(marker present)",
            }.get(p.name, "no platinum rule reaches this file kind")
            cells.append((rel, reach))
            continue
        src = p.read_text(encoding="utf-8")
        if a.perturb == "session" and p.name == "config_flow.py":
            src += "\n_PERTURB = aiohttp.ClientSession()\n"
        tree = ast.parse(src)
        n_sess = n_block = n_entry = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = ann_src(node.func)
                if fn.endswith("ClientSession") or fn in ("httpx.AsyncClient", "httpx.Client"):
                    sessions.append(f"{rel}:{node.lineno} {fn}")
                    n_sess += 1
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                for m in mods:
                    if m in BLOCKING or any(m.startswith(b + ".") for b in BLOCKING):
                        blocking.append(f"{rel}:{node.lineno} {m}")
                        n_block += 1
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_ep = ((p.name == "__init__.py" and node.name in INIT_ENTRY_POINTS)
                         or (p.stem in platforms and node.name == "async_setup_entry")
                         or (p.name == "diagnostics.py" and node.name in DIAG_FUNCS)
                         or node.name == "async_get_options_flow")
                if not is_ep:
                    continue
                args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                for arg in args:
                    if arg.arg in ("entry", "config_entry"):
                        ann = ann_src(arg.annotation)
                        if a.perturb == "entry" and p.name == "sensor.py":
                            ann = "ConfigEntry"
                        good = ann == ALIAS
                        print(f"EP {rel}:{node.lineno} {node.name}({arg.arg}: {ann}) typed={good}")
                        if not good:
                            entry_bare.append(f"{rel}:{node.lineno} {node.name}")
                            n_entry += 1
        cells.append((rel, f"py: sessions={n_sess} blocking_imports={n_block} entry_bare={n_entry}"))

    # --- runtime: coordinator's config_entry annotation ------------------
    from custom_components.heatpump_optimizer import coordinator as cmod
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
    import importlib
    coord_untyped = []
    subclasses = []
    for mod_path in sorted(PKG.glob("*.py")):
        try:
            mod = importlib.import_module(f"custom_components.heatpump_optimizer.{mod_path.stem}")
        except Exception as e:  # pragma: no cover - reported, never silently skipped
            print(f"IMPORT-FAIL {mod_path} {type(e).__name__}: {e}")
            continue
        for obj in vars(mod).values():
            if (inspect.isclass(obj) and issubclass(obj, DataUpdateCoordinator)
                    and obj is not DataUpdateCoordinator
                    and obj.__module__.startswith("custom_components.heatpump_optimizer")
                    and obj not in subclasses):
                subclasses.append(obj)
    patched = None
    if a.perturb == "coord":
        C = cmod.HeatPumpOptimizerCoordinator
        patched = dict(inspect.get_annotations(C))
        new = dict(patched)
        new["config_entry"] = cmod.HeatPumpOptimizerConfigEntry
        C.__annotations__ = new
    for cls in subclasses:
        found = None
        for k in cls.__mro__:
            if not k.__module__.startswith("custom_components.heatpump_optimizer"):
                continue
            ann = inspect.get_annotations(k)
            if "config_entry" in ann:
                found = ann["config_entry"]
        ok = found is not None and ALIAS in str(found) or found is cmod.HeatPumpOptimizerConfigEntry
        print(f"COORD {cls.__module__}.{cls.__name__} config_entry_annotation={found!r} typed={ok}")
        if not ok:
            coord_untyped.append(cls.__name__)

    for rel, what in cells:
        print(f"CELL {rel} :: {what}")
    for s in sessions:
        print(f"SESSION {s}")
    for b in blocking:
        print(f"BLOCKING {b}")
    done = status.get("strict-typing") == "done"
    print("ROWS " + " ".join(f"{r}={status.get(r)}" for r in PLATINUM))
    print(f"RESULT cells_examined={len(cells)} files")
    print(f"RESULT platinum_rows_missing={len(missing)} rows")
    print(f"RESULT untyped_requirements={len(untyped)} requirements")
    print(f"RESULT untyped_requirements_under_done_row={len(untyped) if done else 0} requirements")
    print(f"RESULT coordinator_subclasses={len(subclasses)} classes")
    print(f"RESULT coordinator_untyped_config_entry={len(coord_untyped)} classes")
    print(f"RESULT coordinator_untyped_under_done_row={len(coord_untyped) if done else 0} classes")
    print(f"RESULT entry_point_bare={len(entry_bare)} params")
    print(f"RESULT unshared_http_sessions={len(sessions)} sites")
    print(f"RESULT blocking_io_imports={len(blocking)} imports")
    dp, dt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        import resource
        print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    except Exception:
        print("RESULT swapins=0")


if __name__ == "__main__":
    main()
