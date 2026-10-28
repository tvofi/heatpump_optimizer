// Reviewer-built census: the head's exported attributionClasses over merged PR bodies.
import fs from 'node:fs'
const m = await import(process.argv[2])
const rows = fs.readFileSync(process.argv[3], 'utf8').trim().split('\n').map(JSON.parse)
let hit = 0; const cls = {}; const ex = []
for (const r of rows) { const c = m.attributionClasses(r.b); if (c.length) { hit++; for (const k of c) cls[k] = (cls[k]||0)+1
  const lines = r.b.split(/\r?\n/).filter((l) => /claude/i.test(l) && (/claude\.ai\/code\/session_|^[ \t]*Claude-Session|^[ \t]*Co-Authored-By|Generated (with|by)/i.test(l)))
  ex.push(`#${r.n} ${c.join(',')} :: ${lines.slice(0,3).map(s=>s.slice(0,140)).join(' || ')}`) } }
console.log(`RESULT merged_bodies=${rows.length} refused=${hit} ${JSON.stringify(cls)}`); console.log(ex.join('\n'))
