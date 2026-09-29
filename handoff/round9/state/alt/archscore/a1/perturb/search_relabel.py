"""Support for N3: rank every single seam_map.json relabel by how much it lowers
sum(cut_*) + cross_seam_edges at the given worktree. No code is edited.
usage: python3 search_relabel.py <worktree> [top]"""
import ast, importlib.util, sys
wt = sys.argv[1]; top = int(sys.argv[2]) if len(sys.argv) > 2 else 8
spec = importlib.util.spec_from_file_location("s", f"{wt}/tests/structure.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = ast.parse(open(f"{wt}/custom_components/heatpump_optimizer/coordinator.py").read())
cls = next(n for n in ast.walk(t) if isinstance(n, ast.ClassDef) and n.name == m.COORDINATOR_CLASS_NAME)
seams = m.load_seam_map()
score = lambda r: sum(r["cut_costs"].values()) + r["cross_edges"]
base = m.seam_metrics(cls, seams); b = score(base)
rows = []
for name in seams:
    for lab in (*m.SEAM_LABELS, "core"):
        if lab != seams[name]:
            r = m.seam_metrics(cls, {**seams, name: lab})
            rows.append((score(r) - b, name, seams[name], lab,
                         {k: v - base["cut_costs"][k] for k, v in r["cut_costs"].items() if v != base["cut_costs"][k]},
                         r["cross_edges"] - base["cross_edges"]))
rows.sort()
print(f"{len(rows)} single relabels; {sum(1 for r in rows if r[0] < 0)} lower the cut table")
for r in rows[:top]:
    print(r)
