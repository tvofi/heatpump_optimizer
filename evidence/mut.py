import sys, pathlib, subprocess, tempfile, shutil
src = pathlib.Path(sys.argv[1]).read_text()
MUTS = {
 "reorder": ('        spent = rate_limited(failure.code, line) and headers.get("x-ratelimit-remaining") == "0"\n',
             '        if headers.get("x-ratelimit-remaining") == "0":\n            return named_wait(headers, now(), True)\n        spent = rate_limited(failure.code, line) and headers.get("x-ratelimit-remaining") == "0"\n'),
 "drop-ratelimited": ('spent = rate_limited(failure.code, line) and headers', 'spent = headers'),
 "namedwait-always-spent": ('wait = named_wait(headers, now(), spent)', 'wait = named_wait(headers, now(), True)'),
 "403-any-msg": ('(code == 403 and RATE_LIMIT in line.lower())', '(code == 403)'),
 "or-not-and": ('rate_limited(failure.code, line) and headers.get', 'rate_limited(failure.code, line) or headers.get'),
 "ratelimit-any-code": ('return code == 429 or (code == 403 and', 'return code == 429 or (code >= 400 and'),
}
for name,(a,b) in MUTS.items():
    assert src.count(a)==1, name
    d = tempfile.mkdtemp(); pathlib.Path(d,"gh_read.py").write_text(src.replace(a,b))
    r = subprocess.run([sys.executable,"-I","-c","import sys; sys.path.insert(0,sys.argv[1]); import gh_read; sys.exit(gh_read.self_test())",d],capture_output=True,text=True)
    out=r.stdout+r.stderr
    fails=[l for l in out.splitlines() if l.startswith("FAIL")]
    print(f"MUTANT {name}: rc={r.returncode} {out.strip().splitlines()[-1]}")
    for f in fails: print("   ",f)
    shutil.rmtree(d)
