// reviewer's own probe: loads subjectWriters from the given agreement.mjs, reads [label, text] pairs
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const from = src.indexOf('// WHAT A MERGE CALL IS'); const to = src.indexOf("// WHICH LINE IS MAIN'S")
const block = src.slice(from, to).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const P = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))
for (const [f, t] of P) console.log(JSON.stringify(sw([process.argv[4] || 'f'], () => t + '\n').bad).padEnd(10), f.padEnd(14), JSON.stringify(t))
