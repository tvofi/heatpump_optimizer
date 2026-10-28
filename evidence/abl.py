import sys
p, *steps = sys.argv[1:]; s = open(p).read()
R = {
 "literal": [("and isinstance(args[1], ast.Name) and args[1].id in self.literals", "and False and args[1].id in self.literals")],
 "computed": [("               and not isinstance(n.args[1], ast.Constant) and flow.is_root(n.args[0])\n               for n in ast.walk(flow.fn)):",
               "               and not isinstance(n.args[1], ast.Constant) and flow.is_root(n.args[0])\n               for n in ast.walk(flow.fn)) and False:")],
 "uncalled": [("                and isinstance(node.ctx, ast.Load) and flow.is_root(node.value)):\n            return node.attr   # a property read",
               "                and isinstance(node.ctx, ast.Load) and flow.is_root(node.value) and _is_property(readers[node.attr])):\n            return node.attr   # a property read"),
              ("            return helper_names[node.id]   # a helper handed on uncalled", "            return None")],
 "spread": [("raw = i == 0 and holder.id in plain", "raw = True")],
}
for st in steps:
    for a, b in R[st]:
        assert s.count(a) == 1, (st, a); s = s.replace(a, b)
open(p, "w").write(s)
