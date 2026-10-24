import ast, sys
src = open("tests/entities.py").read()
tree = ast.parse(src)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_workflow_job")
import re
ns = {"re": re}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "entities._workflow_job", "exec"), ns)
job = ns["_workflow_job"](open(".github/workflows/nightly.yml").read(), "mutation-ledger")
w = '--scope full --drain "$out" --max 40'
print("RESULT pinned-literal-present:", w in job)
