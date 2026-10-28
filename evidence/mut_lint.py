import sys,subprocess,pathlib
F=pathlib.Path('tools/policy/policy_lint.mjs'); orig=F.read_text()
G="  if (fetched.ok) writeWindowCache(cacheFile, since, { pullsBySha: { map: [...fetched.map], gapShas: fetched.gapShas } })"
K="  return cache && cache.key === windowKey(since) ? cache : {}"
M={
 'R1':(G,"  writeWindowCache(cacheFile, since, { pullsBySha: { map: [...(fetched.map ?? [])], gapShas: fetched.gapShas ?? [] } })"),
 'R1b':(G,"  writeWindowCache(cacheFile, since, { pullsBySha: { map: [...fetched.map], gapShas: fetched.gapShas } })"),
 'R1c':(G,"  if (fetched.ok || fetched.why) writeWindowCache(cacheFile, since, { pullsBySha: { map: [...(fetched.map ?? [])], gapShas: [] } })"),
 'R2':(K,"  return cache || {}"),
 'R2b':(K,"  return cache && String(cache.key).startsWith(windowKey(since)) ? cache : {}"),
 'R2c':(K,"  return cache && String(cache.key).split('..')[0] === windowKey(since).split('..')[0] ? cache : {}"),
 'R2d':(K,"  return cache && String(cache.key).split('..')[1] === windowKey(since).split('..')[1] ? cache : {}"),
}
for n,(a,b) in M.items():
    assert orig.count(a)==1,n
    F.write_text(orig.replace(a,b))
    r=subprocess.run(['node','tools/policy/policy_lint.mjs'],capture_output=True,text=True)
    out=r.stdout+r.stderr
    lines=[l for l in out.splitlines() if 'FIXTURE' in l or 'window cache' in l.lower() or 'enumeration' in l]
    print(f'== {n} rc={r.returncode}'); print('\n'.join(lines[:6]))
F.write_text(orig)
