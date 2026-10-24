// R10-MERGE-SUBJECT-HARDEN (#2697): the tree census for the merge-call class.
//
//   node dev/audit/harnesses/r10_merge_subject_census.mjs [<old agreement.mjs>]   (from the repository root)
//
// Over the files the merge-subject guard scans (tools/ and .claude/workflows/,
// .py .mjs .js .cjs .sh .md, less tools/audit/round*, fixtures and the guard
// itself), prints:
//  - with <old agreement.mjs>: each line whose MERGE_CALL match count differs
//    between that guard and the working tree's, and both totals;
//  - every line holding the words `pr` and `merge` (any quoting) that no
//    MERGE_CALL match covers, and how many of how many. Each such line is read
//    by hand: a merge call among them is a spelling the guard misses.
import fs from 'node:fs'
import { execFileSync } from 'node:child_process'
const guard = (p) => {
  const src = fs.readFileSync(p, 'utf8')
  const from = src.indexOf('// WHAT A MERGE CALL IS') >= 0 ? src.indexOf('// WHAT A MERGE CALL IS') : src.indexOf('// What a merge call may not carry')
  let block = src.slice(from, src.indexOf("// WHICH LINE IS MAIN'S"))
  // nonTemplateMerges reads constants defined later in the file; cut it out, by position.
  const nt = block.indexOf('function nonTemplateMerges'); if (nt >= 0) block = block.slice(0, nt) + block.slice(block.indexOf('\n}\n', nt) + 3)
  return new Function(block + '\nreturn MERGE_CALL')()
}
const files = execFileSync('git', ['ls-files', 'tools', '.claude/workflows'], { encoding: 'utf8' }).split('\n')
  // The guard's own file filter (mergeSubjectGuard), spelled with string tests so
  // this census registers no second copy of its grammar.
  .filter((f) => ['.py', '.mjs', '.js', '.cjs', '.sh', '.md'].some((x) => f.endsWith(x))
    && !(f.startsWith('tools/audit/round') && '0123456789'.includes(f['tools/audit/round'.length] ?? '')) && !f.includes('/fixtures/') && f !== 'tools/policy/agreement.mjs')
const NEW = guard('tools/policy/agreement.mjs'); const OLD = process.argv[2] ? guard(process.argv[2]) : null
const at = (re, text) => { const m = {}; for (const x of text.matchAll(new RegExp(re.source, 'g'))) { const l = text.slice(0, x.index).split('\n').length; m[l] = (m[l] || 0) + 1 } return m }
let to = 0, tn = 0, unc = 0, both = 0
for (const f of files) {
  const text = fs.readFileSync(f, 'utf8'); const L = text.split('\n')
  if (OLD) {
    const a = at(OLD, text), b = at(NEW, text)
    for (const l of new Set([...Object.keys(a), ...Object.keys(b)])) { to += a[l] || 0; tn += b[l] || 0; if ((a[l] || 0) !== (b[l] || 0)) console.log(`DIFF ${f}:${l} old=${a[l] || 0} new=${b[l] || 0} | ${L[l - 1].trim().slice(0, 140)}`) }
  }
  const covered = new Set()
  for (const m of text.matchAll(new RegExp(NEW.source, 'g'))) { const a = text.slice(0, m.index).split('\n').length; for (let i = a; i < a + m[0].split('\n').length; i++) covered.add(i) }
  L.forEach((l, i) => { if (/(?<![\w-])pr(?![\w-])/.test(l) && /(?<![\w-])merge(?![\w-])/.test(l)) { both++; if (!covered.has(i + 1)) { unc++; console.log(`UNCOVERED ${f}:${i + 1}: ${l.trim().slice(0, 150)}`) } } })
}
if (OLD) console.log(`TOTAL old=${to} new=${tn} over ${files.length} file(s)`)
console.log(`UNCOVERED ${unc} of ${both} line(s) holding both words, over ${files.length} file(s)`)
