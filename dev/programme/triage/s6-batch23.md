# Proposal triage, session s6, batch 23 (P106-)

Rulings from the s6 `proposals.md`, collected 4 or 5 to a pull request under
tvofi's batching rule of 2026-10-24. Numbering continues after
`s6-batch22.md` (P101-P105; P105 withdrawn).

## P106: a PR title op for body_patch.sh (S6-V39)
Verdict: DEFER -> R10-FLOW-BODY-ONLY (one instance; the group owns the body-only update seam and is not started).
Source: s6 `proposals.md` `## V39` (dispatch w29, #2804 round 2).
Instances: 1, the #2804 retitle of 2026-10-25, as V39 records it; I did not open the PR. Nothing recurs yet.
Considered:
- R10-FLOW-BODY-ONLY (not-started, size S): files `update_pr.sh`, `cloud_relay.sh`, `pr_args.sh` and `INSTRUMENTS.md`, and its domain is changing a pull request's metadata without moving a clean head. It is the closest group by seam and domain, though it does not list `body_patch.sh` as a file. If the title arm is ever built, the carry goes here.
- R10-FLOW-JIDOKA (in-progress): owns `prepr.sh`, a pre-push check; a post-open title edit shares no file or seam with it. Does not fit.
- R10-POLICY-LINT-FAMILY (done) and R10-ORCH-MACHINERY (absorbed) mention `body_patch`/`app_mint` only in prose and cannot take work.
Cost: an `--title` arm on `body_patch.sh` is a few dozen lines with a self-test (the PATCH, a read-back of the title and the unchanged head), and one more mint per use. A title needs fixing only when a seat opens a PR under a merge-commit subject, as #2804 did; `handoff_push.sh` and `open_pr.sh` already set the title with `gh pr edit` at open.
Binding: a single instance and an unmeasured benefit; the bar is "clearly", and an unmeasured benefit is DEFER.
What would change the answer: a second retitle that a seat hand-rolls on `tools/pr/app_mint.sh`, counted from the dispatch report.
