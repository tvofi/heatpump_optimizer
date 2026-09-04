// Phase 0 of the open-issues program: make stamping possible in this
// container, then land the two pull requests that were left green and
// unreviewed, then take the overdue release.
// See .claude/workflows/web-fragments.md for the shared prompt block.
export const meta = {
  name: 'web-phase0',
  description: 'Land the stamp REST fallback, refresh and review the two open PRs, merge them and take the overdue stamp',
  phases: [{ title: 'Stamp fallback' }, { title: 'Refresh and review' }, { title: 'Merge' }, { title: 'Stamp' }],
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
nor manifest.json nor the RELEASE_NOTES.md heading. Then, so the owner label means IN-FLIGHT rather than ever-touched, remove owner:${session} from every issue this PR closes (issue_write update, keeping the other labels) -- a label that is only ever added cannot answer the question a resuming session actually asks. Then merge_pull_request
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
// Phase 0. Two pull requests are green and unreviewed, eight merges are
// unstamped, and stamp.py cannot run in this container at all -- its rule 2
// shells out to gh before any flag is read. Nothing else can start: the
// fixture-mover among the two empties the claim files only when a stamp runs,
// and a branch cut from a main that still carries claims fails
// inherited_claims_error.
//
//   Workflow({name: 'web-phase0', args: {repo, session, prs, bump, title}})
//   prs: [{pr, head, fixture}] in merge order
// ---------------------------------------------------------------------------

const { repo, session = 'claude-web', prs = [], bump = 'patch', title } = args ?? {}
if (!repo || !prs.length || !title) throw new Error('args.repo, args.prs and args.title are required')

phase('Stamp fallback')
const fb = await agent(`tools/release/stamp.py cannot run in this container and every release in this program is blocked behind it. Rule 2 (around line 194) calls gh run list unconditionally, BEFORE --allow-red is consulted, so a missing binary raises FileNotFoundError rather than a Refuse; gh is not installed here and cannot be installed. ${GH} ${WT('claude-web/stamp-rest-fallback', 'origin/main')} ${DOC(session)}
Make rule 2 use gh when it is present and otherwise query the REST API directly with urllib: GET https://api.github.com/repos/tvofi/heatpump_optimizer/actions/runs?head_sha=<sha>&event=push, selecting the run whose workflow is Tests, sending Authorization: Bearer with GH_TOKEN when that variable is set (the repository is public, so the unauthenticated path must work too). The refusal semantics must be IDENTICAL on both paths -- same rule number, same message shape, same --allow-red override -- because the point of rule 2 is that a release never publishes ahead of the unscoped gate.
This file's own test has never run (#372 is open about exactly that), so the fallback has to be covered by --self-test: add checks for the pure pieces you can test without the network -- the URL the query builds, how a runs payload is reduced to a conclusion, and which branch is taken when gh is absent. Then execute, and paste into the PR body: python3 tools/release/stamp.py --self-test; python3 tools/release/stamp.py --bump patch --title probe --dry-run at origin/main showing rule 2 evaluating rather than raising; and the same with a broken REST branch showing the refusal.
tools/ is INERT, so the gate scopes to almost nothing -- run PYTHONPATH=tests/hastub python3 tests/entities.py anyway (it checks that every tracked file is classified). Do not change VERSION, the manifest or the notes heading; do not stamp anything. Open the PR with Part of #201 (it closes no issue; #372 will wire the self-test into a lane later). Return {pr, head_sha}.`,
  { model: 'opus', effort: 'high', label: 'stamp fallback', phase: 'Stamp fallback', schema: { type: 'object', required: ['pr', 'head_sha'] } })
if (!fb?.pr) throw new Error('stamp fallback produced no PR; nothing downstream can stamp')

const fbReview = await agent(`You are the adversarial reviewer for PR #${fb.pr} (head ${fb.head_sha}), which teaches tools/release/stamp.py to check the gate without the gh CLI. ${GH} ${WT_REVIEW('stamp-fallback', fb.head_sha)}
This tool is the only way a version is assigned in this repository and it refuses rather than warns, so a fallback that silently answers "green" would be worse than the breakage it fixes. Check: --self-test passes and its new checks actually fail when you break the piece they cover; --dry-run at origin/main reaches rule 2 with GH_TOKEN set and unset; a REST response that reports failure, and one that reports no run at all, both REFUSE with the same message shape gh would have produced; --allow-red still overrides on both paths; nothing outside tools/ changed; VERSION, the manifest and the notes heading are untouched. ${GATE}
Post "Fix review: merge" or "Fix review: blocked — <why>" with your RESULT lines. Return {verdict, comment}.`,
  { model: 'opus', effort: 'high', label: 'review fallback', phase: 'Stamp fallback', schema: { type: 'object', required: ['verdict'] } })
if (fbReview?.verdict !== 'merge') { log(`stamp fallback blocked: ${fbReview?.verdict}`); return { fb, fbReview } }
const fbMerge = await agent(mergePrompt(fb.pr, fb.head_sha), { model: 'opus', label: 'merge fallback', phase: 'Stamp fallback', schema: MERGE })
if (!fbMerge?.merged) { log(`stamp fallback not merged: ${fbMerge?.reason}`); return { fb, fbReview, fbMerge } }
const fbGate = await agent(waitMainPrompt(fbMerge.sha), { model: 'sonnet', label: 'main after fallback', phase: 'Stamp fallback', schema: { type: 'object', required: ['green'] } })
if (!fbGate?.green) { log('main not green after the stamp fallback'); return { fb, fbReview, fbMerge, fbGate } }

phase('Refresh and review')
// Both bodies name a head SHA that is no longer the head -- #367 was rebased
// and then partly reverted, #368 merged main -- and fix-review.md step 7
// makes a strict reviewer block on exactly that. So the evidence is
// re-executed at the real head first, as the fixer contract requires after
// any rebase.
const reviewed = await parallel(prs.map((p) => () => (async () => {
  const refresh = await agent(`You re-execute the fixer contract on an existing pull request whose evidence describes an older tree. PR #${p.pr}, current head ${p.head}; its body names an earlier SHA. ${GH} ${WT_REVIEW('refresh-' + p.pr, p.head)}
Read the PR body and tools/audit/briefs/fixer.md steps 2 to 4, then re-execute them at ${p.head}: re-run the mutation proof and paste the failing check names; re-run the finding's harness before and after; ${p.fixture ? 'run env_drift.py --all against the merge base and confirm every claimed fixture moved and every moved fixture is claimed;' : 'run env_drift.py --all and confirm nothing drifted and both claim files are byte-identical to origin/main;'} run python3 tests/structure.py against origin/main's budgets and report the headroom or the loosening. ${GATE}
Then update the pull request body (update_pull_request) so the head SHA and every number describe ${p.head}. ${p.pr === 367 ? 'Note in particular: this branch re-recorded cross_seam_fraction and then reverted that line in a later commit, so the body paragraph describing the re-record is now wrong -- rewrite it to describe what the head actually does.' : ''}
Change no code unless a number you re-measured contradicts the fix itself; if one does, say so and stop. Return {pr, head_sha, updated, numbers}.`,
    { model: 'opus', effort: 'high', label: `refresh #${p.pr}`, phase: 'Refresh and review', schema: { type: 'object', required: ['pr', 'head_sha'] } })
  const head = refresh?.head_sha ?? p.head
  const review = await agent(`You are the adversarial fix reviewer for PR #${p.pr} (head ${head}), in a fresh context. ${GH} ${WT_REVIEW('pr-' + p.pr, head)}
Read tools/audit/briefs/fix-review.md and follow every step: re-run the mutation proof and confirm the named checks fail; measure with the FINDER's harness rather than the fixer's, at the merge base and at ${head}, printing your own RESULT lines; re-run the null control and the both-ends check; ${p.fixture ? 'run env_drift.py --all against the merge base -- every moved fixture claimed, every claim moved, no may-drift fixture claimed -- and confirm tests/structure_budgets.json is byte-identical to origin/main;' : 'confirm no fixture moved and both claim files are byte-identical to origin/main;'} check VERSION, the manifest and the notes heading are untouched; attack the fix at other configurations; confirm the head SHA in the body is the head you measured. ${GATE}
Post "Fix review: merge" or "Fix review: blocked — <why>" as a PR comment with your RESULT lines. Return {verdict, comment}.`,
    { model: 'opus', effort: 'high', label: `review #${p.pr}`, phase: 'Refresh and review', schema: { type: 'object', required: ['verdict'] } })
  return { ...p, head, verdict: review?.verdict ?? null, comment: review?.comment ?? null }
})()))

phase('Merge')
const merged = []
let lastSha = fbMerge.sha
for (const p of reviewed.filter(Boolean)) {          // args order: the fixture-neutral PR first
  if (p.verdict !== 'merge') { log(`#${p.pr} blocked, not merged: ${p.comment ?? p.verdict}`); continue }
  const m = await agent(mergePrompt(p.pr, p.head), { model: 'opus', label: `merge #${p.pr}`, phase: 'Merge', schema: MERGE })
  if (!m?.merged) { log(`#${p.pr} not merged: ${m?.reason}`); continue }
  lastSha = m.sha
  merged.push({ group: `PR #${p.pr}`, issues: p.issues ?? [], pr: p.pr, sha: m.sha })
}

phase('Stamp')
const gate = await agent(waitMainPrompt(lastSha), { model: 'sonnet', label: 'main gate', phase: 'Stamp', schema: { type: 'object', required: ['green'] } })
if (!gate?.green) { log('main is not green; not stamping'); return { fb, reviewed, merged, gate } }
const stamp = await agent(stampPrompt(repo, bump, title), { model: 'opus', effort: 'high', label: 'stamp', phase: 'Stamp', schema: { type: 'object', required: ['stamped'] } })
log(stamp?.stamped ? `stamped v${stamp.version}` : `not stamped: ${stamp?.reason}`)
return { fb, fbMerge, reviewed, merged, gate, stamp }
