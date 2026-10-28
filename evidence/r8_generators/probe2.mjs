// Reviewer's own generator, part 2: an unmatched closer before the program in
// non-case-arm contexts (Markdown numbered lists, JS/Python statement tails).
import fs from 'node:fs'
const load = p => { const src = fs.readFileSync(p, 'utf8')
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const to = src.indexOf("// WHICH LINE IS MAIN'S")
  const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
const cases = [
  ['f.md', '1) gh pr merge 9 --subject x'], ['f.md', 'a) run `gh pr merge 9 --subject x`'], ['f.md', '- step 2) `gh pr merge 9 -t x`'],
  ['f.md', ':) gh pr merge 9 --subject x'], ['f.md', '(see above) gh pr merge 9 --subject x'],
  ['f.mjs', 'foo(() => {\n  a()\n}); execSync("gh pr merge 9 --subject x")'], ['f.mjs', '}) ; execSync("gh pr merge 9 --subject x")'],
  ['f.py', 'x = [\n 1,\n]; os.system("gh pr merge 9 --subject x")'], ['f.py', 'x = (1\n); os.system("gh pr merge 9 -t x")'],
  ['f.sh', 'x=(\n a\n); gh pr merge 9 --subject x'], ['f.sh', 'echo "a)" ; gh pr merge 9 --subject x'], ['f.sh', "echo 'b)' ; gh pr merge 9 -t x"],
  ['f.sh', '# step 1) then\ngh pr merge 9 --subject x'],
]
for (const p of process.argv.slice(2)) { const sw = load(p); let k = 0
  console.log('== guard', p.split('/').pop())
  for (const [f, t] of cases) { const bad = sw([f], () => t).bad; if (bad.length) k++; console.log(bad.length ? 'refused' : 'MISS   ', f, JSON.stringify(t)) }
  console.log(`PROBE2 refused=${k} of ${cases.length}`) }
