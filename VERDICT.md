Fix review: merge 42115f2c1421ece1aae4dc69b2ba4f0f0f261928

bus-nonce: 60eafef700cf1b821ce7ef4b66b25517
pending-ci: gate

## Scope

Round 1, full scope (no reviewed head). The diff is policy and records only: decision 0018, `dev/audit/config/objective.json`, `dev/audit/yardstick/round10/OBJECTIVE.json` and `dev/programme/RULINGS.md`. It changes no production, test or instrument code. It is code-owned policy, so the owner's approving review is still owed before the merge. This verdict does not stand in for it.

## Evidence

- RESULT head: the PR head is 42115f2c1421ece1aae4dc69b2ba4f0f0f261928, base 8751943e17. The body's `## Head` 42115f2c14 is a prefix of the head I measured (`ev/HEAD.txt`).
- RESULT figures re-derived at the head, counting `R11-INTAKE-R10-RESIDUE` at the base and `R11-READS-RESIDUE` at the head: 0018 has 10 at the base, 10 at the head and 0 left; objective.json has 2, 2 and 0; round-10 OBJECTIVE.json has 7, 7 and 0. These match the body's 10, 2 and 7. Each `-` line pairs with one `+` line, and the diff has no other change in those three files (`ev/three_dot.diff`).
- RESULT class: the class is a builder reference to the deferred group. The rule I used: `git grep R11-INTAKE-R10-RESIDUE` at the head (`ev/remaining_intake_refs_at_head.txt`). It finds `"builder"` fields only in `dev/audit/yardstick/round11/EVALUATION.json`. The body leaves those in place on purpose, as a graded record at its review sha. The other hits are not builder references: carry text in `bugclasses.json:5044`, `R10-RCA-FEATURES-WEEKEND-CLOCK.md:247` and `round10/user-text/verdicts.json`, and the evaluation's proposals. Those carries stay with the deferred group, as the roster on `handoff/audit-r10-roster` at 6d21eb5f41 shows. No class seam is open.
- RESULT ordering claim: I ran `check_scopes.py --repo . --round 11`. At the base it gives FAIL with 9 gaps, none of them a READS builder. At the head it gives FAIL with 18 gaps, exactly 9 more, all `R11-READS-RESIDUE ... is no group the roster at the ref can still hand a build` (`ev/check_scopes_base.txt`, `ev/check_scopes_head.txt`). That matches the body's 9. I then made a local commit of the head plus the roster file from 6d21eb5f41. On it the 9 READS gaps clear, and 0 READS lines remain (`ev/check_scopes_head_plus_roster_6d21eb5f41.txt`). The remaining 13 gaps there are the roster batch's own changes, such as the R11-PRE-ROUND-METRICS terms, and not this PR's. On that roster, R11-READS-RESIDUE is a live `not-started` group (size S, instrument) and R11-INTAKE-R10-RESIDUE is `deferred`, as the body states.
- RESULT rulings entry: the RULINGS.md text agrees with the roster at 6d21eb5f41. R11-SEAM-learners carries "Moved from R11-INTAKE-R10-RESIDUE carry 182 ... kept in round 11 by the owner ruling of tvofi 2026-11-18", so point (2) is true of the roster. I could not re-derive the quoted words "go with all three points" from the tree; they are the owner's words, cited to `plan-verdict/r11` 4494289c0e.
- RESULT mutation: not applicable. No code line changed, so there is no mutant to draw. The body's `n/a` is correct.
- RESULT finder's harness: none named, and none is owed. This is a record re-point following an owner ruling, not a finding fix. The null control in the body (main names a deferred group) is confirmed by the base-side roster state above.
- RESULT claims and version: no golden or claim file is touched. `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are untouched.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` returns rc=0, with no conflict (`ev/merge_tree.txt`).
- RESULT role currency: `git diff <merge-base>...origin/main -- dev/governance/roles/` changes only root-cause and standing wording. Nothing in fix-review.md moved.
- RESULT CI: I polled `merge_train.py classify 42115f2c14... --pr 3740` from 19:56 to 20:27 UTC, at least 60 s apart (`ev/classify_poll.log`). The last line was `WAIT 42115f2c1421ece1aae4dc69b2ba4f0f0f261928 pending: gate red: none`. The live check runs at 20:21 UTC show every job concluded except `gate`, which was queued. In the packet, `tests / nightly-status` is a failure. It is not in `merge_train.py owed-reds`, so it is owed no answer and is not a block.

## Findings

- Follow-up: the landing order. Until the round-11 roster batch (`dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r10-roster`) is on main, `check_scopes.py --round 11` on main gains the 9 READS builder gaps measured above. The batch must land before or with this PR. The body already states this for the orchestrator (orchestrator.md section 10). It is not a new red, because the check already FAILs at the base with 9 gaps. Carry: dismissed: an ordering precondition the body hands to the orchestrator's merge sequence, measured here and not a defect of this diff

## Friction

none
