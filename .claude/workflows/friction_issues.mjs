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

export function parseHistogram(text) {
  const out = { ok: false, why: '', entries: [] }
  if (!/WOULD OPEN: \d+ issue\(s\)/.test(text)) {
    out.why = 'no WOULD OPEN summary line: this is not a completed stats histogram'
    return out
  }
  if (/could not fetch pull-request bodies and comments/.test(text)) {
    out.why = 'the histogram window could not be fetched: no data is not no friction, and a filing lane must not act on an empty measurement'
    return out
  }
  const entries = []
  for (const line of String(text).split('\n')) {
    const m = line.match(WOULD_OPEN_RE)
    if (m) entries.push({ key: m[1], kind: m[2], count: Number(m[3]), threshold: Number(m[4]), line: line.trim() })
  }
  out.ok = true
  out.entries = entries
  return out
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
    return
  }
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
  const STATS_OK = (n) => `\nWOULD OPEN: ${n} issue(s)`

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

  console.log(`\n${pass} passed, ${fail} failed`)
  return fail ? 1 : 0
}

// --- entry -------------------------------------------------------------------

const argv = process.argv.slice(2)
if (argv.includes('--self-test')) process.exit(selfTest())
run(argv)
