// One fix PR group: a fixer in its own worktree under tools/audit/briefs/fixer.md,
// then an adversarial fix reviewer under fix-review.md. The merge is a separate
// /audit-merge invocation so that a sign-off can sit between them. The fixer
// and reviewer each carry their own model tier and a shared effort; a
// reviewer weaker than its fixer is refused before either agent runs.
//
//   /audit-fix with args {group: "B3", issues: [168, 169], repo: "<abs path>", baseline: "<sha>", fixerModel: "opus", reviewerModel: "opus", effort: "high"}
export const meta = {
  name: 'audit-fix',
  description: 'Implement one PR group under the fix protocol, then review it adversarially',
  phases: ['Fix', 'Review'],
}
const { group, issues = [], repo, baseline, fixerModel = 'opus', reviewerModel = 'opus', effort = 'high' } = args ?? {}
if (!group || !issues.length || !repo) throw new Error('args.group, args.issues and args.repo are required')

// Model tier only, independent of effort: a reviewer below the fixer's tier
// cannot be trusted to catch what the fixer missed.
const RANK = { haiku: 0, sonnet: 1, opus: 2, fable: 3 }
if (RANK[reviewerModel] < RANK[fixerModel]) throw new Error('a reviewer below the fixer measures nothing')

phase('Fix')
// This prompt is hand-mirrored (not imported — see .claude/workflows/audit-wave.js's
// header comment for why) as the per-group fixer prompt in audit-wave.js.
const fix = await agent(
  `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${group.toLowerCase()} origin/main (if the branch exists, check it out instead). Read tools/audit/briefs/fixer.md and tools/audit/README.md and follow every step: failing test first importing the production symbol, mutation proof with pasted failing check names, before/after with the finding's harness at head (state the head SHA), null control and both-ends checks where the brief demands them, claims written by you only for drift you measured, GATE_SCOPE=auto ./tests/run.sh through /tmp/hpo-gate.lock (mkdir), never VERSION/manifest/notes heading. Read each issue with gh issue view for the finding and its register row. Push and open a PR whose body closes the issues and carries every number and the head SHA. Return {pr, head_sha, summary}.`,
  { model: fixerModel, effort, label: `fix ${group}`, schema: { type: 'object', required: ['pr', 'head_sha'] } },
)

if (!fix?.pr) throw new Error('fixer returned no PR (agent null or refused); relaunch')

phase('Review')
// Mirrored in audit-wave.js's per-group reviewer prompt; keep both in sync by hand.
const review = await agent(
  `You are the adversarial fix reviewer for PR #${fix.pr} (group ${group}). From ${repo}: git fetch origin; git worktree add ../audit-review-${group} ${fix.head_sha}. Read tools/audit/briefs/fix-review.md and follow it: re-run the mutation proof, measure with the finder's harness at ${baseline ?? 'origin/main before the PR'} and at ${fix.head_sha} printing your own RESULT lines, re-run null controls, compare claim files against env_drift.py --all (and card_drift.mjs for card changes) at the merge base, check VERSION/manifest/notes untouched, attack the fix at other configurations, confirm the head SHA in the body. Post your verdict as a PR comment (gh pr comment) beginning "Fix review: merge" or "Fix review: blocked — <why>", with the RESULT lines. Return {verdict, comment_url}.`,
  { model: reviewerModel, effort, label: `review ${group}`, schema: { type: 'object', required: ['verdict'] } },
)
return { fix, review }
