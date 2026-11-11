Part of R10-TRAIN-RESIDUE: carries 7/11 (the ambient `gh` account is never checked against the owner before the train acts as the owner) and 8/12 (`policy_approval_due` ignores the owner's own `CHANGES_REQUESTED`). Both are decided in `policy_approval_due`, the one read `policy_approve` posts on and `policy_admits` (the pre-flight) judges with, so one refusal each covers the post and the simulation. Alternatives: reusing `ci_probe.owner_check` was rejected (it raises `Refuse` from a class owning its own rate-limit state; the train needs a `why` string, so it reads `gh api user` through `Train.run`); the CHANGES_REQUESTED read repeats `budget_raise_gate.approval`'s rule on the same inputs (non-agent-declared owner reviews, latest decisive) rather than calling `approval()`, whose mandate callbacks the due-read does not have.

Carry 0 (PREFLIGHT-POLICY-ORDER) is already on main: `policy_admits` (#3366) judges the review the train is due to post, so a policy head under a live mandate no longer parks. Not re-built here.

Not done in this pull request (see Forward-carry): carries 1, 2, 3, 4, 5, 6, 9, 10, 13.

## Head

d36a52f94097d979968fe041f911d354ec15fb20, cut from origin/main 32aea942e19d36433713292ae02508e46753e932.

## Mutation proof

Removing the `own`/`gh api user` block in `policy_approval_due` and running `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` fails exactly: "policy post: a gh account that is not the owner posts nothing, and the stop names the account" and "policy post: the owner's own latest CHANGES_REQUESTED posts no mandated approval" (2 failed); restored, 0 failed.

## Null control

The existing checks "policy post: ... gets ONE approval citing `mandate comment <id>`" and "an owner approval already at the head is not re-posted" still pass with the owner as the acting account and no CHANGES_REQUESTED: an owner `gh` account with no adverse review still posts.

## Figures

- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` prints the check count and failures (0 failed at the head).
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED at the head.

## Red checks

none

## Forward-carry

Carry 1 (undraft after a train-recarry draft) and Carry 6 (BOT_HEAD count) need the orchestrator's local train logs; this seat has none. Carry: R10-TRAIN-RESIDUE
Carry 13 (stale gate red): `latest_runs` keeps the worst gate suite per check suite on purpose (A5, #2009: GitHub's ruleset refuses a merge while any suite carries a non-success required run), so judging a red gate superseded by its run's `sha=` may make the train attempt merges GitHub refuses; it needs `platform_gate` evidence from a live head, not buildable offline. Carry: R10-TRAIN-RESIDUE
Carry 2 (stamp hold), Carry 3 and Carry 4 (live-head cancel sender, detector), Carry 10 (merge_pr.sh through classify_at), Carry 5 and Carry 9 (record-autofix deletion; `--require-rows` is still read by tools/release/stamp.py): separate seams beyond this pull request's size bound. Carry: R10-TRAIN-RESIDUE
Carry 0: already on main (#3366), nothing left. Carry 7, Carry 11, Carry 8, Carry 12: built here. Carry 14: already built at the merge base per the roster. Carry 15: built, the same change as carry 11. Carry: dismissed: built or already on main

## Friction

none
