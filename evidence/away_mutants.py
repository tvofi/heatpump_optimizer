# Reviewer's own mutants of tests/replay.py:away_offenders, judged by the lane's controls().
import sys, pathlib, re, importlib.util
tree = pathlib.Path(sys.argv[1]); src = (tree/'tests'/'replay.py').read_text()
sys.path[:0] = [str(tree/'tests'/'hastub'), str(tree/'custom_components'), str(tree/'tests'), str(tree/'tools'/'replay')]
OLD_IF = 'if not (o["active"] and o["override"] and floor_ok):'
OLD_FL = 'floor_ok = o["recovery"] or ('
M = {
 'null': [],
 'drop_override_arm': [(OLD_IF, 'if not (o["active"] and floor_ok):')],
 'drop_floor_arm': [(OLD_IF, 'if not (o["active"] and o["override"]):')],
 'recovering_as_not': [(OLD_FL, 'floor_ok = False or (')],
 'drop_view_arm': [(OLD_IF, 'if not (o["override"] and floor_ok):')],
 'recovery_always': [(OLD_FL, 'floor_ok = True or (')],
}
for name, subs in M.items():
    s = src
    for a, b in subs:
        assert s.count(a) == 1, (name, a); s = s.replace(a, b)
    p = tree/'tests'/f'_mut_replay_{name}.py'; p.write_text(s)
    spec = importlib.util.spec_from_file_location(f'm_{name}', p); m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m); r = [x for x in m.controls() if x[0].startswith('control:away')]
        red = [n for n, ok, _ in r if not ok]
        print(f'RESULT mutant={name} away_controls={len(r)} red={red} {"KILLED" if red else ("NULL-GREEN" if name=="null" else "SURVIVED")}')
    finally:
        p.unlink()
