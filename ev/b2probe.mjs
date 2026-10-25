// Reviewer's own probe: spellings with a closer within 3 characters before `pr`, under each guard given.
import fs from 'node:fs'
const load = p => { const src = fs.readFileSync(p, 'utf8')
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const block = src.slice(from, src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
const cases = [['f.sh', 'echo (\n${GH:-gh} pr merge 9 --subject x\n'], ['f.sh', 'a=(\n$(command -v gh) pr merge 9 --subject x\n'],
  ['f.sh', 'G=${X:-\ngh} pr merge 9 --subject x\n'], ['f.md', 'Run it (with\n`gh`) pr merge 9 --subject x\n'],
  ['f.md', 'Run (see\nabove) `${GH} pr merge 9 --subject x`\n'], ['f.sh', 'x) ${GH:-gh} pr merge 9 --subject x ;;\n'],
  ['f.sh', 'x) $(command -v gh) pr merge 9 --subject x ;;\n'], ['f.py', 'x = (\n1); os.system(f"{GH} pr merge {n} --subject x")\n'],
  ['f.js', 'f([\n]); execSync(`${cfg.gh} pr merge ${n} --subject x`)\n'], ['f.md', '1) `${GH} pr merge 9 --subject x`\n']]
const gs = process.argv.slice(2).map(p => [p.split('/').pop(), load(p)])
for (const [f, t] of cases) console.log(gs.map(([n, sw]) => `${n}=${sw([f], () => t).bad.length ? 'refused' : 'MISS'}`).join(' '), f, JSON.stringify(t))
