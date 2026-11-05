Fix review: merge 2e3a51a9954c6816ba96b6267a1d1fbf8cd54925

bus-nonce: 6a27849dbccefe4217777e24cb512d47

CI re-check at the same head. Code unchanged; the prior block (probe/rev-3197-208f3cf3) was CI-only and has cleared.

## Findings

- Residual: the own-mutant "events: HEAD-MOVED never deduped" (`if same and same[-1] == line:` replaced with `if False:` in `event()`) survives the self-test; under-dedupe is reachable only when a pass is interrupted between event() and the heads.tsv write, or when two passes overlap. Low, not blocking (carried unchanged from the prior verdict). Carry: R10-FLY-STANDING-CONTRACTS

## Evidence

- Head unchanged: refs/pull/3197/head is 2e3a51a9954c6816ba96b6267a1d1fbf8cd54925; the diff against the reviewed head is empty (ev/head_diff.txt).
- merge_train classify at this head: GREEN, pending none, red none, exit 0 (ev/classify.txt).
- Check runs (all 68, one page, read via the API): gate success (three runs, 41931690213, 41931690869, 41933014995), prelude success, pr-contract / pr-contract success, budget-raise-gate / budget-raise-gate success, arch-score success. The only concluded failure is tests / nightly-status (126968676304), inherited from main's scheduled Nightly run and not required; the body's ## Red checks answers it and the diff reaches neither nightly.yml nor tests/nightly_status.py.
- Carries routed: the STUCK-arm carry to R10-HANDOFF-PATH is in the body (Forward-carry, Carry: R10-HANDOFF-PATH) and on handoff/audit-r10-roster groups[316] carry[11] (prior ev/carry_stuck.txt, ev/carry_stuck_prior.txt here). The HEAD-MOVED dedupe residual carries to R10-FLY-STANDING-CONTRACTS above.
- Prior evidence stands at this head (not repeated, per brief): own_mutants2 24 planted, 0 survived; beat_jobs self-test 107 checks, 0 failed; pulse 58/0, sweep_render 34/0; selftest_wiring 112/112/0; structure ratchet passed; entities 2611 passed.
- Merge: git merge-tree --write-tree origin/main at this head, result in ev/merge_tree.txt.
