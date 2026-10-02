"""Reviewer's own instrument. For each name the new builder reads from the horizon,
list every binding of that name in the OLD solve path before the closures were built,
so a local that was not h.<attr> (a reassignment) shows up."""
import ast, sys
p = sys.argv[1]; fn_name = sys.argv[2]; stop_marker = sys.argv[3]
src = open(p).read(); t = ast.parse(src)
names = {"initial_state","prices","dt","n_steps","comfort_targets","outdoor_temps","wind_speeds",
         "precipitation","solar_radiation","temp_min_bounds","temp_max_bounds","solar_gains_per_step",
         "start_time","h","self"}
for c in t.body:
  if isinstance(c, ast.ClassDef) and c.name == "HeatPumpOptimizer":
    for f in c.body:
      if isinstance(f, ast.FunctionDef) and f.name == fn_name:
        lines = src.splitlines()
        stop = next(i for i in range(f.lineno, f.end_lineno) if stop_marker in lines[i-1])
        hits = []
        for node in ast.walk(f):
          if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.For, ast.With, ast.NamedExpr)) and node.lineno < stop:
            tg = node.targets if isinstance(node, ast.Assign) else [getattr(node, "target", None)]
            for tt in tg:
              if tt is None: continue
              for n in ast.walk(tt):
                if isinstance(n, ast.Name) and n.id in names:
                  hits.append((node.lineno, n.id, ast.get_source_segment(src, node).splitlines()[0][:110]))
          # also subscript/in-place mutation of these arrays: x[...] = ..., x += ...
          if isinstance(node, (ast.Assign, ast.AugAssign)) and node.lineno < stop:
            tg = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tt in tg:
              if isinstance(tt, (ast.Subscript, ast.Attribute)):
                base = tt
                while isinstance(base, (ast.Subscript, ast.Attribute)): base = base.value
                if isinstance(base, ast.Name) and base.id in names - {"self"}:
                  hits.append((node.lineno, base.id + "[mut]", ast.get_source_segment(src, node).splitlines()[0][:110]))
          if isinstance(node, ast.Call) and node.lineno < stop and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in names - {"self","h"} and node.func.attr in {"fill","sort","resize","put","itemset","setflags"}:
            hits.append((node.lineno, node.func.value.id + "[mutcall]", ast.get_source_segment(src, node)[:110]))
        print(f"== {fn_name} lines {f.lineno}..{stop}")
        for h in sorted(set(hits)): print("BIND", *h)
        print(f"RESULT bindings {fn_name} {len(set(hits))}")
