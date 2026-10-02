"""Reviewer's own instrument (late binding). Old closures read enclosing locals at CALL
time; the builder's closures read the builder's locals. If the old enclosing method rebinds
a captured name AFTER the closures were defined, the refactor changes what they see.
Prints every binding of each name the closures capture, in the whole enclosing method,
outside nested defs."""
import ast, sys
p, fn_name = sys.argv[1], sys.argv[2]
src = open(p).read(); t = ast.parse(src)
CAP = {"initial_state","prices","dt","outdoor_temps","wind_speeds","precipitation","solar_radiation",
       "comfort_targets","temp_min_bounds","temp_max_bounds","comfort_band","terminal_cost",
       "terminal_cost_batch","cycling","capacity","cycling_batch","capacity_batch","energy_cost_of",
       "_space_traj","objective","objective_batch","h"}
def walk_no_nested(node):
    for ch in ast.iter_child_nodes(node):
        if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)): yield ("def", ch)
            continue
        yield ("node", ch); yield from walk_no_nested(ch)
for c in t.body:
  if isinstance(c, ast.ClassDef) and c.name == "HeatPumpOptimizer":
    for f in c.body:
      if isinstance(f, ast.FunctionDef) and f.name == fn_name:
        out = []
        for kind, n in walk_no_nested(f):
          if kind == "def":
            if n.name in CAP: out.append((n.lineno, n.name, "def"))
            continue
          if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)) and n.id in CAP:
            out.append((n.lineno, n.id, "store"))
          if isinstance(n, (ast.Subscript,)) and isinstance(n.ctx, ast.Store):
            b = n
            while isinstance(b, (ast.Subscript, ast.Attribute)): b = b.value
            if isinstance(b, ast.Name) and b.id in CAP: out.append((n.lineno, b.id, "item-store"))
          if isinstance(n, ast.AugAssign):
            b = n.target
            while isinstance(b, (ast.Subscript, ast.Attribute)): b = b.value
            if isinstance(b, ast.Name) and b.id in CAP: out.append((n.lineno, b.id, "augassign"))
          if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
            b = n
            while isinstance(b, (ast.Subscript, ast.Attribute)): b = b.value
            if isinstance(b, ast.Name) and b.id == "h": out.append((n.lineno, "h." + n.attr, "attr-store"))
        print(f"== {fn_name} {f.lineno}-{f.end_lineno}")
        for o in sorted(out): print("BIND", *o)
        from collections import Counter
        cnt = Counter(o[1] for o in out)
        multi = {k: v for k, v in cnt.items() if v > 1}
        print(f"RESULT rebound-after-first {fn_name} {multi}")
