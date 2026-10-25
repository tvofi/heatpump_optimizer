// Reviewer's own generator (not the finder's, not the fixer's): one-line and
// near-one-line merge writers whose lead (text before the program) holds a
// shell or language closer, plus over-fire nulls. Usage: node probe.mjs <agreement.mjs>...
import fs from 'node:fs'
const load = p => { const src = fs.readFileSync(p, 'utf8')
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const to = src.indexOf("// WHICH LINE IS MAIN'S")
  const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
const sub = ['gh pr merge "$n" --squash --subject "x"', 'gh pr merge 9 -t s', 'gh pr merge 9 --body b']
const leads = {
  'case arm': 'never) ', 'arm (a)': '(never) ', 'arm a|b': 'a|b) ', 'arm *': '*) ', 'arm glob [0-9]*': '[0-9]*) ',
  'subshell close then &&': '( cd x ) && ', '$(...) assign then &&': 'r=$(cat f) && ', 'test ]] &&': '[[ -n "$x" ]] && ',
  'brace group close': '{ true; } && ', 'array close ;': 'a=(1 2); ', 'done close': 'done; ', 'if (( ))': 'if (( n > 0 )); then ',
  'echo ")" ;': 'echo ")"; ', 'arith $(( ))': 'i=$((i+1)); ', 'esac ;': 'esac; ', 'fn() {': 'm() { ', 'fn() { one-liner close': 'f() { :; }; ',
  'none': '', 'indent': '    ',
}
const files = ['f.sh', 'f.md']
const nulls = { 'pr view after case arm': 'never) gh pr view 9 --json title ;;', 'merge no subject in arm': 'never) gh pr merge 9 --squash ;;',
  'later sibling flag': 'x) gh pr merge 9 --squash ;;\ny) gh pr edit 9 --title t ;;', 'prose': 'Run `gh pr merge` and never pass a subject.' }
for (const p of process.argv.slice(2)) {
  const sw = load(p); let miss = 0, n = 0, over = 0
  console.log('== guard', p.split('/').pop())
  for (const [ln, l] of Object.entries(leads)) for (const s of sub) for (const f of files) {
    for (const tail of [' ;;', '']) { n++
      const t = 'case $m in\n' + l + s + tail + '\nesac'
      const bad = sw([f], () => t).bad; if (!bad.length) { miss++; console.log('MISS', JSON.stringify(ln), f, JSON.stringify(s + tail)) } } }
  for (const [ln, t] of Object.entries(nulls)) for (const f of files) { const bad = sw([f], () => t).bad; if (bad.length) { over++; console.log('OVERFIRE', ln, f, JSON.stringify(bad)) } }
  console.log(`PROBE refused=${n - miss} of ${n}; null refused=${over} of ${Object.keys(nulls).length * files.length}`)
}
