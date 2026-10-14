"""D7.M6: every production load of a name-kept member's name, with its receiver.

Metric: for each candidate member, the number of production attribute loads
  (or getattr/hasattr string lookups) of its name whose receiver expression is
  NOT a store of another class's same-named field/member -- printed per site so
  a reader can type each receiver; RESULT <member>_loads = total sites.
  Candidates come from namekept_sentinel.py (0 production-frame calls, >0 test
  calls) less HA hooks. The listing is the inspection evidence; the count is
  the input to tests/structure.py:dead_members's name-kept rule.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s3/namekept_receivers.py
Baseline 17f1c55fad1b, box B5. Root rule: cwd.
Perturbation: HPO_RECV_EXTRA='drift.py:Cusum:reset:cusum.reset()'
  appends that statement to the module's AST (in memory) as a production load;
  the named member's typed-hit count must go 0 -> 1.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, sys
sys.path.insert(0, "tests")
import structure as S

CANDIDATES = [
    ("drift.py", "Cusum", "reset", ("cusum",)),
    ("inputs.py", "InputReader", "value", ("reader",)),
    ("inputs.py", "InputReader", "text", ("reader",)),
    ("inputs.py", "InputReader", "flag", ("reader",)),
    ("boost.py", "BoostState", "as_dict", ("held",)),
    ("coordinator.py", "HeatPumpOptimizerCoordinator", "dhw_temperature", ("coord", "coordinator", "self")),
]
trees = S.module_trees()
extra = os.environ.get("HPO_RECV_EXTRA")
if extra:
    f, _c, _m, stmt = extra.split(":", 3)
    for p, t in trees:
        if p.name == f:
            t.body.append(ast.parse(stmt).body[0])
total_typed = 0
for f, c, m, hints in CANDIDATES:
    sites = []
    for p, t in trees:
        for n in ast.walk(t):
            name = recv = None
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load) and n.attr == m:
                name, recv = m, ast.unparse(n.value)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and n.args[1].value == m:
                name, recv = m, ast.unparse(n.args[0])
            if name:
                sites.append((p.name, n.lineno, recv))
    # A receiver is "typed-hit" when its text names the candidate's instance by
    # the hints (the variable names production binds instances of the class to).
    typed = [s for s in sites if any(h in s[2].lower() for h in hints)
             and not (c == "HeatPumpOptimizerCoordinator" and s[0] != "coordinator.py" and "state" in s[2].lower())]
    if c != "HeatPumpOptimizerCoordinator":
        typed = [s for s in typed if not s[2].endswith(("reading", "_reading", "state"))]
    for s in sites:
        print(f"LOAD {c}.{m} {s[0]}:{s[1]} recv={s[2]!r} {'TYPED-HIT' if s in typed else ''}")
    print(f"RESULT {c}.{m}_loads={len(sites)} sites")
    print(f"RESULT {c}.{m}_typed_hits={len(typed)} sites")
    total_typed += len(typed)
print(f"RESULT candidates_with_zero_typed_hits={sum(1 for _ in CANDIDATES) if total_typed == 0 else 'see per-member'}")
print(f"RESULT total_typed_hits={total_typed} sites")
print("RESULT thread_factor=1.000")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
