// One fix PR group: a fixer in its own worktree under dev/governance/roles/fixer.md,
// then an adversarial fix reviewer under fix-review.md. The merge is a separate
// invocation so that a sign-off can sit between them. The fixer
// and reviewer each carry their own model tier and a shared effort; a
// reviewer weaker than its fixer is refused before either agent runs.
//
//   /audit-fix with args {group: "B3", issues: [168, 169], repo: "<abs path>", baseline: "<sha>", fixerModel: "opus", reviewerModel: "opus", effort: "high"}
export const meta = {
  name: 'audit-fix',
  description: 'RETIRED: Implement one PR group under the fix protocol, then review it adversarially',
  phases: ['Fix', 'Review'],
}
const { group, issues = [], repo, baseline, fixerModel = 'opus', reviewerModel = 'opus', effort = 'high' } = args ?? {}
if (!group || !issues.length || !repo) throw new Error('args.group, args.issues and args.repo are required')
// The base (tools/audit/seat/base_fresh.py; dev/audit/rca/R11-RCA-PLAN-OBJECTIVE-MISSING.md). The run's first
// seat judges the tree its seats read policy, instruments and workflow scripts from, and one that is not
// origin/main's refuses the launch. A reply without the field is one its schema refuses in a run; under a
// driver whose stub predates the field it is unmeasured, never read as a pass by the checker that pins this.
const BASE_FRESH = (dir) => `Before anything else, run \`python3 -I ${repo}/tools/audit/seat/base_fresh.py tree --dir ${dir}\` and return the last line it prints, verbatim, as base_fresh. If that line does not start with "BASE-FRESH PASS", do nothing else: return base_fresh, and every other field as the empty value of its type.`
const baseGate = (reply, dir) => {
  if (reply?.base_fresh !== undefined && !String(reply.base_fresh).startsWith('BASE-FRESH PASS')) throw new Error(`base_fresh.py refuses ${dir}: ${reply.base_fresh} -- its policy, instruments or workflows are not origin/main's. Run python3 -I tools/audit/seat/base_fresh.py ensure --dir ${dir} (a checkout that carries no work), or merge origin/main into its branch, then relaunch so the run loads main's script`)
}

// Model tier only, independent of effort: a reviewer below the fixer's tier
// cannot be trusted to catch what the fixer missed.
const RANK = { haiku: 0, sonnet: 1, opus: 2, fable: 3 }
if (RANK[reviewerModel] < RANK[fixerModel]) throw new Error('a reviewer below the fixer measures nothing')

phase('Fix')
// This prompt is hand-mirrored (not imported — see .claude/workflows/audit-wave.js's
// header comment for why) as the per-group fixer prompt in audit-wave.js.
const fix = await agent(
  `${BASE_FRESH(repo)} You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${group.toLowerCase()} origin/main (if the branch exists, check it out instead). Read dev/governance/roles/fixer.md and dev/audit/README.md and follow every step: failing test first importing the production symbol, mutation proof with pasted failing check names, before/after with the finding's harness at head (state the head SHA), null control and both-ends checks where the brief demands them, claims written by you only for drift you measured, GATE_SCOPE=auto ./tests/run.sh under python3 tests/gate_lock.py take/renew/release with HPO_GATE_LOCK_LABEL set (never mkdir and a shell pid -- #404) and only when the closure selection is MODE: FULL or names tests/stress.py, never VERSION/manifest/notes heading. Read each issue with gh issue view for the finding and its register row. Push and open a PR whose body closes the issues and carries every number and the head SHA. Return {base_fresh, pr, head_sha, summary}.`,
  { model: fixerModel, effort, label: `fix ${group}`, schema: { type: 'object', required: ['base_fresh', 'pr', 'head_sha'] } },
)

baseGate(fix, repo)
if (!fix?.pr) throw new Error('fixer returned no PR (agent null or refused); relaunch')

phase('Review')
// Mirrored in audit-wave.js's per-group reviewer prompt; keep both in sync by hand.
const review = await agent(
  `You are the adversarial fix reviewer for PR #${fix.pr} (group ${group}). From ${repo}: git fetch origin; git worktree add ../audit-review-${group} ${fix.head_sha}. Read dev/governance/roles/fix-review.md and follow it: re-run the mutation proof, measure with the finder's harness at ${baseline ?? 'origin/main before the PR'} and at ${fix.head_sha} printing your own RESULT lines, re-run null controls, compare claim files against env_drift.py --all (and card_drift.mjs for card changes) at the merge base, check VERSION/manifest/notes untouched, attack the fix at other configurations, confirm the head SHA in the body. Post your verdict as a PR comment (gh pr comment) beginning "Fix review: merge" or "Fix review: blocked — <why>", with the RESULT lines. Return {verdict, comment_url}.`,
  { model: reviewerModel, effort, label: `review ${group}`, schema: { type: 'object', required: ['verdict'] } },
)
return { fix, review }
