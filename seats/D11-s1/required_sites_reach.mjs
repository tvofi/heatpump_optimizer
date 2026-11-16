#!/usr/bin/env node
// D11-s1 round 11: the required-contexts class's SITE list against the moved tree.
//
// Metric (one line): of the assertion-site files the class's own comment names
// (the workflow comments, the plan of record, the decision records, the
// handover), how many -- at their CURRENT paths -- would let a planted stale
// claim ("17 required status checks", against a live set of 1) through with 0
// `required-contexts` findings. Count key: policy_lint.mjs's own
// `by check` report for the run with that one site planted.
//
// Run (from the export root):
//   node dev/audit/rounds/round11/D11/s1/required_sites_reach.mjs
//   node dev/audit/rounds/round11/D11/s1/required_sites_reach.mjs --perturb
// --perturb is the one-line production edit, made in the temp copy: the
// REQUIRED_CONTEXT_SITE regex in policy_lint.mjs gains the moved homes
// (dev/programme/plan-*.md, dev/governance/decisions/NNNN-*.md,
// dev/programme/HANDOVER.md). Measured at the baseline: RESULT unreached=0
// of 4 sites (every moved home is already reached, so this is a
// NON-FINDING); the perturbed arm also reads 0. Null control: the unplanted
// copy reports 0 required-contexts findings; each planted site adds 1.
// Every run is policy_lint.mjs on a temp COPY of the export (its linked .git
// file kept, read-only use), with `gh` a shim serving api/*.json: no live API
// call, the export never written.
// Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
// Instrumented symbol: tools/policy/policy_lint.mjs:requiredContextsOverTree
// (REQUIRED_CONTEXT_SITE), driven through main() as a process.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'

for (const v of ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']) process.env[v] ??= '1'
const ROOT = process.cwd()
const HERE = path.join(ROOT, 'dev/audit/rounds/round11/D11/s1')
const TMP = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'd11s1-sites-'))
const PERTURB = process.argv.includes('--perturb')
const REPO = 'repos/tvofi/heatpump_optimizer'
const SITES = [
  '.github/workflows/hassfest.yml',
  'dev/programme/plan-2026-09-open-issues.md',
  'dev/governance/decisions/0011-app-authored-identity.md',
  'dev/programme/HANDOVER.md',
]
const PLANT = '\nThe merge boundary runs 17 required status checks.\n'
const PLANT_YML = '\n# The merge boundary runs 17 required status checks.\n'

// gh shim, serving the snapshot.
const shim = path.join(TMP, 'shim')
fs.mkdirSync(shim)
const served = { [`${REPO}/rules/branches/main`]: JSON.parse(fs.readFileSync(path.join(HERE, 'api/rules-branches-main.json'), 'utf8')) }
for (const id of [22628467, 23698884, 23937752]) served[`${REPO}/rulesets/${id}`] = JSON.parse(fs.readFileSync(path.join(HERE, `api/ruleset-${id}.json`), 'utf8'))
fs.writeFileSync(path.join(shim, 'served.json'), JSON.stringify(served))
fs.writeFileSync(path.join(shim, 'gh'), `#!/usr/bin/env node
const f = require(${JSON.stringify(path.join(shim, 'served.json'))}); const a = process.argv.slice(2);
if (a[0] !== 'api' || !(a[1] in f)) { process.stderr.write('shim: unserved ' + a.join(' ') + '\\n'); process.exit(1) }
process.stdout.write(JSON.stringify(f[a[1]]));
`, { mode: 0o755 })

function copyTree(tag) {
  const dst = path.join(TMP, tag)
  fs.cpSync(ROOT, dst, { recursive: true, filter: (s) => !s.includes(`${path.sep}node_modules${path.sep}`) && path.basename(s) !== '.git' })
  fs.copyFileSync(path.join(ROOT, '.git'), path.join(dst, '.git'))
  if (PERTURB) {
    const p = path.join(dst, 'tools/policy/policy_lint.mjs')
    const src = fs.readFileSync(p, 'utf8')
    const old = "docs\\/HANDOVER\\.md)$/"
    if (src.split(old).length !== 2) { console.log('PERTURBATION DID NOT APPLY'); process.exit(2) }
    fs.writeFileSync(p, src.replace(old, "docs\\/HANDOVER\\.md|dev\\/programme\\/plan-[A-Za-z0-9-]+\\.md|dev\\/governance\\/decisions\\/[0-9]{4}-[A-Za-z0-9-]+\\.md|dev\\/programme\\/HANDOVER\\.md)$/"))
  }
  return dst
}

function rcFindings(dst) {
  let out = ''
  try {
    out = execFileSync('node', ['tools/policy/policy_lint.mjs', '--report'], { cwd: dst, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, PATH: `${shim}:${process.env.PATH}`, HPO_PLANDATA: path.join(dst, '.pd') } })
  } catch (e) { out = `${e.stdout || ''}` }
  const by = out.split('\n').find((l) => l.startsWith('by check:'))
  const skip = out.split('\n').find((l) => /skip\s+required-contexts/.test(l))
  if (skip) return { n: NaN, skip }
  return { n: by ? (JSON.parse(by.slice('by check:'.length)))['required-contexts'] || 0 : NaN }
}

const base = copyTree('null')
const nul = rcFindings(base)
console.log(`null control (unplanted copy): ${nul.n} required-contexts finding(s)${nul.skip ? ` ${nul.skip}` : ''}`)
fs.rmSync(base, { recursive: true, force: true })
let unreached = 0
for (const site of SITES) {
  const dst = copyTree(`plant-${path.basename(site)}`)
  fs.appendFileSync(path.join(dst, site), site.endsWith('.yml') ? PLANT_YML : PLANT)
  const r = rcFindings(dst)
  const delta = r.n - nul.n
  if (!(delta > 0)) unreached++
  console.log(`${site}: planted stale count -> ${r.n} finding(s) (delta ${delta})${delta > 0 ? '' : '  <- UNREACHED'}`)
  fs.rmSync(dst, { recursive: true, force: true })
}
console.log(`RESULT sites=${SITES.length} sites`)
console.log(`RESULT unreached=${unreached} sites`)
console.log(`RESULT null_findings=${nul.n} findings`)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let sw = 'n/a'
try { sw = fs.readFileSync('/proc/vmstat', 'utf8').split('\n').find((l) => l.startsWith('pswpin')).split(' ')[1] } catch {}
console.log(`RESULT swapins=${sw}`)
fs.rmSync(TMP, { recursive: true, force: true })
