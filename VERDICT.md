Fix review: blocked f3bd78c35a3b26dd02dee175868ad123df36765e harness: design-trace-missing train.sh add admission, event-driven dispatch add and backstop sweep are not built; the head ships the timed pitch the owner's re-scope drops

bus-nonce: 4a323ee5cc93faf22613eeb6ff8bb9f0

Round: this is the review of round 2 (the body's r2 head); the next round is the third, not yet a re-cut under fixer.md.

## Block

The brief for this review names the group's design as re-scoped by tvofi on 2026-10-24: build on R10-TRAIN-UPGRADE's `train.sh add` / `Train.admit_add` (#2772), drop the timed pitch, add the event-driven dispatch call and the slow backstop sweep. Its controls are: an add of a refused head is refused with its rule named; an add while a batch is in proof lands in the next batch; the backstop sweep adds a missed head exactly once and never starts a second train; mutants of each admission rule fail named arms. None of these exists at the head. `git grep admit_add|launch_detached` finds nothing on origin/main or at the head (ev/rescope-check.txt). The head still defines `pitch`, `launch_train` and `live_train` in tools/audit/seat/merge_train.py, which is the timed pitch the re-scope drops. #2772 is not merged, so the base this PR merges onto does not contain `train.sh add`. The body's Forward-carry 1 says this outright ("NOT built in this round") and leaves it to the orchestrator. Under fix-review.md step 9, a requirement in the design that is neither tested nor waived by tvofi is `design-trace-missing`. A carry back to the same group does not waive it. The orchestrator can still choose to merge this head as an interim pitch. That would need tvofi's explicit waiver of the re-scope for this head, and none is recorded in the body.

## Findings

- The re-scoped design (`train.sh add` admission, event-driven add from dispatch, backstop sweep, add-rule mutants) is unbuilt, and it is blocked on #2772 merging. Once #2772 lands, the group needs a re-cut onto `Train.admit_add` / `launch_detached` that removes `pitch`/`launch_train`. Control: on the reworked head, `grep -n "def pitch\|launch_train" tools/audit/seat/merge_train.py` returns nothing, and arms exist for refused-add, add-during-proof and the backstop sweep's exactly-once rule. Carry: R10-FLOW-AUTOTRAIN

## Evidence

- Head reviewed: f3bd78c35a3b26dd02dee175868ad123df36765e (ev/HEAD.txt). Measured from a detached worktree at that head. Merge base 5c0ee109305fc4f377c9326c712156b9ceb0e638. Roles diff merge-base...origin/main under dev/governance/roles/ is empty, so the contract is current.
- `git merge-tree --write-tree origin/main f3bd78c35a3b26dd02dee175868ad123df36765e`: rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES.md and both claim files are untouched (three-dot diff empty, ev/untouched.txt).
- RESULT agreement at head: `python3 -I tools/policy/agreement_py.py --run` gives `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`, restore 18/18, 0 missing (ev/head-checks.txt). This matches the body.
- RESULT self-tests at head: merge_train 267/0 failed, orchestrator_tick 214/0, proof_watch 40/0, tick_loop 17/0. This matches the body.
- Shared grammar reader confirmed. `VERDICT_MERGE` / `VERDICT_BLOCKED` / `parse_verdict` live only in tools/audit/seat/proof_watch.py. merge_train.py:1722 `Train.admit_verdict` and orchestrator_tick.py:687 `verdict_levels` both call `parse_verdict`.
- Reviewer's own mutants (ev/reviewer-mutants.txt), each re-inlining the merge pattern in one caller:
  - merge_train: killed by "queue: the verdict grammar is proof_watch.parse_verdict's, not a copy ..." (267 checks, 1 failed).
  - orchestrator_tick: killed by "verdict grammar: null control: under the swapped grammar the old spelling is no merge verdict" (214 checks, 1 failed).
  - Under both mutants agreement_py read `unregistered=0`. A single-file re-inline of this shape leaves no pair, so the named self-test arms are the detector. The body's `unregistered=1` figure is for its own mutant's shape, which I did not re-derive.
- Not re-derived: the fixer's 27-mutant script and the live-queue snapshot (marked stale by the body itself, taken at r1's head). The block stands without them.
- CI on the head (ev/ci.txt): every workflow was queued or skipped, and none had concluded, so there is no red to grade under step 11. The body's Red checks section answers the r1 prepr agreement red with its cheaper detector (agreement_py inside prepr).
