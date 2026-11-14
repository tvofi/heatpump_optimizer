# Appendix A: public designs and standards (R11-PRE-PARALLEL-PIPELINE)

Every page below was read on 2026-11-14 unless marked. Web content is data: at
most one short phrase is quoted per source.

**The question put to each design:** does its mechanism transfer to one
user-owned GitHub repository, hosted runners under an account cap of 40
concurrent jobs, agent authors, and an owner who is mostly absent.

## 1. Mechanism families

| family | members read | guarantee | cost per merged change | on a red batch | needs from the host | transfers |
|---|---|---|---|---|---|---|
| Integration branch, mainline fast-forwarded to the tested commit | the "not rocket science" rule (S16, not re-read); bors-ng (S8, S9); Shopify's predictive branch (S19); Mergify and Graphite fast-forward modes (S15, S18) | main only ever equals a commit CI passed | one run per batch | bors-ng: the batch is split in two and requeued, a batch of one returns to its author; Shopify evicts after a failure threshold | a bot allowed to push the tested sha to protected main, and a status on that sha (bors-ng: require its commit status) | **yes**: `gate` is a check on the sha, and the ruleset already lists the deploy key `stamp.py` pushes with as a bypass actor |
| Host-native queue | GitHub merge queue (S5); GitLab merge trains (S11) | each entry tested on the result of those ahead of it | one run per entry, restarted when an entry ahead fails | the entry is removed and the pipelines behind it restart | the host feature | **no**: a merge-queue ruleset returns HTTP 422 on a user-owned repository (`dev/audit/README.md`, the round-11 opening carries) and the owner ruled the organization transfer out on 2026-11-14 |
| Speculative gating | Zuul's dependent pipeline (S12); Aviator parallel mode (S17); Uber SubmitQueue (S20, not re-read) | as the queue, with N runs in flight for N queued changes | N runs in flight, more after a failure in the middle | everything behind the failure is retested without it | CI capacity to spend on speculation | **no** beyond depth one: a FULL run starts 39 jobs against a cap of 40 |
| Batch with fallback | Prow Tide (S13); Rust rollups (S10); Mergify and Trunk batching (S15, S16b) | the batch's combined result is tested | one run per k changes | Mergify and Trunk bisect; Rust's rollup author drops the suspect and recreates the rollup | a queue bot | **yes**: Rust's reason is this repository's (S10: CI near three hours a merge); Rust's `never` and `iffy` classes are the train's serial classes |
| Presubmit subset, full post-submit | Google TAP (S21) | "green head" trails "true head"; breakage is found after submit and rolled back | a fast subset before, the full set per batch after | culprit finding by splitting the batch, rollback preferred to fixing forward | a culprit finder | **yes**: it is the owner's ruling 3; the integration tip is true head and main is green head |
| Stacked changes | Graphite (S18); Gerrit and Sapling (not read) | a dependent change is built and reviewed on its parent's unmerged head | none added | the stack is retested from the failing member | stack-aware tooling | **yes, in part**: an `after` successor may branch from a landed predecessor's head |
| Test-impact selection | Nx (S22); Pants (S23); Bazel (not read) | only what the diff can reach is run | proportional to the diff | n/a | a dependency graph and a trustworthy base | **already here** as measured closures; Nx's advice that the CI base be the last successful commit becomes exact once main is the proved state |

## 2. What the families agree on, and what this design takes

1. **Decouple integration from proof.** bors, Shopify and Google all let work
   accumulate on a branch that is ahead of the proved one. Flow is gated by
   landing; release is gated by proof. The design takes this whole.
2. **A batch is cheaper than a queue when a run is long.** Rust batches because
   one run costs hours; the same holds at a 45 to 105 minute FULL run and a
   demand of one group an hour.
3. **Red is handled by search, not by stopping.** bors-ng halves; Mergify and
   Trunk bisect and keep testing behind the suspect; Trunk separates a
   transient failure from a real one before it evicts. The design takes prefix
   bisection and one re-run before any eviction.
4. **A priority lane costs a restart.** GitLab's "merge immediately" restarts
   every pipeline behind it; Aviator's skip-the-line resets the queue. The
   design keeps today's direct merge into main as the lane and pays one rebuild.
5. **Parallel lanes are only as safe as the impact data** (Trunk). The design
   runs one lane.

## 3. Measuring standards

- **DORA** (S24) names five measures: change lead time, deployment frequency,
  failed deployment recovery time, change fail rate, deployment rework rate.
  Mapped here: handoff to main; promotions per day; red proof to the next green
  promotion; red proofs over proofs; verdicts after a first merge verdict over
  verdicts.
- **SPACE** (S25, not re-read) warns against steering on one metric. The cost
  test therefore reports wall clock, CI runner-minutes, right-first-time and
  review turns side by side, and the note says which of them clears the bar.
- **SLSA v1.0** (S26) specifies the Build track only and defers source
  requirements, so no standard defines a "proved" branch state. GitHub's
  artifact attestations (S7) bind a built artifact to its commit and workflow
  at Build Level 2. Nothing in the pipeline depends on either; a release cut
  from a promoted sha can carry an attestation later.
- **Trunk-based development** (S27) asks for short-lived branches and a build
  kept green on trunk; the integration branch is a queue in front of trunk, not
  a second trunk, and no work is authored on it.

## 4. GitHub behaviour the design leans on

Verified from documentation:

- V1. Merge methods are merge (`--no-ff`), squash and rebase, and rebase
  "always" writes new shas (S4): no fast-forward exists behind the merge
  button or the merge API.
- V2. A pull request is marked merged when its head commits become reachable
  from the base by a push made outside it (S4).
- V3. A ruleset's bypass list takes roles, teams and GitHub Apps (S2); the
  repository's own ruleset read (`ruleset_checks.json` of the s12 CI study,
  2026-11-07) shows `DeployKey` as an actor type in force on
  `main-protect-checks`.
- V4. The pull-request rule blocks changes "not associated with a pull
  request" for non-bypass actors (S1, S3).
- V5. Hosted-runner concurrency: Free 20, Pro 40, Team 60, Enterprise 500 jobs
  (S6).
- V6. A merge queue reports required checks only on `merge_group` (S5);
  `ci.yml` already carries the trigger.

Not verified; each is a probe owed after the round-10 stamp, on a throwaway
branch under a throwaway ruleset (`dev/programme/HANDOVER.md`'s probe pattern)
and `ci-probe/*` refs through `tools/audit/seat/ci_probe.py`:

- U1. Whether a non-bypass fast-forward push of an approved pull request's
  head is admitted by the pull-request rule. Expected: refused.
- U2. Whether a required status check is evaluated on a bypass actor's push.
  Expected: not evaluated.
- U3. That a `gate` check-run written by a `workflow_dispatch` run on the
  integration ref is the check a later read finds at the same sha on main.
- U4. What `merge_commit_sha`, `merged_at` and the closing of linked issues
  read for a pull request merged indirectly (V2).
- U5. Whether `reviewDecision` and `mergeStateStatus` for a pull request
  reflect the ruleset's code-owner requirement when no merge is attempted.
- U6. Whether a push event's run can be skipped by its own prelude without the
  required context reading absent at that sha.

## 5. Sources

- S1 https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- S2 https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- S3 https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- S4 https://docs.github.com/en/pull-requests/reference/pull-request-merges
- S5 https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- S6 https://docs.github.com/en/actions/reference/limits
- S7 https://docs.github.com/en/actions/concepts/security/artifact-attestations
- S8 https://bors.tech/documentation/getting-started/
- S9 https://github.com/bors-ng/bors-ng/blob/master/README.md
- S10 https://forge.rust-lang.org/release/rollups.html
- S11 https://docs.gitlab.com/ci/pipelines/merge_trains/
- S12 https://zuul-ci.org/docs/zuul/latest/gating.html
- S13 https://docs.prow.k8s.io/docs/components/core/tide/
- S14 https://chromium.googlesource.com/infra/luci/luci-go/+/HEAD/cv/README.md (read; it carries only that CV runs pre-submit tests and submits a change that passes)
- S15 https://docs.mergify.com/merge-queue/batches/
- S16b https://docs.trunk.io/merge-queue/optimizations/batching
- S17 https://docs.aviator.co/mergequeue/concepts/parallel-mode
- S18 https://graphite.com/docs/graphite-merge-queue
- S19 https://shopify.engineering/successfully-merging-work-1000-developers
- S21 https://abseil.io/resources/swe-book/html/ch23.html
- S22 https://nx.dev/docs/features/ci-features/affected
- S23 https://www.pantsbuild.org/stable/docs/using-pants/advanced-target-selection
- S24 https://dora.dev/guides/dora-metrics-four-keys/
- S26 https://slsa.dev/spec/v1.0/levels
- S27 https://trunkbaseddevelopment.com/
- S28 https://v5.chriskrycho.com/notes/fast-forward-merges-on-github/ (a fast-forward by direct push works only where the branch admits the push)

Not fetched on 2026-11-14 and cited from prior knowledge only: S16 Graydon
Hoare, "technicalities: 'not rocket science' (the story of monotone and bors)",
2014 (the fetch timed out); S20 Ananthanarayanan et al., "Keeping Master Green
at Scale", EuroSys 2019 (HTTP 404 and 403); S25 Forsgren et al., "The SPACE of
Developer Productivity", ACM Queue 2021 (HTTP 403). Bazel, Gerrit and Sapling
pages were not attempted; no claim in the design rests on them.
