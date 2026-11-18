// Leads seat (round 10), owner D13-s2, step D13.M6: a moved policy file's real path and its
// canonical spelling resolve to different friction keys.
//
// Metric: number of policy-corpus files (git ls-files | policy_lint.mjs --corpus-filter) that
//   counts.mjs:canon() spells differently and for which policy_lint.mjs:frictionKey(real path)
//   != frictionKey(canon spelling); each such file splits one contract's friction across two
//   histogram keys. Count key: the key string frictionKey returns, read through policy_lint's own
//   --normalize-friction-keys mode (the production function, unmodified in the base arm).
// Command (from the root of a git checkout of the baseline; policy_lint needs `git ls-files`):
//   node dev/audit/rounds/round10/D13/leads/friction_key_split.mjs [--perturb]
// Expected at 17f1c55fad1b: RESULT split_keys=34 count (34 of 34 moved corpus files) (tolerance 0); --perturb -> 0.
// Perturbation (--perturb): tools/policy/*.mjs copied to a mkdtemp root whose ROOT constant is
//   redirected to this checkout (plumbing only; the plumbing-only arm is printed and must equal the
//   base arm), plus ONE production edit in frictionKey: `const bare = canon(raw.replace(...))`,
//   i.e. canonicalise the id the way trackedFiles canonicalises the corpus. split_keys must fall to 0.
// Seam rule: this loop over every corpus file with canon(f) !== f.
// Machine: macOS arm64 (leads seat). Counts only, contention-immune.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const ROOT = process.cwd()
const perturb = process.argv.includes('--perturb')
const sh = (cmd, args, input, env) =>
  execFileSync(cmd, args, { cwd: ROOT, encoding: 'utf8', input, maxBuffer: 64 << 20, env: { ...process.env, ...(env ?? {}) } })

const tracked = sh('git', ['ls-files'])
function measure(lint, env) {
  const corpus = sh('node', [lint, '--corpus-filter'], tracked, env).split('\n').filter(Boolean)
  const counts = path.join(path.dirname(lint), 'counts.mjs')
  const canonOut = sh('node', ['--input-type=module', '-e',
    `import { canon } from ${JSON.stringify(counts)}; import fs from 'node:fs';` +
    `for (const f of fs.readFileSync(0,'utf8').split('\\n').filter(Boolean)) console.log(f + '\\t' + canon(f))`],
  corpus.join('\n'), env).split('\n').filter(Boolean).map((l) => l.split('\t'))
  const moved = canonOut.filter(([f, c]) => f !== c)
  const ids = moved.flatMap(([f, c]) => [f, c])
  const keyOf = new Map(sh('node', [lint, '--normalize-friction-keys'], ids.join('\n'), env)
    .split('\n').filter(Boolean).map((l) => l.split('\t')))
  const split = moved.filter(([f, c]) => keyOf.get(f) !== keyOf.get(c))
  return { corpus: corpus.length, moved: moved.length, split, keyOf }
}

const base = measure(path.join(ROOT, 'tools/policy/policy_lint.mjs'))
for (const [f, c] of base.split.slice(0, 5)) console.log(`split ${f} -> ${base.keyOf.get(f)} | ${c} -> ${base.keyOf.get(c)}`)
console.log(`RESULT corpus_files=${base.corpus} count`)
console.log(`RESULT moved_corpus_files=${base.moved} count`)
console.log(`RESULT split_keys=${base.split.length} count`)

if (perturb) {
  const tmp = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'hpo-fkey-')))
  const dst = path.join(tmp, 'tools', 'policy')
  fs.cpSync(path.join(ROOT, 'tools/policy'), dst, { recursive: true })
  for (const f of fs.readdirSync(dst)) {
    if (!f.endsWith('.mjs')) continue
    let s = fs.readFileSync(path.join(dst, f), 'utf8')
    s = s.replace("const ROOT = path.resolve(HERE, '..', '..')", "const ROOT = process.env.HPO_POLICY_ROOT ?? path.resolve(HERE, '..', '..')")
    fs.writeFileSync(path.join(dst, f), s)
  }
  const env = { HPO_POLICY_ROOT: ROOT }
  const plumb = measure(path.join(dst, 'policy_lint.mjs'), env)
  console.log(`RESULT split_keys_plumbing_only=${plumb.split.length} count`)
  const lintPath = path.join(dst, 'policy_lint.mjs')
  const src = fs.readFileSync(lintPath, 'utf8')
  const edited = src.replace("const bare = raw.replace(/^`+|`+$/g, '').replace(/#.*$/, '')",
    "const bare = canon(raw.replace(/^`+|`+$/g, '').replace(/#.*$/, ''))")
  if (edited === src) throw new Error('perturbation anchor not found')
  fs.writeFileSync(lintPath, edited)
  const pert = measure(lintPath, env)
  console.log(`RESULT split_keys_perturbed=${pert.split.length} count`)
  fs.rmSync(tmp, { recursive: true, force: true })
}
console.log(`RESULT thread_factor=1.000`)
console.log(`RESULT load1=${os.loadavg()[0].toFixed(2)}`)
console.log('RESULT swapins=na')
