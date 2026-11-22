import sys, subprocess, pathlib, json, re
muts = json.load(open(sys.argv[1]))
for m in muts:
    p = pathlib.Path('/tmp/wh') / m['file']; src = p.read_text()
    n = src.count(m['old'])
    if n != 1:
        print(f"SKIP {m['id']} occurrences={n}"); continue
    p.write_text(src.replace(m['old'], m['new']))
    try:
        cmd = m.get('cmd', 'bash /tmp/blk.sh')
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1500).stdout
    finally:
        p.write_text(src)
    fails = [l for l in out.splitlines() if l.startswith('  FAIL') or 'FAIL ' in l[:8]]
    tail = out.strip().splitlines()[-1] if out.strip() else ''
    print(f"MUT {m['id']} fails={len(fails)} {'KILLED' if fails or 'PASSED' not in tail else 'SURVIVED'} | {tail[:120]}")
    for f in fails[:3]: print('   ', f[:200])
    sys.stdout.flush()
