# The shared prompt fragments for the `web-*.js` workflows

Workflow scripts cannot import each other — every script this repository
ships is evaluated as a function body handed `args`/`agent()`/`phase()`, with
a top-level `return`, so a static `import` would not be legal
(`.claude/workflows/audit-wave.js` records the same finding). The five
`web-*.js` scripts therefore each carry their own copy of the block below,
between the `meta` literal and the first `phase()`.

**Keep the copies in sync by hand.** When one changes, change them all; the
canonical text is here.

```js
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
```
