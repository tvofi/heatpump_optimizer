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
```

## Substitutions for a session running outside the original container

The canonical `GH`/`GATE`/`WT` blocks above are left unedited on purpose — the
five `web-*.js` scripts each carry their own copy by hand, and
`check-wave-script.mjs`'s recorded fixtures pin those scripts' text, so editing
the canonical copy here without editing all five would desynchronise them for
no reason. A session running on the owner's own Mac instead of the original
4-core container substitutes exactly two things, and the substitution does not
change the control flow of any `web-*.js` script.

**1. The `GH` block's premise is false here.** "No `gh` CLI exists in this
environment" does not hold on the owner's machine, which has `gh` 2.98
authenticated as `tvofi`. Use these equivalents in place of the named MCP
tools:

| MCP tool (as `GH` names it) | `gh` CLI equivalent |
|---|---|
| `issue_read` (get / get_comments) | `gh issue view N --comments` / `gh issue view N --json body,comments,labels` |
| `add_issue_comment` | `gh issue comment N --body-file <file>` |
| `issue_write` (labels, state) | `gh issue edit N --add-label X --remove-label Y`; `gh issue close N --reason completed\|"not planned"` |
| `create_pull_request` | `gh pr create --base main --head <branch> --title ... --body-file <file>` |
| `update_pull_request` | `gh pr edit N --body-file <file>` |
| `pull_request_read` (get, get_check_runs, get_comments, get_files, get_diff) | `gh pr view N --json number,state,headRefOid,mergeable,mergeStateStatus,body,comments,files`; `gh pr diff N`; `gh pr checks N` |
| `merge_pull_request` (squash) | `gh pr merge N --squash --delete-branch` |
| `actions_list` (list_workflow_runs) | `gh run list --branch <branch> --workflow tests.yml --json databaseId,headSha,status,conclusion,createdAt` |
| `actions_get` | `gh run view <id> --json jobs` |
| `get_job_logs` (failed_only) | `gh run view <id> --log-failed` |

**2. The `WT` block's worktree root is a parameter, not a constant.** It is
`/home/user/wt/` in the original container and `/Users/timmalmstrom/wt/` on the
owner's Mac. A brief names the root for its own run; an agent never hard-codes
the other one.

Keep this short and factual, and keep it in sync only with the two lines above
— it does not need to grow every time a new machine runs this programme.
