import subprocess,sys,pathlib
R=pathlib.Path('.')
M={
 'M1-band-ignored':('tests/ci_ratchet.py','        band = bands.get(key, 0)\n','        band = 0\n'),
 'M2-band-every-row':('tests/ci_ratchet.py','        band = bands.get(key, 0)\n','        band = next(iter(bands.values()), 0)\n'),
 'M3-MAX-not-MAX0':('tools/policy/budget_raise_gate.py','(("critical_path_minutes_band",), MAX0),','(("critical_path_minutes_band",), MAX),'),
 'M3b-row-deleted':('tools/policy/budget_raise_gate.py','        (("critical_path_minutes_band",), MAX0),\n',''),
 'M4-bounds-dropped':('tests/ci_ratchet.py','            if not 0 <= value <= 10:\n','            if False:\n'),
 'M5-ge':('tests/ci_ratchet.py','over = cur > budget + band','over = cur >= budget + band'),
 'M6-record-carry':('tests/ci_ratchet.py','            **{k: budgets[k] for k in BAND_KEYS if k in budgets},\n',''),
 'M8-band-on-counter-skip-continue':('tests/ci_ratchet.py','                problems.append(f"{key}={value!r} is outside 0..10 minutes")\n            continue\n','                problems.append(f"{key}={value!r} is outside 0..10 minutes")\n'),
}
def run(f):
    s='tests/ci_ratchet.py' if 'ci_ratchet' in f else 'tools/policy/budget_raise_gate.py'
    p=subprocess.run(['env','-u','BASH_ENV','python3','-I',s,'--self-test'],capture_output=True,text=True)
    out=(p.stdout+p.stderr).strip().splitlines()
    return [l for l in out if 'FAIL' in l][:3]+[l for l in out if 'self-test:' in l]
for n,(f,a,b) in M.items():
    t=(R/f).read_text(); assert t.count(a)==1,(n,t.count(a))
    (R/f).write_text(t.replace(a,b))
    try: print('RESULT',n,'::',' | '.join(run(f)))
    finally: (R/f).write_text(t)
print('RESULT baseline ci ::',run('tests/ci_ratchet.py')[-1])
print('RESULT baseline gate ::',run('budget_raise_gate')[-1])
