import sys,subprocess,pathlib
S=pathlib.Path(sys.argv[1]); C=S/'c_head'; F=C/'tools/policy/policy_lint.mjs'; Y=C/'.github/workflows/governance.yml'
orig=F.read_text(); yorig=Y.read_text()
M=[
 ('M1/M-A readWindowCache returns {} (per-mode fetch restored)', F, "  return cache && cache.key === windowKey(since) ? cache : {}", "  return {}"),
 ('M-B serve a cache missing a PR', F, "if (cached && prs.every(({ pr }) => Object.hasOwn(cached, pr))) {", "if (cached) {"),
 ('M-C stats enum not given cache', F, "function cmdStats(since, cacheFile) {\n  const enumerated = mergedPRsFromWindow(since, cacheFile)", "function cmdStats(since, cacheFile) {\n  const enumerated = mergedPRsFromWindow(since, null)"),
 ('M-D sunset reads not given cache', F, "fetchWindowShared(prs, since, cacheFile)\n  console.log(windowCacheLine(cacheFile, [['commit-to-PR map', enumerated.fromCache], ['per-PR reads', fromCache]]))\n  const friction", "fetchWindowShared(prs, since, null)\n  console.log(windowCacheLine(cacheFile, [['commit-to-PR map', enumerated.fromCache], ['per-PR reads', fromCache]]))\n  const friction"),
 ('M-E map never written', F, "  if (fetched.ok) writeWindowCache(cacheFile, since, { pullsBySha:", "  if (false) writeWindowCache(cacheFile, since, { pullsBySha:"),
 ('R1 failed enumeration cached (ok guard dropped)', F, "  if (fetched.ok) writeWindowCache(cacheFile, since, { pullsBySha: { map: [...fetched.map], gapShas: fetched.gapShas } })", "  writeWindowCache(cacheFile, since, { pullsBySha: { map: [...(fetched.map||[])], gapShas: fetched.gapShas||[] } })"),
 ('R2 cache key ignored (stale file trusted)', F, "  return cache && cache.key === windowKey(since) ? cache : {}", "  return cache || {}"),
 ('R3 failed per-PR fetch served as empty-success (fetchError dropped on cached path n/a): write failure as all-PR empty reads', F, "  writeWindowCache(cacheFile, since, { prReads: Object.fromEntries(out.fetched) })", "  writeWindowCache(cacheFile, since, { prReads: out.fetchError ? Object.fromEntries(prs.map(({ pr }) => [pr, { body: '', title: '', comments: [], reviews: [] }])) : Object.fromEntries(out.fetched) })"),
 ('R4 --window-cache arg parsed but not passed to --record', F, "cmdRecordDispositions(requireSince(since, '--record'), windowCache)", "cmdRecordDispositions(requireSince(since, '--record'), null)"),
 ('Y1 job: --sunset .claude arm drops --window-cache', Y, 'node .claude/workflows/policy_lint.mjs --sunset --since "${{ steps.window.outputs.since }}" --window-cache "$RUNNER_TEMP/window.json"', 'node .claude/workflows/policy_lint.mjs --sunset --since "${{ steps.window.outputs.since }}"'),
 ('M0 job: both rate_limit steps deleted', Y, None, None),
 ('M2 job: concurrency block deleted', Y, "    concurrency:\n      group: governance-record\n      cancel-in-progress: false\n", ""),
]
import re
for name,f,a,b in M:
    F.write_text(orig); Y.write_text(yorig)
    t=f.read_text()
    if a is None:
        n=re.sub(r"\n      - name: GITHUB_TOKEN rate limit (before|after) the window walk\n(?:        .*\n)+?(?=\n|      - |      #)", "\n", t)
        assert n!=t and 'rate_limit' not in n, 'M0 sub failed'
    else:
        assert t.count(a)==1,(name,t.count(a)); n=t.replace(a,b)
    f.write_text(n)
    h=subprocess.run(['bash','dev/audit/harnesses/record_api_calls.sh','v7.0.2'],cwd=C,capture_output=True,text=True)
    tot=[l for l in (h.stdout+h.stderr).splitlines() if l.startswith('TOTAL') or 'record_api_calls:' in l]
    a_=subprocess.run(['node','tools/policy/policy_lint.mjs'],cwd=C,capture_output=True,text=True)
    al=[l for l in a_.stdout.splitlines() if l.startswith('FIXTURE') or 'error(s) across' in l]
    e=subprocess.run(['python3','tests/entities.py'],cwd=C,capture_output=True,text=True,env={**__import__('os').environ,'PYTHONPATH':'tests/hastub'})
    print(f"MUTANT {name}\n  harness rc={h.returncode} {tot}\n  acceptance rc={a_.returncode} {[x[:300] for x in al]}\n  entities rc={e.returncode} {(e.stdout+e.stderr).strip().splitlines()[-1][:200] if (e.stdout+e.stderr).strip() else ''}",flush=True)
F.write_text(orig); Y.write_text(yorig)
print("restored", subprocess.run(['git','status','--porcelain'],cwd=C,capture_output=True,text=True).stdout or "clean")
