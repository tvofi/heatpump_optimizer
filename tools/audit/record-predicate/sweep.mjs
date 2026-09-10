#!/usr/bin/env node
// How much HONEST WORK would a candidate `record` predicate refuse?
//
// WHY THIS EXISTS (#752). `checkRecord` tested `#<pr>` against the whole record
// region, so any occurrence discharged the obligation -- a row, a citation, or a
// sentence inside another pull request's row saying it is NOT dispositioning
// that number. Narrowing it is easy; narrowing it without reddening honest work
// is the whole problem, and this repository has already refused a countermeasure
// on that ground (#679). So a candidate is MEASURED before it is written: over
// every first-parent head on `main` in a range, with each head's window rebuilt
// the way `.github/workflows/governance.yml` does, it reports every pull request
// the candidate refuses that the shipped predicate accepts.
//
// A refusal reported here is one of two things and the script cannot tell them
// apart: a real gap, or a legitimate disposition written in a shape the
// candidate does not recognise. READING THEM IS THE SEAT'S JOB. What the script
// guarantees is that the list is complete for the range it was given.
//
// `today` is in the table as the instrument's OWN null control: it is the
// shipped predicate measured by the same code, and a run in which it reports
// anything at all means the harness disagrees with `policy_lint` about what the
// region is, so no other row in that run can be believed.
//
//   tools/audit/record-predicate/sweep.mjs --range v6.3.16..origin/main
//   tools/audit/record-predicate/sweep.mjs --range <a..b> --verify
//   tools/audit/record-predicate/sweep.mjs --in-flight --since <tag>
//   tools/audit/record-predicate/sweep.mjs --self-test
//
// HISTORY IS NOT THE WHOLE FALSE-REFUSAL SURFACE. A range sweep says what the
// candidate would have refused; `--in-flight` says what it refuses NOW, for work
// that has not landed -- every open pull request, read at its own head with that
// pull request added to the window. It is deliberately NOT a merge simulation: a
// branch behind `main` is read as it stands, which over-reports rather than
// under-reports, and it moves no ref. Moving `refs/remotes/origin/main` to
// simulate a merge is what a scratch clone is for; a git worktree shares the
// repository's refs with every sibling worktree and must never be used for it.
//
// `--verify` re-enumerates the NEWEST window one commit at a time through
// `/commits/<sha>/pulls`, which is the enumerator `policy_lint --record` itself
// uses, and compares the two sets. The bulk listing is used for the sweep
// because a per-commit walk over hundreds of heads reaches the secondary rate
// limit, which is invisible in `gh api rate_limit` and answers a swallowed
// refusal as a real zero. Every API call is counted and `API_REFUSALS=` is
// printed on every run, beside every figure, for that reason.
import { execFileSync } from 'node:child_process'

const PLAN = 'docs/plan-2026-09-open-issues.md'
const HAND = 'docs/HANDOVER.md'
const SECTION = 'Delivery status'

// ---------------------------------------------------------------------------
// The candidates. Each answers, for one LINE of the region and one pull request
// number: may this line disposition that number?
//
// `cand` is what shipped. The other three are the alternatives it was chosen
// over, kept here because a later seat proposing one of them should see its
// number rather than re-derive the argument.
const A_PULL = /^\s*[-*]\s+\[#(\d+)\]\((?:[^()\s]*\/pull\/)(\d+)\)/
const A_ANY = /^\s*[-*]\s+\[#(\d+)\]\(/
const A_CELL = /^\s*\|\s*\**\s*\[?#(\d+)/
const anchorPull = (l) => { const m = A_PULL.exec(l); return m && m[1] === m[2] ? m[1] : null }
const anchorAny = (l) => { const m = A_ANY.exec(l); return m ? m[1] : null }
const anchorCell = (l) => { const m = A_CELL.exec(l); return m ? m[1] : null }

export const PREDICATES = {
  // the shipped `#N` anywhere test, and this harness's own null control
  today: () => true,
  // shipped from #752: a row anchored `- [#M](.../pull/M)` speaks for #M alone
  cand: (l, pr) => { const a = anchorPull(l); return !a || a === pr },
  // the same, with the anchor's link target unread
  'cand-any': (l, pr) => { const a = anchorAny(l); return !a || a === pr },
  // the anchor extended to table rows
  'cand-tables': (l, pr) => { const a = anchorPull(l) ?? anchorCell(l); return !a || a === pr },
  // the shape #752 floated: ONLY a row that leads with the number
  rowanchor: (l, pr) => new RegExp(`^\\s*[-*]\\s+\\[#${pr}\\]`).test(l),
}

// ---------------------------------------------------------------------------
// Pure over its inputs, so `--self-test` drives it with no repository and no
// network. Mirrors `policy_lint.mjs`'s `recordRegion`, INCLUDING the part that
// is easy to get wrong: the plan contributes the one section, the handover
// contributes all of itself, and a missing section is reported as its own fact
// rather than as an empty region -- an empty region reads as "every merge
// undispositioned", which is a true statement about the wrong thing.
export function recordRegion(planText, handoverText) {
  const out = []
  let inside = false
  for (const line of String(planText).split('\n')) {
    const h2 = /^##\s+(.*?)\s*$/.exec(line)
    if (h2) inside = h2[1] === SECTION
    else if (inside) out.push(line)
  }
  return { lines: [...out, ...String(handoverText ?? '').split('\n')], sectionFound: out.length > 0 }
}

// A pull request the candidate refuses and the shipped predicate accepts. A
// number no line mentions at all is NOT reported: `record` already refuses it,
// so it is not a change this candidate makes.
export function newlyRefused(lines, prs, predicate) {
  const out = []
  for (const pr of prs) {
    const re = new RegExp(`#${pr}(?![0-9])`)
    const hits = lines.filter((l) => re.test(l))
    if (!hits.length) continue
    if (!hits.some((l) => predicate(l, pr))) out.push(pr)
  }
  return out
}

// ---------------------------------------------------------------------------
let refusals = 0
const git = (...a) => execFileSync('git', a, { encoding: 'utf8', maxBuffer: 1 << 28 })
function gh(pathArg, jq) {
  try {
    return execFileSync('gh', ['api', pathArg, '--jq', jq], { encoding: 'utf8', maxBuffer: 1 << 28 })
  } catch {
    refusals += 1
    return null
  }
}
// stdio ignores stderr: a head that predates one of the two files is an ordinary
// outcome of sweeping history, and `git show`'s fatal on it is noise, not news.
const show = (rev, p) => {
  try { return execFileSync('git', ['show', `${rev}:${p}`], { encoding: 'utf8', maxBuffer: 1 << 28, stdio: ['pipe', 'pipe', 'ignore'] }) } catch { return null }
}

// The merge-commit SHA of every merged pull request, from the listing rather
// than one commit at a time. Paged until a page comes back empty; a page the
// API refused is counted and does not end the walk, because ending on a refusal
// would silently truncate the map and every window built from it.
function shaToPr(slug) {
  const map = new Map()
  for (let page = 1; page <= 12; page++) {
    const out = gh(`repos/${slug}/pulls?state=closed&base=main&per_page=100&page=${page}&sort=updated&direction=desc`,
      '.[] | select(.merged_at != null) | [.number, .merge_commit_sha] | @tsv')
    if (out === null) continue
    const rows = out.trim().split('\n').filter(Boolean)
    if (!rows.length) break
    for (const r of rows) { const [pr, sha] = r.split('\t'); if (sha) map.set(sha, pr) }
  }
  return map
}

function sweep(range, map) {
  const heads = git('log', '--first-parent', '--format=%H', range).trim().split('\n').filter(Boolean)
  const newly = {}
  for (const k of Object.keys(PREDICATES)) newly[k] = {}
  let noRegion = 0, unmapped = 0, windows = 0, observations = 0
  for (const H of heads) {
    const since = git('describe', '--tags', '--abbrev=0', '--match', 'v*', H).trim()
    const commits = git('log', '--first-parent', '--format=%H', `${since}..${H}`).trim().split('\n').filter(Boolean)
    const { lines, sectionFound } = recordRegion(show(H, PLAN) ?? '', show(H, HAND) ?? '')
    if (!sectionFound) { noRegion++; continue }
    windows++
    const prs = []
    for (const sha of commits) {
      const pr = map.get(sha)
      if (!pr) { unmapped++; continue }
      if (!prs.includes(pr)) prs.push(pr)
    }
    observations += prs.length
    for (const [name, p] of Object.entries(PREDICATES)) {
      for (const pr of newlyRefused(lines, prs, p)) (newly[name][pr] ??= []).push(H.slice(0, 7))
    }
  }
  return { heads: heads.length, windows, noRegion, unmapped, observations, newly }
}

// `--verify`: the bulk map against the per-commit enumerator `--record` uses.
function verifyNewest(range, map, slug) {
  const H = git('log', '--first-parent', '--format=%H', range).trim().split('\n')[0]
  const since = git('describe', '--tags', '--abbrev=0', '--match', 'v*', H).trim()
  const commits = git('log', '--first-parent', '--format=%H', `${since}..${H}`).trim().split('\n').filter(Boolean)
  const fromMap = new Set(), fromApi = new Set()
  for (const sha of commits) {
    if (map.has(sha)) fromMap.add(map.get(sha))
    const out = gh(`repos/${slug}/commits/${sha}/pulls`, '.[0].number')
    const n = out === null ? '' : out.trim()
    if (n) fromApi.add(n)
  }
  const only = (a, b) => [...a].filter((x) => !b.has(x))
  return { window: `${since}..${H.slice(0, 7)}`, map: fromMap.size, api: fromApi.size,
    onlyMap: only(fromMap, fromApi), onlyApi: only(fromApi, fromMap) }
}

// --in-flight. The two disposition files are read over the API at each open pull
// request's head, so nothing is fetched into the caller's repository and no ref
// moves. A refusal on any call is counted and that pull request is reported as
// unread rather than as clean -- an unread file is not evidence of anything.
function inFlight(slug, since) {
  const listing = gh(`repos/${slug}/pulls?state=open&per_page=100`, '.[] | [.number, .head.sha] | @tsv')
  if (listing === null) return null
  const openPrs = listing.trim().split('\n').filter(Boolean).map((l) => l.split('\t'))
  const windowPrs = []
  for (const line of git('log', '--first-parent', '--format=%s', `${since}..${mainRef()}`).trim().split('\n')) {
    const m = /\(#(\d+)\)\s*$/.exec(line)
    if (m && !windowPrs.includes(m[1])) windowPrs.push(m[1])
  }
  const rows = []
  for (const [pr, sha] of openPrs) {
    const plan = contents(slug, PLAN, sha)
    const hand = contents(slug, HAND, sha)
    if (plan === null || hand === null) { rows.push({ pr, unread: true }); continue }
    const { lines, sectionFound } = recordRegion(plan, hand)
    if (!sectionFound) { rows.push({ pr, unread: true }); continue }
    const prs = windowPrs.includes(pr) ? windowPrs : [...windowPrs, pr]
    rows.push({ pr,
      shipped: newlyRefusedAbsolute(lines, prs, PREDICATES.today),
      candidate: newlyRefusedAbsolute(lines, prs, PREDICATES.cand) })
  }
  return rows
}

// The ABSOLUTE answer `--record` gives -- every pull request the predicate finds
// no disposition for -- as opposed to `newlyRefused`, which is the difference
// against the shipped predicate.
export function newlyRefusedAbsolute(lines, prs, predicate) {
  return prs.filter((pr) => {
    const re = new RegExp(`#${pr}(?![0-9])`)
    return !lines.some((l) => re.test(l) && predicate(l, pr))
  })
}

function mainRef() {
  try { git('rev-parse', '--verify', '--quiet', 'origin/main'); return 'origin/main' } catch { return 'HEAD' }
}

function contents(slug, p, ref) {
  const b64 = gh(`repos/${slug}/contents/${p}?ref=${ref}`, '.content')
  if (b64 === null) return null
  try { return Buffer.from(b64.replace(/\s+/g, ''), 'base64').toString('utf8') } catch { return null }
}

function selfTest() {
  const fails = []
  const eq = (what, got, want) => { if (JSON.stringify(got) !== JSON.stringify(want)) fails.push(`${what}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`) }
  // The live #741 shape: the only occurrence is prose inside another row.
  const live = recordRegion(`## ${SECTION}\n- [#748](x/pull/748) 2 without (#746 and #741). This dispositions #746. #741 stays #745's.\n`, '').lines
  eq('cand refuses the mention-only number', newlyRefused(live, ['741'], PREDICATES.cand), ['741'])
  // THE COST, asserted rather than left to be discovered. `cand` cannot tell
  // "This dispositions #746" from "#741 stays #745's": both are prose inside
  // #748's row, and it refuses both. Over the measured range that cost nothing,
  // because every pull request dispositioned inside another's row also had a row
  // of its own -- run the sweep to see whether that still holds. A seat that
  // dispositions a merge ONLY from inside somebody else's row is refused, and
  // the remedy is the row the rule asks for anyway.
  eq('and refuses one dispositioned ONLY from inside that row -- the stated cost', newlyRefused(live, ['746'], PREDICATES.cand), ['746'])
  eq('cand accepts the row it is anchored to', newlyRefused(live, ['748'], PREDICATES.cand), [])
  eq('today refuses nothing here', newlyRefused(live, ['741', '746', '748'], PREDICATES.today), [])
  // The three shapes a plainer candidate refuses, which is why it was rejected.
  const cell = recordRegion(`## ${SECTION}\n| linter | landed as #9001 |\n`, '').lines
  eq('cand accepts a table cell', newlyRefused(cell, ['9001'], PREDICATES.cand), [])
  eq('rowanchor refuses a table cell', newlyRefused(cell, ['9001'], PREDICATES.rowanchor), ['9001'])
  const issueRow = recordRegion(`## ${SECTION}\n| **#9002** the probe | **CLOSED by [#9003](x/pull/9003)** |\n`, '').lines
  eq('cand accepts a row anchored to an issue', newlyRefused(issueRow, ['9003'], PREDICATES.cand), [])
  eq('cand-tables refuses it', newlyRefused(issueRow, ['9003'], PREDICATES['cand-tables']), ['9003'])
  const hand = recordRegion('## other\n', '- **a seam move was sequenced (#9004)** (owner)\n').lines
  eq('cand accepts the handover prose bullet', newlyRefused(hand, ['9004'], PREDICATES.cand), [])
  eq('rowanchor refuses it', newlyRefused(hand, ['9004'], PREDICATES.rowanchor), ['9004'])
  // A number nothing mentions is not this candidate's doing, in either direction.
  eq('an unmentioned number is not reported as newly refused', newlyRefused(live, ['9999'], PREDICATES.cand), ['9999'].slice(1))
  // ... and the ABSOLUTE form does report it, which is the difference between
  // the two and the reason both exist. A run where they agree on an unmentioned
  // number means one of them is not the function it is named for.
  eq('the absolute form reports an unmentioned number', newlyRefusedAbsolute(live, ['9999'], PREDICATES.cand), ['9999'])
  // No section, no region -- reported as absence rather than as an empty region.
  eq('a plan with no such heading reports the absence', recordRegion('# plan\nnothing\n', '').sectionFound, false)
  eq('and the handover still contributes when the plan section is missing', newlyRefused(hand, ['9004'], PREDICATES.today), [])
  for (const f of fails) console.log(`FAIL ${f}`)
  console.log(`\nSWEEP SELF-TEST: ${fails.length} failure(s) over 14 assertion(s)`)
  return fails.length ? 1 : 0
}

function main(argv) {
  if (argv.includes('--self-test')) return selfTest()
  const range = argv[argv.indexOf('--range') + 1]
  const since = argv[argv.indexOf('--since') + 1]
  const wantFlight = argv.includes('--in-flight')
  if (!wantFlight && (!argv.includes('--range') || !range || range.startsWith('--'))) {
    console.log('usage: sweep.mjs --range <since>..<ref> [--verify] | --in-flight --since <tag> | --self-test')
    return 2
  }
  const remote = git('remote', 'get-url', 'origin').trim()
  const slug = (remote.match(/github\.com[:/](.+?)(?:\.git)?$/) ?? [])[1]
  if (!slug) { console.log('no github remote on origin; the enumerator needs one'); return 2 }
  if (wantFlight) {
    if (!since || since.startsWith('--')) { console.log('--in-flight needs --since <tag>'); return 2 }
    const rows = inFlight(slug, since)
    if (!rows) { console.log(`the open-pull-request listing was refused; API_REFUSALS=${refusals}`); return 1 }
    console.log(`open pull requests read at their own head, window ${since}..${mainRef()} plus the pull request itself`)
    for (const r of rows) {
      if (r.unread) { console.log(`#${r.pr.padEnd(5)} UNREAD -- a disposition file could not be read at this head`); continue }
      console.log(`#${r.pr.padEnd(5)} shipped_reports=[${r.shipped.map((x) => '#' + x).join(' ')}]  candidate_reports=[${r.candidate.map((x) => '#' + x).join(' ')}]`)
    }
    console.log(`API_REFUSALS=${refusals}`)
    return 0
  }
  const map = shaToPr(slug)
  const r = sweep(range, map)
  console.log(`range=${range} heads=${r.heads} windows_measured=${r.windows} heads_with_no_region=${r.noRegion} unmapped_first_parent_commits=${r.unmapped} pr_window_observations=${r.observations}`)
  for (const name of Object.keys(PREDICATES)) {
    const b = r.newly[name]
    const prs = Object.keys(b).sort((a, c) => a - c)
    const obs = Object.values(b).reduce((s, v) => s + v.length, 0)
    console.log(`${name.padEnd(12)} newly_refused_prs=${String(prs.length).padStart(3)} pr_window_observations_refused=${String(obs).padStart(4)}  ${prs.map((p) => '#' + p).join(' ')}`)
  }
  if (argv.includes('--verify')) {
    const v = verifyNewest(range, map, slug)
    console.log(`VERIFY ${v.window}: bulk_listing=${v.map} per_commit_api=${v.api} only_in_listing=[${v.onlyMap.join(' ')}] only_in_api=[${v.onlyApi.join(' ')}]`)
  }
  console.log(`API_REFUSALS=${refusals}`)
  return 0
}

if (process.argv[1] && process.argv[1].endsWith('sweep.mjs')) process.exit(main(process.argv.slice(2)))
