// Triage: one judge per measure-first issue, closing it on a number or
// rewriting its proposed fix so the wave that follows has a correct brief.
// See .claude/workflows/web-fragments.md for the shared prompt block.
export const meta = {
  name: 'web-triage',
  description: 'Re-measure each measure-first issue at current main, then close it with the number or re-scope its body',
  phases: [{ title: 'Judge', detail: 'one judge per issue; timing judges run alone' }],
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
BLAS thread variables pinned to 1. One gate at a time: mkdir
/tmp/hpo-gate.lock and write an owner file (your label, pid, UTC); if it
exists, read it and check the pid, then wait and retry -- never remove a lock
you did not create. Under the lock: GATE_SCOPE=auto GOLDEN_MODE=drift
GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh; release with
rm -rf (not rmdir: the owner file makes it non-empty). tests/stress.py only
under the lock, with the concurrent-process count beside every timing RESULT.
Browser lane: NODE_PATH=/opt/node22/lib/node_modules
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs
(indicative only; CI's browser job decides). CI fast + closures + browser on
the PR are the authority; wait for them with actions_list. Value-bearing
golden fixtures are never re-recorded on this box: value drift is claimed;
golden.py --record --only is for new key paths, and the body says so.`

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
// Judges, not fixers. Each issue here rests on a number that has moved, or on
// a mechanism a later release already changed, so spending a fixer on it
// would implement a superseded plan. One judge per issue re-measures at
// current main, runs the perturbation, and either closes the issue with the
// number or rewrites its proposed-fix section so the fix wave has a correct
// brief.
//
// An issue marked quiet: true carries a timing number and runs ALONE -- the
// box has no idle window while other agents work, and a timing RESULT taken
// under load measures the box.
//
//   Workflow({name: 'web-triage', args: {repo, session, issues: [...]}})
//   issue: {issue, expect, quiet, extra}
// ---------------------------------------------------------------------------

const { issues = [], repo, session = 'claude-web' } = args ?? {}
if (!issues.length || !repo) throw new Error('args.issues and args.repo are required')

const judgePrompt = (it) => `You are the judge for issue #${it.issue} of the open-issues program, working from tools/audit/briefs/judge.md. You do not trust the finder or the verifiers; you re-measure. ${GH} ${WT_REVIEW('triage-' + it.issue, 'origin/main')}
Read the issue body AND every comment: the comments carry judge verdicts, corrections and claims that override the body.
What the plan of record expects, which you may confirm or overturn with a number: ${it.expect}
${it.extra ?? ''}
Method: re-run the finding's harness from the ref that carries it -- most round-2 harnesses are NOT on main, they are at tag audit-round2-evidence (757e164); copy a harness into the tree under test before running it, because they disagree about how they find the repository root, and say in your verdict which root rule it used. Run the finding's perturbation: if the number does not move in the stated direction the harness is void and the finding is unreproduced whatever anyone voted. Re-run leave-one-out for an aggregate and the null control for any cost, gain or time claim. ${GATE}
On this box load1 never reaches the brief's 1.5 (the ambient floor is higher), so quote the load1 and thread_factor you measured and rest the verdict on ratio metrics and the null control rather than waiting for a quiet window that never comes.
Then act, and say which you did:
 - if the finding is fixed, superseded or refuted: comment the number and the reasoning, then close the issue (issue_write update, state closed, state_reason completed for fixed/superseded, not_planned for a decision or an accepted limit);
 - if it survives but its body is wrong: rewrite the body, preserving the original under a "## Superseded (original text)" heading and putting your corrected claim and proposed fix above it, so the fixer who reads it next cannot implement the old plan. Leave it open.
Never start coding a fix. Return {issue, verdict, action, headline, brief}, where action is "closed" or "rescoped" and brief is the two-to-four-sentence corrected instruction a fixer should receive (empty when closed).`

phase('Judge')
const loud = issues.filter((i) => !i.quiet)
const quiet = issues.filter((i) => i.quiet)
const SCHEMA = { type: 'object', required: ['issue', 'verdict', 'action'] }

const loudVerdicts = await parallel(loud.map((it) => () =>
  agent(judgePrompt(it), { model: 'opus', effort: 'high', label: `judge #${it.issue}`, phase: 'Judge', schema: SCHEMA })))

// The quiet ones run one at a time, after the others are done, so nothing
// else is on the box while a timing number is taken.
const quietVerdicts = []
for (const it of quiet) {
  quietVerdicts.push(await agent(
    `${judgePrompt(it)}\nYou have the box to yourself for this measurement. Before every timing RESULT, run ps aux | grep -E "[s]tress\\.py|[t]ests/run\\.sh|[p]ython3 tests/" and print the concurrent-process count beside the number; if anything else is running, wait rather than measuring.`,
    { model: 'opus', effort: 'high', label: `judge #${it.issue} (quiet)`, phase: 'Judge', schema: SCHEMA }))
}

const verdicts = [...loudVerdicts, ...quietVerdicts].filter(Boolean)
log(`triage: ${verdicts.filter((v) => v.action === 'closed').length} closed, ${verdicts.filter((v) => v.action === 'rescoped').length} re-scoped, ${issues.length - verdicts.length} returned null`)
return { verdicts, missing: issues.map((i) => i.issue).filter((n) => !verdicts.some((v) => Number(v.issue) === Number(n))) }
