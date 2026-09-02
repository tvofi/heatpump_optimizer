// Runs the same two phases as audit-fix.js (fixer, then adversarial fix
// reviewer) for many PR groups at once, honoring each group's `after`
// dependencies and scheduling with parallel() in chunks of at most three so
// no more than three groups are mid-fix (or mid-review) at the same time.
//
// The fixer and reviewer prompts below are hand-mirrored from audit-fix.js,
// not imported from a shared module: the four scripts this repo already
// ships (audit-find.js, audit-fix.js, audit-merge.js, audit-verify.js) carry
// no `import` of a sibling file anywhere, and every one of them (this file
// included) is written with a top-level `return`, which is only legal
// syntax inside a function body — this workflow runtime evidently evaluates
// each script as a function body handed `args`/`agent`/`phase`/`log`/
// `pipeline`/`parallel`, not as a loaded ES module, so a static `import`
// would not be legal there either. A `.claude/workflows/lib/audit-prompts.js`
// module was therefore not created; keep the two prompt blocks in sync by
// hand instead. audit-fix.js's Fix and Review phases carry a comment
// pointing back at this file with the same note.
//
// Merges are not run here. Each entry this returns with a `pr` still goes
// through its own separate /audit-merge, exactly as after a solo
// /audit-fix — a wave only parallelizes fix-and-review; the merge queue
// stays one PR at a time (tools/audit/README.md, docs/audit-2026-09.md).
//
//   /audit-wave with args {groups: [{group: "B3", issues: [168, 169], fixerModel: "opus", reviewerModel: "opus", after: []}, {group: "B4", issues: [170], fixerModel: "sonnet", reviewerModel: "opus", after: ["B3"]}], repo: "<abs path>", baseline: "<sha>"}
export const meta = {
  name: 'audit-wave',
  description: 'Fix and adversarially review many PR groups in parallel, honoring after-dependencies; merges stay a separate /audit-merge per PR',
  phases: ['Fix and review'],
}

const { groups = [], repo, baseline, effort: waveEffort = 'high' } = args ?? {}
if (!groups.length || !repo) throw new Error('args.groups and args.repo are required')
for (const g of groups) if (!g.group || !g.issues?.length) throw new Error('every entry in args.groups needs group and issues')

// Same invariant as audit-fix.js, checked for every group before any agent
// runs: a reviewer below the fixer's tier cannot be trusted to catch what
// the fixer missed.
const RANK = { haiku: 0, sonnet: 1, opus: 2, fable: 3 }
for (const g of groups) {
  const fixerModel = g.fixerModel ?? 'opus'
  const reviewerModel = g.reviewerModel ?? 'opus'
  if (RANK[reviewerModel] < RANK[fixerModel]) throw new Error(`${g.group}: a reviewer below the fixer measures nothing`)
}

// Hand-mirrored copy of audit-fix.js's Fix-phase prompt; see the header
// comment above for why this is not a shared import.
const fixerPrompt = (group, issues, repo, baseline) =>
  `You own fix group ${group} of the audit: issues #${issues.join(', #')}. From ${repo}: git fetch origin; git worktree add ../audit-fix-${group} -b claude/audit-fix-${group.toLowerCase()} origin/main (if the branch exists, check it out instead). Read tools/audit/briefs/fixer.md and tools/audit/README.md and follow every step: failing test first importing the production symbol, mutation proof with pasted failing check names, before/after with the finding's harness at head (state the head SHA), null control and both-ends checks where the brief demands them, claims written by you only for drift you measured, GATE_SCOPE=auto ./tests/run.sh through /tmp/hpo-gate.lock (mkdir), never VERSION/manifest/notes heading. Read each issue with gh issue view for the finding and its register row. Push and open a PR whose body closes the issues and carries every number and the head SHA. Return {pr, head_sha, summary}.`

// Hand-mirrored copy of audit-fix.js's Review-phase prompt; same note.
const reviewerPrompt = (group, repo, baseline, fix) =>
  `You are the adversarial fix reviewer for PR #${fix.pr} (group ${group}). From ${repo}: git fetch origin; git worktree add ../audit-review-${group} ${fix.head_sha}. Read tools/audit/briefs/fix-review.md and follow it: re-run the mutation proof, measure with the finder's harness at ${baseline ?? 'origin/main before the PR'} and at ${fix.head_sha} printing your own RESULT lines, re-run null controls, compare claim files against env_drift.py --all (and card_drift.mjs for card changes) at the merge base, check VERSION/manifest/notes untouched, attack the fix at other configurations, confirm the head SHA in the body. Post your verdict as a PR comment (gh pr comment) beginning "Fix review: merge" or "Fix review: blocked — <why>", with the RESULT lines. Return {verdict, comment_url}.`

phase('Fix and review')
const byName = Object.fromEntries(groups.map((g) => [g.group, g]))
const prs = []
const skipped = []
const done = {} // group name -> its resolved outcome object
const pending = new Set(groups.map((g) => g.group))

// One group's Fix then Review, sequentially — the same two phases
// audit-fix.js runs for a single group. A null fixer result is retried
// once; still null, the group is recorded rather than thrown. Same for a
// null reviewer, once the fixer has succeeded.
const runGroup = async (g) => {
  const fixerModel = g.fixerModel ?? 'opus'
  const reviewerModel = g.reviewerModel ?? 'opus'
  const fixSchema = { type: 'object', required: ['pr', 'head_sha'] }

  let fix = await agent(fixerPrompt(g.group, g.issues, repo, baseline), { model: fixerModel, effort: waveEffort, label: `fix ${g.group}`, schema: fixSchema })
  if (!fix?.pr) fix = await agent(fixerPrompt(g.group, g.issues, repo, baseline), { model: fixerModel, effort: waveEffort, label: `fix ${g.group}`, schema: fixSchema })
  if (!fix?.pr) return { group: g.group, pr: null, reason: 'fixer returned no PR after one retry' }

  const reviewSchema = { type: 'object', required: ['verdict'] }
  let review = await agent(reviewerPrompt(g.group, repo, baseline, fix), { model: reviewerModel, effort: waveEffort, label: `review ${g.group}`, schema: reviewSchema })
  if (!review) review = await agent(reviewerPrompt(g.group, repo, baseline, fix), { model: reviewerModel, effort: waveEffort, label: `review ${g.group}`, schema: reviewSchema })
  if (!review) return { group: g.group, pr: fix.pr, head_sha: fix.head_sha, verdict: null, reason: 'reviewer returned null after one retry' }

  return { group: g.group, pr: fix.pr, head_sha: fix.head_sha, verdict: review.verdict }
}

// Round-based scheduling, like audit-find.js's WAVES: each round takes every
// group whose `after` list is fully satisfied (its dependencies produced a
// PR), runs at most three of them concurrently through parallel(), then
// re-evaluates. A round with nothing ready means every remaining group is
// stuck behind a dependency that never produced a PR (or names a group
// outside this wave) — those are recorded as skipped, not retried forever.
while (pending.size) {
  const ready = [...pending].filter((name) => (byName[name].after ?? []).every((dep) => done[dep]?.pr))
  if (!ready.length) {
    for (const name of pending) {
      const unmet = (byName[name].after ?? []).filter((dep) => !done[dep]?.pr)
      skipped.push({ group: name, pr: null, reason: `unmet dependency: ${unmet.join(', ')}` })
    }
    break
  }
  const batch = ready.slice(0, 3)
  const results = await parallel(batch, (name) => runGroup(byName[name]))
  batch.forEach((name, i) => {
    const r = results[i]
    done[name] = r
    pending.delete(name)
    if (r.pr && !r.reason) prs.push(r)
    else skipped.push(r)
  })
}

log(`wave done: ${prs.length} PR(s), ${skipped.length} skipped`)
return { prs, skipped }
