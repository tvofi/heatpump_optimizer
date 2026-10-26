import sys, json, importlib.util
spec = importlib.util.spec_from_file_location("ed", sys.argv[1]); ed = importlib.util.module_from_spec(spec); sys.modules["ed"] = ed; spec.loader.exec_module(ed)
arm = json.load(open(sys.argv[2])); base = json.load(open(sys.argv[3]))
LINE = "shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'"
shapes = ed.shape_claims({LINE: ["r"]})
may = set(n for n, *_ in ed.MAY_DRIFT_ALLOWED) if ed.MAY_DRIFT_ALLOWED and isinstance(ed.MAY_DRIFT_ALLOWED[0], tuple) else set(ed.MAY_DRIFT_ALLOWED)
moved = loose_total = 0; hit_cells = 0
for key in sorted(arm):
    name = key.split("@")[0]
    diffs, loose, matched = ed.shaped_leaves(name, base[key], arm[key], shapes)
    if diffs:
        moved += 1; hit_cells += bool(matched); loose_total += len(loose)
        print(f"{key}: moved={len(diffs)} loose={len(loose)} shape_hit={bool(matched)} may_drift={name in may}")
        for l in loose[:5]: print("   LOOSE", l)
print(f"RESULT cells={len(arm)} moved_cells={moved} shape_hit_cells={hit_cells} loose_leaves={loose_total}")
