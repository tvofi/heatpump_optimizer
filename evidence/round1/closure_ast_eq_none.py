"""Reviewer's own instrument: specialise the builder's closures to dhw_plan_power=None
(fold `A if dhw_plan_power is None else B` to A, drop the alias assignment, drop the
defaulted parameter, substitute the alias by its value) and AST-compare with the
base space-only closures. Equal = 'with None the arithmetic is the space-only path's'."""
import ast, sys, copy
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from closure_ast_eq import load, closures, dump
class Fold(ast.NodeTransformer):
    def __init__(self): self.alias = {}
    def visit_FunctionDef(self, n):
        n.args.args = [a for a in n.args.args if a.arg != "dhw_plan_power"]
        n.args.defaults = [d for d in n.args.defaults if not (isinstance(d, ast.Constant) and d.value is None)]
        new = []
        for st in n.body:
            if (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                and isinstance(st.value, ast.IfExp) and isinstance(st.value.test, ast.Compare)
                and isinstance(st.value.test.left, ast.Name) and st.value.test.left.id == "dhw_plan_power"
                and isinstance(st.value.test.ops[0], ast.Is)):
                self.alias[st.targets[0].id] = st.value.body.id
                continue
            new.append(st)
        n.body = new
        self.generic_visit(n); return n
    def visit_Name(self, n):
        if n.id in self.alias: n.id = self.alias[n.id]
        return n
base, head = load(sys.argv[1]), load(sys.argv[2])
H = closures(head["_solve_objectives"]); B = closures(base["_optimize_space_only"])
for name in ("objective", "objective_batch"):
    f = Fold(); spec = f.visit(copy.deepcopy(H[name]))
    print(f"RESULT ast-equal base._optimize_space_only.{name} == head.{name}[dhw_plan_power=None]: {dump(B[name]) == dump(spec)}  aliases={f.alias}")
