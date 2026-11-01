# Reviewer's own harness (duty F): gate_checks() at a tree, plus nulls.
import sys, json, shutil, tempfile, pathlib
tree = pathlib.Path(sys.argv[1]); mode = sys.argv[2]
sys.path[:0] = [str(tree/'tests'/'hastub'), str(tree/'custom_components'), str(tree/'tools'/'replay'), str(tree/'tests')]
import debug_replay as d
if mode != 'plain':
    tmp = pathlib.Path(tempfile.mkdtemp()); (tmp/'tests'/'replay').mkdir(parents=True)
    doc = json.loads((tree/'tests'/'replay'/'synthetic-dhw-only.json').read_text())
    pe = doc['entry']['data']['price_entity']
    if mode == 'unrenamed':   # a fixture whose price entity keeps a raw-shaped id
        new = 'sensor.nordpool_kwh_zz9_xyz'
        doc['states'][new] = doc['states'].pop(pe); doc['entry']['data']['price_entity'] = new
        doc['inputs'] = [new if i == pe else i for i in doc['inputs']]
    elif mode == 'none':      # no price entity
        doc['entry']['data']['price_entity'] = None
    elif mode == 'absent':
        del doc['entry']['data']['price_entity']
    (tmp/'tests'/'replay'/'synthetic-dhw-only.json').write_text(json.dumps(doc))
    d.ROOT = tmp
try:
    r = d.gate_checks()
    for n, ok, det in r: print('PASS' if ok else 'FAIL', n, det[:80])
    print(f'RESULT tree={tree.name} mode={mode} passed={sum(x[1] for x in r)}/{len(r)}')
except Exception as e:
    print(f'RESULT tree={tree.name} mode={mode} raised {type(e).__name__}: {e}')
