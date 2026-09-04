// One stamp per wave, then the wave's record on #201 and in the two
// planning documents. See .claude/workflows/web-fragments.md for the shared
// prompt block below, which is hand-copied into every web-*.js.
export const meta = {
  name: 'web-stamp',
  description: 'Stamp main once for everything merged since the last tag, then record the wave on #201 and in the plan of record',
  phases: [{ title: 'Stamp' }, { title: 'Record' }],
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
which has already happened once. Under it run
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
// One stamp for everything merged since the last tag, then the wave's record.
// Invoked once per wave (once per stage in the decomposition program), never
// concurrently with itself: stamp.py refuses a tag that exists, a red gate,
// and notes that omit a merged PR, and this script refuses a main that is
// already tagged.
//
//   Workflow({name: 'web-stamp', args: {repo, bump, title, wave, merged: [...]}})
// ---------------------------------------------------------------------------

const { repo, bump = 'patch', title, wave, session = 'claude-web', merged = [] } = args ?? {}
if (!repo || !title) throw new Error('args.repo and args.title are required')

phase('Stamp')
const lastSha = merged.filter((m) => m?.sha).map((m) => m.sha).pop()
if (lastSha) {
  const gate = await agent(waitMainPrompt(lastSha), { model: 'sonnet', label: 'main gate', phase: 'Stamp', schema: { type: 'object', required: ['green'] } })
  if (!gate?.green) { log(`main is not green at ${lastSha}; not stamping`); return { gate } }
}
const stamp = await agent(stampPrompt(repo, bump, title), { model: 'opus', effort: 'high', label: 'stamp', phase: 'Stamp', schema: { type: 'object', required: ['stamped'] } })
if (!stamp?.stamped) log(`not stamped: ${stamp?.reason ?? 'stamp agent returned null'}`)

phase('Record')
const record = await agent(`Record wave ${wave} of the open-issues program. ${GH} ${WT('claude-web/record-wave-' + wave, 'origin/main')}
These groups merged: ${JSON.stringify(merged)}. The release is ${stamp?.version ? 'v' + stamp.version : 'not stamped yet'}.
Update docs/plan-2026-09-open-issues.md's Delivery status table (each wave row gets its release and a status; add a per-issue line where the row is now partly delivered). Update docs/audit-2026-09.md: set each finding's status cell to "fixed (PR #N)" or "released (vX.Y.Z)" -- where a status cell and a body paragraph disagree, the cell is the truth, so change the cell. Open the pull request (docs are INERT, so the gate scopes to almost nothing; still run PYTHONPATH=tests/hastub python3 tests/entities.py, which checks that no tracked file is unclassified) and merge it once its checks are green.
Then post one comment on issue #201: a table of group, issues, PR, verdict and release for this wave, and one paragraph on anything that surprised you -- a correction to a brief, a number that did not reproduce, a rule that bit. Return {pr, comment_url}.`,
  { model: 'sonnet', effort: 'medium', label: 'record', phase: 'Record', schema: { type: 'object', required: ['pr'] } })

return { stamp, record }
