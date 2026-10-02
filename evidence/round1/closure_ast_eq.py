"""Reviewer's own instrument: AST-dump equality of the nested closures, docstrings
stripped, under an explicit renaming table. Equal dumps = same code modulo the table."""
import ast, sys, copy
RENAME = {"power_schedule": "space_power", "power_matrix": "space_matrix", "space_penalty": "penalty"}
def load(p):
    t = ast.parse(open(p).read())
    for c in t.body:
        if isinstance(c, ast.ClassDef) and c.name == "HeatPumpOptimizer":
            return {f.name: f for f in c.body if isinstance(f, ast.FunctionDef)}
class N(ast.NodeTransformer):
    def visit_FunctionDef(self, n):
        self.generic_visit(n)
        if n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:]
        return n
    def visit_Name(self, n):
        n.id = RENAME.get(n.id, n.id); return n
    def visit_arg(self, n):
        n.arg = RENAME.get(n.arg, n.arg); n.annotation = None; return n
def closures(fn):
    return {d.name: d for d in ast.walk(fn) if isinstance(d, ast.FunctionDef) and d is not fn}
def dump(d): return ast.dump(N().visit(copy.deepcopy(d)), include_attributes=False)
if __name__ == "__main__":
    base, head = load(sys.argv[1]), load(sys.argv[2])
    H = closures(head["_solve_objectives"])
    for path in ("_optimize_space_only", "_optimize_with_dhw"):
        B = closures(base[path])
        for name in ("_space_traj", "objective", "objective_batch"):
            eq = dump(B[name]) == dump(H[name])
            print(f"RESULT ast-equal base.{path}.{name} == head._solve_objectives.{name}: {eq}")
