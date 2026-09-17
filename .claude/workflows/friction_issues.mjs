#!/usr/bin/env node
// The filing half of `policy_lint --stats` (#959, option B).
//
// WHAT THIS IS. The stats histogram has always PRINTED what it would open and
// opened nothing -- its own line says so ("Not opened here: a seat measures and
// files, a report does not") -- and the audit's finding (#959) was that the
// report reached nobody: both informational lanes ran under `|| true`, no
// contract obliged a seat to read either, and a class sat over its own
// threshold in silence. The owner's option B (#201 comment 5670207248, item 4)
// makes the cron ACT on exactly one thing: when the histogram prints a
// would-open verdict, the lane files `[policy] recurring friction: <key>`
// itself. The grant is `issues: write` on the one `record` job, owner-approved;
// the informational lanes (`--sunset`, and the histogram's own printing) keep
// their `|| true` and stay informational. This script is the deliberate path,
// and it is the only step in that job that runs unsuppressed.
//
// THE TRIGGER TEXT IS THE HISTOGRAM'S OWN LINE, not a re-derivation. This
// script does not recount friction and does not classify verdicts: it parses
// the `would open "[policy] recurring friction: <key>"` lines out of a stats
// output the job has already produced. The classifier -- the verdict grammar
// read from web-fix-wave.js, the threshold of three, and the exclusion that
// withholds the passing verdict because a merge is rework nowhere -- stays in
// exactly one place, policy_lint.mjs, and this script cannot fire on a class
// that classifier excluded, because an excluded class prints `not opened:` and
// never `would open "`.
//
// IDEMPOTENCE IS THE WHOLE SAFETY ARGUMENT. A cron with `issues: write` and no
// memory would file one issue per beat per key, and a flaky API that made the
// search fail open would file one per retry. The control is per window and per
// key: search before creating, scoped to the exact title, and on a hit update
// the existing issue's BODY in place rather than filing again. The body is a
// pure function of the measurement (key, kind, count, threshold, window), so
// two runs of the same window with the same counts produce byte-identical
// bodies and the second run is a no-op -- no create, no edit, no comment. A
// moved measurement within the window (a count that grew) edits the body once;
// it never opens a second issue.
//
// FAIL CLOSED ON EVERY UNKNOWN. A search that errored, that printed prose, or
// that returned a shape this parser does not recognise is `unknown`, and
// `unknown` refuses: treating it as "no existing issue" is precisely the
// flaky-API double-file this exists to prevent. The same rule closes the
// no-data trap on the input side: a stats output whose fetch failed carries a
// zero that means "no data", not "no friction", and this script refuses it
// rather than filing nothing in silence. A missing `WOULD OPEN:` summary line
// means the file is not a histogram at all, and that refuses too.
//
//   node .claude/workflows/friction_issues.mjs --stats-file <path> --since <ref>
//   node .claude/workflows/friction_issues.mjs --stats-file <path> --since <ref> --dry-run
//   node .claude/workflows/friction_issues.mjs --self-test
//
// --dry-run performs the read-only half against the live repository (the
// search) and prints the decision and the exact body it would file, writing
// nothing. --self-test drives the decisions offline over fixture shapes,
// network-free, the same pattern as push.sh's and gh_comment.py's.
import fs from 'node:fs'
import { spawnSync } from 'node:child_process'

const FRICTION_PREFIX = '[policy] recurring friction: '
const STATS_TOOL = '.claude/workflows/policy_lint.mjs'

// --- the pure decisions ------------------------------------------------------
// Everything a run decides, decided here so the self-test can drive it without
// a network and the demonstrations can quote it without re-running the lane.

// Parse a `--stats` output into the entries its would-open verdicts name.
//
// REFUSED, not empty, when the output is not evidence: no `WOULD OPEN:`
// summary line means policy_lint did not complete a histogram (an unreadable
// verdict grammar exits before printing one); the fetch-failure marker means
// the API would not answer, and a zero over no data is the opposite claim of a
// zero over no friction -- the distinction the --record fetch guard exists to
// keep and this lane must not lose on its way to a write.
const WOULD_OPEN_RE =
  /would open "\[policy\] recurring friction: (.+?)" -- (.+?) at (\d+) in this window, threshold (\d+)\./
// The per-key census policy_lint prints beside the would-open lines: one
// tab-separated row per key, the key LAST because one key (the unlabelled
// bucket) carries spaces. The would-open lines alone name only the keys still
// AT or over the threshold, so a lane that also has to speak about the keys
// that are not -- the close path below -- reads this instead of recounting.
const CENSUS_RE = /^CENSUS\t([^\t]*)\t(\d+)\t(\d+)\t(.*)$/
const CENSUS_SUMMARY_RE = /^CENSUS: (\d+) key\(s\)$/m
// The threshold is READ, never typed here, for the same reason the classifier
// is not reimplemented: one number, in policy_lint.mjs, printed by the run this
// lane is acting on.
const THRESHOLD_RE = /^threshold: (\d+) or more of one key/m

export function parseHistogram(text) {
  const out = { ok: false, why: '', entries: [], census: new Map(), threshold: null }
  if (!/WOULD OPEN: \d+ issue\(s\)/.test(text)) {
    out.why = 'no WOULD OPEN summary line: this is not a completed stats histogram'
    return out
  }
  if (/could not fetch pull-request bodies and comments/.test(text)) {
    out.why = 'the histogram window could not be fetched: no data is not no friction, and a filing lane must not act on an empty measurement'
    return out
  }
  // Both refusals are the same argument as the one above, one step along: a
  // census that is absent and a census that is empty are opposite claims, and
  // the close path writes on the strength of a key being BELOW threshold --
  // which an absent census would assert about every key at once.
  if (!CENSUS_SUMMARY_RE.test(text)) {
    out.why = 'no CENSUS summary line: this histogram carries no per-key census, so no key can be shown to be below threshold rather than merely unmentioned'
    return out
  }
  const win = /^STATS: (\d+) merged pull request\(s\) in /m.exec(text)
  if (!win) {
    out.why = 'the histogram does not say how many pull requests its window holds, and a window whose size is unknown cannot be shown capable of reaching the threshold'
    return out
  }
  const th = THRESHOLD_RE.exec(text)
  if (!th) {
    out.why = 'the histogram does not print its own threshold, and this lane does not carry a second copy of it'
    return out
  }
  const entries = []
  const census = new Map()
  for (const line of String(text).split('\n')) {
    const m = line.match(WOULD_OPEN_RE)
    if (m) entries.push({ key: m[1], kind: m[2], count: Number(m[3]), threshold: Number(m[4]), line: line.trim() })
    const c = line.replace(/\r$/, '').match(CENSUS_RE)
    if (c) census.set(c[4], { kind: c[1], prs: Number(c[2]), entries: Number(c[3]) })
  }
  const declared = Number(CENSUS_SUMMARY_RE.exec(text)[1])
  if (census.size !== declared) {
    out.why = `the census summary declares ${declared} key(s) and ${census.size} row(s) parsed: a partial census is not a measurement of the keys it is missing`
    return out
  }
  out.ok = true
  out.entries = entries
  out.census = census
  out.threshold = Number(th[1])
  out.windowPrs = Number(win[1])
  return out
}

// --- the close path ----------------------------------------------------------
// The filer creates and edits and never closes, so an issue filed off a window
// that has since moved past it stays open with nothing saying so. This half
// re-measures every open `[policy] recurring friction:` issue on each beat and,
// where the key is below threshold in the CURRENT window, says so once, with
// the measurement. It does not close: CLAUDE.md's "fix it; if you cannot,
// verify it independently; only then file it" makes a disposition a seat's act,
// the issue owes one in the Delivery-status table, and a bot that closed its
// own issues would dispose of them by deleting the question. `issues: write` is
// already the grant the `record` job holds; a comment needs nothing wider.
//
// SILENCE WHERE IT CANNOT SPEAK HONESTLY. Three cases are skipped rather than
// commented on: a key still at or over threshold; a key the current run would
// open (the same thing, said from the other side); and -- the one that is not
// obvious -- a key at or over threshold that the classifier WITHHELD, which is
// the passing verdict and, while the grammar is binary, the whole verdict arm.
// Those issues are open and their keys are not below anything, so "below
// threshold in the current window" would be false about them.
// `normalize` maps an issue's OWN title key to the key the histogram would use
// today. It matters because an issue filed before the keying was fixed carries
// the spelling a seat typed -- #1095 is `gate-scoping`, #1087 is `fixer.md` --
// while the census is keyed on the policy file, so a raw lookup would find
// nothing for them and call every one of them below threshold while the rule
// behind them recurs. It is not a second copy of the normalization: it is
// produced by `policy_lint.mjs --normalize-friction-keys`, which is the same
// `frictionKey` the histogram keys with. An id the map does not carry is used
// as written.
export function belowThreshold({ openIssues, census, wouldOpenKeys, threshold, normalize = new Map() }) {
  const out = []
  for (const row of openIssues) {
    const title = String(row?.title ?? '')
    if (!title.startsWith(FRICTION_PREFIX)) continue
    const key = title.slice(FRICTION_PREFIX.length)
    const canonical = normalize.get(key) ?? key
    if (wouldOpenKeys.has(key) || wouldOpenKeys.has(canonical)) continue
    const cell = census.get(canonical) ?? census.get(key)
    const prs = cell ? cell.prs : 0
    if (prs >= threshold) continue
    out.push({
      number: row.number,
      key,
      canonical,
      prs,
      entries: cell ? cell.entries : 0,
      measured: Boolean(cell),
    })
  }
  return out
}

export function issueKeys(openIssues) {
  return openIssues
    .map((r) => String(r?.title ?? ''))
    .filter((t) => t.startsWith(FRICTION_PREFIX))
    .map((t) => t.slice(FRICTION_PREFIX.length))
}

// The normalizer's answer, checked before it is used: one row per id sent, in
// the `<raw>\t<key>` shape. A short or malformed answer is `unknown` and
// refuses, for the same reason an unanswered search does -- reading a partial
// mapping as "these ids normalize to themselves" would put the whole sweep back
// where it started, and silently.
export function parseNormalization(rc, stdout, sent) {
  if (rc !== 0) return 'unknown'
  const map = new Map()
  for (const line of String(stdout).split('\n')) {
    if (!line.trim()) continue
    const i = line.indexOf('\t')
    if (i < 0) return 'unknown'
    map.set(line.slice(0, i), line.slice(i + 1).replace(/\r$/, ''))
  }
  for (const id of sent) if (!map.has(id)) return 'unknown'
  return map
}

// The idempotence control, and the reason the marker carries the window: one
// comment per issue per WINDOW. The same window re-measured on the next beat
// finds its own marker and writes nothing; a new window (a tag was cut) is a
// new measurement and earns one new comment. The marker is an HTML comment so
// a reader sees the prose and the parser sees the key.
export function markerFor(key, since) {
  return `<!-- friction-below-threshold key:${key} window:${since}..origin/main -->`
}

export function commentFor(entry, since, threshold, tool = STATS_TOOL) {
  const seen = entry.measured
    ? `${entry.prs} distinct pull request(s) (${entry.entries} entr${entry.entries === 1 ? 'y' : 'ies'} in all)`
    : 'no pull request at all'
  return [
    markerFor(entry.key, since),
    `Re-measured by the governance cron's friction step: this key is BELOW the`,
    `threshold in the current window.`,
    ``,
    `## Measurement`,
    ``,
    `- key: \`${entry.key}\``,
    ...(entry.canonical && entry.canonical !== entry.key
      ? [`- re-measured as: \`${entry.canonical}\` (this issue's title predates the keying fix; the histogram now keys a friction id on the policy file it names, so every spelling of this rule counts here)`]
      : []),
    `- window: \`${since}..origin/main\``,
    `- in this window: ${seen}`,
    `- threshold: ${threshold} or more DISTINCT pull requests in the window`,
    `- derivation command: \`node ${tool} --stats --since ${since}\``,
    ``,
    `## What this is not`,
    ``,
    `This is not a close. The bot files and re-measures; a seat disposes, per`,
    `\`CLAUDE.md\` and \`.claude/rules/delivery-status-tracking.md\`. A key below`,
    `the threshold in one window is not a fixed problem -- the window moved when`,
    `the last tag was cut, and the friction may simply be older than it. Close`,
    `this if the underlying friction is dealt with; leave it open if it is not.`,
    ``,
    `One comment per issue per window: the next beat over this same window finds`,
    `this marker and writes nothing.`,
    ``,
  ].join('\n')
}

// `existingComments` is the ARRAY of comment bodies, or the string 'unknown'
// when the read did not answer. Unknown refuses: a comment thread that could
// not be read is exactly the flaky-API repeat this control exists to prevent,
// and the same fail-closed rule the search already follows.
export function decideComment(existingComments, marker) {
  if (existingComments === 'unknown' || !Array.isArray(existingComments)) return 'refuse'
  return existingComments.some((b) => String(b).includes(marker)) ? 'no-op' : 'comment'
}

// Any gh JSON call's three outcomes, decided from the TEXT rather than from an
// absence of error -- push.sh's measured reason: gh exits 0 with empty output
// for `--jq` filters that match nothing, so a filter bug and "no such issue"
// print the same bytes. `null` is a POSITIVE statement that the call answered;
// the string 'unknown' means it did not, and a caller that files on 'unknown'
// is the flaky-API double-file.
export function jsonCall(rc, stdout) {
  if (rc !== 0) return 'unknown'
  try {
    return JSON.parse(String(stdout))
  } catch {
    return 'unknown'
  }
}

// The search's outcome additionally asserts the ARRAY shape `issue list`
// prints; anything else -- prose, a single object -- is `unknown` and refuses.
export function searchOutcome(rc, stdout) {
  const parsed = jsonCall(rc, stdout)
  return Array.isArray(parsed) ? parsed : 'unknown'
}

// The exact-title filter the search's own scoping is checked against: the
// query is issued as `"<title>" in:title`, and GitHub's phrase search can still
// return issues whose titles merely CONTAIN the phrase (a key that is a prefix
// of another key, "blocked" inside "blocked-on-review"), so the create/update
// decision keys on byte equality of the whole title.
export function pickExact(rows, title) {
  for (const r of rows) {
    if (r && typeof r.title === 'string' && r.title === title) {
      return { number: r.number, state: r.state, body: r.body }
    }
  }
  return null
}

// The issue body: a PURE function of the measurement. No timestamp, no run id,
// no ref -- anything that moves between two runs of one window would make the
// idempotence check edit on every beat. The count and the window move only when
// the measurement itself moved, which is exactly when an update is owed. What
// a disposer needs is in here by contract: the histogram line that fired, the
// window, and the command that re-derives it.
export function bodyFor(entry, since) {
  return [
    `Filed by the governance cron's friction-filing step (the \`record\` job,`,
    `governance.yml): the stats histogram printed a would-open verdict for this`,
    `key over its window and the lane files what its own classifier named`,
    `(#959, option B; owner approval #201 comment 5670207248, item 4). The bot`,
    `is scoped to the key it measured -- it files this issue and updates it in`,
    `place; it never disposes, never reassigns, never closes.`,
    ``,
    `## Measurement`,
    ``,
    `- histogram line: \`${entry.line}\``,
    `- window: \`${since}..origin/main\``,
    `- rule: ${entry.threshold} or more of one key in the window opens one issue per key per window (idempotent: search before create, update in place, never a duplicate)`,
    `- derivation command: \`node ${STATS_TOOL} --stats --since ${since}\``,
    ``,
    `Re-derivable at any time with the command above; the body is refreshed in`,
    `place when the count moves within the window.`,
    ``,
    `## Disposition`,
    ``,
    `A seat disposes this issue; a bot cannot act on it. It enters the`,
    `Delivery-status table and owes a disposition per`,
    `\`.claude/rules/delivery-status-tracking.md\`. The friction key names the`,
    `${entry.kind} the window measured -- that is the subject to dispose.`,
    ``,
  ].join('\n')
}

export function titleFor(key) {
  return FRICTION_PREFIX + key
}

// create / edit / no-op, decided before anything is written so --dry-run and
// the self-test drive the same decision the live run acts on. `refuse` is the
// only other answer: an existing issue whose body cannot be read is not an
// excuse to file a second one.
export function decide({ existing, currentBody, body }) {
  if (!existing) return 'create'
  if (currentBody == null) return 'refuse'
  return currentBody === body ? 'no-op' : 'edit'
}

// --- the gh layer ------------------------------------------------------------
// Thin on purpose: every decision above it is driven offline by the self-test,
// and everything below it is demonstrated end to end on the pull request that
// lands this file, twice, in one window.

function gh(args, { input } = {}) {
  const res = spawnSync('gh', args, {
    encoding: 'utf8',
    input: input ?? undefined,
    maxBuffer: 32 * 1024 * 1024,
  })
  return { rc: res.status, stdout: String(res.stdout ?? ''), stderr: String(res.stderr ?? '') }
}

function searchIssue(title) {
  const res = gh([
    'issue', 'list',
    '--state', 'all',
    '--search', `"${title}" in:title`,
    '--json', 'number,title,state',
    '--limit', '30',
  ])
  return { res, rows: searchOutcome(res.rc, res.stdout) }
}

function listOpenFrictionIssues() {
  const res = gh([
    'issue', 'list',
    '--state', 'open',
    '--search', `"${FRICTION_PREFIX}" in:title`,
    '--json', 'number,title',
    '--limit', '100',
  ])
  return { res, rows: searchOutcome(res.rc, res.stdout) }
}

function commentBodies(number) {
  const res = gh(['issue', 'view', String(number), '--json', 'comments'])
  const parsed = jsonCall(res.rc, res.stdout)
  if (parsed === 'unknown' || !Array.isArray(parsed?.comments)) return 'unknown'
  return parsed.comments.map((c) => String(c?.body ?? ''))
}

function die(why) {
  console.error(`FRICTION FILED: nothing -- refusing: ${why}`)
  process.exit(1)
}

// --- the run -----------------------------------------------------------------

function run(args) {
  const statsFile = valueOf(args, '--stats-file')
  const since = valueOf(args, '--since')
  const dryRun = args.includes('--dry-run')
  if (!statsFile || !since) {
    console.error('usage: friction_issues.mjs --stats-file <path> --since <ref> [--dry-run]')
    process.exit(2)
  }
  let text
  try {
    text = fs.readFileSync(statsFile, 'utf8')
  } catch (e) {
    die(`the stats output is unreadable (${String(e.message).slice(0, 120)}) -- a filing step with no histogram files nothing in silence`)
  }
  const parsed = parseHistogram(text)
  if (!parsed.ok) die(`${parsed.why} (stats output: ${statsFile})`)
  if (!parsed.entries.length) {
    console.log(`FRICTION: histogram names no key at or over threshold in ${since}..origin/main; filing nothing`)
  } else {
    fileEntries(parsed, since, dryRun)
  }
  sweepBelowThreshold(parsed, since, dryRun)
}

function fileEntries(parsed, since, dryRun) {
  console.log(`FRICTION: histogram names ${parsed.entries.length} key(s) at or over threshold in ${since}..origin/main`)
  for (const entry of parsed.entries) {
    const title = titleFor(entry.key)
    const body = bodyFor(entry, since)
    const { res, rows } = searchIssue(title)
    if (rows === 'unknown') {
      die(`the exact-title search for ${JSON.stringify(title)} did not answer (gh exit ${res.rc}, <<${res.stdout.slice(0, 120)}>> <<${res.stderr.slice(0, 120)}>>): treating an unanswered search as "no existing issue" is the flaky-API double-file, so nothing is filed`)
    }
    const exact = pickExact(rows, title)
    let currentBody = null
    if (exact) {
      const view = gh(['issue', 'view', String(exact.number), '--json', 'body'])
      const parsedView = jsonCall(view.rc, view.stdout)
      if (parsedView === 'unknown' || typeof parsedView?.body !== 'string') {
        die(`issue #${exact.number} carries the exact title but its body could not be read (gh exit ${view.rc}); filing a second issue beside an unreadable one is the duplicate this exists to prevent`)
      }
      currentBody = parsedView.body
    }
    const action = decide({ existing: exact, currentBody, body })
    if (action === 'refuse') die(`issue #${exact.number} exists but its body is unreadable, so the idempotence check cannot compare`)
    if (dryRun) {
      console.log(`DRY-RUN ${action === 'create' ? `would file` : action === 'edit' ? `would update` : 'no-op, already current'}: ${JSON.stringify(title)}${exact ? ` (#${exact.number}, ${exact.state})` : ''} -- ${entry.kind} at ${entry.count}`)
      if (action !== 'no-op') console.log(body)
      continue
    }
    if (action === 'create') {
      const file = writeTemp(body)
      const res = gh(['issue', 'create', '--title', title, '--body-file', file])
      if (res.rc !== 0) die(`gh issue create refused ${JSON.stringify(title)} (gh exit ${res.rc}, <<${res.stderr.slice(0, 200)}>>) -- the lane reddens rather than retries, so no beat can double-file`)
      console.log(`FILED: ${JSON.stringify(title)} -- ${res.stdout.trim()}`)
    } else if (action === 'edit') {
      const file = writeTemp(body)
      const res = gh(['issue', 'edit', String(exact.number), '--body-file', file])
      if (res.rc !== 0) die(`gh issue edit refused #${exact.number} (gh exit ${res.rc}, <<${res.stderr.slice(0, 200)}>>)`)
      console.log(`UPDATED: #${exact.number} ${JSON.stringify(title)} -- ${entry.kind} at ${entry.count} in this window (one issue per key per window; the body, not a duplicate)`)
    } else {
      console.log(`CURRENT: #${exact.number} ${JSON.stringify(title)} already carries this measurement (${entry.kind} at ${entry.count}); no write made`)
    }
  }
}

function sweepBelowThreshold(parsed, since, dryRun) {
  const { res, rows } = listOpenFrictionIssues()
  if (rows === 'unknown') {
    die(`the open-issue listing for ${JSON.stringify(FRICTION_PREFIX)} did not answer (gh exit ${res.rc}, <<${res.stdout.slice(0, 120)}>> <<${res.stderr.slice(0, 120)}>>): a listing that did not answer is not an empty listing, and re-measuring nothing in silence is the failure this sweep exists to end`)
  }
  // A window holding fewer pull requests than the threshold cannot put ANY key
  // at the threshold, so "below threshold" measured there is a statement about
  // the window's size and not about the friction. It is the same opposite-claims
  // rule the fetch guard makes one step up: a zero over a window incapable of
  // reaching the threshold and a zero over a window that reached it and fell
  // back are different claims, and only the second is worth a comment.
  if (parsed.windowPrs < parsed.threshold) {
    console.log(`FRICTION SWEEP: not run -- ${since}..origin/main holds ${parsed.windowPrs} merged pull request(s), fewer than the threshold of ${parsed.threshold}, so no key in it could have reached the threshold and "below threshold" here would measure the window rather than the friction`)
    return
  }
  const wouldOpenKeys = new Set(parsed.entries.map((e) => e.key))
  const sent = issueKeys(rows)
  let normalize = new Map()
  if (sent.length) {
    const n = spawnSync('node', [STATS_TOOL, '--normalize-friction-keys'], {
      encoding: 'utf8',
      input: `${sent.join('\n')}\n`,
      maxBuffer: 8 * 1024 * 1024,
    })
    normalize = parseNormalization(n.status, String(n.stdout ?? ''), sent)
    if (normalize === 'unknown') {
      die(`${STATS_TOOL} --normalize-friction-keys did not answer for all ${sent.length} open issue key(s) (exit ${n.status}): without the mapping an issue filed under an older spelling reads as a key the window never saw, which is exactly the false "below threshold" this sweep must not post`)
    }
  }
  const below = belowThreshold({ openIssues: rows, census: parsed.census, wouldOpenKeys, threshold: parsed.threshold, normalize })
  console.log(`FRICTION SWEEP: ${rows.length} open ${JSON.stringify(FRICTION_PREFIX)} issue(s); ${below.length} below threshold ${parsed.threshold} in ${since}..origin/main`)
  for (const entry of below) {
    const marker = markerFor(entry.key, since)
    // Read even under --dry-run: the read-only half runs against the live
    // repository there by design, and a dry run that skipped it would report
    // `would comment` for an issue the live run would leave alone.
    const bodies = commentBodies(entry.number)
    const action = decideComment(bodies, marker)
    if (action === 'refuse') {
      die(`the comment thread of #${entry.number} could not be read, so the one-comment-per-window control cannot be evaluated; commenting anyway is the repeat this control exists to prevent`)
    }
    if (action === 'no-op') {
      console.log(`SWEEP CURRENT: #${entry.number} (${entry.key}) already carries this window's below-threshold comment; no write made`)
      continue
    }
    const body = commentFor(entry, since, parsed.threshold)
    if (dryRun) {
      console.log(`DRY-RUN would comment on #${entry.number} (${entry.key}): ${entry.prs} distinct PR(s) in this window`)
      console.log(body)
      continue
    }
    const out = gh(['issue', 'comment', String(entry.number), '--body-file', writeTemp(body)])
    if (out.rc !== 0) die(`gh issue comment refused #${entry.number} (gh exit ${out.rc}, <<${out.stderr.slice(0, 200)}>>)`)
    console.log(`SWEPT: #${entry.number} (${entry.key}) -- ${entry.prs} distinct PR(s), below threshold ${parsed.threshold}; a seat closes it, not this lane. ${out.stdout.trim()}`)
  }
}

function valueOf(args, flag) {
  const i = args.indexOf(flag)
  return i >= 0 && i + 1 < args.length ? args[i + 1] : null
}

function writeTemp(body) {
  const fsync = fs.openSync(`${process.env.RUNNER_TEMP ?? '/tmp'}/friction-issue-body.md`, 'w')
  fs.writeSync(fsync, body)
  fs.closeSync(fsync)
  return `${process.env.RUNNER_TEMP ?? '/tmp'}/friction-issue-body.md`
}

// --- the self-test -----------------------------------------------------------
// Offline, network-free, over the OBSERVED shapes: the finding line
// policy_lint prints, the search listings gh prints, and the refusals each
// malformed input owes. Every refusal sits beside the healthy input it must
// NOT refuse, because a classifier that answers `refuse` to everything
// satisfies the refusal assertions alone (push.sh's pairing rule).
export function selfTest() {
  let pass = 0
  let fail = 0
  const st = (got, want, what) => {
    if (got === want) { pass += 1; console.log(`  ok   ${what}`) }
    else { fail += 1; console.log(`  FAIL ${what} (got ${JSON.stringify(got)}, wanted ${JSON.stringify(want)})`) }
  }

  // The trigger line, exactly as printFindings emits it: two leading spaces,
  // severity padded to 7, the [stats] check tag, the (window) where.
  const LINE = (key, kind, n) =>
    `  INFO    [stats] (window): would open "[policy] recurring friction: ${key}" -- ${kind} at ${n} in this window, threshold 3. Not opened here: a seat measures and files, a report does not.`
  // Everything policy_lint prints that this lane reads: the would-open lines,
  // the per-key census, its summary, and the threshold line. A histogram
  // missing any of them is refused, and each refusal below sits beside the
  // healthy input it must not refuse.
  const CENSUS = (rows) =>
    `${rows.map(([kind, prs, ent, key]) => `CENSUS\t${kind}\t${prs}\t${ent}\t${key}`).join('\n')}\nCENSUS: ${rows.length} key(s)`
  const THRESHOLD_LINE = '\nthreshold: 3 or more of one key in the window opens "[policy] recurring friction: <key>". Nothing is opened here.'
  const WINDOW_LINE = (w) => `STATS: ${w} merged pull request(s) in v9.9.9..origin/main; verdict grammar ["blocked","merge"]`
  const STATS_OK = (n, rows = [['verdict class', 3, 4, 'blocked']], w = 12) =>
    `\n${WINDOW_LINE(w)}\n${CENSUS(rows)}${THRESHOLD_LINE}\nWOULD OPEN: ${n} issue(s)`

  // The healthy histogram: entries parsed, key and kind and count intact.
  const good = parseHistogram(`${LINE('blocked', 'verdict class', 4)}\n${STATS_OK(1)}`)
  st(good.ok, true, 'a completed histogram with one would-open line parses')
  st(good.entries.length, 1, 'and yields exactly one entry')
  st(good.entries[0].key, 'blocked', 'the friction key is read out of the quoted title')
  st(good.entries[0].kind, 'verdict class', 'the kind (which histogram counted it) is kept for the disposer')
  st(good.entries[0].count, 4, 'the count is kept so the body can carry it')

  // The merge-is-not-rework exclusion, respected WITHOUT reimplementing it:
  // the passing verdict prints `not opened:`, and that line is not a trigger.
  const excluded = parseHistogram(
    `  INFO    [stats] (window): not opened: verdict class "merge" at 9 is the passing verdict .claude/workflows/web-fix-wave.js requires before a merge, so it counts rework nowhere. Friction is rework.\n${STATS_OK(0)}`)
  st(excluded.ok && excluded.entries.length, 0,
    'a passing-verdict line over threshold is NOT a trigger (the exclusion lives in policy_lint and this parser only reads `would open`)')

  // Under threshold lines never exist (the histogram only prints over-threshold
  // findings), but a would-open line is parsed only in its full shape: a
  // truncated line is not half-filed.
  const truncated = parseHistogram(`  INFO    [stats] (window): would open "[policy] recurring friction: blocked" -- verdict cla\n${STATS_OK(0)}`)
  st(truncated.ok && truncated.entries.length, 0, 'a truncated would-open line matches nothing rather than something')

  // The refusals, each beside the healthy input it must not refuse.
  const noSummary = parseHistogram(LINE('blocked', 'verdict class', 4))
  st(noSummary.ok, false, 'a stats output with no WOULD OPEN summary line is refused (not a completed histogram)')
  st(noSummary.ok || /not a completed stats histogram/.test(noSummary.why), true, 'and the refusal says why')
  const flaky = parseHistogram(`  INFO    [stats] (github api): could not fetch pull-request bodies and comments: HTTP 502. Printing no histogram rather than a histogram of zeroes.\n${STATS_OK(0)}`)
  st(flaky.ok, false, 'a histogram whose window could NOT be fetched is refused: no data is not no friction')
  st(parseHistogram(LINE('blocked', 'verdict class', 4) + STATS_OK(1)).ok, true,
    'null control: the same line WITH its summary parses (the refusals above fired on the missing evidence, not on the line)')

  // The search's three outcomes, from the listing TEXT.
  st(Array.isArray(searchOutcome(0, '[]')), true, "gh's empty listing is a POSITIVE statement that no issue carries the title")
  st(searchOutcome(0, '[]')?.length, 0, 'and it is empty: no row to pick')
  st(Array.isArray(searchOutcome(0, '[{"number":31,"title":"[policy] recurring friction: blocked","state":"OPEN"}]')), true,
    'a listing naming the issue parses into rows')
  st(searchOutcome(1, ''), 'unknown', 'a search that FAILED is unknown, never none -- fail-open here is the double-file')
  st(searchOutcome(0, 'GraphQL: Could not resolve to a Repository'), 'unknown',
    'prose on stdout is not a listing')
  st(searchOutcome(0, '{"number":31}'), 'unknown', 'a non-array JSON object is unknown for a listing')

  // The body read's outcome: `gh issue view --json body` prints one OBJECT.
  st(typeof jsonCall(0, '{"body":"x"}')?.body, 'string', "the body read parses gh issue view's single object")
  st(jsonCall(1, ''), 'unknown', 'a body read that failed is unknown (the run refuses on it, never files beside it)')
  st(typeof jsonCall(0, '[]')?.body, 'undefined', 'an array where the object was expected carries no body -- the run\'s typeof guard refuses it')

  // The exact-title filter: phrase search can return containers, the decision
  // keys on byte equality of the whole title.
  const rows = [
    { number: 40, title: '[policy] recurring friction: blocked-on-review', state: 'OPEN' },
    { number: 41, title: '[policy] recurring friction: blocked', state: 'OPEN' },
  ]
  st(pickExact(rows, '[policy] recurring friction: blocked')?.number, 41,
    'the exact title is picked out of a listing whose other row merely contains the phrase')
  st(pickExact(rows, '[policy] recurring friction: zz-absent'), null,
    'a title no row carries exactly answers null (null control on the pick)')
  st(pickExact(rows, '[policy] recurring friction: blocked-on-review')?.number, 40,
    'the longer key picks its own row -- one issue per KEY, keys not prefixes')

  // The decision matrix.
  const body = bodyFor({ key: 'blocked', kind: 'verdict class', count: 4, threshold: 3, line: LINE('blocked', 'verdict class', 4).trim() }, 'v9.9.9')
  st(decide({ existing: null, currentBody: null, body }), 'create', 'no existing issue: file')
  st(decide({ existing: { number: 41 }, currentBody: body, body }), 'no-op', 'an existing issue already carrying this exact measurement: NO write')
  st(decide({ existing: { number: 41 }, currentBody: body + 'x', body }), 'edit', 'a measurement that moved within the window: edit the one issue in place')
  st(decide({ existing: { number: 41 }, currentBody: null, body }), 'refuse', 'an existing issue whose body cannot be read: refuse, never a second file')

  // The body is the idempotence contract: byte-identical for the same
  // measurement, different only when the measurement moved. The entries carry
  // the line TRIMMED, exactly as parseHistogram produces it.
  const ENTRY = (key, kind, n) => ({ key, kind, count: n, threshold: 3, line: LINE(key, kind, n).trim() })
  const body2 = bodyFor(ENTRY('blocked', 'verdict class', 4), 'v9.9.9')
  st(body === body2, true, 'the body is a pure function of the measurement (same inputs, byte-identical body)')
  const bodyMoved = bodyFor(ENTRY('blocked', 'verdict class', 6), 'v9.9.9')
  st(body !== bodyMoved, true, 'a moved count produces a different body (the in-place update has something to carry)')
  for (const needle of ['histogram line: `INFO    [stats] (window): would open "[policy] recurring friction: blocked" -- verdict class at 4 in this window, threshold 3.',
    '`v9.9.9..origin/main`',
    `derivation command: \`node ${STATS_TOOL} --stats --since v9.9.9\``,
    'A seat disposes this issue; a bot cannot act on it']) {
    st(body.includes(needle), true, `the body carries the data a disposer needs: ${needle.slice(0, 60)}...`)
  }
  st(body.includes(new Date().toISOString().slice(0, 10)), false,
    'and carries no timestamp: anything that moves between two runs of one window would edit on every beat')

  // Two drives in one window, end to end over the pure decisions -- the
  // control the owner's card asked to see demonstrated, before the live
  // demonstration runs the same shape through real gh calls.
  const d1 = decide({ existing: null, currentBody: null, body })
  const d2 = decide({ existing: { number: 41 }, currentBody: body, body })
  st(`${d1},${d2}`, 'create,no-op', 'two drives over one window and one measurement: ONE file, then NO write at all')

  // --- the close path ---------------------------------------------------
  // The census, and the two refusals that keep "below threshold" from being
  // said about a window that never measured the key.
  const CROWS = [
    ['friction rule id', 4, 6, '.claude/rules/gate-scoping.md'],
    ['friction rule id', 1, 3, '.claude/rules/claim-files.md'],
  ]
  const withCensus = parseHistogram(
    `${LINE('.claude/rules/gate-scoping.md', 'friction rule id', 4)}${STATS_OK(1, CROWS)}`)
  st(withCensus.ok, true, 'a histogram carrying a census parses')
  st(withCensus.threshold, 3, 'the threshold is READ from the histogram, never a second copy typed here')
  st(withCensus.windowPrs, 12, "and the window's own size, which is what says whether the threshold was reachable in it at all")
  st(parseHistogram(`${LINE('blocked', 'verdict class', 4)}\n${CENSUS(CROWS)}${THRESHOLD_LINE}\nWOULD OPEN: 1 issue(s)`).ok, false,
    'a histogram that does not say how large its window is is refused: a below-threshold claim over an unknown window measures nothing')
  st(withCensus.census.get('.claude/rules/claim-files.md')?.prs, 1,
    'the census carries the distinct-PR count of a key BELOW threshold, which no would-open line names')
  st(withCensus.census.get('.claude/rules/claim-files.md')?.entries, 3,
    'and its entry count beside it, so a comment can say 3 entries from 1 pull request')
  const noCensus = parseHistogram(`${LINE('blocked', 'verdict class', 4)}\n${WINDOW_LINE(12)}\n${THRESHOLD_LINE}\nWOULD OPEN: 1 issue(s)`)
  st(noCensus.ok, false, 'a histogram with NO census is refused: an absent census would read as every key at zero')
  const partial = parseHistogram(
    `${LINE('blocked', 'verdict class', 4)}\n${WINDOW_LINE(12)}\nCENSUS\tverdict class\t3\t4\tblocked\nCENSUS: 2 key(s)${THRESHOLD_LINE}\nWOULD OPEN: 1 issue(s)`)
  st(partial.ok, false, 'a census that declares more keys than it prints is refused (a partial census is not a measurement of what it omits)')
  const noThreshold = parseHistogram(`${LINE('blocked', 'verdict class', 4)}\n${WINDOW_LINE(12)}\n${CENSUS(CROWS)}\nWOULD OPEN: 1 issue(s)`)
  st(noThreshold.ok, false, 'a histogram that does not print its own threshold is refused rather than compared against a number typed here')

  // The sweep's selection: which open issues are below threshold, and the
  // three it must stay silent about.
  const OPEN = [
    { number: 1095, title: '[policy] recurring friction: .claude/rules/gate-scoping.md' },
    { number: 1087, title: '[policy] recurring friction: .claude/rules/claim-files.md' },
    { number: 1041, title: '[policy] recurring friction: blocked' },
    { number: 1060, title: '[policy] recurring friction: zz-never-measured' },
    { number: 201, title: 'Open-issues programme' },
  ]
  const census = new Map([
    ['.claude/rules/gate-scoping.md', { kind: 'friction rule id', prs: 4, entries: 6 }],
    ['.claude/rules/claim-files.md', { kind: 'friction rule id', prs: 1, entries: 3 }],
    ['blocked', { kind: 'verdict class', prs: 22, entries: 33 }],
  ])
  const swept = belowThreshold({
    openIssues: OPEN,
    census,
    wouldOpenKeys: new Set(['.claude/rules/gate-scoping.md']),
    threshold: 3,
  })
  st(swept.map((e) => e.number).join(','), '1087,1060',
    'the sweep speaks about the key that fell below threshold and the key the window never saw, and about nothing else')
  st(swept[0].prs, 1, 'and carries the current distinct-PR count, not the entry count that used to file it')
  st(swept[0].entries, 3, 'with the entry count beside it -- 3 entries from 1 pull request is the shape that used to fire')
  st(swept[1].measured, false, 'a key absent from the census is reported as measured-at-zero rather than silently dropped')
  st(swept.some((e) => e.number === 1095), false,
    'NULL CONTROL: an issue whose key the current window WOULD open is not called below threshold')
  st(swept.some((e) => e.number === 1041), false,
    'NULL CONTROL: an issue whose key is at 22 and merely WITHHELD by the classifier is not called below threshold either -- withheld is not below')
  st(swept.some((e) => e.number === 201), false, 'an issue that is not a friction issue is not touched')
  st(belowThreshold({ openIssues: OPEN, census, wouldOpenKeys: new Set(), threshold: 3 }).map((e) => e.number).join(','),
    '1087,1060', 'NULL CONTROL on the threshold: gate-scoping at 4 stays silent even with nothing filed this beat')

  // The pre-fix titles, which is what every issue open today carries. Without
  // the mapping the census has no row for `gate-scoping` and the sweep would
  // post "below threshold" on a rule sitting at 4.
  const OLD = [
    { number: 1095, title: '[policy] recurring friction: gate-scoping' },
    { number: 1087, title: '[policy] recurring friction: claim-files' },
  ]
  const NORM = new Map([
    ['gate-scoping', '.claude/rules/gate-scoping.md'],
    ['claim-files', '.claude/rules/claim-files.md'],
  ])
  st(belowThreshold({ openIssues: OLD, census, wouldOpenKeys: new Set(), threshold: 3, normalize: NORM }).map((e) => e.number).join(','),
    '1087', 'an issue filed under an older spelling is re-measured through the SAME normalization the histogram keys with')
  st(belowThreshold({ openIssues: OLD, census, wouldOpenKeys: new Set(), threshold: 3 }).map((e) => e.number).join(','),
    '1095,1087', 'NULL CONTROL: without that mapping the same sweep calls a rule at 4 distinct PRs below threshold -- the false comment the mapping exists to prevent')
  st(issueKeys(OPEN).join(','), '.claude/rules/gate-scoping.md,.claude/rules/claim-files.md,blocked,zz-never-measured',
    'the ids sent to the normalizer are the open FRICTION issues\' keys and nothing else')
  st(parseNormalization(0, 'a\t.claude/rules/a.md\nb\tb\n', ['a', 'b'])?.get('a'), '.claude/rules/a.md',
    'a complete mapping parses')
  st(parseNormalization(0, 'a\t.claude/rules/a.md\n', ['a', 'b']), 'unknown',
    'a mapping SHORT of what was sent is unknown: a missing row would read as "normalizes to itself"')
  st(parseNormalization(1, '', ['a']), 'unknown', 'a normalizer that failed is unknown, never an identity map')
  st(parseNormalization(0, 'no tab here\n', ['a']), 'unknown', 'a line outside the `<raw>\\t<key>` shape is unknown')
  const renamed = belowThreshold({ openIssues: OLD, census, wouldOpenKeys: new Set(), threshold: 3, normalize: NORM })[0]
  st(commentFor(renamed, 'v6.6.2', 3).includes('re-measured as: `.claude/rules/claim-files.md`'), true,
    'and the comment says which key the re-measurement used, so a reader is not comparing two different things')
  st(commentFor(swept[0], 'v6.6.2', 3).includes('re-measured as:'), false,
    'NULL CONTROL: an issue whose title is already the canonical key carries no such line')

  // One comment per issue per window, and a new window earns a new one.
  const mk = markerFor('.claude/rules/claim-files.md', 'v6.6.2')
  const cmt = commentFor(swept[0], 'v6.6.2', 3)
  st(cmt.includes(mk), true, 'the comment carries its own marker, which is what the next beat reads')
  st(decideComment([], mk), 'comment', 'an issue with no such comment gets one')
  st(decideComment(['unrelated', cmt], mk), 'no-op', 'an issue already carrying THIS window\'s comment gets none (one per issue per window)')
  st(decideComment([cmt], markerFor('.claude/rules/claim-files.md', 'v6.7.0')), 'comment',
    'a NEW window is a new measurement and earns one new comment')
  st(decideComment([commentFor({ ...swept[0], key: 'other' }, 'v6.6.2', 3)], mk), 'comment',
    'another key\'s comment on the same issue is not this key\'s marker')
  st(decideComment('unknown', mk), 'refuse', 'a comment thread that could not be read refuses, never comments')
  st(/close/i.test(cmt) && !/^\s*Closes #/m.test(cmt), true,
    'the comment talks about closing without carrying a closing keyword that would close something itself')
  st(cmt.includes('This is not a close'), true, 'and says in words that it is not one: a seat disposes, per CLAUDE.md')

  console.log(`\n${pass} passed, ${fail} failed`)
  return fail ? 1 : 0
}

// --- entry -------------------------------------------------------------------

const argv = process.argv.slice(2)
if (argv.includes('--self-test')) process.exit(selfTest())
run(argv)
