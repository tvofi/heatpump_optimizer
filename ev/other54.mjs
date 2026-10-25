// Reviewer's own wrapper (not the finder's, fixer's or RCA's): the RCA differential's planted corpus and
// load()/shape() verbatim, listing each line main refuses and <old> does not, with its status at <head>.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
const show = ref => execFileSync('git', ['show', `${ref}:tools/policy/agreement.mjs`], { encoding: 'utf8', maxBuffer: 1 << 26 })
const load = ref => { const src = show(ref)
  const h = src.indexOf('// WHAT A MERGE CALL IS'); const from = h < 0 ? src.indexOf('// What a merge call may not carry') : h
  const block = src.slice(from, src.indexOf("// WHICH LINE IS MAIN'S")).replace(/^function nonTemplateMerges[\s\S]*?\n}\n/m, '')
  return new Function(block + '\nreturn subjectWriters')() }
const SCANNED = new Set(['py', 'mjs', 'js', 'cjs', 'sh', 'md'])
const hit = (sw, f, t) => sw([f], () => t).bad.length > 0
const shape = l => { let d = 0; for (const c of l) { if ('([{'.includes(c)) d++; else if (')]}'.includes(c)) { if (d) d--; else return 'unmatched-closer-in-lead' } }
  return /^\s*(#|\/\/|\*|<!--)/.test(l) ? 'comment-line' : 'other' }
const [base, old, head] = process.argv.slice(2).map(load)
const files = execFileSync('git', ['ls-files', 'tools', '.claude/workflows'], { encoding: 'utf8' }).split('\n')
  .filter(f => SCANNED.has(f.slice(f.lastIndexOf('.') + 1)) && !f.startsWith('tools/audit/round') && !f.includes('fixture') && f !== 'tools/policy/agreement.mjs')
const cnt = {}
for (const f of files) fs.readFileSync(f, 'utf8').split('\n').forEach((l, i) => {
  if (!l.trim() || /\bpr\b.*\bmerge\b/.test(l)) return
  const t = l + ' gh pr merge 9 --subject x\n'
  if (hit(base, f, t) && !hit(old, f, t)) { const k = shape(l), hh = hit(head, f, t) ? 'head=refused' : 'head=MISSED'
    cnt[k + ' ' + hh] = (cnt[k + ' ' + hh] || 0) + 1
    if (k === 'other') console.log(`other ${f}:${i + 1} ${hh} ${JSON.stringify(l.trim().slice(0, 100))}`) } })
console.log('SUMMARY ' + JSON.stringify(cnt))
