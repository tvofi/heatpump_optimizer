// R10-POLICY-LINT-FAMILY (#2410): what does policy_lint.mjs's family arm file
// over a recorded window, and on which distinct pull requests?
//
//   node dev/audit/harnesses/r10_family_replay.mjs [<repo root>]
//
// Replays dev/audit/rca/harness-friction/verdict_first_lines.tsv -- every
// `Fix review:` first line of every merged pull request in v7.0.0..df6ca4bc,
// fetched for #2561 -- through the `statsFindings` of the policy_lint.mjs under
// <repo root> (default: this tree), so the same recorded input is read by the
// base's fold and the head's. No API read. Metric, one line each:
//   RESULT line=<key> kind=<kind> count=<n>     -- every would-open line of the
//                                                  mutation family and its members
//   PRS <key> <pr,...>                          -- the distinct-PR list per member
//                                                  word: the null control a count
//                                                  is checked against
//   CLAUSE <text>                               -- the family line's own account
//                                                  of what it counted
// The tsv's bodies are first lines; statsFindings reads a verdict's first line
// only, so nothing it keys on is missing.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const here = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')
const root = path.resolve(process.argv[2] ?? here)
const tsv = path.join(here, 'dev/audit/rca/harness-friction/verdict_first_lines.tsv')
const mod = await import(pathToFileURL(path.join(root, 'tools/policy/policy_lint.mjs')).href)

const fetched = new Map()
for (const line of fs.readFileSync(tsv, 'utf8').split('\n')) {
  const [pr, at, body] = line.split('\t')
  if (!body) continue
  if (!fetched.has(pr)) fetched.set(pr, { body: '', title: '', comments: [], reviews: [] })
  fetched.get(pr).comments.push({ body, created_at: at })
}
const prs = [...fetched.keys()].map((pr) => ({ pr }))
const words = ['mutation', 'mutation-vacuous', 'mutation-survivor', 'test-vacuous', 'vacuous-test', 'vacuous-check', 'mutant-survives']
const RE = /would open "\[policy\] recurring friction: (.+?)" -- (.+?) at (\d+) in this window/
for (const f of mod.statsFindings({ prs, fetched, fetchError: null, classes: ['blocked', 'merge'] })) {
  const m = f.message.match(RE)
  if (m && (words.includes(m[1]) || m[1] === 'mutation (family)')) console.log(`RESULT line=${m[1]} kind=${m[2].replace(' ', '-')} count=${m[3]}`)
  if (m && m[1] === 'mutation (family)') console.log(`CLAUSE ${f.message.match(/counted as DISTINCT[^;]*/)[0]}`)
}
const { verdicts } = mod.statsHistogram(prs, fetched, ['blocked', 'merge'])
for (const w of words) console.log(`PRS ${w} ${[...(verdicts.get(w)?.prs ?? [])].sort().join(',') || '-'}`)
