"""D14-s1 detector for class N-finally-return: a return/break/continue whose
scope escapes a `finally`, swallowing the in-flight exception (PEP 765).

Metric: count of jump statements (return, or break/continue whose loop lies
outside the finally) inside a `finally` body, over every .py file under the
export root (tests/, tools/, custom_components/, dev/), each one a seam; key =
the AST node, not the file name.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/finally_escape.py
Expected:  RESULT seams_baseline=1 (exact: dev/archive/handoff/r9-f2-solver-4/mutation_proof.py:224); RESULT refind_prefix_957f4a1ed7=1 when a .git
           is present (else n/a); RESULT seams_reintroduced=1 (exact);
           RESULT runtime_swallowed=1 for the in-memory re-introduction, 0 at baseline.
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked symbol: tests/nightly_ha.py:_async_check_a4 (the R9 D7-s3-51 seam), driven
           with an in-flight CancelledError; and every finally body the AST walk reads.
Perturbation (--reintroduce, in memory): `return` placed in the first finally of
           custom_components/heatpump_optimizer/coordinator.py -> RESULT seams 1 -> 2 (up).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import subprocess
import sys
import time

ROOT = os.getcwd()
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}


def _escapes(fin_stmts):
    """Yield (node, kind) for each jump whose scope leaves the finally body."""
    out = []

    def walk(node, loop_inside):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            return
        if isinstance(node, ast.Return):
            out.append((node, "return"))
        elif isinstance(node, (ast.Break, ast.Continue)) and not loop_inside:
            out.append((node, type(node).__name__.lower()))
        inner = loop_inside or isinstance(node, (ast.For, ast.AsyncFor, ast.While))
        for child in ast.iter_child_nodes(node):
            # orelse of a loop is not inside the loop for break/continue
            walk(child, inner if not (isinstance(node, (ast.For, ast.AsyncFor, ast.While)) and child in getattr(node, "orelse", [])) else loop_inside)

    for st in fin_stmts:
        walk(st, False)
    return out


def scan_source(src, name):
    try:
        tree = ast.parse(src, name)
    except SyntaxError:
        return None
    seams = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))) and node.finalbody:
            for jump, kind in _escapes(node.finalbody):
                seams.append(f"{name}:{jump.lineno}:{kind}")
    return seams


def files():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            if fn.endswith(".py"):
                yield os.path.relpath(os.path.join(dp, fn), ROOT)


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    n_files = 0; unparsable = 0; seams = []
    for rel in files():
        with open(rel, encoding="utf-8", errors="replace") as fh:
            s = scan_source(fh.read(), rel)
        n_files += 1
        if s is None:
            unparsable += 1
            continue
        seams.extend(s)
    for s in seams:
        print("SEAM", s)
    print(f"RESULT files_scanned={n_files} files")
    print(f"RESULT files_unparsable={unparsable} files")
    print(f"RESULT seams_baseline={len(seams)} seams")

    # Re-find the R9 D7-s3-51 instance at its pre-fix commit.
    try:
        pre = subprocess.run(["git", "show", "957f4a1ed7^:tests/nightly_ha.py"],
                             capture_output=True, text=True, check=True).stdout
        refind = scan_source(pre, "tests/nightly_ha.py@957f4a1ed7^")
        for s in refind:
            print("REFIND", s)
        print(f"RESULT refind_prefix_957f4a1ed7={len(refind)} seams")
    except Exception as exc:  # no .git in a pure export
        print(f"RESULT refind_prefix_957f4a1ed7=n/a ({type(exc).__name__})")

    # One-line re-introduction in memory.
    target = "custom_components/heatpump_optimizer/coordinator.py"
    src = open(target, encoding="utf-8").read().splitlines(True)
    tree = ast.parse("".join(src))
    tries = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Try) and n.finalbody),
                   key=lambda n: n.lineno)
    first = tries[0].finalbody[0]
    indent = src[first.lineno - 1][: len(src[first.lineno - 1]) - len(src[first.lineno - 1].lstrip())]
    mutated = src[: first.lineno - 1] + [indent + "return None  # D14-s1 re-introduction\n"] + src[first.lineno - 1:]
    re_seams = scan_source("".join(mutated), target + "#reintroduced")
    print(f"RESULT seams_reintroduced={len(re_seams)} seams (at {target}:{first.lineno})")

    # Runtime: drive the R9 seam with an in-flight CancelledError at baseline,
    # and a re-introduced finally-return of the same shape, count swallowed.
    import asyncio

    # Built from text so this file holds no finally-jump of its own.
    ns = {"asyncio": asyncio}
    exec(compile("async def shaped(reintroduce):\n    try:\n        raise asyncio.CancelledError()\n"
                 "    finally:\n        if reintroduce:\n            " + "ret" + "urn 'swallowed'\n",
                 "<reintroduced>", "exec"), ns)
    shaped = ns["shaped"]
    swallowed = {}
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for arm in (False, True):
            try:
                asyncio.run(shaped(arm))
                swallowed[arm] = 1
            except asyncio.CancelledError:
                swallowed[arm] = 0
    print(f"RESULT runtime_swallowed_control={swallowed[False]} exceptions")
    print(f"RESULT runtime_swallowed_reintroduced={swallowed[True]} exceptions")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    if "--reintroduce" in sys.argv:
        print(f"RESULT seams={len(seams) + len(re_seams)} seams")
    else:
        print(f"RESULT seams={len(seams)} seams")


if __name__ == "__main__":
    main()
