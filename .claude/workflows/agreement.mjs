// agreement.mjs -- two readers of one governance concept must give one answer
// (round-9 class I4 barrier, prototype from the root-cause seat;
// handoff/r9-rca-i4).
//
// THE SHAPE IT REFUSES. A governance concept -- which globs a rule's `paths:`
// declares, which ids a finding's class_guess may carry, which pull request a
// first-parent subject names -- gets a second reader written beside the first,
// usually across a file or a language boundary, and nothing compares them. The
// two agree on the cases their authors tried and part on the rest. `#615` wrote
// both frontmatter parsers in one diff; `#1538` moved dead_top_level_symbols off
// bare names and left dead_methods, "the same screen", on them. tests/README.md
// forbids a TEST re-implementing production (closure.py no-copies enforces it);
// nothing forbids one governance tool re-implementing another.
//
// TWO ARMS.
//  1. PAIRS. Each registered concept names its readers and a corpus -- the live
//     tree's own instances plus the boundary cases a finding has shown. Every
//     reader answers every corpus item; any disagreement is refused. A reader
//     that throws, or a corpus that is empty, is a refusal, never a pass.
//  2. DISCOVERY (the bounded direction, decision 0003). A regex source that
//     appears in two or more governance code files is a grammar written twice.
//     Each such grammar must be named in SHARED_GRAMMARS with a disposition --
//     a PAIR above that drives it, the one module that now holds it, or why it
//     is not a concept -- and an entry whose grammar no longer spans two files
//     is DEAD. A second reader written tomorrow with a copied grammar is found
//     without anyone listing it; one with a DIFFERENT grammar is not, which is
//     why the pairs arm exists and why a fix that finds a sibling registers it.
//
//   node .claude/workflows/agreement.mjs [--only pairs|discovery]
// exit 0: no disagreement, no unregistered or dead grammar, no refusal.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(HERE, '..', '..')
const rd = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8')
const git = (args) => execFileSync('git', args, { cwd: ROOT, encoding: 'utf8' })

// A definition that lives in a script with no exports is read from its source
// text, as policy_lint.mjs reads web-fix-wave.js's VERDICT_RE: the reader
// compared is the one that runs, never a copy made here.
function fnFromSource(rel, name) {
  const src = rd(rel)
  const m = new RegExp(`\\nfunction ${name}\\(([^)]*)\\) \\{\\n([\\s\\S]*?)\\n\\}\\n`).exec(src)
  if (!m) throw new Error(`${rel}: no top-level function ${name}`)
  return new Function(...m[1].split(',').map((s) => s.trim()), m[2])
}
function constFromSource(rel, name) {
  const m = new RegExp(`\\nconst ${name} = (/(?:\\\\.|[^/\\n])+/[a-z]*)\\n`).exec(rd(rel))
  if (!m) throw new Error(`${rel}: no top-level const ${name} regex`)
  return new Function(`return ${m[1]}`)()
}
let plMod = null
async function policyLint() {
  if (plMod) return plMod
  // Prototype only: these are not exported at this base; the barrier pull
  // request exports them, and this does not edit policy_lint.mjs.
  const tmp = path.join(HERE, `.agreement-policy-lint-${process.pid}.mjs`)
  fs.writeFileSync(tmp, rd('.claude/workflows/policy_lint.mjs') + '\nexport { rulePaths as __agRulePaths, mergedPRs as __agMergedPRs }\n')
  try { plMod = await import(pathToFileURL(tmp).href) } finally { fs.rmSync(tmp, { force: true }) }
  return plMod
}
function python(code, input) {
  return JSON.parse(execFileSync('python3', ['-I', '-c', code], { cwd: ROOT, input: JSON.stringify(input), encoding: 'utf8' }))
}

// ---- the registered concepts ------------------------------------------------

// The six legal `paths:` shapes round 9 drove (D11-s1-71), plus every live rule.
const FM_SHAPES = {
  quoted_list: '---\ndescription: d\npaths:\n  - "tests/**"\n  - "docs/**"\n---\nbody\n',
  trailing_comment: '---\ndescription: d\npaths:\n  - "tests/**"   # the suite\n  - "custom_components/**"\n---\nbody\n',
  list_under_other_key: '---\ndescription: d\npaths:\n  - "tests/**"\nsee_also:\n  - "docs/**"\n---\nbody\n',
  single_quoted: "---\ndescription: d\npaths:\n  - 'tests/**'\n---\nbody\n",
  unquoted: '---\ndescription: d\npaths:\n  - tests/**\n---\nbody\n',
  flow_style: '---\ndescription: d\npaths: ["tests/**"]\n---\nbody\n',
  tab_indent: '---\ndescription: d\npaths:\n\t- "tests/**"\n---\nbody\n',
}

const PAIRS = [
  {
    concept: 'rule-frontmatter-paths',
    what: 'the globs a .claude/rules/*.md `paths:` key declares (decides when the harness loads the rule)',
    async corpus() {
      const live = git(['ls-files', '.claude/rules']).split('\n').filter((f) => /\.md$/.test(f)).map((f) => [f, rd(f)])
      return [...live, ...Object.entries(FM_SHAPES).map(([k, t]) => [`shape:${k}`, t])]
    },
    async readers() {
      const pl = await policyLint()
      const parse = fnFromSource('.claude/workflows/rules_sync.mjs', 'parse')
      const tmpDir = fs.mkdtempSync(path.join(ROOT, '.agreement-fm-'))
      return {
        'policy_lint.mjs rulePaths': (text, name) => {
          const rel = path.relative(ROOT, path.join(tmpDir, name.replace(/[/:]/g, '_')))
          fs.writeFileSync(path.join(ROOT, rel), text)
          return pl.__agRulePaths(rel) || []
        },
        'rules_sync.mjs parse': (text, name) => parse(text, name).paths,
        cleanup: () => fs.rmSync(tmpDir, { recursive: true, force: true }),
      }
    },
  },
  {
    concept: 'finding-class-id',
    what: 'the class ids a finding\'s class_guess may carry (the ledger, the schema, the intake)',
    async corpus() {
      const ledger = Object.keys(JSON.parse(rd('tools/audit/bugclasses.json'))).filter((k) => !k.startsWith('_'))
      const probes = ['new', 'P99', 'I99', 'P0', 'p1', 'P1x', 'xP1', 'X1', '']
      return [...new Set([...ledger, ...probes])].map((id) => [id, id])
    },
    async readers() {
      const ledger = new Set([...Object.keys(JSON.parse(rd('tools/audit/bugclasses.json'))).filter((k) => !k.startsWith('_')), 'new'])
      const schema = JSON.parse(rd('tools/audit/finding.schema.json'))
      const enumOf = (o) => (o && typeof o === 'object' ? (o.class_guess && o.class_guess.enum) || Object.values(o).map(enumOf).find(Boolean) : null)
      const schemaEnum = new Set(enumOf(schema) || [])
      if (!schemaEnum.size) throw new Error('finding.schema.json: no class_guess enum found')
      const intake = constFromSource('.claude/workflows/audit-find.js', 'CLASS_GUESS')
      return {
        'bugclasses.json ids + "new"': (id) => ledger.has(id),
        'finding.schema.json enum': (id) => schemaEnum.has(id),
        'audit-find.js CLASS_GUESS (intake)': (id) => intake.test(id),
      }
    },
  },
  {
    concept: 'merge-subject-pr',
    what: 'the pull request a first-parent subject on main names',
    async corpus() {
      const since = git(['describe', '--tags', '--abbrev=0', '--match', 'v6.5.0']).trim() || 'v6.5.0'
      const live = git(['log', '--first-parent', '--format=%s', `${since}..HEAD`]).split('\n').filter(Boolean)
      const shapes = ['Merge pull request #1052 from tvofi/fix/d11-pins', 'Merge pull request #13: Broaden the disclaimer', 'fix: a squash (#1234)', 'v6.7.1: stamp', 'ci: re-record closures']
      return [...new Set([...live, ...shapes])].map((s) => [s, s])
    },
    async readers() {
      const pl = await policyLint()
      const subjects = (await this.corpus()).map(([s]) => s)
      const stamp = python('import json,sys; sys.path[:0]=["tools/release"]; import stamp; print(json.dumps({s: stamp.pr_from_subject(s) for s in json.load(sys.stdin)}))', subjects)
      const ds = python('import json,sys; sys.path[:0]=["tests"]; import delivery_status as d; print(json.dumps({s: (str(d.subject_number(s)) if d.subject_number(s) is not None else None) for s in json.load(sys.stdin)}))', subjects)
      return {
        'stamp.py pr_from_subject': (s) => stamp[s],
        'delivery_status.py subject_number': (s) => ds[s],
        'policy_lint.mjs mergedPRs (subject mode)': (s) => (pl.__agMergedPRs([s])[0] || {}).pr || null,
      }
    },
  },
]

// ---- discovery ---------------------------------------------------------------

// Normalized regex source -> disposition. `pair:<concept>` (driven above),
// `module:<path>` (one module holds it; the other files import it), or
// `not-a-concept:<why>`. Seeded by the root-cause seat with the round-9
// instances only; the barrier pull request classifies every entry the
// discovery arm prints.
const SHARED_GRAMMARS = {
  '-"([^"]+)"': 'pair:rule-frontmatter-paths',
  '\\(#(\\d+)\\)': 'pair:merge-subject-pr',
  'Merge pull request #(\\d+)\\b': 'pair:merge-subject-pr',
}

function governanceCode() {
  return git(['ls-files']).split('\n').filter((f) => /\.(py|mjs|js|cjs)$/.test(f)
    && /^(\.claude|tools|tests)\//.test(f) && !/^tools\/audit\/round\d/.test(f)
    && !/\/fixtures\//.test(f) && !/^tests\/(hastub|pwlane)\//.test(f))
}
// A regex literal can start only where an operand can: after one of these
// punctuators or `return`. Anything else between two slashes is division or
// text in a string, which the round-9 seed run showed matching otherwise.
const JS_RE = /(?:^|[(,=:[!&|?{};>]|\breturn)\s*\/((?:\\.|\[(?:\\.|[^\]\\\n])*\]|[^/\\\n[*])(?:\\.|\[(?:\\.|[^\]\\\n])*\]|[^/\\\n[])*)\/[gimsuy]*/gm
const PY_RE = /re\.(?:compile|match|search|fullmatch|findall|finditer|sub)\(\s*r?(["'])((?:\\.|(?!\1).)+)\1/g
const norm = (r) => r.replace(/^\^/, '').replace(/\$$/, '').replaceAll('\\s*', '').replaceAll('[ \\t]*', '')

function discovery(report) {
  const occ = new Map()
  const files = governanceCode()
  for (const f of files) {
    const s = rd(f)
    const add = (r) => { if (r.length < 8) return; const k = norm(r); if (!occ.has(k)) occ.set(k, new Set()); occ.get(k).add(f) }
    if (f.endsWith('.py')) for (const m of s.matchAll(PY_RE)) add(m[2])
    else for (const m of s.matchAll(JS_RE)) if (!/^\s/.test(m[1])) add(m[1])
  }
  if (!files.length || !occ.size) { report.refused.push('discovery: enumerated no governance code or no grammar'); return }
  const shared = [...occ].filter(([k, fs_]) => fs_.size >= 2 && k.length >= 8)
  const pairs = new Set(PAIRS.map((p) => p.concept))
  for (const [k, fs_] of shared) {
    const d = SHARED_GRAMMARS[k]
    if (!d) { report.unregistered.push(`${JSON.stringify(k)} in ${[...fs_].sort().join(', ')}`); continue }
    if (d.startsWith('pair:') && !pairs.has(d.slice(5))) report.refused.push(`discovery ${JSON.stringify(k)}: names pair ${d.slice(5)}, which is not registered`)
  }
  for (const k of Object.keys(SHARED_GRAMMARS)) if (!shared.some(([s]) => s === k)) report.dead.push(`SHARED_GRAMMARS ${JSON.stringify(k)} no longer spans two files`)
  report.note.push(`discovery: ${files.length} governance code files, ${occ.size} distinct grammars, ${shared.length} shared by two or more files`)
}

async function pairsArm(report) {
  for (const p of PAIRS) {
    let corpus; let readers
    try { corpus = await p.corpus(); readers = await p.readers() } catch (e) { report.refused.push(`${p.concept}: ${String(e.message).split('\n')[0]}`); continue }
    const names = Object.keys(readers).filter((k) => k !== 'cleanup')
    if (!corpus.length || names.length < 2) { report.refused.push(`${p.concept}: ${corpus.length} corpus item(s), ${names.length} reader(s)`); readers.cleanup?.(); continue }
    let diverge = 0
    try {
      for (const [name, item] of corpus) {
        const ans = names.map((n) => JSON.stringify(readers[n](item, name)))
        if (new Set(ans).size === 1) continue
        diverge++
        report.divergent.push(`${p.concept} ${JSON.stringify(name.length > 60 ? name.slice(0, 57) + '...' : name)}: ${names.map((n, i) => `${n}=${ans[i]}`).join('  ')}`)
      }
    } catch (e) { report.refused.push(`${p.concept}: a reader threw: ${String(e.message).split('\n')[0]}`) } finally { readers.cleanup?.() }
    report.note.push(`pair ${p.concept}: ${names.length} readers, ${corpus.length} items, ${diverge} divergent`)
  }
}

async function main() {
  const argv = process.argv.slice(2)
  const only = argv[0] === '--only' ? argv[1] : null
  if (argv.length && !only) { console.error('usage: agreement.mjs [--only pairs|discovery]'); process.exit(2) }
  const t0 = Date.now()
  const report = { divergent: [], unregistered: [], dead: [], refused: [], note: [] }
  if (!only || only === 'pairs') await pairsArm(report)
  if (!only || only === 'discovery') discovery(report)
  for (const x of report.note) console.log(`  ${x}`)
  for (const x of report.divergent) console.log(`  DIVERGENT     ${x}`)
  for (const x of report.unregistered) console.log(`  UNREGISTERED  ${x}`)
  for (const x of report.dead) console.log(`  DEAD          ${x}`)
  for (const x of report.refused) console.log(`  REFUSED       ${x}`)
  const bad = report.divergent.length + report.unregistered.length + report.dead.length + report.refused.length
  console.log(`RESULT divergent=${report.divergent.length} unregistered=${report.unregistered.length} dead=${report.dead.length} refused=${report.refused.length} seconds=${((Date.now() - t0) / 1000).toFixed(1)}`)
  console.log(bad ? 'AGREEMENT REFUSED: one concept, readers that disagree or a grammar written twice and unregistered' : 'AGREEMENT ok')
  process.exit(bad ? 1 : 0)
}

main()
