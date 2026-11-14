# Proposal triage, session s14, batch 184 (P606)

This batch records the orchestrator's ruling on the part of P602 (batch 183, queue line 281) that
was routed to the owner. The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster`, read at 11:05Z.
- The orchestrator's relay, 2026-11-11, after batch 183.

## P606: CODEQL-PR-PATHS

Verdict: ACCEPT, as the new S group R10-CODEQL-PR-PATHS: sonnet fixer, opus reviewer, serial on the
train.

**Authority.** This verdict is the orchestrator's ruling under mandate 6715477401 (scope `all`). It
was not given by tvofi in person. Triage records it and adds what the tree says. It is not a triage
judgement of the owner-routed arms.

### The ruling, as relayed

- **Pull-request runs.** These analyse Python with `tests/` and `dev/` path-ignored, on the PR leg
  only.
- **The push-to-main run.** It keeps the full path set. No finding class is dropped from main. A
  finding is only moved from before the merge to main's own run.
- **Missed findings.** A finding that main's full run raises and the PR leg missed is a main red,
  handled like any other.
- **The required context.** `codeql / Analyze (python)` stays required on PRs, under the same name.
  The non-gating-leg arm is DECLINED.
- **Acceptance.** The PR python Analyze job must run in under 15 min. The body states before and
  after job seconds from `tools/audit/seat/ci_critpath.py` over at least 5 runs each.

### What the tree adds (for the fixer)

- **There is no scheduled run.** `codeql.yml` is a `workflow_call` callee of ci.yml alone
  (`:63-70`, `:86-94`); "the schedule is gone". The full path set therefore survives on main's
  push runs only.
- **How the leg learns the event.** The leg cannot see the event itself, because ci.yml's `codeql`
  job calls it. ci.yml must pass the event, or a paths input, through `workflow_call`.
- **The existing paths-ignore is pinned.** The one entry today is `.claude/workflows/*.js`
  (`codeql.yml:199-202`), and `tests/entities.py` pins it (`:19999`, `:21919-21929`). The pins move
  in the same PR.
- **Comparison risk.** GitHub compares a PR's analysis against the base branch's analysis in the
  same category. Alerts in the ignored paths may then read as "fixed" on every PR. The fixer
  measures this on one PR before handoff. If they do read as fixed, the PR leg gets its own category,
  so the comparison is not polluted.
- **Overlap.** R10-HOTFIX-RESTORE-BASE-SKEW (in-progress) also lists `ci.yml` and `codeql.yml`.
  The seam is distinct: the PR leg's paths. The overlap is admitted, and the train's serial
  workflow rule orders them.

### Bar

- **Before.** The PR python Analyze job takes 2173-3623 s. The sibling legs take 48-104 s. The job
  is on the critical path of every code PR and of the train's admission wait.
- **Target.** Under 900 s.
- **Expected cut.** At least 58% of that job's duration, and up to 75%.
- **Owner's axis.** CI time, well over 20%.
