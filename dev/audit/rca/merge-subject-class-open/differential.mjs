// R10-RCA-MERGE-SUBJECT-CLASS-OPEN's evidence (dev/audit/rca/R10-RCA-MERGE-SUBJECT-CLASS-OPEN.md).
// The root-cause seat's own instrument: not the finder's harness, not a fixer's or a reviewer's.
// It reads the merge-subject guard's `subjectWriters` out of tools/policy/agreement.mjs at each
// <ref> (the same block cut the PR's argv-seam harness uses) and compares refused sets.
//
//   node dev/audit/rca/merge-subject-class-open/differential.mjs named   <base ref> <head ref>...
//   node dev/audit/rca/merge-subject-class-open/differential.mjs corpus  <base ref> <head ref>...
//   node dev/audit/rca/merge-subject-class-open/differential.mjs planted <base ref> <head ref>...
//
// named:   each block's own example spelling (verdicts 1 to 8 of #2697) under <base> and its round's
//          head; prints REGRESSION (base refuses, head does not) or OPEN-AT-BOTH. Heads are fixed in
//          the table; the refs given after <base> are ignored.
// corpus:  a generated corpus: 16 leads that close a bracket they did not open on the line, 8
//          control leads, 3 subject writers, 4 file kinds, plus 8 over-fire nulls; prints each
//          family's refused count and main_not_head (refused under <base>, not under <head>).
// planted: a corpus generated from the tree, not a hand list: every non-blank line of every file
//          the guard scans (git ls-files at the checkout) becomes a lead with a subject writer
//          planted after it on the same line; prints main_not_head and buckets it by the lead's
//          shape. Run with <base> as a head too for the null control (main_not_head=0).
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
const show = ref => execFileSync('git', ['show', `${ref}:tools/policy/agreement.mjs`], { encoding: 'utf8', maxBuffer: 1 << 26 })
const load = ref => { const src = show(ref)
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const block = src.slice(from, src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
// The guard's scanned kinds, as a set rather than its pattern (one grammar, one owner: agreement.mjs).
const SCANNED = new Set(['py', 'mjs', 'js', 'cjs', 'sh', 'md'])
const hit = (sw, f, t) => sw([f], () => t).bad.length > 0
const [mode, baseRef, ...heads] = process.argv.slice(2)
if (!['named', 'corpus', 'planted'].includes(mode) || !baseRef) { console.error('usage: differential.mjs named|corpus|planted <base ref> [<head ref>...]'); process.exit(2) }
const base = load(baseRef)
if (mode === 'named') {
  const R = [
    [1, 'b4dd11917', 'f.sh', '(cd repo) && gh pr merge 9 --merge --subject "Merge pull request #9 (x)"\n', 'M13 shape (mutant only)'],
    [2, '96ad30e87', 'f.sh', 'gh pr \\\n  merge 9 --merge --subject "Merge pull request #9 (x)"\n', 'continuation in the name'],
    [3, '455d7c200', 'f.sh', 'gh pr "merge" 9 --subject x\n', 'quoted word'],
    [3, '455d7c200', 'f.sh', 'gh pr -R o/r merge 9 --subject x\n', 'flag between words'],
    [3, '455d7c200', 'f.py', "run(['gh', 'pr', 'merge', n, '--subject', s])\n", 'single-quoted argv'],
    [4, '5d79db511', 'f.sh', 'gh pr --subject "x y" merge 9 --merge\n', 'multi-word value in a gap'],
    [4, '5d79db511', 'f.sh', '${GH:-gh} pr merge 1 --merge --subject x\n', '${VAR:-} program'],
    [4, '5d79db511', 'f.sh', '$(command -v gh) pr merge 1 --merge --subject x\n', '$(...) program'],
    [5, 'd0d35231c', 'f.py', 'os.system(f"{GH} pr merge {n} --subject x")\n', 'f-string program'],
    [5, 'd0d35231c', 'f.py', 'os.system("%s pr merge %s --subject x" % (GH, n))\n', '% program'],
    [5, 'd0d35231c', 'f.js', 'execSync(`${cfg.gh} pr merge ${n} --subject x`)\n', '${cfg.gh} program'],
    [6, '683dd52cb', 'f.py', 'subprocess.run(["gh",\n "pr", "merge", str(n), "--squash",\n "--subject", s], check=True)\n', 'wrapped argv'],
    [7, 'e73424f24', 'f.sh', 'case $m in\n  never) gh pr merge "$n" --squash --subject "..." ;;\nesac\n', 'case arm, no paren'],
    [8, '4aad9c117', 'f.md', 'Merge it by hand (the train is\ndown) with `gh pr merge 9 --subject x`.\n', 'Markdown parenthetical'],
    [8, '4aad9c117', 'f.md', '1) gh pr merge 9 --subject x\n', 'list item 1)'],
  ]
  for (const [r, h, f, t, label] of R) { const b = hit(base, f, t), hh = hit(load(h), f, t)
    console.log(`r${r} ${h} ${label.padEnd(26)} base=${b ? 'refused' : 'missed '} head=${hh ? 'refused' : 'missed '} ${b && !hh ? 'REGRESSION' : !b && !hh ? 'OPEN-AT-BOTH' : ''}`) }
  process.exit(0)
}
const rows = []
if (mode === 'corpus') {
  const subs = ['gh pr merge 9 --subject x', 'gh pr merge "$n" --squash --subject "x"', 'gh pr merge 9 -t s']
  const closers = ['never) ', '  never) ', '\tnever) ', 'a|b) ', '*) ', '[0-9]*) ', '1) ', 'a) ', '- step 2) ', ':) ',
    'down) with `', '); ', ']; ', '}); ', 'done) ', 'x) ']
  const controls = ['', '    ', '(never) ', '( cd x ) && ', 'r=$(cat f) && ', 'a=(1 2); ', 'echo ")"; ', 'if (( n > 0 )); then ']
  const prev = { sh: 'case $m in\n', md: 'Merge it by hand (the train is\n', py: 'x = (\n', js: 'f([\n' }
  for (const [fam, leads] of [['lead-closer', closers], ['control', controls]])
    for (const l of leads) for (const s of subs) for (const ext of Object.keys(prev)) rows.push({ fam, f: 'f.' + ext, t: prev[ext] + l + s + '\n' })
  for (const t of ['never) gh pr view 9 --json title ;;', 'never) gh pr merge 9 --squash ;;', 'down) with `gh pr merge 9`.', '1) gh pr merge 9 --merge'])
    for (const ext of ['sh', 'md']) rows.push({ fam: 'null', f: 'f.' + ext, t: prev[ext] + t + '\n' })
} else {
  const files = execFileSync('git', ['ls-files', 'tools', '.claude/workflows'], { encoding: 'utf8' }).split('\n')
    .filter(f => SCANNED.has(f.slice(f.lastIndexOf('.') + 1)) && !f.startsWith('tools/audit/round') && !f.includes('fixture') && f !== 'tools/policy/agreement.mjs')
  for (const f of files) for (const l of fs.readFileSync(f, 'utf8').split('\n'))
    if (l.trim() && !/\bpr\b.*\bmerge\b/.test(l)) rows.push({ fam: 'planted', f, lead: l, t: l + ' gh pr merge 9 --subject x\n' })
  console.log(`files=${files.length}`)
}
const fams = [...new Set(rows.map(r => r.fam))]
const B = rows.map(r => hit(base, r.f, r.t)); const count = (v, fam) => rows.filter((r, i) => r.fam === fam && v[i]).length
console.log(`corpus ${fams.map(f => `${f}=${rows.filter(r => r.fam === f).length}`).join(' ')}`)
console.log(`base ${baseRef}: ${fams.map(f => `${f}=${count(B, f)}`).join(' ')}`)
// A lead's shape, by a quote-blind bracket count: a closer with no opener before it on the line.
const shape = l => { let d = 0; for (const c of l) { if ('([{'.includes(c)) d++; else if (')]}'.includes(c)) { if (d) d--; else return 'unmatched-closer-in-lead' } }
  return /^\s*(#|\/\/|\*|<!--)/.test(l) ? 'comment-line' : 'other' }
for (const h of heads) { const sw = load(h); const H = rows.map(r => hit(sw, r.f, r.t)); const bk = {}; let mnh = 0
  rows.forEach((r, i) => { if (r.fam !== 'null' && B[i] && !H[i]) { mnh++; if (r.lead !== undefined) { const k = shape(r.lead); bk[k] = (bk[k] || 0) + 1 } } })
  console.log(`head ${h}: ${fams.map(f => `${f}=${count(H, f)}`).join(' ')} main_not_head=${mnh}${mode === 'planted' ? ' ' + JSON.stringify(bk) : ''}`) }
