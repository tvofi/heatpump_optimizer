import fs from 'node:fs'
import { execFileSync } from 'node:child_process'
const m = await import(process.cwd() + '/tools/policy/brief_lint.mjs')
const text = fs.readFileSync('dev/audit/README.md', 'utf8')
const refs = ['c398fc84','757e164','d5d8c4a','8542e51','291ae76','32f309f','613bff1b','audit-round2-evidence']
const lists = {}
for (const r of refs) { try { lists[r] = execFileSync('git',['ls-tree','-r','--name-only',r],{encoding:'utf8'}).split('\n') } catch { lists[r]=[] } }
const toks = m.playbookCitations(text)
let blind = 0, slash = 0
for (const t of toks) {
  if (!t.includes('/') || t.endsWith('/')) continue
  slash++
  const at = refs.filter((r) => lists[r].some((f) => f === t || f.endsWith('/' + t)))
  if (at.length) { blind++; console.log(`BLIND ${t} (present at ${at.join(',')})`) }
}
console.log(`RESULT playbook_file_citations=${slash} blind_to_rename=${blind}`)
