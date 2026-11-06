"""R10-RCA-PROCESS-WORKER-HANG harness: waits on another party that stays alive and silent.

Two arms, one class: a synchronous wait on a peer (pipe, child, lock, queue)
with no deadline.

``--scan`` enumerates every such call in a package by AST: ``pickle.load`` of
a stream, a zero-argument ``wait``/``join``/``recv``/``recv_bytes``/
``communicate``/``acquire`` with no ``timeout``/``blocking``, ``select.select``
with no timeout, ``subprocess.run``/``call``/``check_call``/``check_output``
with no ``timeout``, a queue's ``get()`` with no timeout, and a ``with`` over a
module-level name ending ``_LOCK`` (a lock taken with no deadline). An awaited
call is skipped (a coroutine's wait is cancellable at unload). Each site prints
with its enclosing function, the key a reasoned disposition needs: the
defect's ``pickle.load(stdout)`` and its fix's descriptor-less fallback share
file, call and snippet, and differ only there.

``--drive`` runs a job in the real process worker that stays alive and never
answers (``time.sleep(--silent)``), on a thread, and reports whether
``_run_in_process`` came back within ``--cap`` seconds, then fires the stop
path while that call is in flight and times it. ``--reply-timeout S`` sets the
tree's ``PROCESS_REPLY_TIMEOUT_S`` when the tree has one: the perturbation.
``--answer`` replaces the silent job with one that answers in 0.1 s: the null
control, which returns in every tree.

    PYTHONPATH=<root>/tests/hastub:<root>/custom_components python3 dev/audit/harnesses/silent_peer_waits.py --scan <root>/custom_components/heatpump_optimizer
    PYTHONPATH=<root>/tests/hastub:<root>/custom_components python3 dev/audit/harnesses/silent_peer_waits.py --drive [--cap 6] [--silent 30] [--reply-timeout 2] [--answer]

Results by tree are recorded in dev/audit/rca/r10-process-worker-hang.md;
this header carries none, because they change when the fix lands.
"""
from __future__ import annotations

import argparse
import ast
import sys
import threading
import time
from pathlib import Path

ZERO_ARG = {"wait", "join", "recv", "recv_bytes", "communicate", "acquire"}
SUBPROCESS_CALLS = {"run", "call", "check_call", "check_output"}


def _has_kw(call: ast.Call, *names: str) -> bool:
    return any(k.arg in names for k in call.keywords)


def _why(node: ast.AST) -> str | None:
    """The reason ``node`` is a deadline-less wait on a peer, else ``None``."""
    if isinstance(node, ast.With):
        for item in node.items:
            expr = item.context_expr
            if isinstance(expr, ast.Name) and expr.id.endswith("_LOCK"):
                return f"with {expr.id} (no deadline)"
        return None
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
    owner = ast.unparse(func.value) if isinstance(func, ast.Attribute) else ""
    if owner == "pickle" and name == "load":
        return "pickle.load of a stream"
    if False and name in ZERO_ARG and not node.args and not _has_kw(node, "timeout", "blocking"):
        return f".{name}() with no timeout"
    if owner == "select" and name == "select" and len(node.args) < 4 and not _has_kw(node, "timeout"):
        return "select.select with no timeout"
    if owner == "subprocess" and name in SUBPROCESS_CALLS and not _has_kw(node, "timeout"):
        return f"subprocess.{name} with no timeout"
    if name == "get" and not node.args and not _has_kw(node, "timeout", "block") and "queue" in owner.lower():
        return "queue get() with no timeout"
    return None


def scan_file(path: Path) -> list[tuple[int, str, str, str]]:
    """(line, enclosing function, reason, source) for each site in ``path``."""
    tree = ast.parse(path.read_text(), str(path))
    awaited: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Await):
            awaited.update(id(sub) for sub in ast.walk(node))
    sites: list[tuple[int, str, str, str]] = []

    def visit(node: ast.AST, func: str) -> None:
        for child in ast.iter_child_nodes(node):
            inner = child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else func
            if id(child) not in awaited:
                why = _why(child)
                if why:
                    src = ast.unparse(child).splitlines()[0]
                    sites.append((child.lineno, inner, why, src))
            visit(child, inner)

    visit(tree, "<module>")
    return sorted(sites)


def scan(package: Path) -> int:
    total = 0
    for path in sorted(package.rglob("*.py")):
        for line, func, why, src in scan_file(path):
            print(f"SITE {path.relative_to(package)}:{line} {func}: {why}: {src}")
            total += 1
    print(f"RESULT unbounded_sites={total}")
    return 0


def drive(cap_s: float, silent_s: float, reply_timeout_s: float | None, answer: bool) -> int:
    from heatpump_optimizer import coordinator as cm

    if reply_timeout_s is not None:
        if hasattr(cm, "PROCESS_REPLY_TIMEOUT_S"):
            cm.PROCESS_REPLY_TIMEOUT_S = reply_timeout_s
        else:
            print("NOTE this tree has no PROCESS_REPLY_TIMEOUT_S; --reply-timeout has nothing to set")
    cm._run_in_process(abs, (-1,))  # a warm worker, so spawn time is not in the figure
    job = (time.sleep, (0.1,)) if answer else (time.sleep, (silent_s,))
    out: dict[str, object] = {}

    def solve() -> None:
        start = time.monotonic()
        try:
            out["outcome"] = f"returned {cm._run_in_process(*job)!r}"
        except BaseException as err:  # noqa: BLE001 - the outcome is the measurement
            out["outcome"] = f"raised {type(err).__name__}"
        out["elapsed"] = time.monotonic() - start

    worker = threading.Thread(target=solve, daemon=True)
    worker.start()
    worker.join(cap_s)
    returned = not worker.is_alive()
    elapsed = out.get("elapsed")
    print(f"RESULT reply_returned_within_cap={int(returned)}")
    print(f"RESULT reply_elapsed_s={elapsed:.2f}" if returned else f"RESULT reply_elapsed_s=>{cap_s:g}")
    print(f"OUTCOME {out.get('outcome', 'still waiting on the worker reply')}")
    start = time.monotonic()
    stopper = threading.Thread(target=cm._shutdown_process_pool, daemon=True)
    stopper.start()
    stopper.join(cap_s)
    stop_s = time.monotonic() - start
    print(f"RESULT stop_returned_within_cap={int(not stopper.is_alive())}")
    print(f"RESULT stop_elapsed_s={stop_s:.2f}")
    worker.join(cap_s)
    print(f"RESULT reply_released_after_stop={int(not worker.is_alive())}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", type=Path)
    ap.add_argument("--drive", action="store_true")
    ap.add_argument("--cap", type=float, default=6.0)
    ap.add_argument("--silent", type=float, default=30.0)
    ap.add_argument("--reply-timeout", type=float)
    ap.add_argument("--answer", action="store_true")
    a = ap.parse_args()
    if a.scan:
        return scan(a.scan)
    if a.drive:
        return drive(a.cap, a.silent, a.reply_timeout, a.answer)
    ap.error("one of --scan or --drive")
    return 2


if __name__ == "__main__":
    sys.exit(main())
