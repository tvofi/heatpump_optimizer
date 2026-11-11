Part of R10-TRAIN-RESIDUE: carries 7/11 (the ambient `gh` account is never checked against the owner before the train acts as the owner) and 8/12 (`policy_approval_due` ignores the owner's own `CHANGES_REQUESTED`). Both are decided in `policy_approval_due`, the one read `policy_approve` posts on and `policy_admits` (the pre-flight) judges with, so one refusal each covers the post and the simulation. Alternatives: reusing `ci_probe.owner_check` was rejected (it raises `Refuse` from a class owning its own rate-limit state; the train needs a `why` string, so it reads `gh api user` through `Train.run`); the CHANGES_REQUESTED read repeats `budget_raise_gate.approval`'s rule on the same inputs (non-agent-declared owner reviews, latest decisive) rather than calling `approval()`, whose mandate callbacks the due-read does not have.

Carry 0 (PREFLIGHT-POLICY-ORDER) is already on main: `policy_admits` (#3366) judges the review the train is due to post, so a policy head under a live mandate no longer parks. Not re-built here.

Not done in this pull request (see Forward-carry): carries 1, 2, 3, 4, 5, 6, 9, 10, 13.

## Head

5e91c2cfe5d8e7671072adbc45b549229fc2c5ef: repair round on PR head 175556657aca03c1803e89860281e7c39ab4efae (first fixer's code head d36a52f94097d979968fe041f911d354ec15fb20, cut from origin/main 32aea942e19d36433713292ae02508e46753e932). The repair is one commit, `tools/audit/seat/queue_pre_flight.py` only: its self-test fixture `fake()` answers `gh api user` as the owner (`mt._mandate_gate().OWNER_LOGIN`), the stub merge_train's own fixture has. Alternative rejected: a shared fixture module for the two self-tests, because the two fixtures differ in every other answer (reviews, comments, heads) and the stub is one line; `queue_pre_flight` already takes the owner constant from `merge_train`, so no concept is duplicated.

## Mutation proof

Removing the `own`/`gh api user` block in `policy_approval_due` and running `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` fails exactly: "policy post: a gh account that is not the owner posts nothing, and the stop names the account" and "policy post: the owner's own latest CHANGES_REQUESTED posts no mandated approval" (2 failed); restored, 0 failed.

## Repair round mutation proof

Before: `python3 tools/audit/seat/queue_pre_flight.py --self-test` printed `queue_pre_flight self-test: 53 checks, 3 failed` (the policy-head-passes-under-mandate check, its revoked-mandate null control, and the `policy_approval_due` names-the-mandate check). After: `queue_pre_flight self-test: 53 checks, 0 failed`. Mutation: the stub changed to `return 1, "gh: no account"` (the account unreadable) gives `53 checks, 3 failed` again; restored, 0 failed. `python3 tools/audit/seat/merge_train.py --self-test` after the repair: `merge_train self-test: 610 checks, 0 failed`; `python3 tools/audit/carry_audit.py --self-test`: `carry_audit self-test: 402 checks, 0 failed`. Callers of `policy_approval_due` (the seam enumeration, `git grep -l 'policy_approval_due\|policy_fixture_builders'` over tools/ and tests/): `merge_train.py` and `queue_pre_flight.py` only, both now green.

## Null control

The existing checks "policy post: ... gets ONE approval citing `mandate comment <id>`" and "an owner approval already at the head is not re-posted" still pass with the owner as the acting account and no CHANGES_REQUESTED: an owner `gh` account with no adverse review still posts.

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` prints the check count and failures (0 failed at the head).
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED at the head.

## Red checks

`merge_train.py owed-reds` at this head prints, among others, `gate`; `governance / instrument-self-tests` is not in that set (not required), and is answered because it is the cause of the `gate` red.

- `governance / instrument-self-tests` (job 130260336504), step `python3 tools/audit/seat/queue_pre_flight.py --self-test`: cause, the first fixer changed `policy_approval_due` to read `gh api user` and stubbed it in merge_train's self-test fixture only; queue_pre_flight's fixture drives the same method and had no stub. Process state (b): the process existed and was not followed, `fixer.md` step 8 (enumerate the readers of the changed seam: the `git grep` above returns two callers, one fixed). Cheaper detector: that grep, seconds, and `queue_pre_flight.py --self-test` itself, 0.1 s measured. Why the handoff did not run it: `prepr.sh` step 3h runs only its own self-test (`selftest_owed` keys on prepr's own inputs; a `merge_train.py` diff skips it), and the first fixer ran merge_train's self-test alone. The scoped selection did not miss it: `python3 -I tools/ci/selftest_scope.py select --base $(git merge-base origin/main HEAD) --head HEAD` selects the steps `merge-train` and `carry-check-and-the` (the step holding queue_pre_flight), and CI ran it, which is how it went red. Finding: `prepr.sh` does not run the self-tests `selftest_scope.py` selects for the diff. Recorded refusal to build it: the selected `merge-train` step alone is 65 s measured locally, added to every prepr whose diff touches a train file, against a miss seen once in this PR with the step-8 grep (seconds) already naming the sibling; no class frequency is measured, the estimate is one in many train-seam PRs. Carry: dismissed: step 8's grep and the selected self-tests, 0.1 s here, already detect it; a prepr arm adds 65 s per train-touching diff for a miss seen once
- `gate`: red because it aggregates the required checks and `governance / instrument-self-tests` was red at 175556657aca; the same answer, no separate cause.

## Forward-carry

Carry 1 (undraft after a train-recarry draft) and Carry 6 (BOT_HEAD count) need the orchestrator's local train logs; this seat has none. Carry: R10-TRAIN-RESIDUE
Carry 13 (stale gate red): `latest_runs` keeps the worst gate suite per check suite on purpose (A5, #2009: GitHub's ruleset refuses a merge while any suite carries a non-success required run), so judging a red gate superseded by its run's `sha=` may make the train attempt merges GitHub refuses; it needs `platform_gate` evidence from a live head, not buildable offline. Carry: R10-TRAIN-RESIDUE
Carry 2 (stamp hold), Carry 3 and Carry 4 (live-head cancel sender, detector), Carry 10 (merge_pr.sh through classify_at), Carry 5 and Carry 9 (record-autofix deletion; `--require-rows` is still read by tools/release/stamp.py): separate seams beyond this pull request's size bound. Carry: R10-TRAIN-RESIDUE
Carry 0: already on main (#3366), nothing left. Carry 7, Carry 11, Carry 8, Carry 12: built here. Carry 14: already built at the merge base per the roster. Carry 15: built, the same change as carry 11. Carry: dismissed: built or already on main
Carry 16, Carry 17, Carry 18 and Carry 19: the later part of the group, dispatched at this pull request's merge, outside this repair round. Carry: dismissed: later part dispatched at this merge, not this repair

## Friction

none
