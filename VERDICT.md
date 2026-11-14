Fix review: blocked d95a3490ef0a1ae41a1bd20095f665a44e40d40a mutation-vacuous: fixer-guard-off readback-nonce legacy-refusal-swallow

bus-nonce: 077d25185454a0512b76a38f9ec359cb

Round 3 of review (the body's "Round 3 (this repair)"); measured at d95a3490ef0a1ae41a1bd20095f665a44e40d40a, reviewed from detached worktrees at that head.

## Block

Three mutants of production lines this diff adds to `tools/audit/seat/cloud_dispatch.py` survive `cloud_dispatch.py --self-test` (167 checks, 0 failed under each), recorded in `ev/own-mutants.log`:

- `fixer-guard-off`: `if role == "fixer" and (part or len(...) > PART_CARRIES)` with the `role == "fixer" and` conjunct deleted. Not equivalent: with it gone, every non-fixer seat of a group holding over five pending carries (reviewer, design, probe) is refused with the fixer's split, which would refuse the reviewer dispatch of this very group. Demonstrated with a probe check (`ev/probe-cloud_dispatch.py`, `ev/fixer-guard-probe.log`): `not why_any("R10-SPLIT", "probe")` passes on the unmutated file (168 checks, 0 failed) and fails under the mutant (168 checks, 1 failed). The body pins the other half, `--part` for another role refusing, but not that a non-fixer seat of an over-five group dispatches unrefused.
- `readback-nonce`: the read-back ref `{nonce.strip()[:8]}` changed to `{nonce.strip()}`. It survives because the self-test's nonce `abc123` is shorter than eight characters; with a real 32-hex nonce, the mutant tells the seat to `ls-remote` a ref it never pushed, so the read-back always misses.
- `legacy-refusal-swallow`: `raise Refusal(str(e))` in the `RosterNotFound` arm changed to `pass`. No fixture raises `RosterNotFound` on this path, so the mutant's NameError, which replaces the refusal, is never reached.

Each mutant was applied alone and the file restored afterwards (`git status` was clean after each run). To repair this: pin a non-fixer dispatch of an over-five group as unrefused, use a nonce of at least nine characters in the stop-path arm, and add one fixture with a missing roster on the part path.

## Findings

- The head was already merged to main through #3450 (merge a7887485de, `ev/merged-on-main.txt`) before this review at the handoff returned. So this block cannot hold the merge, and the three pins above are owed on main by a later part of this group. Carry: R10-REVIEW-DISPATCH-RESIDUE

## Evidence

- No pull request existed when this was dispatched, so there was no review packet and no CI to wait on (handoff review). `merge_train.py owed-reds` was not consulted because the head had no PR checks to read.
- RESULT harness=r10_flow_dispatch_mutants.py head=d95a3490ef0a1ae41a1bd20095f665a44e40d40a mutants=63 survived=0 rc=0 (`ev/mutants.log`): 58 killed, 5 CRASHED (parent-drop, topic-to-id, head-ignored, roster-repo-ignored, pointer-off), M0 null-ok. These match the body's Figures line for line. This part's 35 named mutants each read verdict=killed.
- RESULT selftest head=d95a3490ef0a1ae41a1bd20095f665a44e40d40a checks=167 failed=0 (`ev/selftest-head.log`).
- RESULT own-mutants (`ev/own-mutants.log`): killed topic-part-gt2, fold-lt, part-index-off, small-lt, selfskip-off, seat-refused-head, ci-wait-head; survived fixer-guard-off, readback-nonce, legacy-refusal-swallow. My first ci-wait-head spelling matched two sites and was not applied, so it was re-aimed at the unique f-string and then killed.
- Body's Unpinned sites: the prefilter `>` vs `>=` is equivalent on output as argued, because five raw carries hold at most five pending. `carry_only` is a pre-existing default. Neither of these is the block.
- Merge: `git merge-tree --write-tree origin/main d95a3490ef0a1ae41a1bd20095f665a44e40d40a` exits 0 (tree 619ee4c132), trivially, since the head is an ancestor of origin/main 8c10361eb1.
- `tests/closure.py select --diff cbd23f1c8b` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (`ev/closure.log`). `tests/structure.py`: STRUCTURE RATCHET PASSED (`ev/structure.log`).
- The diff touches none of VERSION, the manifest, RELEASE_NOTES.md, tests/golden or the claim files, so there is no drift to claim.
- The body's head and merge base (cbd23f1c8b) match the fetched handoff tip. The body records "Forward-carry: none" and "Red checks: none"; with no CI, the latter could not be checked against live runs.
- `dev/governance/roles/` differs between the merge base and origin/main only in design-review.md and others outside fix-review.md's steps, which this review applied as rendered at the current checkout through role_pack.py.
