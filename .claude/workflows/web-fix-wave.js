// One wave of the open-issues program: fix, adversarially review and merge
// each PR group from one fork SHA. See .claude/workflows/web-fragments.md for
// the shared prompt block below, which is hand-copied into every web-*.js.
export const meta = {
  name: 'web-fix-wave',
  description: 'Fix, adversarially review and merge PR groups from one fork SHA, honoring merge-gated dependencies',
  phases: [{ title: 'Wave', detail: 'fixer, adversarial reviewer, then a serialized merge per group' }],
}
const GH = `No gh CLI exists in this environment. For every GitHub action run
ToolSearch with "select:<tool>" first, then call it (owner tvofi, repo
heatpump_optimizer): issue_read (get / get_comments), add_issue_comment,
issue_write (update: labels, state, state_reason), create_pull_request,
update_pull_request, pull_request_read (get, get_check_runs, get_comments,
get_files, get_diff), merge_pull_request (squash), actions_list
(list_workflow_runs on tests.yml, branch main), actions_get, get_job_logs
(failed_only).`

const GATE = `Gate rules on this 4-core box. The shell's working directory
resets between calls: pin cd in every command. PYTHONPATH=tests/hastub for
direct script runs; python3 tests/structure.py before every push; the five
BLAS thread variables pinned to 1.

THE LOCK IS FOR tests/stress.py, SO ASK WHETHER YOUR CHANGE RUNS IT.
/tmp/hpo-gate.lock exists because stress.py's solve-time guard measures this
machine while it solves, and three concurrent stress runs at load 6.5 once
destroyed the very budget table they were recording. Nothing else in the
suite is timing-sensitive, so a change that does not select stress.py does
not need the lock -- and taking it anyway serialises every other agent for
no measurement reason. Decide it, do not assume it:

    D=$(mktemp -d) && python3 tests/closure.py select \
      --diff $(git merge-base origin/main HEAD) --workdir "$D"

  * that command FAILS, or "$D/scope.txt" contains "MODE: FULL", or you are
    deliberately running GATE_SCOPE=full  ->  TAKE THE LOCK. MODE: FULL is
    how the gate reports a change it cannot reason about -- a gate file, or
    a file in no recorded closure -- and it then runs every script including
    stress.py. It prints ZERO selected scripts while meaning the opposite of
    zero, so key on the mode line, never on the count.
  * "$D/scope.run" names tests/stress.py  ->  TAKE THE LOCK.
  * otherwise  ->  NO LOCK. Run the scripts scope.run names, directly.

Taking the lock: mkdir /tmp/hpo-gate.lock and write an owner file (your
label, the work's pid, UTC). If it exists, read it and check the pid, then
wait and retry -- NEVER remove a lock you did not create, EXCEPT when its
owner is provably dead: the owner file records a pid precisely so that is a
decidable fact rather than a judgement call. If that pid is not running AND no
run.sh/stress.py/golden.py/env_drift.py/derive_closures process exists AND load1
is low, the holder died (a container restart, an agent killed mid-gate). Write
down the owner file verbatim and those three observations, then clear it -- a
literal reading of the older rule deadlocks the whole wave behind a dead pid,
which has already happened once.
ONE TRAP IN THAT TEST, found by applying it: the pid in the owner file is usually
the GATE SHELL, which exits normally the moment the gate finishes -- while the
agent that took the lock is still alive, reading its log, and may be about to use
the lock again. So a dead pid ALONE is not enough when the gate log ends in a
completed run. Clear it only when the owning agent has also gone quiet for several
minutes; when in doubt wait, because yanking a live agent's lock costs more than
queueing behind a finished one. Write your own label into the owner file so the
next reader knows whose it is. Under it run
GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main
HEAD) ./tests/run.sh, and release with rm -rf, not rmdir: the owner file
makes the directory non-empty, and rmdir leaves the lock standing behind a
green gate, which has blocked two sessions before. Print the concurrent
process count beside every timing RESULT.

CI IS THE AUTHORITY EITHER WAY. Its fast, closures and browser jobs run the
same run.sh in the same drift mode against the same merge base, on a runner
that is not competing with you -- so wait for them with actions_list and let
them be the verdict. What you run locally is the evidence CI structurally
CANNOT produce, and that is the reason to run it: the mutation proof (delete
the production line, run the closure, paste the failing check names,
restore), the failing test at the merge base before the fix exists, and the
finder's harness before and after. CI only ever runs the committed tree, and
tools/ is INERT so no CI job runs a harness at all.

Browser lane: NODE_PATH=/opt/node22/lib/node_modules
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs
(indicative only; CI's browser job decides). Value-bearing golden fixtures
are never re-recorded on this box: value drift is claimed; golden.py
--record --only is for new key paths, and the body says so.`

const DOC = (session) => `Documentation you must leave, in this order: before
cutting the branch, label every issue owner:${session} (issue_write update,
keeping the existing labels) and comment "claimed-by: ${session} · branch
<name> · <UTC>"; push the branch after the failing-test commit and after
every commit thereafter; immediately after opening the PR, comment its URL
and head SHA on every issue; if you cannot finish, comment "state at stop:
<branch>, <pushed SHA>, <last green check>, <what is missing>" on every issue
before returning.`

const WT = (branch, fork) => `Work in your own worktree: from the repository
run git fetch origin --tags; if ${branch} already exists on origin, git
worktree add /home/user/wt/${branch} ${branch} (reuse the worktree if the
path exists), otherwise git worktree add /home/user/wt/${branch} -b ${branch}
${fork}. Never commit in /home/user/heatpump_optimizer itself.`

const WT_REVIEW = (name, sha) => `Fresh detached worktree, per the reviewer's
contract: git fetch origin; git worktree add --detach
/home/user/wt/review-${name} ${sha}.`

const RANK = { haiku: 0, sonnet: 1, opus: 2 }
const tierOk = (f, r) => RANK[f] !== undefined && RANK[r] !== undefined && RANK[r] >= RANK[f]

const MERGE = { type: 'object', required: ['merged'] }
const mergePrompt = (pr, head) => `${GH} Merge PR #${pr} only if ALL of:
pull_request_read get shows mergeable_state clean and head sha ${head};
get_check_runs shows every check success or skipped; the newest "Fix review:"
comment says merge and post-dates that head; the diff touches neither VERSION
nor manifest.json nor the RELEASE_NOTES.md heading. Then merge_pull_request
with merge_method squash and return {merged: true, sha: <merge commit sha>}.
If mergeable_state is dirty, return {merged: false, reason: "needs repair"} --
do not merge main into the branch yourself, the fixer must, because a rebase
invalidates the evidence. Otherwise {merged: false, reason}.`

const waitMainPrompt = (sha) => `${GH} Poll actions_list (workflow tests.yml,
branch main) until the run for ${sha} completes; check every three minutes,
give up after two hours. Require both fast and closures to be success. On a
red run, fetch the failing job log (get_job_logs, failed_only) and return
{green: false, log_excerpt}. Return {green, run_id}.`

const stampPrompt = (repo, bump, title) => `In ${repo}: git fetch origin
--tags; git worktree add --detach /home/user/wt/stamp origin/main (if the
path exists, reuse it and git reset --hard origin/main). If git tag
--points-at HEAD is non-empty, return {stamped: false, reason: "already
stamped"} and change nothing. Otherwise write the RELEASE_NOTES.md section
"## v<next ${bump}>" at the top of the file: a "### <subsection>" per PR
merged since the last tag, written from its body (git log <last-tag>..HEAD
--format=%s lists them; read each body with pull_request_read), so every
"(#N)" is named -- stamp.py rule 4 refuses notes that omit one. Run python3
tools/release/stamp.py --bump ${bump} --title "${title}" --dry-run, then the
same command with --push. It refuses on its own rules; if it refuses, change
nothing and return {stamped: false, reason: <its message>}. Return {stamped:
true, version, tag_sha}.`

// ---------------------------------------------------------------------------
// One wave: every group is fixed, adversarially reviewed and merged. A group
// with `after` waits for its dependencies to be MERGED (not merely to have a
// PR) and then starts by merging origin/main, so its claim file and its
// budget table are its own -- two consecutive movers that each kept the
// other's claims is how a green PR turns main red.
//
// Concurrency is the runtime's own agent cap (min(16, CPUs-2)); this script
// launches every ready group and lets the runtime queue them. Merges are
// serialized through one promise chain, and main is waited on after each.
//
//   Workflow({name: 'web-fix-wave', args: {repo, fork, session, groups: [...]}})
//   group: {group, issues: [..], brief, fixture: bool, after: [..],
//           fixerModel, reviewerModel, effort}
// ---------------------------------------------------------------------------

const { groups = [], repo, fork, session = 'claude-web' } = args ?? {}
if (!groups.length || !repo || !fork) throw new Error('args.groups, args.repo and args.fork are required')
for (const g of groups) {
  if (!g.group || !g.issues?.length || !g.brief) throw new Error(`every group needs group, issues and brief (${g.group ?? '?'})`)
  if (!tierOk(g.fixerModel ?? 'opus', g.reviewerModel ?? 'opus')) throw new Error(`${g.group}: a reviewer below the fixer measures nothing`)
}

const RESUMED = (g) => g.resume?.stage === 'fix' ? `THIS GROUP IS BEING RESUMED. An earlier fixer stopped after pushing ${g.resume.pushed_sha} to claude-web/${g.group.toLowerCase()}: ${g.resume.what}. That work is NOT lost and is NOT yours to redo -- the worktree command below re-attaches to that branch. Read the pushed diff first (git log origin/main..HEAD, git diff origin/main...HEAD) and continue from it. What is still missing: ${g.resume.missing}` : ''
const fixerPrompt = (g, repair) => `You own fix group ${g.group} of the open-issues program: issues #${g.issues.join(', #')}. ${GH} ${WT('claude-web/' + g.group.toLowerCase(), fork)} ${(g.after ?? []).length ? 'Your dependencies have already merged, so your first action in the worktree is: git merge origin/main (never rebase). Resolve any claim-file or budget-table conflict by keeping ONLY your own lines -- your dependency already landed its own.' : ''} ${RESUMED(g)} ${DOC(session)}
Read tools/audit/briefs/fixer.md and tools/audit/README.md, then every issue's body AND its comments -- the comments carry corrections that override the body, and a fixer who reads only the body will implement the superseded plan. Your brief, which already applies those corrections:
${g.brief}
Follow every step of the fixer contract: a failing test first that imports the production symbol; the mutation proof with the failing check names pasted; the finding's own harness re-run before and after at your head SHA (copy a harness into the tree under test before running it -- the harnesses disagree about how they find the repository root); a null control on any cost, gain or time claim; both ends of the range for a learner or guard change. ${GATE}
${g.fixture ? 'This group moves fixtures. Claim each one with its expected direction in the right claim file, and never claim a fixture that is already may-drift -- env_drift refuses a name that is both. Run env_drift.py --fixtures before and after.' : 'This group must move no fixture: env_drift.py --all against the merge base reports no unclaimed drift, and both claim files stay byte-identical to origin/main.'}
Never touch VERSION, the manifest version or the RELEASE_NOTES.md heading. Open the pull request with a body that carries Closes #N for each issue, Part of #201, the head SHA you measured, and every executed number; then wait for CI (fast, closures, browser) with actions_list and fix red until it is green.
${repair ? `A reviewer BLOCKED your previous head. Their comment: ${repair}\nRepair in the same worktree, re-execute fixer steps 2-4 (the evidence described the old tree), push, and return the new head SHA.` : ''}
Return {pr, head_sha, summary} where pr is the PR NUMBER as an integer. If you could not open a PR -- you ran out of budget, the gate never went green, anything -- return pr: null with the reason in summary, and post the contractual "state at stop:" comment on every issue first. NEVER put prose in the pr field: a sentence there satisfies the schema, is read as a PR number, and sends a reviewer to a PR that does not exist.`

const reviewerPrompt = (g, fix, round) => `You are the adversarial fix reviewer for PR #${fix.pr} (group ${g.group}, head ${fix.head_sha}), in a fresh context. ${GH} ${WT_REVIEW(g.group + '-' + round, fix.head_sha)}
Read tools/audit/briefs/fix-review.md and follow it. You are not checking that the code looks right; four implementations on this project looked right and were wrong, one worse than its bug. Check that the numbers are real: re-run the mutation proof the body names and confirm those checks fail; measure with the FINDER's harness rather than the fixer's, at ${fork} and at ${fix.head_sha}, printing your own RESULT lines; re-run every null control and both-ends check the body claims; run env_drift.py --all (and card_drift.mjs for card changes) against the merge base and confirm every moved fixture is claimed, every claim moved, and no may-drift fixture is claimed; run python3 tests/structure.py against origin/main's budgets and require any loosened metric to be named and argued in the body; confirm VERSION, the manifest and the notes heading are untouched; attack the fix at other topologies, other price profiles and the zero-evidence install; confirm the head SHA in the body is the head you measured. ${GATE}
Post your verdict as a PR comment beginning "Fix review: merge" or "Fix review: blocked — <why>", with your RESULT lines. Return {verdict, comment}.`

phase('Wave')

const promises = {}
let mergeChain = Promise.resolve(null)

// One merge at a time, main waited on after each, so two movers never land
// together. Shared by the normal path and by a group resuming at stage 'merge'.
const mergeGroup = async (g, fix) => {
  const outcome = await (mergeChain = mergeChain.then(async () => {
    const m = await agent(mergePrompt(fix.pr, fix.head_sha), { model: 'opus', label: `merge ${g.group}`, phase: 'Wave', schema: MERGE })
    if (!m?.merged) return { merged: false, reason: m?.reason ?? 'merge agent returned null' }
    const gate = await agent(waitMainPrompt(m.sha), { model: 'sonnet', label: `main after ${g.group}`, phase: 'Wave', schema: { type: 'object', required: ['green'] } })
    return { merged: true, sha: m.sha, green: !!gate?.green, red: gate?.green ? null : gate }
  }))
  if (outcome.merged && !outcome.green) log(`MAIN IS RED after ${g.group} (${outcome.sha}) -- stop and repair before the next merge: ${JSON.stringify(outcome.red)}`)
  return { group: g.group, issues: g.issues, pr: fix.pr, head_sha: fix.head_sha, verdict: 'merge', ...outcome }
}

const runGroup = async (g) => {
  const deps = await Promise.all((g.after ?? []).map((d) => promises[d] ?? Promise.resolve(null)))
  const unmet = (g.after ?? []).filter((d, i) => !deps[i]?.merged)
  if (unmet.length) return { group: g.group, issues: g.issues, pr: null, merged: false, reason: `dependency not merged: ${unmet.join(', ')}` }

  const fm = g.fixerModel ?? 'opus'
  const rm = g.reviewerModel ?? 'opus'
  const ef = g.effort ?? 'high'
  const FIX = { type: 'object', required: ['pr', 'head_sha'],
    properties: { pr: { type: ['integer', 'null'] }, head_sha: { type: ['string', 'null'] } } }
  const VERDICT = { type: 'object', required: ['verdict'] }

  // A group whose PR is already open -- because an earlier run of this wave was
  // killed after the fixer finished -- starts at the ADVERSARIAL REVIEWER. Re-running
  // a finished fixer redoes the work and, worse, hands the reviewer a head nobody
  // measured. Set resume: {stage:'review', pr, head_sha} on the group to do that;
  // resume: {stage:'fix', pushed_sha, what, missing} instead tells a fixer it is
  // continuing from a pushed branch rather than starting clean.
  // stage 'done': already merged. It stays in the roster so the group list is
  // complete, but running it again would re-open finished work.
  if (g.resume?.stage === 'done') {
    log(`${g.group}: already merged as PR #${g.resume.merged_pr} (${g.resume.merge_sha}) -- skipping`)
    return { group: g.group, issues: g.issues, pr: g.resume.merged_pr, head_sha: g.resume.merge_sha,
      verdict: 'merge', merged: true, green: true, sha: g.resume.merge_sha, skipped: 'already merged' }
  }
  let fix
  // stage 'merge': a reviewer already returned merge at THIS head, so re-reviewing
  // spends a reviewer to re-derive a verdict that is already on the PR.
  if (g.resume?.stage === 'merge') {
    fix = { pr: g.resume.pr, head_sha: g.resume.head_sha }
    log(`${g.group}: resuming at merge -- PR #${fix.pr} at ${fix.head_sha} is already reviewed`)
    return await mergeGroup(g, fix)
  }
  if (g.resume?.stage === 'review') {
    fix = { pr: g.resume.pr, head_sha: g.resume.head_sha }
    log(`${g.group}: resuming at review -- PR #${fix.pr} at ${fix.head_sha}`)
  } else {
    fix = await agent(fixerPrompt(g), { model: fm, effort: ef, label: `fix ${g.group}`, phase: 'Wave', schema: FIX })
    // Number.isInteger, not truthiness: a fixer that returns its excuse as the pr
    // field satisfies the schema, and `!fix.pr` is false for a non-empty string.
    if (!Number.isInteger(fix?.pr)) {
      if (fix?.pr) log(`${g.group}: no usable PR number (${JSON.stringify(fix.pr).slice(0, 160)}) -- retrying`)
      fix = await agent(fixerPrompt(g), { model: fm, effort: ef, label: `fix ${g.group} (retry)`, phase: 'Wave', schema: FIX })
    }
    if (!Number.isInteger(fix?.pr)) return { group: g.group, issues: g.issues, pr: null, head_sha: fix?.head_sha ?? null,
      merged: false, reason: `fixer opened no PR after one retry: ${JSON.stringify(fix?.pr ?? null).slice(0, 300)}` }
  }

  let review = await agent(reviewerPrompt(g, fix, 1), { model: rm, effort: 'high', label: `review ${g.group}`, phase: 'Wave', schema: VERDICT })
  if (review && review.verdict !== 'merge') {
    const repaired = await agent(fixerPrompt(g, review.comment ?? review.verdict), { model: fm, effort: ef, label: `repair ${g.group}`, phase: 'Wave', schema: FIX })
    if (repaired?.head_sha) {
      fix = repaired
      review = await agent(reviewerPrompt(g, fix, 2), { model: rm, effort: 'high', label: `re-review ${g.group}`, phase: 'Wave', schema: VERDICT })
    }
  }
  if (review?.verdict !== 'merge') {
    log(`${g.group}: not merged -- ${review?.verdict ?? 'reviewer returned null'}`)
    return { group: g.group, issues: g.issues, pr: fix.pr, head_sha: fix.head_sha, verdict: review?.verdict ?? null, merged: false }
  }

  return await mergeGroup(g, fix)
}

for (const g of groups) promises[g.group] = runGroup(g)
const settled = await parallel(groups.map((g) => () => promises[g.group]))
const results = settled.map((r, i) => r ?? { group: groups[i].group, issues: groups[i].issues, pr: null, merged: false, reason: 'group threw' })
const merged = results.filter((r) => r.merged)
log(`wave done: ${merged.length} merged, ${results.length - merged.length} outstanding`)
return { results, merged, redMain: results.some((r) => r.merged && !r.green) }
