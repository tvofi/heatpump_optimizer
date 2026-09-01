// One merge, one wait, one stamp. Invoked once per PR so that a relaunch can
// never double-merge or double-stamp: every step checks state before acting.
//
//   /audit-merge with args {pr: 165, bump: "patch", title: "the closures lane and the stamp", repo: "<abs path>"}
export const meta = {
  name: 'audit-merge',
  description: 'Merge one reviewed PR, wait for the unscoped main gate, stamp and tag with tools/release/stamp.py',
  phases: ['Merge', 'Wait for main', 'Stamp'],
}
const { pr, bump = 'patch', title, repo } = args ?? {}
if (!pr || !title || !repo) throw new Error('args.pr, args.title and args.repo are required')

phase('Merge')
const merge = await agent(
  `In ${repo}: gh pr view ${pr} --json state,mergeStateStatus,headRefOid,body,statusCheckRollup. If state is MERGED, return {merged: true, sha: <merge commit from gh pr view --json mergeCommit>} without doing anything. Otherwise refuse (return {merged: false, reason}) unless: every check is SUCCESS or SKIPPED; the body names a measured head SHA equal to headRefOid; the body carries a fix-review verdict of "merge"; git diff origin/main...<head> -- VERSION custom_components/heatpump_optimizer/manifest.json is empty. Then gh pr merge ${pr} --squash --delete-branch and return {merged: true, sha}.`,
  { label: `merge #${pr}`, schema: { type: 'object', required: ['merged'] } },
)
if (!merge?.merged) { log(`not merged: ${merge?.reason ?? 'merge agent returned null'}`); return merge }

phase('Wait for main')
const gate = await agent(
  `In ${repo}: git fetch origin. Find the Tests workflow run for commit ${merge.sha} on main (gh run list --workflow Tests --branch main --commit ${merge.sha} --json databaseId,status,conclusion); if none exists yet wait up to 10 minutes for it to appear, then gh run watch <id> --exit-status with a 2-hour ceiling. Return {green: <bool>, run_id, conclusion, failed_jobs: [..]}.`,
  { label: 'main gate', schema: { type: 'object', required: ['green'] } },
)
if (!gate?.green) { log(`main is not green after #${pr}: ${JSON.stringify(gate)}`); return { merge, gate } }

phase('Stamp')
const stamp = await agent(
  `In ${repo}: git fetch origin && git checkout --detach origin/main (HEAD must equal origin/main). If git tag --list shows a tag whose commit is origin/main already, return {stamped: false, reason: "already stamped"}. Otherwise write the RELEASE_NOTES.md section for the next ${bump} version at the top of the file: heading "## v<next>", a "### <title>" subsection written from PR #${pr}'s body (its executed numbers, mutation output, claims), and one line per other PR merged since the last tag (git log <last-tag>..HEAD --format=%s) so every "(#N)" is mentioned. Then run python tools/release/stamp.py --bump ${bump} --title "${title}" --push. It refuses on its own rules; if it refuses, return {stamped: false, reason: <its message>} and change nothing. Return {stamped: true, version} on success.`,
  { label: 'stamp', schema: { type: 'object', required: ['stamped'] } },
)
return { merge, gate, stamp }
