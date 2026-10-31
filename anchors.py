import ast, subprocess, pathlib, sys
head = pathlib.Path('.').resolve()
base_src = subprocess.run(["git","show","3b4180dcc:dev/audit/harnesses/r10_sav_baseline_mutants.py"],
                          capture_output=True, text=True, check=True).stdout
mod = ast.parse(base_src)
M = None
for node in mod.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "M":
        M = ast.literal_eval(node.value)
for name, f, old, new in M:
    short = name.split()[0]
    p = head / "custom_components/heatpump_optimizer" / f
    n = p.read_text().count(old)
    print(f"{short:4s} {f:13s} base-anchor-occurrences-at-head={n}")
