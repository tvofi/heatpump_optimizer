import re,json
p='.claude/workflows/policy_lint.mjs'; s=open(p).read()
a="""      for (const h of g.hooks || []) {
"""
b="""      for (const h of g.hooks || []) {
        // Field coverage (I3): the harness runs a hook only when its type is
        // `command`, and a PreToolUse group only for tools its matcher matches.
        if (h.type !== 'command') { rows.push({ event, script: h.command || '(none)', verdict: 'NOT A COMMAND', why: `type ${JSON.stringify(h.type)}: the harness runs only a "command" hook as a script` }); continue }
        const cannot = event === 'PreToolUse' ? EDIT_TOOLS.filter((t) => !matcherFires(g.matcher, t)) : []
        if (cannot.length) { rows.push({ event, script: h.command || '(none)', verdict: 'CANNOT FIRE', why: `matcher ${JSON.stringify(g.matcher)} matches no call to ${cannot.join(', ')}` }); continue }
"""
assert s.count(a)==1; s=s.replace(a,b)
a2="function cmdHooks(settingsPath) {\n"
b2="""const EDIT_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit']
function matcherFires(m, tool) {
  if (m == null || m === '' || m === '*') return true
  try { return new RegExp(`^(?:${m})$`).test(tool) } catch { return false }
}
function cmdHooks(settingsPath) {
"""
assert s.count(a2)==1; s=s.replace(a2,b2)
a3="""    if (r.lines > cap) {"""
b3="""    const tcap = b.files_tokens ? b.files_tokens[r.file] : undefined
    if (b.files_tokens && !refused(r.file, `files_tokens["${r.file}"]`, tcap) && Math.round(r.bytes / 4) > tcap) {
      out.push({ severity: 'error', check: 'budgets', where: r.file, message: `about ${Math.round(r.bytes / 4)} tokens exceeds its per-file token cap of ${tcap}. Cut, or state the case for a higher cap in the pull request body.` })
    }
    if (r.lines > cap) {"""
assert s.count(a3)==1; s=s.replace(a3,b3)
open(p,'w').write(s)
p='.claude/workflows/counts.mjs'; s=open(p).read()
a="""      shapes.push({ id, rules:"""
b="""      objects[id] = rs
      shapes.push({ id, rules:"""
assert s.count(a)==1; s=s.replace(a,b)
a="""    const shapes = []
"""
b="""    const shapes = []
    const objects = {}
"""
assert s.count(a)==1; s=s.replace(a,b)
a="return { contexts: a, count: a.length, rulesets: [...ids].sort((x, y) => x - y), shapes }"
assert s.count(a)==1
s=s.replace(a,"return { contexts: a, count: a.length, rulesets: [...ids].sort((x, y) => x - y), shapes, objects }")
a="""export function requiredContextsDrift(fixtureRel, fixture, live) {
  if (fixture == null || live == null) return []
  const out = []
"""
b="""// Field coverage (I3): every leaf of each ruleset object is compared with the
// recorded shape, except these, which GitHub rewrites with no boundary change.
// ONE definition: field_coverage.mjs imports it.
export const RULESET_VOLATILE = ['node_id', 'created_at', 'updated_at', '_links', 'current_user_can_bypass', 'source', 'source_type', 'name']
export function rulesetLeaves(o) {
  const out = {}
  const walk = (v, p) => {
    if (Array.isArray(v)) {
      const xs = v.map((x) => JSON.stringify(x)).sort().map((x) => JSON.parse(x))
      if (!xs.length) out[p] = '[]'
      xs.forEach((x, i) => walk(x, `${p}[${i}]`))
    } else if (v && typeof v === 'object') {
      const ks = Object.keys(v).filter((k) => !(p === '' && RULESET_VOLATILE.includes(k)))
      if (!ks.length) out[p] = '{}'
      for (const k of ks) walk(v[k], p ? `${p}.${k}` : k)
    } else out[p] = JSON.stringify(v)
  }
  walk(o, '')
  return out
}
export function requiredContextsDrift(fixtureRel, fixture, live) {
  if (fixture == null || live == null) return []
  const out = []
  const recObjs = fixture.ruleset_objects || null
  if (!recObjs) out.push({ severity: 'error', check: 'required-contexts', where: fixtureRel, message: 'records no `ruleset_objects`, so no ruleset field beyond the context names is compared.' })
  for (const [id, obj] of Object.entries((live && live.objects) || {})) {
    const want = recObjs && recObjs[id] ? rulesetLeaves(recObjs[id]) : null
    if (!want) continue
    const got = rulesetLeaves(obj)
    for (const k of new Set([...Object.keys(want), ...Object.keys(got)])) {
      if (want[k] === got[k]) continue
      out.push({ severity: 'error', check: 'required-contexts', where: fixtureRel, message: `ruleset ${id} field \\`${k}\\` is ${got[k] ?? '(absent)'} live, ${want[k] ?? '(absent)'} recorded. The boundary changed or the record is wrong: re-read every assertion site against it.` })
    }
  }
"""
assert s.count(a)==1; s=s.replace(a,b)
open(p,'w').write(s)
S='/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad'
rs=json.load(open(S+'/ruleset-23698884.json'))
for k in ['node_id','created_at','updated_at','_links','current_user_can_bypass','source','source_type','name']: rs.pop(k,None)
for r in rs['rules']:
    if r['type']=='pull_request': r['parameters']['dismiss_stale_reviews_on_push']=True
p='.claude/workflows/fixtures/required-contexts.json'; f=json.load(open(p))
f['ruleset_objects']={'23698884':rs}
f['_ruleset_objects']="Recorded as the policy ASSERTS the boundary: decision 0008 step 3(d) sets dismiss_stale_reviews_on_push true. Prototype (handoff/r9-rca-i3); F11.2 records the owner's decision here."
open(p,'w').write(json.dumps(f,indent=2)+'\n')
