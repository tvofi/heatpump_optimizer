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
function constFromSource(rel, name) {
  const m = new RegExp(`\\nconst ${name} = (/(?:\\\\.|[^/\\n])+/[a-z]*)\\n`).exec(rd(rel))
  if (!m) throw new Error(`${rel}: no top-level const ${name} regex`)
  return new Function(`return ${m[1]}`)()
}
const load = (rel) => import(pathToFileURL(path.join(ROOT, rel)).href)


const CC = 'custom_components/heatpump_optimizer'
function entityLeaves(rel) {
  const out = {}
  const walk = (o, pre) => { for (const [k, v] of Object.entries(o)) (v && typeof v === 'object') ? walk(v, `${pre}${k}.`) : (out[`${pre}${k}`] = v) }
  walk(JSON.parse(rd(`${CC}/${rel}`)).entity ?? {}, '')
  if (!Object.keys(out).length) throw new Error(`${rel}: no entity section`)
  return out
}

// The Python-side readers run in agreement_py.py (its own step, under `python3 -I`
// after the job's restore from the base); this reads the JSON it wrote.
let PY = null
function py(key) {
  if (!PY) {
    const i = process.argv.indexOf('--py-json')
    if (i < 0 || !process.argv[i + 1]) throw new Error('no --py-json FILE: run `python3 -I .claude/workflows/agreement_py.py --run`')
    PY = JSON.parse(fs.readFileSync(process.argv[i + 1], 'utf8'))
  }
  if (!PY[key]) throw new Error(`the Python readers' JSON has no ${key}`)
  return PY[key]
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
      const pl = await load('.claude/workflows/policy_lint.mjs')
      const { parse } = await load('.claude/workflows/rules_sync.mjs')
      const tmpDir = fs.mkdtempSync(path.join(ROOT, '.agreement-fm-'))
      return {
        'policy_lint.mjs rulePaths': (text, name) => {
          const rel = path.relative(ROOT, path.join(tmpDir, name.replace(/[/:]/g, '_')))
          fs.writeFileSync(path.join(ROOT, rel), text)
          return pl.rulePaths(rel) || []
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
      return Object.keys(py('merge')).map((s) => [s, s])
    },
    // A live item that is a merge commit and that EVERY reader answers null for
    // is refused (merge_shape_guard, RCA-BULK-3 section 5, #1041): agreement
    // cannot see a misreading all readers share, and a count of zero PRs read
    // from a non-empty window is the alarm. Stamps are direct commits, never merges.
    mustAnswer: (s) => /^Merge pull request #\d+ from /.test(s),
    async readers() {
      const pl = await load('.claude/workflows/policy_lint.mjs')
      const m = py('merge')
      return {
        'stamp.py pr_from_subject': (s) => m[s].stamp,
        'delivery_status.py subject_number': (s) => m[s].delivery_status,
        'policy_lint.mjs resolvePrFromCommit (gap recovery)': (s) => (pl.resolvePrFromCommit(s, []) || {}).pr || null,
        'policy_lint.mjs enumerateMerges (offline subject mode)': Object.assign(
          (s) => (pl.enumerateMerges([{ sha: 'x', subject: s }], null).prs[0] || {}).pr || null,
          // ACCEPTED ASYMMETRY (F11.1 forward-carry): the
          // offline mode reads the squash `(#N)` shape only. Its zero is the
          // could-not-enumerate signal (`enumSkipLine`); widening it would change
          // what that zero means. The merge-commit shape must therefore answer
          // null HERE: an answer means the asymmetry is stale and is refused.
          { narrow: /^Merge pull request #\d+ from /, why: 'offline subject mode reads the squash shape only (enumSkipLine)' }),
      }
    },
  },
  {
    concept: 'dead-member-liveness',
    what: 'whether a production class is live: structure.py dead_top_level_symbols (bound_references) against dead_members (reachability over methods), D7-s3-02',
    async corpus() {
      return Object.keys(py('structure')).sort().map((i) => [i, i])
    },
    async readers() {
      const rows = py('structure')
      return {
        'structure.py bound_references (top-level)': (i) => rows[i].bound,
        'structure.py dead_members (methods)': (i) => rows[i].live_methods,
      }
    },
  },
  {
    concept: 'governance-workflow-jobs',
    what: 'which workflow jobs are governance: tests/entities.py\'s pinned file list against governance_cost.py\'s GOV derivation, D11-s1-72',
    async corpus() {
      return py('governance_jobs').jobs.map((j) => [j, j])
    },
    async readers() {
      const out = py('governance_jobs')
      const gov = new Set(out.gov); const pin = new Set(out.pin)
      return { 'governance_cost.py GOV': (j) => gov.has(j), "tests/entities.py _GOV_FILES (+ the 'briefs' null control)": (j) => pin.has(j) }
    },
  },
  {
    concept: 'entity-names',
    what: "the display name of each entity key: strings.json (what tests/entities.py's entity-name resolver reads for the contiguity check) against translations/en.json (what the archscore family_splits enumerator reads); hassfest never compares the two files' values. R9-F7.5 carry-in, route A",
    async corpus() {
      const keys = new Set()
      for (const f of ['strings.json', 'translations/en.json']) for (const k of Object.keys(entityLeaves(f))) keys.add(k)
      return [...keys].sort().map((k) => [k, k])
    },
    async readers() {
      const a = entityLeaves('strings.json'); const b = entityLeaves('translations/en.json')
      return { 'strings.json entity section': (k) => a[k] ?? null, 'translations/en.json entity section': (k) => b[k] ?? null }
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
  "  ([A-Za-z][\\w-]*):": "identical:the job-id scan of a workflow's jobs: block, a disclosed copy of entities.py _workflow_job_ids in the governance-workflow-jobs reader, null-controlled by the 'briefs' job",
  "wave-.*-groups\\.json": "identical:three directory filters over the wave rosters, one listing rule",
  "const VERDICT_CLASSES = \\[([^\\]]*)\\]": "identical:the wave script's verdict-class list extractor, read in three tools",
  "const VERDICT_RE = new RegExp\\(\\n([\\s\\S]*?)\\n\\)": "identical:the wave script's verdict-regex extractor, read in two tools",
  "'([a-z][a-z0-9-]*)'": "identical:the word extractor applied to the VERDICT_CLASSES array text",
  "\\/rules\\/branches\\/main": "not-a-concept:an API path suffix; counts.mjs strips it, field_coverage.mjs matches whole paths",
  "rulesets": "not-a-concept:the GitHub endpoint word, no grammar of ours",
  "(?:\\||-\\[#\\d+\\])": "identical:the Delivery-status row anchor, counts.mjs and policy_lint.mjs",
  "[.+^${}()|[\\]\\\\]": "not-a-concept:the standard regexp-escape idiom",
  "\\.{0,2}\\/?[\\w.@-]+(\\/[\\w.@-]+)+\\.(sh|py|mjs|js)": "identical:figure_census and figure_lint's script-path word grammar (one census, one lint)",
  "[A-Za-z_][A-Za-z0-9_]*=": "identical:figure_census and figure_lint's env-assignment word",
  "##\\s+(.*?)": "identical:the h2 heading grammar, policy_lint.mjs and the record-predicate sweep",
  "\\|[\\s|:-]+\\|": "identical:the markdown table separator row, three readers",
  "[-*]\\s+\\[#(\\d+)\\]\\((?:[^()\\s]*\\/pull\\/)(\\d+)\\)": "identical:the Delivery-status row anchor, policy_lint.mjs and the record-predicate sweep",
  "refuse\\s+since-ref\\b": "identical:the `refuse since-ref` output marker, policy_lint.mjs and its env-matrix",
  "<svg class=\"setup-svg[\\s\\S]*?<\\/svg>": "identical:the setup-page SVG extractor, card.mjs and setup_qa_render.mjs",
  "\\d+\\.\\d+\\.\\d+": "not-a-concept:the semantic-version shape",
  "[\\[{]\"(\\d+)\\xb7([^\"<]+?)(?:<br/>|\")": "identical:the README flow-diagram step grammar, doc_claims.py and entities.py",
  "\\*\\*(\\d+)\\xb7([^*]+?)\\.?\\*\\*": "identical:the README flow-diagram bold-step grammar, doc_claims.py and entities.py",
  "[^a-z0-9 ]": "identical:the README table-label normaliser, doc_claims.py and entities.py",
  "const CARD_VERSION = \"(\\d+\\.\\d+\\.\\d+)\";": "identical:the card version constant, doc_claims.py and stamp.py",
  "[^a-z0-9]+": "not-a-concept:two unrelated slug normalisers (entities.py prose, gen_device_fixtures.py ids)",
  "\\{(\\w+)\\}": "not-a-concept:the Python format-placeholder token",
  "[^:\\s]+:\\d+ [A-Z_]+": "identical:the mutation ledger line key, mutation_table.py and ledger_merge.py",
  "\"version\": \"[^\"]*\"": "not-a-concept:two audit probe scripts editing a manifest fixture",
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

function discovery(report, files = governanceCode(), read = rd, registry = SHARED_GRAMMARS, pairNames = PAIRS.map((p) => p.concept)) {
  const occ = new Map()
  for (const f of files) {
    const s = read(f)
    const add = (r) => { if (r.length < 8) return; const k = norm(r); if (!occ.has(k)) occ.set(k, new Set()); occ.get(k).add(f) }
    if (f.endsWith('.py')) for (const m of s.matchAll(PY_RE)) add(m[2])
    else for (const m of s.matchAll(JS_RE)) if (!/^\s/.test(m[1])) add(m[1])
  }
  if (!files.length || !occ.size) { report.refused.push('discovery: enumerated no governance code or no grammar'); return }
  const shared = [...occ].filter(([k, fs_]) => fs_.size >= 2 && k.length >= 8)
  const pairs = new Set(pairNames)
  for (const [k, fs_] of shared) {
    const d = registry[k]
    if (!d) { report.unregistered.push(`${JSON.stringify(k)} in ${[...fs_].sort().join(', ')}`); continue }
    if (!/^(pair|module|identical|not-a-concept):\S/.test(d)) report.refused.push(`discovery ${JSON.stringify(k)}: disposition ${JSON.stringify(d)} is not pair:, module:, identical: or not-a-concept:`)
    if (d.startsWith('pair:') && !pairs.has(d.slice(5))) report.refused.push(`discovery ${JSON.stringify(k)}: names pair ${d.slice(5)}, which is not registered`)
  }
  for (const k of Object.keys(registry)) if (!shared.some(([s]) => s === k)) report.dead.push(`SHARED_GRAMMARS ${JSON.stringify(k)} no longer spans two files`)
  report.note.push(`discovery: ${files.length} governance code files, ${occ.size} distinct grammars, ${shared.length} shared by two or more files`)
}

async function pairsArm(report, pairs = PAIRS) {
  for (const p of pairs) {
    let corpus; let readers
    try { corpus = await p.corpus(); readers = await p.readers() } catch (e) { report.refused.push(`${p.concept}: ${String(e.message).split('\n')[0]}`); continue }
    const names = Object.keys(readers).filter((k) => k !== 'cleanup')
    if (!corpus.length || names.length < 2) { report.refused.push(`${p.concept}: ${corpus.length} corpus item(s), ${names.length} reader(s)`); readers.cleanup?.(); continue }
    let diverge = 0
    try {
      for (const [name, item] of corpus) {
        const ans = {}
        const comparing = []
        for (const n of names) {
          const a = readers[n](item, name)
          const nar = readers[n].narrow
          if (nar && nar.test(String(item))) {
            // A declared narrow reader must stay narrow on its shape; an answer there is a stale asymmetry.
            if (a != null) { diverge++; report.divergent.push(`${p.concept} ${JSON.stringify(name)}: ${n} was declared blind to this shape (${readers[n].why}) and now answers ${JSON.stringify(a)}: drop its \`narrow\``) }
            continue
          }
          ans[n] = JSON.stringify(a)
          comparing.push(n)
        }
        if (p.mustAnswer && p.mustAnswer(item) && comparing.every((n) => ans[n] === 'null')) {
          diverge++
          report.divergent.push(`${p.concept} ${JSON.stringify(name)}: every reader answers null for a live item that must name one (merge-shape guard)`)
          continue
        }
        if (new Set(comparing.map((n) => ans[n])).size === 1) continue
        diverge++
        report.divergent.push(`${p.concept} ${JSON.stringify(name.length > 60 ? name.slice(0, 57) + '...' : name)}: ${comparing.map((n) => `${n}=${ans[n]}`).join('  ')}`)
      }
    } catch (e) { report.refused.push(`${p.concept}: a reader threw: ${String(e.message).split('\n')[0]}`) } finally { readers.cleanup?.() }
    report.note.push(`pair ${p.concept}: ${names.length} readers, ${corpus.length} items, ${diverge} divergent`)
  }
}

// --self-test: the instrument refuses each shape it exists to refuse, driven on
// synthetic readers and a synthetic tree, so a comparator that stopped comparing
// reads red here (fixer.md step 2: a check is shown failing on its defect).
async function selfTest() {
  const probes = []
  const run = async (name, pair, want) => {
    const r = { divergent: [], unregistered: [], dead: [], refused: [], note: [] }
    await pairsArm(r, [pair])
    probes.push([name, want(r)])
  }
  const mk = (readers, corpus, extra = {}) => ({ concept: 'synthetic', corpus: async () => corpus, readers: async () => readers, ...extra })
  const items = [['a', 'a'], ['b', 'b']]
  await run('agreeing readers pass', mk({ x: (i) => i, y: (i) => i }, items), (r) => !r.divergent.length && !r.refused.length)
  await run('a disagreeing reader is divergent', mk({ x: (i) => i, y: (i) => (i === 'b' ? 'z' : i) }, items), (r) => r.divergent.length === 1)
  await run('a reader that throws is refused, never a pass', mk({ x: (i) => i, y: () => { throw new Error('boom') } }, items), (r) => r.refused.length === 1)
  await run('an empty corpus is refused', mk({ x: (i) => i, y: (i) => i }, []), (r) => r.refused.length === 1)
  await run('one reader is refused', mk({ x: (i) => i }, items), (r) => r.refused.length === 1)
  const nar = Object.assign((i) => (i === 'a' ? 'A' : i), { narrow: /^a$/, why: 'synthetic' })
  await run('a stale narrow declaration is divergent', mk({ x: (i) => i, y: nar }, items), (r) => r.divergent.length === 1)
  await run('every reader null on a must-answer item is refused (merge-shape guard)', mk({ x: () => null, y: () => null }, items, { mustAnswer: (i) => i === 'a' }), (r) => r.divergent.length === 1)
  await run('null on an item that need not answer passes', mk({ x: () => null, y: () => null }, items), (r) => !r.divergent.length)
  const disc = (files, registry) => {
    const r = { divergent: [], unregistered: [], dead: [], refused: [], note: [] }
    discovery(r, Object.keys(files), (f) => files[f], registry, [])
    return r
  }
  const g = 'const A = /^some-shared-grammar-(\\d+)-x$/\n'
  probes.push(['a grammar in two files and unregistered is found', disc({ 'a.mjs': g, 'b.mjs': g }, {}).unregistered.length === 1])
  probes.push(['a registered grammar passes', !disc({ 'a.mjs': g, 'b.mjs': g }, { 'some-shared-grammar-(\\d+)-x': 'identical:synthetic' }).unregistered.length])
  probes.push(['a grammar in one file is not shared', !disc({ 'a.mjs': g, 'b.mjs': 'const B = 1\n' }, {}).unregistered.length])
  probes.push(['an entry that no longer spans two files is DEAD', disc({ 'a.mjs': g, 'b.mjs': 'const B = 1\n' }, { 'some-shared-grammar-(\\d+)-x': 'identical:synthetic' }).dead.length === 1])
  probes.push(['a disposition of no known kind is refused', disc({ 'a.mjs': g, 'b.mjs': g }, { 'some-shared-grammar-(\\d+)-x': 'whatever' }).refused.length === 1])
  let bad = 0
  for (const [name, ok] of probes) { console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${name}`); if (!ok) bad++ }
  console.log(`SELF-TEST ${probes.length - bad} of ${probes.length} probes held`)
  process.exit(bad ? 1 : 0)
}

async function main() {
  const argv = process.argv.slice(2)
  const pj = argv.indexOf('--py-json')
  if (pj >= 0) argv.splice(pj, 2)
  if (argv[0] === '--self-test') return selfTest()
  const only = argv[0] === '--only' ? argv[1] : null
  if (argv.length && !only) { console.error('usage: agreement.mjs [--only pairs|discovery | --self-test]'); process.exit(2) }
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
