// reviewer's follow-up probes on the four head misses: node probe2.mjs <agreement.mjs>
import fs from 'node:fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
const block = src.slice(src.indexOf('// WHAT A MERGE CALL IS'), src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
const sw = new Function(block + '\nreturn subjectWriters')()
const P = [
  ['sh case arm, one line', 'sh', 'case $x in\n  a) gh pr merge "$n" --subject "$s" ;;\nesac'],
  ['sh case arm, one line, .md', 'md', 'case $x in\n  a) gh pr merge "$n" --subject "$s" ;;\nesac'],
  ['sh case arm, (a) form control', 'sh', 'case $x in\n  (a) gh pr merge "$n" --subject "$s" ;;\nesac'],
  ['sh stray closer then call', 'sh', 'x) gh pr merge 9 -t s'],
  ['py blank line inside argv before pr', 'py', 'run([\n    "gh",\n\n    "pr", "merge", n,\n    "--subject", s])'],
  ['js blank line inside argv before pr', 'mjs', "execFileSync('gh', [\n\n  'pr', 'merge', n,\n  '--subject', s])"],
  ['py blank line, control: flag in sibling', 'py', 'run([\n    "gh",\n\n    "pr", "merge", n])\nx = ["--subject", s]'],
  ['js block comment with closer after merge', 'mjs', "execFileSync('gh', ['pr', 'merge', n, /* ) */ '--subject', s])"],
  ['js block comment no closer after merge (control)', 'mjs', "execFileSync('gh', ['pr', 'merge', n, /* x */ '--subject', s])"],
  ['js regex closer', 'mjs', "execFileSync('gh', ['pr', 'merge', String(n).replace(/\\)/g, ''), '--subject', s])"],
]
for (const [n, x, t] of P) console.log(`${sw(['f.' + x], () => t).bad.length ? 'refused' : 'PASSES '} ${x} ${n}`)
