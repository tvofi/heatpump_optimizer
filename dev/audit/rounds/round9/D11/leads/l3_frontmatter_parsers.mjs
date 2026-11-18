// l3_frontmatter_parsers: two in-tree parsers of one rule file's `paths:` frontmatter.
//
// Metric (one line): frontmatter cells where rules_sync.mjs:parse().paths (what the generated
// .cursor/rules/*.mdc globs carry) differs from policy_lint.mjs:rulePaths() (what rule-binding,
// role budgets and the always-loaded cap read); key = the two returned path lists, compared as JSON.
// Command:  node tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs [--perturb eol]
// Expected: divergent_cells=2 of 6 probe cells (exact: a trailing YAML comment on a paths entry,
//           and a quoted list item under another key); null control: 0 of 3 well-formed cells and
//           0 of the live .claude/rules/*.md corpus (capability, not incidence).
//           --perturb eol (rules_sync's `"\s*$` anchor dropped, one-line edit in memory) -> 1 of 6.
// Both functions are extracted from the files at run time and evaluated, not copied; neither
// script is imported because both run their main at module top level.
// Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, node v22.
// Instrumented symbols: .claude/workflows/rules_sync.mjs:parse, .claude/workflows/policy_lint.mjs:rulePaths
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

process.env.HPO_PLANDATA ??= fs.mkdtempSync(path.join(os.tmpdir(), 'l3fm-'))
const t0 = process.cpuUsage()
const perturb = process.argv.includes('--perturb') && process.argv[process.argv.indexOf('--perturb') + 1] === 'eol'

function extract(file, name) {
  const src = fs.readFileSync(file, 'utf8')
  const start = src.indexOf(`function ${name}(`)
  if (start < 0) throw new Error(`${name} not found in ${file}`)
  let i = src.indexOf('{', start), depth = 0
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++
    else if (src[i] === '}' && --depth === 0) break
  }
  return src.slice(start, i + 1)
}

let parseSrc = extract('.claude/workflows/rules_sync.mjs', 'parse')
if (perturb) {
  const before = parseSrc
  parseSrc = parseSrc.replace('"([^"]+)"\\s*$/gm', '"([^"]+)"/gm')
  if (before === parseSrc) throw new Error('perturbation matched nothing')
}
const parse = new Function(`${parseSrc}; return parse`)()
let current = ''
const rulePaths = new Function('read', `${extract('.claude/workflows/policy_lint.mjs', 'rulePaths')}; return rulePaths`)(() => current)

const doc = (fm) => `---\ndescription: probe\n${fm}\n---\n# body\n`
const PROBES = {
  trailing_comment: 'paths:\n  - "tests/**"   # the suite\n  - "custom_components/**"',
  list_under_other_key: 'paths:\n  - "tests/**"\nsee_also:\n  - "docs/**"',
  single_quoted: "paths:\n  - 'tests/**'",
  unquoted: 'paths:\n  - tests/**',
  flow_style: 'paths: ["tests/**"]',
  tab_indent: 'paths:\n\t- "tests/**"',
}
const CONTROLS = {
  one: 'paths:\n  - "tests/**"',
  two: 'paths:\n  - "tests/**"\n  - "docs/plan*.md"',
  none: 'other: 1',
}
function cell(fm) {
  current = doc(fm)
  const a = parse(current, 'probe').paths
  const b = rulePaths('probe') ?? []
  return { a, b, div: JSON.stringify(a) !== JSON.stringify(b) }
}
let div = 0
for (const [k, fm] of Object.entries(PROBES)) {
  const r = cell(fm)
  div += r.div
  console.log(`cell ${k.padEnd(22)} rules_sync=${JSON.stringify(r.a)} policy_lint=${JSON.stringify(r.b)} divergent=${+r.div}`)
}
let ctl = 0
for (const fm of Object.values(CONTROLS)) ctl += cell(fm).div
let live = 0, liveN = 0
for (const f of fs.readdirSync('.claude/rules').filter((x) => x.endsWith('.md'))) {
  current = fs.readFileSync(path.join('.claude/rules', f), 'utf8')
  const a = parse(current, f).paths, b = rulePaths(f) ?? []
  liveN++
  live += JSON.stringify(a) !== JSON.stringify(b)
}
console.log(`RESULT divergent_cells=${div} of ${Object.keys(PROBES).length} count`)
console.log(`RESULT null_control_wellformed_divergent=${ctl} of ${Object.keys(CONTROLS).length} count`)
console.log(`RESULT live_rules_divergent=${live} of ${liveN} count`)
console.log(`RESULT perturbed=${+perturb}`)
const u = process.cpuUsage(t0)
console.log('RESULT thread_factor=1.000')
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
let sw = -1
try { sw = +fs.readFileSync('/proc/vmstat', 'utf8').split('\n').find((l) => l.startsWith('pswpin')).split(' ')[1] } catch {}
console.log(`RESULT swapins=${sw}`)
void u
