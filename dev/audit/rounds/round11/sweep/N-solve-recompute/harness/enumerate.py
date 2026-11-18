"""N-solve-recompute sweep enumerator (round 11, SW2).

Seam: a call site in the package that makes the planner solve run --
a coordinator refresh (async_request_refresh / async_refresh /
async_refresh_now), async_run_optimization, _await_optimize or
optimize_in_process -- outside the coordinator's own update body.  Each
seam is one trigger of a full solve; the sweep then asks whether the
trigger's purpose needs the solve it buys (D9-s1-01: a diagnose press
re-solves to publish an analysis that needs none).

Usage:  python3 enumerate.py [ROOT]      (default custom_components/heatpump_optimizer)
        python3 enumerate.py --controls  (positive, null, perturbation)
"""
import ast
import pathlib
import sys
import tempfile

TRIGGERS = {"async_request_refresh", "async_refresh", "async_refresh_now",
            "async_run_optimization", "_await_optimize", "optimize_in_process"}
EXEMPT_FUNCS = {"_async_update_data"}  # the cycle itself is the solve, not a trigger of it


def seams(root):
    out = []
    for path in sorted(pathlib.Path(root).rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        stack = []

        def visit(node):
            is_fn = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            if is_fn:
                stack.append(node.name)
            if isinstance(node, ast.Call):
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None
                if name is None:  # passed as an argument: run_in_executor(optimize_in_process, ...)
                    pass
                hits = [name] if name in TRIGGERS else []
                for a in node.args:
                    an = a.attr if isinstance(a, ast.Attribute) else a.id if isinstance(a, ast.Name) else None
                    if an in TRIGGERS and an != name:
                        hits.append(an)
                fn = "<module>" if not stack else ".".join(stack)
                if hits and not (set(stack) & EXEMPT_FUNCS):
                    for h in hits:
                        out.append((str(path), node.lineno, fn, h))
            for child in ast.iter_child_nodes(node):
                visit(child)
            if is_fn:
                stack.pop()

        visit(tree)
    return out


def controls():
    here = pathlib.Path(__file__).resolve()
    repo = here.parents[6]
    pkg = repo / "custom_components" / "heatpump_optimizer"
    real = seams(pkg)
    pos = [s for s in real if s[2].endswith("async_diagnose_interval") and s[3] == "async_request_refresh"]
    print(f"positive: D9-s1-01 site coordinator.async_diagnose_interval -> async_request_refresh found={len(pos)}")
    clean = (
        "class C:\n"
        "    async def async_diagnose_interval(self):\n"
        "        report = await self._diagnose()\n"
        "        self.data = self._build_data_dict()\n"
        "        self.async_update_listeners()\n"
        "        return report\n"
        "    async def _async_update_data(self):\n"
        "        return await self.async_run_optimization()\n"
    )
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "m.py"
        p.write_text(clean)
        null = len(seams(d))
        p.write_text(clean.replace("        return report\n", "        await self.async_request_refresh()\n        return report\n"))
        pert = len(seams(d))
    print(f"null: clean fixture seams={null}")
    print(f"perturbation: one-line re-introduction seams={pert}")
    ok = len(pos) == 1 and null == 0 and pert == 1
    print("controls", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--controls"]:
        sys.exit(controls())
    root = sys.argv[1] if len(sys.argv) > 1 else "custom_components/heatpump_optimizer"
    rows = seams(root)
    for f, ln, fn, h in rows:
        print(f"{f}:{ln}\t{fn}\t{h}")
    print(f"seams={len(rows)}")
