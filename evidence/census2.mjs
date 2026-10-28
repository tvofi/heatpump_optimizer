// Reviewer-built: per-line view. A refused body whose every matching line is not a footer/link = false positive.
import fs from 'node:fs'
const m = await import(process.argv[2])
const rows = fs.readFileSync(process.argv[3], 'utf8').trim().split('\n').map(JSON.parse)
let fpBodies = 0, passMention = 0, fn = []
for (const r of rows) {
  const c = m.attributionClasses(r.b)
  const lines = r.b.split(/\r\n|\n|\r/)
  // a "true" attribution line: whole line is the footer or a bare session link (optionally prefixed by label/punct)
  const real = lines.filter((l) => /^\W*(🤖\s*)?Generated (with|by) \[?Claude Code/i.test(l.trim()) || /claude\.ai\/code\/session_/i.test(l) || /^\s*(Co-Authored-By:\s*Claude|Claude-Session:)/i.test(l))
  if (c.length && !real.length) fpBodies++
  if (!c.length && /claude/i.test(r.b)) passMention++
  if (!c.length && /generated (with|by).{0,4}claude code|claude\.ai\/code\/session/i.test(r.b)) fn.push('#' + r.n + ' ' + lines.filter((l) => /generated (with|by).{0,4}claude code|claude\.ai\/code\/session/i.test(l)).map((s) => s.slice(0, 160)).join(' || '))
}
console.log(`RESULT bodies=${rows.length} refused_without_a_real_attribution_line=${fpBodies} passed_bodies_mentioning_claude=${passMention} passed_bodies_with_footer_words=${fn.length}`)
console.log(fn.join('\n'))
