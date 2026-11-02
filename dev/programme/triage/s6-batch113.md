# Proposal triage, session s10, batch 113 (P371)

The rolling batch after batch 112. Facts were read at origin/main `dfb4ce2b5`, at the round's
roster branch `origin/handoff/audit-r10-roster`, in the seat ledger and in the root-cause record
for the class. This is a root-cause countermeasure for an audit class with 4 instances in one round.
The triage contract keeps such a countermeasure on its own route, so the owner's 2026-11-01 LOG
rule does not apply to it. The ruling still weighs each part on its cost.

## P371: the base-copy grader bootstrap: a pull request teaches a pinned grader, and CI grades it with the base's copy

Verdict: ACCEPT parts (a), (b) and (c), as one carry on R10-FLY-CIPREDICT-RESTORING. Part (d) is
DEFERRED to the owner. It moves the trust boundary decision 0013 drew, and the owner's own words
on that boundary are "Don't reopen the 1558 CI trust holes".

Source: the orchestrator's queue line of 2026-11-02T08:16:24Z, from the root-cause seat's record
for the class. Its parts:
- **(a)** `fixer.md`: the fixer splits the change itself, or moves the registration to unpinned
  data, without returning BLOCKED.
- **(b)** `designer.md` and `design-review.md`: a design names its p1/p2 split.
- **(c)** `tools/pr/ci_predict.py`: the graders arm prints a BOOTSTRAP remedy line.
- **(d)** grader registries move to unpinned data, behind a pinned superset check.

Instances:
- **Four in round 10, all in 2026-11-01T19:11Z to 2026-11-02T08:07Z**, each confirmed in the seat
  ledger:
  - R10-DEPS-ACTIONS-BUMP, line 3772: "fixer BLOCKED 11-01 19:11Z (base-graded codeowners_gap
    allowlist ...), unactioned for 7 h. Ruling: split."
  - R10-MACHINERY-RATCHETS, line 3840: "returned BLOCKED at 23:39Z and sat unactioned for 5h45m.
    Base copies of policy_lint.mjs ..."
  - R10-BASH-KILL-HOOK, line 3884: "r2 chose the split (Case 2, the base-copy bootstrap)".
  - R10-AGREEMENT-BOOTSTRAP #3166, line 3890: "blocked architecture-unsound ... use the p1 grader
    / p2 entry split".
- **The ruling was the same split every time.** The record measures 20 h 43 m of delay against a
  split planned at dispatch. 12 h 45 m of that (62%) is BLOCKED returns waiting for that ruling.
  The figures are taken from the record; I re-checked the four ledger lines above.
- **The remedy exists and reaches no acting seat.**
  - Decision 0013 *Consequences* (line 103 of `dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md`)
    reads "two pull requests -- the grader first, the artifact second".
  - `git grep -n -i -E 'split|two pull requests'` over `dev/governance/roles/fixer.md` finds only
    the structure-ratchet sense (lines 249 and 277) and "the orchestrator splits or closes it"
    (line 314). No line lets the fixer split for this cause.
- **The detector prescribes an impossible repair.** `tools/pr/ci_predict.py` line 1107 prints
  "repair before the handoff" for every predicted red, including base-copy grader refusals that
  no edit inside the pull request can repair.

Cost:
- **(c)** is a membership test over the refusals the arm already computes, plus the text of one
  line. The standing cost is about 0 s per run. `tools/pr/ci_predict.py` is 1670 lines and is not
  in any `*_budgets.json`.
- **(a) and (b) are about 120 tokens of role text, and every touched file sits at its cap.**
  `node tools/policy/policy_lint.mjs --budgets` at `dfb4ce2b5` reads:
  - `dev/governance/roles/fixer.md` (printed under its retired path): 314 of 315 lines, 5216 of 5216 words;
  - `dev/governance/roles/designer.md`: 60 of 60 lines, 878 of 878 words;
  - `dev/governance/roles/design-review.md`: 53 of 53 lines, 778 of 778 words;
  - `role fixer ~6285 tokens, cap 5852 +band 500 = 6352`, so 67 tokens of headroom.

  The builder pays under `ratchet-budgets.md`, for example by moving 0013's sequencing sentence
  rather than copying it. A raise is not this ruling's to grant.
- **Policy.** (a) and (b) change what a seat must do, so they are policy. They merge on the owner's
  approving review, or under a mandate in force.
- **(d)**:
  - It refactors five registries (POLICY_GLOBS, DECLARED, the hooks list, SHARED_GRAMMARS and the
    codeowners action allowlist) into data files, plus one pinned check per registry.
  - Its benefit is the inherent second PR cycle per instance. #3160 took 1 h 46 m from open to
    merge.
  - The owner's machinery freeze after v10.0.0 (seat ledger line 3521) lowers the expected rate in
    round 11.

Binding:
- **Why ACCEPT (a) to (c).**
  - At one instance per round, the saving is about 3 h of idle per occurrence, against about 0 s
    of standing cost and about 120 tokens per session that the builder must pay for.
  - The class is past the audit-class threshold. These parts remove the response latency that is
    62% of the measured cost.
  - They change no verdict and no trust boundary. A self-split p1 is still graded by the base's
    copy and still reviewed.
- **Why one carry, and why this group.**
  - No live group owns `fixer.md`, `designer.md`, `design-review.md` or `ci_predict.py` by its
    `files`. Every group that did is `done`.
  - R10-FLY-CIPREDICT-RESTORING is `queued` with no pull request. Its brief widens this same
    graders arm to every restoring job, which will surface more base-copy refusals locally.
  - (c)'s line cites the `fixer.md` route that (a) adds, so they land together or (a) lands first.
  - The group is sized S, and the policy text may make it M. That is a dispatch decision for the
    orchestrator.
- **Why DEFER (d), and what would change it.**
  - Grading a pull request with anything its own diff can add reopens #1403. The record itself
    shows additions are not monotone-safe: "a DECLARED entry that 'declares none', or a corpus
    exclusion, is an addition that shrinks grading".
  - So a superset check is safe only per registry, after each registry's addition kinds are shown
    unable to shrink grading. That is a design per registry, not a carry.
  - It changes on the owner's ruling to open that boundary, and then a designer's note per
    registry that names its exempting kinds and the check that refuses them.
  - Until then, (a) to (c) are the class's recorded barrier, and 0013's two-PR cost stays as
    accepted.
- **A known interaction.** Until R10-OPENER-REUSE carry 10 (P363) is built, a self-split `-p1`
  topic is opened by hand. That is P370, and it is not a reason to hold this one.

Carry text (for `roster_edit.py append-carry R10-FLY-CIPREDICT-RESTORING`, citing
`triage: dev/programme/triage/s6-batch113.md#P371`) is the file queued with this batch. It is
reproduced in the pull-request body.
