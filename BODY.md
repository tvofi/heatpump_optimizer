Adds `dev/programme/triage/s6-batch15.md`: one ruling, P84 (S6-V19, parallel record and policy merges run through hand-rolled shell), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P84 ACCEPT NARROWED -> R10-TRAIN-UPGRADE, the owner-ordered group, already dispatched. Re-scoped before merge: the first ruling at cf58e6a8 named a new group, R10-FLY-TRAIN-POLICY-APPROVE, which is withdrawn, and the accepted change folds into the owner's train-upgrade order. Under a numeric `--mandate` in force for policy, `merge_train.py` posts the citing owner approval that its own `policy_gate` already requires, so policy heads land on-train. A separate `merge_par.py` lane stays REJECTED. Triage and record heads need no change, because `policy_lint.mjs --corpus-filter` classes them as non-policy and `--bot-prs` already carries record PRs. The owner's order sets the group's wider scope (sequenced batches, loading a running train), which this ruling does not rule.

Round-2 repair: review/2758 blocked at `7f91e684` on body-head-stale, because the body named `feb44bd88`. The repair is to the body only. The tree and head are unchanged, so `handoff/triage-s6-batch15` is `7f91e684` itself.

## Head

`7f91e684293abb4ba0276d8b16eb7010448d9fff`, on merge base `a260e5630`. That is the ruling commits (the latest `feb44bd8`) plus one commit holding only this PR's own delivery row, `dev/programme/delivery/2758.md`. Not merged up to main: `git merge-tree --write-tree origin/main HEAD` is clean against origin/main `5c0ee1093` (2026-10-25), and the merge is the orchestrator's after handoff (fixer.md step 6).

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the one entry (P84 -> ACCEPT).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None, and on `P84` returns ACCEPT. Re-run at `7f91e684` this round. Round 1's carry lint, not re-run this round: `node tools/policy/brief_lint.mjs` over the carry, placed as a not-started R10-TRAIN-UPGRADE in a scratch copy of the roster, gave 0 errors. The same copy with the carry's `merge_train.py` path made unresolvable gave 1 error, so the linter does read that text.

## Figures

- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch15.md | sort | uniq -c` (1 ACCEPT), re-run at `7f91e684`.
- Diff: `git diff --stat $(git merge-base origin/main HEAD)...HEAD`: 2 files, 21 insertions.

## Red checks

- `pr-contract / pr-contract` (run 40127337036, 2026-10-24T20:22Z): failure, because the body then named `feb44bd88` and not the head `7f91e684`. That is the block this round repairs. The re-run after the body edit (run 40131058585, 20:55Z) concluded success. Cheaper detector: `prepr.sh --body-check`, which `body_push.sh` runs before this body is published. No other check at this head concluded failure.

## Forward-carry

n/a: once this file is on main, the orchestrator routes the carry through `roster_edit.py`, citing this file.

## Friction

none
