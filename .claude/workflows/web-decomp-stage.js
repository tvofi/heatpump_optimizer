// One stage of the #193 decomposition program: survey the seam, move it
// verbatim, review the move adversarially, merge. Stamping is a separate
// web-stamp run, because every stage moves the budget table.
// See .claude/workflows/web-fragments.md for the shared prompt block.
export const meta = {
  name: 'web-decomp-stage',
  description: 'Survey, move, adversarially review and merge one seam of the coordinator decomposition program',
  phases: [{ title: 'Measure' }, { title: 'Move' }, { title: 'Review' }, { title: 'Merge' }],
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
wait and retry -- NEVER remove a lock you did not create. Under it run
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
// One stage of the #193 decomposition program. Move, don't rewrite: bodies
// land byte-identical, goldens compare clean with an empty claim list, stress
// ratios hold. The reviewer's job is the one CI cannot do -- diff the moved
// block against origin/main rather than against the text it was cut from,
// because a fix that landed inside the relocated lines reverts SILENTLY: no
// conflict, no failing test, since the reverted state is what the tests were
// written against.
//
//   Workflow({name: 'web-decomp-stage', args: {repo, fork, session, stage}})
//   stage: {name, issues, brief, holds, budgets}
// ---------------------------------------------------------------------------

const { repo, fork, session = 'claude-web', stage } = args ?? {}
if (!repo || !fork || !stage?.name || !stage?.brief) throw new Error('args.repo, args.fork and args.stage {name, brief} are required')
const issues = stage.issues ?? []

phase('Measure')
const survey = await agent(`Before stage ${stage.name} of the coordinator decomposition program (#193) is cut, re-measure the seam table so the stage is still the cheapest remaining cut rather than the one the plan guessed months ago. ${GH} ${WT_REVIEW('survey-' + stage.name, fork)}
Run python3 tests/structure.py and record every cut_* metric and the class sizes. Then copy tools/audit/round2/D7/coordinator_clusters.py from tag audit-round2-evidence (757e164) into the tree under test and run it for the attribute co-usage graph, the hub attributes by fan-in and the minimum-cut search. ${GATE}
Report: the measured cut cost of the seam this stage proposes; the three cheapest alternatives; the live-in variable count across the proposed boundary (this is what decides, not line count -- a seam whose extraction needs fifteen parameters is a monolith with an argument list in front of it, and two earlier stages were re-planned for exactly that); and whether any of these still hold: ${JSON.stringify(stage.holds ?? [])}.
Return {proceed, cut_cost, live_ins, cheaper_alternatives, note} -- proceed false if the seam is no longer the right cut or a hold is unmet, with the reason in note.`,
  { model: 'opus', effort: 'high', label: `survey ${stage.name}`, phase: 'Measure', schema: { type: 'object', required: ['proceed'] } })

if (!survey?.proceed) { log(`stage ${stage.name} not cut: ${survey?.note ?? 'survey returned null'}`); return { survey } }
if (survey.live_ins !== undefined && survey.live_ins > 8) log(`stage ${stage.name}: ${survey.live_ins} live-in variables across the boundary -- this wants a carrier object and its own design argument, not a verbatim move`)

phase('Move')
const fix = await agent(`You own stage ${stage.name} of the coordinator decomposition program (#193)${issues.length ? `, which advances issues #${issues.join(', #')}` : ''}. ${GH} ${WT('claude-web/decomp-' + stage.name.toLowerCase(), fork)} ${DOC(session)}
The plan of record is #193's own comment as amended by the round-2 panel and the 2026-09-03 seam measurements; your stage:
${stage.brief}
The survey just measured: cut cost ${survey.cut_cost ?? 'n/a'}, ${survey.live_ins ?? 'n/a'} live-in variables across the boundary. ${survey.note ?? ''}
Ground rules, and they are the whole safety argument for moving eleven thousand lines behind a differential gate:
 - MOVE, DON'T REWRITE. Method bodies land byte-identical -- not byte-identical-after-dedent. Verify by extracting each moved range and comparing it to the pre-move text, and say so in the body. The plan goldens compare at six decimals and a retyped float expression moves the last one.
 - The facade rule holds until the final stage: HeatPumpOptimizerCoordinator, COP_LEARNING_MAX_STEP, HOUSE_LOSS_MAX_STEP, PLAN_STALE_FLOOR_MINUTES, SOLVE_FAILURE_ISSUE_COUNT and house_loss_confidence stay importable from heatpump_optimizer.coordinator, and every test-poked private name keeps resolving on the class or instance through a one-line delegate seam.
 - State moves with its methods. A cross-seam reference becomes an explicit parameter where that is cheap and a coordinator back-reference where it is not; the back-reference count is itself ratcheted.
 - _multi_start_minimize stays top-level in optimizer.py: tests/optimality.py mocks it by that path.
 - Ship a re-derived tests/closures.json (./tests/derive_closures.sh, or --single per script) or the closures job turns main red; closure.py no-copies must pass.
 - Keep indirection out of the per-solve hot loops; the stress sweep-ratio headroom is about 1.8x and stress.py is what notices.
 - The budget table: re-record ONLY through the guarded --record, naming in the COMMIT which metrics tightened and why. If the stage would LOOSEN coordinator_loc or max_class_loc, stop and report instead -- that is a decision for the program's owner, not bookkeeping. cross_seam_fraction is never re-recorded.
${stage.budgets ? `Expected budget movement: ${stage.budgets}` : ''}
Run the full local mirror rather than the scoped gate, because a move touches everything: GOLDEN_MODE=drift GATE_SCOPE=full GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh. ${GATE}
Open the PR with the before/after class and method sizes, the byte-identity proof, the budget table diff with each moved metric argued, and Part of #193${issues.length ? ' and Closes #' + issues.join(', Closes #') : ''}. Return {pr, head_sha, summary}.`,
  { model: 'opus', effort: 'high', label: `move ${stage.name}`, phase: 'Move', schema: { type: 'object', required: ['pr', 'head_sha'] } })

if (!fix?.pr) { log(`stage ${stage.name}: no PR`); return { survey, fix } }

phase('Review')
const review = await agent(`You are the adversarial reviewer for decomposition stage ${stage.name}, PR #${fix.pr} (head ${fix.head_sha}), in a fresh context. ${GH} ${WT_REVIEW('decomp-' + stage.name, fix.head_sha)}
Read tools/audit/briefs/fix-review.md, then check the four things that are specific to a move and that CI cannot see:
 1. Every moved block is byte-identical to the block on origin/main -- diff the moved range against ORIGIN/MAIN, not against the PR's own claim. This is the check that catches a silent revert: a fix that merged inside the relocated lines comes back reverted with no conflict and no failing test.
 2. Nothing merged since ${fork} lies inside a moved range. List what merged (git log ${fork}..origin/main) and intersect it with the moved line ranges.
 3. env_drift.py --all against the merge base is byte-identical with an EMPTY claim list, and tests/structure.py passes with every changed budget argued in the commit; no metric loosened without the owner's decision; cross_seam_fraction untouched.
 4. Every facade name still imports from heatpump_optimizer.coordinator, closure.py no-copies passes, tests/closures.json was re-derived rather than hand-edited, and the stress sweep ratio kept its headroom.
${GATE} Post "Fix review: merge" or "Fix review: blocked — <why>" with your RESULT lines. Return {verdict, comment}.`,
  { model: 'opus', effort: 'high', label: `review ${stage.name}`, phase: 'Review', schema: { type: 'object', required: ['verdict'] } })

if (review?.verdict !== 'merge') { log(`stage ${stage.name} blocked: ${review?.verdict ?? 'reviewer returned null'}`); return { survey, fix, review } }

phase('Merge')
const m = await agent(mergePrompt(fix.pr, fix.head_sha), { model: 'opus', label: `merge ${stage.name}`, phase: 'Merge', schema: MERGE })
if (!m?.merged) { log(`stage ${stage.name} not merged: ${m?.reason}`); return { survey, fix, review, merge: m } }
const gate = await agent(waitMainPrompt(m.sha), { model: 'sonnet', label: `main after ${stage.name}`, phase: 'Merge', schema: { type: 'object', required: ['green'] } })
return { survey, fix, review, merge: m, gate, merged: [{ group: stage.name, issues, pr: fix.pr, sha: m.sha }] }
