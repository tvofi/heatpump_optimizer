"""The shape an installation actually runs, which nothing else here runs (#513).

Every other script in this directory imports the integration as
``heatpump_optimizer.*`` out of a checkout that has ``tests/`` sitting beside
``custom_components/``. No installation has either property: Home Assistant
imports it as ``custom_components.heatpump_optimizer.*``, and there is no
``tests/`` anywhere near it. ``coordinator._worker_env`` branches on that
sibling directory, so the branch every installation takes was the branch no
test run had ever taken, and #511 — every solve failing, on every install,
permanently — shipped green in v6.3.15.

So this lane builds the deployment shape instead of the checkout shape: the
tracked package alone, under ``<tmp>/custom_components/heatpump_optimizer``,
with no ``tests/`` sibling, imported under its production qualified name, and
it drives the real process-worker round trip through the real ``_worker_env``.

WHAT THIS LANE DOES NOT REPRODUCE. ``homeassistant`` has to be importable in
the worker child. In production that is Home Assistant's own interpreter; here
it is ``tests/hastub`` on the child's ``PYTHONPATH``. Divergence 3 of #513 —
real Home Assistant import semantics — therefore remains covered by nothing,
and this lane must not be read as covering it. It covers the other two, the
qualified name and the filesystem layout. The stub is contained on purpose: it
contributes one directory whose only entry is ``homeassistant/``, so it cannot
make the package under test resolvable and cannot mask the failure this lane
exists to catch. ``_check_stub_cannot_mask`` asserts that rather than trusting
it, because a lane that quietly stubs away the thing under test is worse than
no lane at all.

The parent process here never imports the integration. It measures by running
a driver of itself (``--driver``) under ``-P``, so neither the current
directory nor this file's directory reaches the driver's ``sys.path``. The trap
that guards against: any path from which the repository's own copy of the
package resolves turns every check below green while proving nothing, and it
looks exactly like a pass. Isolation is therefore not trusted — the package's
provenance is asserted, in the parent from ``coordinator.__file__`` and in the
child from ``inspect.getfile``.

    python tests/deployment_shape.py
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Home Assistant loads an integration from ``<config>/custom_components/<domain>``.
# These two names are the deployment convention and the only place either
# spelling is written down in this file: every module name the checks below
# compare against is derived from a runtime object, so asserting the invariant
# does not quietly pin the one symbol #511 happened to break.
CONFIG_DIR_NAME = "custom_components"
PACKAGE_NAME = "heatpump_optimizer"
PACKAGE_REL = f"{CONFIG_DIR_NAME}/{PACKAGE_NAME}"

# The two seams that hand an object to the worker child. ``_await_process``
# takes ``(hass, fn, *args)``; ``_run_in_process`` takes ``(fn, args)``.
WORKER_SEAMS = {"_await_process": 1, "_run_in_process": 0}

# A module the package launches by PATH rather than importing runs only inside
# a child interpreter, so nothing measuring this process can see it. That is
# how process_worker.py reached v6.3.15 with 36 of 36 statements untested
# (#505) and took #511 with it. The set is derived from the package's own
# source, never listed, and every member must be a script this lane actually
# launched -- so a second worker script cannot arrive without a lane.

MARKER = "<<<deployment-shape-json>>>"

FAILS = 0


def check(name: str, cond: object, detail: str = "") -> bool:
    global FAILS
    if cond:
        print(f"  ok   {name}")
        return True
    FAILS += 1
    print(f"  FAIL {name}" + (f"  [{detail}]" if detail else ""))
    return False


# --- the driver: runs inside the deployment shape, measures, prints JSON -----


def _resolve(root: object, dotted: str) -> object:
    obj = root
    for part in dotted.split("."):
        obj = getattr(obj, part)
    return obj


def _call_target(node: ast.Call) -> str | None:
    """The dotted name of ``node``'s worker-bound argument, or None."""
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
    index = WORKER_SEAMS.get(name)
    if index is None or len(node.args) <= index:
        return None
    arg = node.args[index]
    parts: list[str] = []
    while isinstance(arg, ast.Attribute):
        parts.append(arg.attr)
        arg = arg.value
    if not isinstance(arg, ast.Name):
        return None
    parts.append(arg.id)
    return ".".join(reversed(parts))


def _shipped_objects(module: object) -> tuple[list[tuple[int, str, object]], list[str]]:
    """Every object the integration hands to the worker, found by call site.

    Enumerated from the source rather than listed here, because a list would
    pin today's two symbols and #513 asks for the invariant that catches the
    next one.
    """
    source = Path(module.__file__).read_text(encoding="utf-8")
    found: list[tuple[int, str, object]] = []
    unresolved: list[str] = []
    for node in ast.walk(ast.parse(source, module.__file__)):
        if not isinstance(node, ast.Call):
            continue
        dotted = _call_target(node)
        if dotted is None:
            func = node.func
            label = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if label in WORKER_SEAMS:
                unresolved.append(f"line {node.lineno}: {ast.dump(node.func)}")
            continue
        try:
            found.append((node.lineno, dotted, _resolve(module, dotted)))
        except AttributeError:
            unresolved.append(f"line {node.lineno}: {dotted} does not resolve")
    return found, unresolved


def _path_named_scripts(package: Path) -> list[str]:
    """Package modules the package reaches by path, not by import.

    A module named as a string is launched or loaded as a file, so importing
    the package never executes it and no in-process measurement of this suite
    can reach it. Derived from the source so a second one cannot be added
    silently; ``process_worker.py`` at ``coordinator.py``'s ``_ensure_worker``
    is the only one today.
    """
    names = {p.name for p in package.glob("*.py")}
    found: set[str] = set()
    for src in sorted(package.glob("*.py")):
        tree = ast.parse(src.read_text(encoding="utf-8"), str(src))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in names:
                found.add(node.value)
    return sorted(found)


def _expected_module(obj: object) -> str:
    return getattr(obj, "__module__", None) or type(obj).__module__


def _driver(tmp: str, hastub: str) -> int:
    # What Home Assistant does: the config directory goes on ``sys.path`` in
    # this process. It does NOT go into the environment, which is the whole of
    # #511 — ``_worker_env`` copies ``os.environ`` and so cannot see it.
    os.environ["PYTHONPATH"] = hastub
    sys.path.insert(0, tmp)

    coordinator = __import__(
        f"{CONFIG_DIR_NAME}.{PACKAGE_NAME}.coordinator", fromlist=["coordinator"]
    )
    inherited = os.environ["PYTHONPATH"].split(os.pathsep)
    built = coordinator._worker_env()["PYTHONPATH"].split(os.pathsep)
    out: dict[str, object] = {
        "coordinator_file": coordinator.__file__,
        "worker_env_added": built[: len(built) - len(inherited)],
        "worker_env_inherited": inherited,
        "driver_pid": os.getpid(),
    }

    # os.getpid pickles as a stdlib name that resolves in any layout, so this
    # round trip succeeds on a broken tree too. That is deliberate: it proves
    # the worker mechanism itself works, which is what isolates #511 to the
    # qualified name, and it lets the launch below be observed either way.
    try:
        out["child_pid"] = coordinator._run_in_process(os.getpid, ())
    except Exception as err:  # noqa: BLE001 - reported, then asserted on
        out["child_pid_error"] = f"{type(err).__name__}: {err}"
    worker = coordinator._PROCESS_WORKER
    out["launched_scripts"] = sorted(
        {Path(a).name for a in (worker.args if worker else []) if str(a).endswith(".py")}
    )

    shipped, unresolved = _shipped_objects(coordinator)
    out["unresolved_call_sites"] = unresolved
    records: list[dict[str, object]] = []
    for lineno, dotted, obj in shipped:
        record: dict[str, object] = {
            "line": lineno,
            "symbol": dotted,
            "module": _expected_module(obj),
        }
        # The invariant: whatever the parent ships, the child must be able to
        # import that object's own module. Asked of the CHILD, by shipping the
        # object and having the child read ``__module__`` back off it — which
        # it can only do once the unpickle by qualified name has succeeded.
        # ``inspect.getfile`` then answers the question the module name cannot:
        # WHERE the child resolved it. Both callables are stdlib, so they
        # pickle by a name that resolves anywhere and only the argument is
        # under test.
        try:
            record["child_module"] = coordinator._run_in_process(
                getattr, (obj, "__module__")
            )
            record["child_file"] = coordinator._run_in_process(inspect.getfile, (obj,))
        except Exception as err:  # noqa: BLE001 - reported, then asserted on
            record["error"] = f"{type(err).__name__}: {err}"
        records.append(record)
    out["shipped"] = records

    package = Path(tmp) / PACKAGE_REL
    out["path_named_scripts"] = _path_named_scripts(package)
    print(MARKER)
    print(json.dumps(out))
    return 0


# --- the parent: builds the shape, runs the driver, asserts ------------------


def _tracked(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--", PACKAGE_REL],
        capture_output=True,
        check=True,
    ).stdout.decode()
    return [rel for rel in out.split("\0") if rel]


def _materialise(repo: Path, dest: Path) -> int:
    """The tracked package, alone, with no ``tests/`` sibling.

    Tracked paths only: an installation ships what the repository ships, not
    ``__pycache__`` or whatever else is lying in the working tree. Content
    comes from the working tree so that a fix under test is the thing measured
    rather than whatever HEAD happens to hold.

    Files the gate declares INERT are skipped. Copying one would open it, the
    audit hook would record it, and ``closure.py check`` refuses a file that is
    both declared unread and recorded as read (#357) -- a contradiction no CI
    autofix repairs. The predicate is asked of ``closure.py`` rather than
    restated here, so a file entering or leaving INERT needs no edit in this
    lane. Nothing dropped this way can change what the lane measures: INERT
    means no test reads it, and ``quality_scale.yaml`` -- the only package file
    it covers -- is a register hassfest skips for custom repositories.
    """
    # Local: `tests/` is deliberately off this file's sys.path, because the
    # driver half runs under -P and must not resolve anything from here.
    sys.path.insert(0, str(repo / "tests"))
    import closure

    rels = [rel for rel in _tracked(repo) if not closure.is_inert(rel)]
    for rel in rels:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, target)
    return len(rels)


def _check_stub_cannot_mask(hastub: Path) -> None:
    entries = sorted(p.name for p in hastub.iterdir() if not p.name.startswith("."))
    check(
        "the Home Assistant stub cannot make the package under test resolvable",
        entries == ["homeassistant"],
        f"tests/hastub holds {entries}",
    )


def _run_driver(tmp: Path, hastub: Path, neutral: Path) -> dict | None:
    env = dict(os.environ)
    # The child inherits this and nothing else, so it must not name any path
    # from which the package could resolve. That is what makes the round trip
    # below a measurement rather than a formality.
    env["PYTHONPATH"] = str(hastub)
    proc = subprocess.run(
        [sys.executable, "-P", str(Path(__file__).resolve()), "--driver", str(tmp), str(hastub)],
        capture_output=True,
        text=True,
        cwd=str(neutral),
        env=env,
    )
    if proc.stderr.strip():
        print("  -- driver stderr (the child's traceback lands here) --")
        for line in proc.stderr.rstrip().splitlines():
            print(f"     {line}")
    if MARKER not in proc.stdout:
        check(
            "the driver reported its measurements",
            False,
            f"rc={proc.returncode}, no marker in stdout: {proc.stdout[-400:]!r}",
        )
        return None
    return json.loads(proc.stdout.split(MARKER, 1)[1].strip().splitlines()[0])


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    hastub = repo / "tests" / "hastub"
    print("\n=== deployment shape: an installation's layout and module name (#513) ===")

    print("\n-- the shape")
    with tempfile.TemporaryDirectory(prefix="hpo-deployment-") as work:
        # Resolved, because the integration reports itself through
        # ``Path(__file__).resolve()`` and macOS hands out /var/folders paths
        # that resolve to /private/var — comparing the two spellings is a
        # check that fails for a reason having nothing to do with the subject.
        root = Path(work).resolve()
        tmp = root / "config"
        neutral = root / "cwd"
        neutral.mkdir(parents=True)
        copied = _materialise(repo, tmp)
        check("the tracked package materialised", copied > 0, f"{copied} files")
        check(
            "there is no tests/ sibling, so _worker_env takes production's branch",
            not (tmp / "tests").exists(),
            f"{tmp / 'tests'} exists",
        )
        _check_stub_cannot_mask(hastub)

        data = _run_driver(tmp, hastub, neutral)
        if data is None:
            return _close()

        print("\n-- what the parent built for the child")
        added = data["worker_env_added"]
        check(
            "_worker_env ran against the deployment layout, not this checkout",
            all(str(tmp) == p or p.startswith(f"{tmp}{os.sep}") for p in added),
            f"added {added}",
        )
        check(
            "and so added no tests/ or stub directory",
            not any(Path(p).name in ("tests", "hastub") for p in added),
            f"added {added}",
        )
        check(
            "the integration under test came from the temporary tree",
            data["coordinator_file"].startswith(f"{tmp}{os.sep}"),
            data["coordinator_file"],
        )
        # The child inherits these. If any of them could resolve the package,
        # the round trip below would succeed for a reason that has nothing to
        # do with the fix and this lane would be green and worthless — the
        # exact trap that made #513 hard to reproduce by hand.
        leaks = [
            p
            for p in data["worker_env_inherited"]
            if (Path(p) / PACKAGE_REL).exists() or (Path(p) / PACKAGE_NAME).exists()
        ]
        check(
            "no inherited path can resolve the package, so the child has only "
            "what _worker_env gave it",
            not leaks,
            f"{leaks}",
        )

        print("\n-- the process-worker round trip")
        check(
            "the round trip reached a second interpreter",
            data.get("child_pid") not in (None, data["driver_pid"]),
            data.get("child_pid_error", f"child_pid={data.get('child_pid')}"),
        )

        print("\n-- every object shipped to the worker is importable there")
        shipped = data["shipped"]
        check(
            "the worker seams were enumerated from the source",
            len(shipped) > 0,
            "no call site of _await_process/_run_in_process resolved",
        )
        check(
            "every worker call site resolved to an object",
            not data["unresolved_call_sites"],
            "; ".join(data["unresolved_call_sites"]),
        )
        for record in shipped:
            where = f"coordinator.py:{record['line']} {record['symbol']}"
            check(
                f"{where} -> the child imports {record['module'].split('.')[0]}",
                record.get("child_module") == record["module"],
                record.get("error", f"child said {record.get('child_module')!r}"),
            )
            check(
                f"{where} -> and resolved it from the deployment tree",
                str(record.get("child_file", "")).startswith(f"{tmp}{os.sep}"),
                record.get("error", f"child read it from {record.get('child_file')!r}"),
            )
        crossed = data.get("child_pid") not in (None, data["driver_pid"])

        print("\n-- nothing runs only in a child interpreter unwatched")
        # The package reaches these by path, so importing it never executes
        # them and no in-process measurement of this suite can see them. Each
        # must be a script this lane launched. Derived from the package source
        # and observed from the worker's own argv, so neither side is a list
        # anyone has to maintain.
        named = data["path_named_scripts"]
        launched = data["launched_scripts"]
        check(
            "the package names at least one script it runs by path",
            bool(named),
            "if this is now empty the derivation broke, not the package",
        )
        check(
            "every module the package runs by path is exercised here",
            set(named) == set(launched),
            f"named {named}, launched {launched} — a module reached by path "
            f"runs only in a child interpreter, where nothing measures it; "
            f"process_worker.py entered the tree that way in #461 with 36 of "
            f"36 statements untested and #511 followed",
        )
    return _close()


def _close() -> int:
    if FAILS:
        print(f"\n{FAILS} DEPLOYMENT SHAPE CHECK(S) FAILED")
        return 1
    print("\nALL DEPLOYMENT SHAPE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--driver":
        sys.exit(_driver(sys.argv[2], sys.argv[3]))
    sys.exit(main())
