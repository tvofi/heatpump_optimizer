#!/usr/bin/env node
// PROTOTYPE (out of tree): the driver's own denominator refusal for one finder
// report, run by a cloud box seat that dispatches finders as Agent subagents
// rather than through the workflow runtime. The predicate is NOT re-typed: the
// DISPATCH:BEGIN..END block of audit-find.js is evaluated on its own, as
// tools/policy/check-wave-script.mjs evaluates it.
//
//   node check_report.mjs --repo <checkout> --round 11 --seat D1-s2 --report <REPORT.json>
//
// Prints `ok <seat>` and exits 0, or one `gap <seat>: ...` line per gap and
// exits 1 (the driver's "report refused, re-running the seat"); exit 2 on a
// usage error or an unreadable report (a seat not reported, never a pass).
import fs from 'node:fs'
import path from 'node:path'

const a = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => (v.startsWith('--') ? [...acc, [v.slice(2), arr[i + 1] ?? '']] : acc), []))
for (const k of ['repo', 'round', 'seat', 'report']) if (!a[k]) { console.error(`refuse: --${k} is required`); process.exit(2) }
const repo = path.resolve(a.repo)
const src = fs.readFileSync(path.join(repo, '.claude/workflows/audit-find.js'), 'utf8')
const m = /\/\/ DISPATCH:BEGIN[^\n]*\n([\s\S]*?)\/\/ DISPATCH:END/.exec(src)
if (!m) { console.error('refuse: audit-find.js has no DISPATCH block'); process.exit(2) }
const api = new Function(`${m[1]}\nreturn { seatsFromScopes, seatCarry, denominatorGaps }`)()
const scopes = JSON.parse(fs.readFileSync(path.join(repo, 'dev/audit/config/scopes.json'), 'utf8'))
const rotation = JSON.parse(fs.readFileSync(path.join(repo, 'dev/audit/config/rotation.json'), 'utf8'))
const seatId = a.seat.replace(/-twin$/, '')
const dim = seatId.split('-')[0]
const seat = api.seatsFromScopes(scopes, dim).find((s) => s.id === seatId)
if (!seat) { console.error(`refuse: ${seatId} is no seat of scopes.json`); process.exit(2) }
let rep
try {
  rep = JSON.parse(fs.readFileSync(a.report, 'utf8'))
  if (rep && rep.reports) rep = rep.reports[seatId]
  if (!rep || typeof rep !== 'object') throw new Error('no report object')
} catch (e) { console.error(`unread ${a.seat}: ${e.message}`); process.exit(2) }
const gaps = api.denominatorGaps(seat, rep, api.seatCarry(rotation, Number(a.round), seat))
if (!gaps.length) { console.log(`ok ${a.seat}`); process.exit(0) }
for (const g of gaps) console.log(`gap ${a.seat}: ${g}`)
process.exit(1)
