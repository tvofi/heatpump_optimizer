// D6-s7: does web-fix-wave.js stop merging once main turns red?
//
// Metric (one line): merges_after_red = merge-agent calls the real web-fix-wave.js body
// makes AFTER a `main after <group>` gate answered green:false, over one wave of two
// independent groups at stage `merge`. Count key: the labels the script itself hands
// agent() (`merge <group>`), in call order; nothing here re-implements the merge chain.
//
// Claim checked: dev/programme/plan-2026-09-open-issues.md, "When a merge turns main red":
// "`web-fix-wave.js` logs `MAIN IS RED after <group>` and stops merging." Expected 0 if true.
//
// Run (from the export root):
//   node dev/audit/rounds/round11/D6/s7/wave_red.mjs [--perturb red-guard]
// --perturb red-guard: the merge chain is given a red latch in memory (one guard line at
//   the head of mergeChain.then and one latch line after the gate): merges_after_red must
//   go TO ZERO. Null control (always printed): every gate green, merges_after_red=0 and both
//   groups merge.
// Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: merges_after_red=1 exact,
// red_logged=1 exact, null merges=2. Machine: box B13, linux x86_64. Node, single thread.
// The stub idiom is tools/policy/check-wave-script.mjs's run() (agent/log/phase/parallel).
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const ROOT = process.cwd()
const perturb = process.argv.includes('--perturb') ? process.argv[process.argv.indexOf('--perturb') + 1] : ''
const src = fs.readFileSync(path.join(ROOT, '.claude', 'workflows', 'web-fix-wave.js'), 'utf8')
const i = src.indexOf('export const meta')
let body = src.slice(0, i) + src.slice(src.indexOf('\n}\n', i) + 3)
if (perturb === 'red-guard') {
  const head = 'const outcome = await (mergeChain = mergeChain.then(async () => {'
  const tail = "return { merged: true, sha: m.sha, green: !!gate?.green"
  if (!body.includes(head) || !body.includes(tail)) throw new Error('perturbation anchors not found')
  body = 'let __red = false\n' + body
    .replace(head, head + "\n    if (__red) return { merged: false, reason: 'main is red' }")
    .replace(tail, 'if (!gate?.green) __red = true\n    ' + tail)
}

const OK = { provenance_ok: true, groups: [], mismatches: [], summary: 'ok' }
const G = (group) => ({ group, issues: [1], brief: 'b', resume: { stage: 'merge', pr: group === 'A' ? 1 : 2, head_sha: `${group}`.repeat(7) } })

async function wave(greens) {
  const calls = []
  const logs = []
  let redSeen = false
  let after = 0
  const agent = async (prompt, o) => {
    const label = o?.label ?? '?'
    calls.push(label)
    if (label.startsWith('reconcile')) return OK
    if (label.startsWith('merge ')) {
      if (redSeen) after++
      return { merged: true, sha: `m-${label.slice(6)}` }
    }
    if (label.startsWith('main after ')) {
      const g = greens.shift() ?? true
      if (!g) redSeen = true
      return { green: g }
    }
    return null
  }
  const fn = new Function('agent', 'log', 'phase', 'parallel', 'args', `return (async () => { ${body} })()`)
  const out = await fn(agent, (m) => logs.push(String(m)), () => {},
    (thunks) => Promise.all(thunks.map((t) => t().catch(() => null))),
    { groups: [G('A'), G('B')], groupsFile: 'r.json', repo: '/repo', fork: 'deadbeef', session: 'claude-web' })
  return { out, calls, logs, after }
}

// The tier arm (the plan's "Model routing": `web-fix-wave.js` ranks haiku < sonnet < opus
// and throws if a reviewer ranks below its fixer): one wave per (fixer, reviewer) pair.
const TIERS = ['haiku', 'sonnet', 'opus']
let tierThrows = 0, tierWrong = 0
for (const f of TIERS) for (const r of TIERS) {
  let threw = false
  try {
    const fn = new Function('agent', 'log', 'phase', 'parallel', 'args', `return (async () => { ${body} })()`)
    await fn(async (p, o) => (o?.label?.startsWith('reconcile') ? OK : null), () => {}, () => {},
      (thunks) => Promise.all(thunks.map((t) => t().catch(() => null))),
      { groups: [{ ...G('A'), fixerModel: f, reviewerModel: r }], groupsFile: 'r.json', repo: '/repo', fork: 'deadbeef' })
  } catch (e) { threw = /reviewer below the fixer/.test(e.message) }
  const below = TIERS.indexOf(r) < TIERS.indexOf(f)
  if (threw) tierThrows++
  if (threw !== below) tierWrong++
}
console.log(`RESULT tier_pairs_throwing=${tierThrows} of 9 (expected 3: reviewer below fixer)`)
console.log(`RESULT tier_pairs_wrong=${tierWrong} of 9`)

const t0 = process.cpuUsage()
const red = await wave([false, true])
const nul = await wave([true, true])
const merges = (r) => r.calls.filter((c) => c.startsWith('merge ')).length
console.log(`calls (red arm): ${JSON.stringify(red.calls)}`)
console.log(`RESULT merges_after_red=${red.after} merges`)
console.log(`RESULT red_logged=${red.logs.filter((l) => l.startsWith('MAIN IS RED after')).length} lines`)
console.log(`RESULT red_arm_merged=${red.out.merged.length} groups`)
console.log(`RESULT red_arm_redMain=${red.out.redMain ? 1 : 0}`)
console.log(`RESULT null_merges_after_red=${nul.after} merges`)
console.log(`RESULT null_merges=${merges(nul)} merges`)
const u = process.cpuUsage(t0)
console.log(`RESULT cpu_ms=${((u.user + u.system) / 1000).toFixed(1)} ms (provisional)`)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
console.log(`RESULT swapins=${process.resourceUsage().majorPageFault}`)
