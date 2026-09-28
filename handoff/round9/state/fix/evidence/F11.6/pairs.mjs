import fs from 'node:fs'; import zlib from 'node:zlib'; import path from 'node:path'
import * as PL from './.claude/workflows/policy_lint.mjs'
const snap = JSON.parse(zlib.gunzipSync(fs.readFileSync('tools/audit/round9/D13/s1/window.json.gz')).toString())
const seen = new Set(), merges = []
for (const c of snap.commits) { if (!c.pulls?.length) continue; const pr = String(c.pulls[0].number); if (seen.has(pr)) continue; seen.add(pr); merges.push([pr, c.sha]) }
const VRE = PL.waveVerdictRe()
for (const [pr, msha] of merges) {
  const p = snap.prs[pr]; if (!p || p.comments == null || p.reviews == null) continue
  const w = [...p.comments.map(c=>({body:c.body,at:c.at})), ...p.reviews.map(c=>({body:c.body,at:c.at}))].sort((a,b)=>String(a.at??'').localeCompare(String(b.at??'')))
  let prev = null
  for (const c of w) { const m = VRE.exec(String(c.body ?? '').trim().split('\n')[0]); if (!m) continue
    const cur = { pass: Boolean(m[1]), head: (m[2] ?? m[4]).toLowerCase() }
    if (prev && prev.pass && cur.head !== prev.head) console.log(pr, prev.head, cur.head, cur.pass ? "merge" : "blocked", msha)
    prev = cur }
}
