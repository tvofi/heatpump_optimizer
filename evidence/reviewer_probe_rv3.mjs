// Reviewer's probe for surviving mutant RV3: node reviewer_probe_rv3.mjs <agreement.mjs>
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const block = src.slice(src.indexOf('// WHAT A MERGE CALL IS'), src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
for (const t of ['run([GH, "pr" , "merge", n, "-t", s])', 'run([GH, "pr",\n    "merge", n, "-t", s])', "execFileSync(GH, ['pr',  'merge', n, '--subject', s])"]) {
  const r = sw(['f'], () => t + '\n'); console.log(`calls=${r.calls.length} bad=${JSON.stringify(r.bad)}`, JSON.stringify(t)) }
