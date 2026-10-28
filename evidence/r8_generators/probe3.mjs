// Reviewer's own generator, part 3: a Markdown parenthetical that opens on one
// wrapped line and closes on the next, before the program.
import fs from 'node:fs'
const load = p => { const src = fs.readFileSync(p, 'utf8')
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const to = src.indexOf("// WHICH LINE IS MAIN'S")
  const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
const cases = [
  ['f.md', 'Merge it by hand (the train is\ndown) with `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand (the train is\n\ndown) with `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand (the train is down)\nwith `gh pr merge 9 --subject x`.'],
  ['f.md', 'Merge it by hand, the train is\ndown, with `gh pr merge 9 --subject x`.'],
]
for (const p of process.argv.slice(2)) { const sw = load(p); console.log('== guard', p.split('/').pop())
  for (const [f, t] of cases) console.log(sw([f], () => t).bad.length ? 'refused' : 'MISS   ', f, JSON.stringify(t)) }
