// D13-s1 round 11 -- the window fetch shared by this seat's harnesses (not a harness itself).
// Reads, for every first-parent commit in <since>..<base>: /commits/<sha>/pulls; for every
// merged PR so enumerated (production enumerateMerges + resolvePrFromCommit): /pulls/<n>,
// /issues/<n>/comments and /pulls/<n>/reviews, EVERY page (per_page=100 until a short page).
// Cache: $D13S1_CACHE or <os.tmpdir()>/hpo-d13s1-<base12>-<since>.json; delete it to re-fetch.
// Auth: GITHUB_TOKEN (as policy_lint.mjs's ghGet).
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { enumerateMerges, resolvePrFromCommit } from '../../../../../../tools/policy/policy_lint.mjs'

export const SLUG = 'tvofi/heatpump_optimizer'

function get(pathname) {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || ''
  let raw
  try {
    raw = execFileSync('curl', ['-sS', '-w', '\n%{http_code}', '-K', '-', 'https://api.github.com' + pathname], {
      input: `header = "Authorization: Bearer ${token}"\nheader = "Accept: application/vnd.github+json"\nheader = "X-GitHub-Api-Version: 2022-11-28"\n`,
      encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
    })
  } catch (e) { return { ok: false, why: 'curl ' + String(e.message).slice(0, 80) } }
  const cut = raw.lastIndexOf('\n')
  const code = raw.slice(cut + 1).trim()
  if (code !== '200') return { ok: false, why: `HTTP ${code} ${pathname}` }
  try { return { ok: true, data: JSON.parse(raw.slice(0, cut)) } } catch { return { ok: false, why: 'json ' + pathname } }
}

function getAll(pathname, stats) {
  const out = []
  for (let page = 1; page <= 50; page++) {
    let r = get(`${pathname}?per_page=100&page=${page}`)
    if (!r.ok) r = get(`${pathname}?per_page=100&page=${page}`) // one retry
    if (!r.ok) { stats.api_failures.push(r.why); return null }
    out.push(...r.data)
    stats.pages[pathname] = page
    if (r.data.length < 100) return out
  }
  return out
}

export function git(args) { return execFileSync('git', args, { encoding: 'utf8' }) }

export function loadWindow(since, base) {
  const baseSha = git(['rev-parse', base]).trim()
  const file = process.env.D13S1_CACHE || path.join(os.tmpdir(), `hpo-d13s1-${baseSha.slice(0, 12)}-${since.replace(/[^\w.-]/g, '_')}.json`)
  if (fs.existsSync(file)) return { ...JSON.parse(fs.readFileSync(file, 'utf8')), cacheFile: file, fromCache: true }
  const commits = git(['log', '--first-parent', '--format=%H%x09%s', `${since}..${baseSha}`]).split('\n').filter(Boolean)
    .map((l) => { const i = l.indexOf('\t'); return { sha: l.slice(0, i), subject: l.slice(i + 1) } })
  const stats = { api_failures: [], pages: {}, gap: [], calls_commit_pulls: 0 }
  const map = new Map()
  for (const { sha, subject } of commits) {
    stats.calls_commit_pulls++
    let r = get(`/repos/${SLUG}/commits/${sha}/pulls`)
    if (!r.ok) r = get(`/repos/${SLUG}/commits/${sha}/pulls`)
    if (!r.ok) { stats.api_failures.push(r.why); continue }
    const res = resolvePrFromCommit(subject, Array.isArray(r.data) ? r.data : [])
    if (!res) continue
    if (res.source === 'subject-gap') stats.gap.push(sha)
    map.set(sha, res.pr)
  }
  const { prs } = enumerateMerges(commits, map)
  const fetched = {}
  for (const { pr } of prs) {
    const p = get(`/repos/${SLUG}/pulls/${pr}`)
    if (!p.ok) { stats.api_failures.push(p.why); continue }
    const comments = getAll(`/repos/${SLUG}/issues/${pr}/comments`, stats)
    const reviews = getAll(`/repos/${SLUG}/pulls/${pr}/reviews`, stats)
    if (!comments || !reviews) continue
    const slim = (c) => ({ body: c.body ?? '', created_at: c.created_at, submitted_at: c.submitted_at, user: c.user?.login ?? null, id: c.id })
    fetched[pr] = {
      title: p.data.title ?? '', body: p.data.body ?? '', author: p.data.user?.login ?? null,
      merged_at: p.data.merged_at, merge_commit_sha: p.data.merge_commit_sha,
      comments: comments.map(slim), reviews: reviews.map(slim),
    }
  }
  const out = { since, base: baseSha, commits, prs, stats, fetched, fetched_at: new Date().toISOString() }
  fs.writeFileSync(file, JSON.stringify(out))
  return { ...out, cacheFile: file, fromCache: false }
}
