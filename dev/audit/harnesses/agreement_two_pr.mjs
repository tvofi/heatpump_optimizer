// agreement_two_pr.mjs -- the two-pull-request sequence of a shared grammar,
// graded the way CI grades it (#3100, #3166's review).
//
//   node dev/audit/harnesses/agreement_two_pr.mjs <grader.mjs> '<disposition>'
//
// CI grades a pull request with its BASE's tools/policy/agreement.mjs, the
// SHARED_GRAMMARS registry with it (governance.yml restores it before the
// agreement step), and main's push run with main's own. Every self-test probe
// passes one registry to one tree; this harness instead makes real commits in a
// throwaway clone of this repository's HEAD, with <grader.mjs> as the grader,
// and runs `--only discovery` at each step. <disposition> is the entry PR A
// adds for a synthetic grammar; `{P}` in it names the second reader's path.
//
// The sequence, and the verdict each step must read on the synthetic grammar:
//   main1 push             one reader, no entry                      clean
//   PR A by main1          adds the entry                            clean
//   main2 push             the entry spans one file                  clean
//   PR B by main2          adds the second reader at {P}             clean
//   main3 push                                                       clean
//   PR D by main3          removes the second reader                 DEAD
//   expiry: PR A's commit and merge dated 8 days back, PR U unrelated, then
//   mainU push             the entry still spans one file            DEAD
//   PR C by mainU          drops the entry                           clean
//   mainC push                                                       clean
// It prints each step's verdict lines and RESULT, then TWO-PR HELD or
// TWO-PR BROKEN naming every step that read otherwise; exit 0 or 1.
// The DEAD steps are keyed on the grammar's DEAD line, never on a count.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
const [graderArg, disposition] = process.argv.slice(2)
if (!graderArg || !disposition) { console.error("usage: agreement_two_pr.mjs <grader.mjs> '<disposition>'"); process.exit(2) }
const grader = fs.readFileSync(path.resolve(graderArg), 'utf8')
const GRADER = 'tools/policy/agreement.mjs'
const SOLE = 'tools/policy/zz_two_pr_1.mjs'; const P = 'tools/policy/zz_two_pr_2.mjs'
const KEY = 'zz-two-pr-grammar-(\\d+)-q'
const SRC = 'export const ZZ = /^zz-two-pr-grammar-(\\d+)-q$/\n'
const anchor = 'const SHARED_GRAMMARS = {\n'
if (!grader.includes(anchor)) { console.error(`${graderArg}: no SHARED_GRAMMARS block`); process.exit(2) }
const entryLine = `  ${JSON.stringify(KEY)}: ${JSON.stringify(disposition.replaceAll('{P}', P))},\n`

const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'agreement-two-pr-'))
const failed = []
try {
  // tests/throwaway_git.py: the one way a tracked script makes a throwaway repository.
  const env = JSON.parse(execFileSync('python3', ['-I', '-c',
    'import json, sys; sys.path.insert(0, sys.argv[3]); from throwaway_git import throwaway_git_clone; print(json.dumps(throwaway_git_clone(sys.argv[1], sys.argv[2], "-q", "--shared")))',
    ROOT, repo, path.join(ROOT, 'tests')], { encoding: 'utf8' }))
  const g = (args, extra = {}) => execFileSync('git', args, { cwd: repo, encoding: 'utf8', env: { ...env, ...extra }, stdio: ['ignore', 'pipe', 'pipe'] }).trim()
  const put = (rel, text) => { const f = path.join(repo, rel); if (text === null) fs.rmSync(f); else { fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, text) } }
  const at = (secs) => (secs ? { GIT_COMMITTER_DATE: `@${secs} +0000`, GIT_AUTHOR_DATE: `@${secs} +0000` } : {})
  const commit = (msg, when) => { g(['add', '-A']); g(['commit', '-q', '--no-verify', '-m', msg], at(when)) }
  const branch = (name, from) => g(['checkout', '-q', '-B', name, from])
  const merge = (into, pr, n, when) => { g(['checkout', '-q', into]); g(['merge', '-q', '--no-ff', '--no-edit', '-m', `Merge pull request #${n} from t/${pr}`, pr], at(when)) }
  const grade = (step, want) => {
    let out = ''
    try { out = execFileSync('node', [GRADER, '--only', 'discovery'], { cwd: repo, encoding: 'utf8', env }) } catch (e) { out = String(e.stdout) }
    const lines = out.split('\n').filter((l) => /^\s+(UNREGISTERED|DEAD|REFUSED)\s/.test(l) && l.includes(JSON.stringify(KEY))).map((l) => l.trim().replace(/\s+/, ' '))
    const result = (out.match(/^RESULT .*/m)?.[0] ?? 'RESULT missing').replace(/ seconds=\S+/, '')
    const ok = want === null ? !lines.length : lines.length === 1 && lines[0].startsWith(`DEAD SHARED_GRAMMARS ${JSON.stringify(KEY)} `)
    console.log(`${ok ? 'held  ' : 'BROKEN'} ${step}: ${result}`)
    for (const l of lines) console.log(`         ${l}`)
    if (!ok) failed.push(step)
  }
  // A pull request's run: the merge of its head into its base, with the
  // grader restored from the base, as governance.yml's restore step does.
  const ci = (step, base, pr, want) => {
    g(['checkout', '-q', '--detach', base]); g(['merge', '-q', '--no-ff', '--no-edit', '-m', 'ci merge', pr])
    g(['checkout', base, '--', GRADER]); grade(step, want); g(['checkout', '-q', '-f', base])
  }
  const now = Number(g(['log', '-1', '--format=%ct', 'HEAD']))
  g(['checkout', '-q', '-B', 'main'])
  put(GRADER, grader); put(SOLE, SRC); commit('main1')
  g(['branch', '-f', 'main1'])
  grade('main1 push', null)
  branch('a', 'main1'); put(GRADER, grader.replace(anchor, anchor + entryLine)); commit('PR A: the entry')
  ci('PR A by main1', 'main', 'a', null)
  merge('main', 'a', 1); grade('main2 push', null)
  branch('b', 'main'); put(P, SRC); commit('PR B: the second reader')
  ci('PR B by main2', 'main', 'b', null)
  merge('main', 'b', 2); grade('main3 push', null)
  branch('d', 'main'); put(P, null); commit('PR D: the second reader leaves')
  ci('PR D by main3', 'main', 'd', 'DEAD')
  // The expiry line, cut from main1: PR A landed 8 days before HEAD.
  const old = now - 8 * 86400
  branch('main', 'main1'); branch('a2', 'main1'); put(GRADER, grader.replace(anchor, anchor + entryLine)); commit('PR A: the entry', old)
  merge('main', 'a2', 3, old)
  branch('u', 'main'); put('docs/zz_two_pr_unrelated.md', 'unrelated\n'); commit('PR U')
  merge('main', 'u', 4); grade('mainU push', 'DEAD')
  branch('c', 'main'); put(GRADER, grader); commit('PR C: drop the entry')
  ci('PR C by mainU', 'main', 'c', null)
  merge('main', 'c', 5); grade('mainC push', null)
} finally { fs.rmSync(repo, { recursive: true, force: true }) }
console.log(failed.length ? `TWO-PR BROKEN at ${failed.join(', ')}` : 'TWO-PR HELD')
process.exit(failed.length ? 1 : 0)
