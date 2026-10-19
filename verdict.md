Fix review: merge 4c9dc5d92fade9e622fa56a86fd07e8ca98d60b1

bus-nonce: 03cf3d90583f8a3000235623b29f34d4

Round 2. The PR's earlier `Fix review:` comments (6267286930, 6267405240) are one round-1 verdict posted twice: blocked at this same head on an unrouted body (pr-contract red, `## Red checks` stale). The head has not moved; the body was re-pushed, and this round reviews it plus the code again. Measured head 4c9dc5d92fade9e622fa56a86fd07e8ca98d60b1 (ev/HEAD); still `refs/pull/2448/head` at write time, body byte-identical to ev/BODY.md. Roles contract current (`git diff $(merge-base)...origin/main -- dev/governance/roles/` empty).

## Round-1 blocker: closed
- `python3 tools/audit/carry_audit.py check --body ev/BODY.md`, run from an origin/main worktree (e8c67e1d3): `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry.txt). Both Friction items go to R10-BRIEFS-FOLD, which is a group in origin/main's `wave-r10-groups.json`.
- pr-contract at this head: green in the runs at 12:38:00, 12:38:23 and 13:17:00 (13:17 is after every other workflow concluded). The round-1 red runs no longer appear in the check-runs listing.

## CI (ev/ci.txt, commit check-runs API, 51 runs, all concluded)
Every run is success, skipped or neutral except `nightly-status` (118057836241): main's `record-autofix` nightly failed. This diff does not reach what that check reads, and `## Red checks` answers it. The body also answers the earlier pr-contract red (step 11): it names the cheaper detector, `carry_audit.py check` before `body_push.sh`, and its standing cost. fast (3.14), coverage, closures, coverage-ratchet, mutation, typing, env-matrix, policy-docs, instrument-self-tests, browser, CodeQL and arch-score are all green. Mutation log: `MUTATION TABLE PASSED (empty pool)`, `no mutant is both generatable and drivable`; unpinned sites 4170 vs 4171 at the ratchet base. The empty pool is why I ran the targeted mutants below. Heavy runs are cited from CI, not re-run.

## RESULT lines, reviewer-run (ev/harness.txt)
Harness: `dev/audit/harnesses/r10_dead_rate_limit.py`, sha1 99b702cb6ed433e9531307f710e49299c6dc4b3c. It is the fixer's own instrument, and the body discloses it as such. The finding had no committed harness (step 9, disclosed: it is the R10-TRUST-RELATIVE seat's forward-carry). I ran it from git worktrees: base 90557e39e, mb 05c39d3a6, head.
- shipped: binds=0/181440 at base, mb, head. max_moved_fraction is 0.033333333333 at base and 0.010000000000 at mb and head (bound 0.01). digest 3187402b35f5… at mb = head, 0cd34c4c10ee… at base. Matches the body.
- --alpha 1.0: binds=173200 at all three. digest at mb aab107495a1e… vs head f114d1008253…. Matches the body.
- --current-min 0.05 --current-max 0.2: binds=156444 at base, 0 at mb, 0 at head. Matches the body.
- --limit 0.005: binds=158586 at mb and head (base 99336, which the body does not quote). digest at mb 52a4b217daaa… vs head 3187402b…. Matches the body.
Finder's harnesses at both ends (ev/finder_harness.txt), mb vs head:
- reparam_sites: RESULT sha1 89dcd7a6ebbd… at both.
- newton_bias: none 0.0034, asym 0.4731 at both, rc 0 on Linux.
- D14 enumerate.py: rc 0 at both, but it prints no RESULT lines, so it compares nothing.
- r10_trust_relative_bundle.py: not re-run. The body's input is a synthetic bundle that is not committed, so this figure is not verified.

## Mutation proof (ev/mutants.txt, features_block on the #193 S7 block, restored after each; `git status` clean)
- unmutated: ALL 7 PASSED.
- M2, clip 0.005: 2 of 7 FAILED, the two checks the body names.
- M3, unused `max_step_fraction=0.05` parameter: 1 of 7 FAILED, the signature check.
- M1, clip 0.05: ALL 7 PASSED. This is the finding itself, as the body says: a clip that never binds cannot be seen by value.
- My own mutants: a clip at 0.0099 (just under alpha*trust_region) and a ×(1+1e-4) EWMA bias each fail 2 of 7.

## Other steps
- merge-tree origin/main (e8c67e1d3) against the head: rc 0, tree 12d24068… (ev/merge-tree.txt). No conflict.
- VERSION, manifest, RELEASE_NOTES.md and tests/golden: no diff in the three-dot range. `env_drift.py --claims-only 05c39d3a6`: ok. No claim file is touched, and the step is bit-identical at the shipped constants (digest), so no golden can move.
- structure (step 14): `STRUCTURE RATCHET PASSED` at the head. Removing the mechanism (re-adding the two `max_step_fraction=` call-site lines) gives `FAIL class_excess_loc 18303 > 18301 (+2)`, so the -1 is earned by the change.
- Class (step 6), reviewer re-run. Rule 1 at mb returns two seams, thermal_model.py:1938 (the trust region) and :1944 (the deleted clip). At the head it returns only the trust region. Rule 2 returns HOUSE_LOSS_MAX_STEP, kept as the re-anchor gate (coordinator.py:4876), and COP_LEARNING_MAX_STEP. I read `_fold_measured_cop`: nothing bounds its step before the clip (`judge_ratio` gates against the walking ratio, not this step), and with alpha 0.03 the clip binds when |commanded/measured − 1| > 1.67. So it is not the dominated shape, and the body's disposition holds.
- `git grep -ln max_step_fraction` at the head finds only the new harness and the roster. All four harness callers are updated.
- Forward-carry: `none`. The findings that matter are routed to R10-BRIEFS-FOLD.
- Architecture (step 15): the added lines are a docstring, comments, a float() wrap and tests. No breach.
- Head in the body (step 7): 4c9dc5d92 is named, with measurement at the code head d85b8c246. The main merge (3310f9b08) reaches none of the measured files.
