Fix review: merge c46a9c6abe46e17a30fcfd9add85390dc9c603ac

bus-nonce: fe7eeaa956aea8226133471406dc9739

## Summary

Round 2 of the fix review of #3200 (R10-TICK-LEVELS part 1), measured at head c46a9c6abe46e17a30fcfd9add85390dc9c603ac against merge base d7582ed404a87603bd02fefda610d7ebbe4181e1, which is origin/main (0 commits behind). The first-round block at d7e67e0d (nonce f943e190) is answered:

- The T3 seat mutant now anchors once and is killed. `r10_ledger_mutants --self-test` is 135 checks, 0 failed.
- Every survivor that review listed is now pinned, each red under my own re-plant: M06, M10–M15, M21, M24, M27, M29 and M30.
- O3 is fixed: a failed handoff read is UNREADABLE.
- O4 is fixed: the count line now names the excluded PRs.
- The ci_predict host rule keeps `tests/lane_skip.py <- tests/entities.py`. With the finder's harness, every pair it still drops is one the body classifies.

Four new mutants survive on lines this PR adds but does not name. One end-to-end gap remains in ci_predict, and it predates this PR. Both are handed on under Findings. CI on this head is classified GREEN.

## Findings

- Residual: four mutants on lines this PR adds survive, and neither the body's mutation proof nor its null controls name them. Each leaves `orchestrator_tick self-test: 272 checks, 0 failed` (`ev/mutants.txt`). A24: in `_seat_on`, the handoff-ref arm loses its `age <= SEAT_WINDOW_MIN` bound, so a ref moved at any age counts as "a seat is on it". A25: `_bucket`'s waiting-on overlap loses its `CLAIM_FILES` exclusion. A26: `verdict_kind` no longer requires the verdict's SHA to equal the head, so a verdict at an older head reads as verdicted or blocked at this head. A27: the train arm loses its `merge-base --is-ancestor` clause; a queue verdict at an ancestor of the head should count as `train`. A26 is the one with live consequence: after a fixer pushes, a PR whose last verdict names the old head would be bucketed `verdicted` instead of `review-owed`, and nothing pins it. Owed: one fixture per predicate (a verdict at an older head, a queue verdict at an ancestor, a claim-file-only overlap, a handoff ref older than SEAT_WINDOW_MIN). Carry: R10-TICK-LEVELS | #2265 | O1 | dismissed: none, owed by the group's next part
- Residual: ci_predict, end to end. The head's `_RUNS_SELF_TEST` makes `self_test_hosts` return `tests/entities.py` for `tests/lane_skip.py`. But `self_test_reads` drops any changed file whose source lacks the text `--self-test` before it asks for hosts (`tools/pr/ci_predict.py:393`), and the recorder runs only `--self-test` argv (`_RECORD_DRIVER`). `lane_skip.py` has no `--self-test` text and takes the `self-test` subcommand, so a diff touching it still predicts nothing: the recorder is never reached, at the base and at the head alike (`ev/lane_skip_e2e.txt`, `ev/lane_skip_e2e_base.txt`). This is not a regression and not class-open under the body's rule, whose enumeration (the finder's harness) returns no undispositioned pair. The quoted-subcommand alternative is still unreachable on the real path until the candidate filter and the recorder argv accept the subcommand spelling, and only the unit fixture kills it (A32). It belongs with the ci_predict instrument arm already routed to the friction group. Carry: R10-FRICTION-RECORDS | #2429 | O2 | dismissed: none, the group's ci_predict arm

## Evidence

- RESULT head c46a9c6abe46e17a30fcfd9add85390dc9c603ac, re-derived (`ev/*.head.txt`):
  - `orchestrator_tick self-test: 272 checks, 0 failed`
  - `r10_ledger_mutants self-test: 135 checks, 0 failed`
  - `ci_predict self-test: 0 failed`
  - `ledger self-test: 77 checks, 0 failed`
- RESULT finder's harness (round-1 review `ev/hosts_diff.py` from probe/rev-3200-f943e190, copied to `ev/finder/`):
  - At the base: 1573 files, old 24 pairs, new 24 pairs. Flat, as expected, since the base rule is the old rule.
  - At the head: old 24 pairs, new 14, lost 10. To run it at the head I adapted one line to swap the compiled `_RUNS_SELF_TEST`, because the head no longer calls `re.search` with the pattern string (`ev/finder/hosts_diff_head_adapted.py`).
  - The 10 lost pairs are exactly the 10 the body lists and classifies. `tests/lane_skip.py <- tests/entities.py` is KEPT. This matches the body's "24 → 14, 10 lost".
  - My own harness (`ev/hosts_diff.py`, reviewer-built) restricts candidates to the files `self_test_reads` really considers, those containing `--self-test`. It finds 12 → 8, lost 4, all four in the body's list. The body's quoted harness `/tmp/ev/hosts_diff2.py` is out of tree and I could not run it; I re-derived its figure with the finder's harness instead.
- RESULT mutation, reviewer-built driver `ev/mutants_driver.py`, 36 mutants, each anchor checked to occur once: 32 KILLED, 4 SURVIVED (A24–A27, under Findings).
  - Killed: every arm the body names. These are A01 train (M06), A02 newer-handoff (M10), A03 verdicted (M11), A04 verdict-pending (M12), A05 and A06 waiting-on (M13, M14), A07 DIRTY (M15, 6 failed), A08 in_head (M21), A09 FIRE grace (M24), A10 unwired pass (M27), A11 record skip (M29), A12 critical-path order (M30), A13 and A15 O3 (M33), A14 O4 tail (M34), A32 quoted subcommand (M35, 1 failed) and A33 old word (M36).
  - Also killed: the carry-8 arms (A16 null started_at, A17 self-test not a train, A35 GATE_CONTEXTS, A36 STUCK_FACTOR), re-cut (A18, A19), blocked stall (A20), red-unowned (A21), PARK (A22), body-ahead seat (A23), heads None (A28), FIRED window (A29), and the REVIEW OWED record skip at both ends (A30 tick arg, A31 ledger `skip_branch`).
  - A30 also turns `r10_ledger_mutants` red, which is expected: my plant rewrites the T3 anchor.
- RESULT CI mutation lane: `tests / mutation` ran its plan job only (`count=1, shards=[1]`), and `mutation-pins` was skipped. No CI mutant evaluated this diff's lines, so CI does not cover the survivors above.
- Merge: `git merge-tree --write-tree origin/main c46a9c6a` exits 0, tree 110475f186159bc63dad666bc15c5ef41a6b20fd, no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched in the three-dot diff. No golden or claim file is touched, so `env_drift` has nothing to compare.
- Cheap figures, re-derived (`ev/cheap_checks.txt`):
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `policy_lint.mjs`: rc 0.
  - `--budgets`: `standing-dispatch.md` is 38 of 39 lines and 505 of 509 tokens.
  - `closure.py select`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`.
- No budget is raised, and `tests/closures.json`, `INERT` and the ledgers are unmoved, so step 14 has no instrument movement to un-earn.
- Policy: `standing-dispatch.md` is policy and code-owned, so it merges on tvofi's approving review or under the mandate the body names. This verdict does not stand in for either.
- Roles drift: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- Head named in the body: c46a9c6abe46e17a30fcfd9add85390dc9c603ac, the head I measured. The live `fix/r10-tick-levels-p1` is still at that SHA (`ev/live_head.txt`).
- CI: see `ev/classify.log` and `ev/classify_final.txt`.
  - The first terminal classify at 19:26 was RED on `gate`. That gate run (job 126801513121) printed `FAIL run(s) [41893179305] at this head are still being judged; their gate decides`, the early-gate race.
  - `pr-contract` 126795759554 went red on `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`, a CodeQL wait timeout. Its preflight was otherwise clean (`clean no refusal`, CARRY-AUDIT 0, FIGURES 8 resolved, 1 not verified).
  - Once umbrella run 41893179305 concluded, classify read GREEN at 19:47. A re-triggered `gate` (WAIT at 19:47:28) concluded GREEN at 19:49, and the final `merge_train.py classify` at this head exits 0: `GREEN c46a9c6abe46e17a30fcfd9add85390dc9c603ac pending: none red: none`.
  - `tests / nightly-status` is red, and it is main's: this diff reaches nothing it reads.
  - None of these reds is caused by this diff's code. Two are timing races of the CI's own machinery and one is main's, so none owes a root-cause answer beyond naming it.
- Packet: rendered by this seat (`ev/review-packet.md`): no refusals; advisory `HPO_BUS_TRAIN_STATE is unset`.
- Self-audit: `carry_audit.py check` over this verdict: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit.txt`). The body side is CI's own run on the PR body: 0 items. #2265 is the R10-TICK-LEVELS issue the audit resolves; #3136 and #3135 resolve to no owner.
- Round: this is the second review round.
