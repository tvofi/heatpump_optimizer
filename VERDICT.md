Fix review: blocked c696f49ec50610ba1fe868149668b1c226105dba part-topic-collision: --part k>1 publishes <topic>-p<k>, which on the live roster is another group's own topic (R10-TRAIN-RESIDUE-P2, R10-TICK-RESIDUE-P2), and dispatch_group does not refuse it

bus-nonce: 6e2334367da35df8bdd8bc6d956735c8

Round: first review (no prior verdict at any head of #3450).

## Block

- Carry 13's part topic collides with existing roster groups. For k over 1, `dispatch_group` sets `topic = f"{topic}-p{part}"` (cloud_dispatch.py, `dispatch_group`). The body states that `roster_lib.group_for_branch` "already maps back" that topic. Its own docstring limits that: a phase branch answers for its group only "when no group is itself named `<group>-pN`". The live roster has two such groups. At origin/handoff/audit-r10-roster e0458e6fd809cb73d4cc1f165d7d6917e2ccacf2, the reviewer's probe `ev/collide.py` prints:
  - `COLLISION R10-TRAIN-RESIDUE --part 2: topic r10-train-residue-p2 = topic of R10-TRAIN-RESIDUE-P2 (stage not-started); ref dispatch/fixer-r10-train-residue-p2; group_for_branch(fix/r10-train-residue-p2) -> R10-TRAIN-RESIDUE-P2`
  - `COLLISION R10-TICK-RESIDUE --part 2: topic r10-tick-residue-p2 = topic of R10-TICK-RESIDUE-P2 (stage not-started); ref dispatch/fixer-r10-tick-residue-p2; group_for_branch(fix/r10-tick-residue-p2) -> R10-TICK-RESIDUE-P2`

  Both groups are over five pending carries, 20 and 30, so the new refusal itself points the orchestrator at `--part 2`. That dispatch shares a ref with the other group's fixer. The self-test pins that a re-dispatch fast-forwards an existing ref. The resulting PR branch is then credited by `group_for_branch` to the wrong group, which feeds delivery records and carry routing. Nothing refuses the collision: `part_line` and `dispatch_group` check only the part range and the role. At the body's roster SHA 17578fc4 the -P2 groups did not exist yet, so the fixer's enumeration could not show it. The mechanism, though, is the one the brief asked to attack, and it fails under the live roster (fix-review.md step 6).
  Owed: refuse, or re-spell, a part topic that equals any roster group's topic or normalized id, with a self-test arm whose fixture holds `<G>` and `<G>-P2`, and a mutant that removes the refusal. The body's sentence about group_for_branch should then match whichever behaviour is built.

## Findings

- Follow-up: part indices renumber once an earlier part merges, because `part_split` runs over `pending_carries` at dispatch time. The refusal says to dispatch "each at the previous part's handoff". If part 1 (0-4) of a 21-carry group has merged by part 2's handoff, `--part 3` resolves to 15-20, and carries 10-14 are never assigned (`ev/part-index-shift.txt`). The split should be pinned at the first refusal, or each part should name the carries by index rather than by k. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Follow-up: the class enumeration's figure (`live groups over five pending: 15`) comes from `over_five.py`, a scratch probe that is not in the tree (figure_lint: `unverified`). fix-review.md step 9 counts an uncommitted harness as a finding. The reviewer re-derived the figure with its own probe, `ev/probe-over-five.py`, disclosed as the reviewer's: 15 at 17578fc4, matching the body's groups and counts, and 17 at the live roster e0458e6f. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Follow-up: Carry 8's new reviewer text tells an incomplete review past the 30-minute WAIT bound to push `Fix review: blocked <head> ci-wait: ...`. fix-review.md step 11 says a seat that cannot reach a verdict while CI refuses should "wait or hand back unverdicted, saying so", and fix-review.md defines no `ci-wait` class. The relay would post a blocked verdict whose cause is CI latency, not a defect in the PR. Either fix-review.md names the class, or the prompt routes this case to `pending-ci:`/unverdicted. Carry: R10-REVIEW-DISPATCH-RESIDUE

## Evidence

- Head reviewed: c696f49ec50610ba1fe868149668b1c226105dba, the same as the PR head and the body's head (`ev/HEAD.txt`). Base f24d107bd7aa170bea7419251a4b7f4f48b732f6.
- `git merge-tree --write-tree origin/main <head>`: rc=0, merges cleanly (`ev/merge-tree.txt`).
- CI: `merge_train.py classify` prints `GREEN c696f49ec50610ba1fe868149668b1c226105dba pending: none red: none` (`ev/classify.txt`). The only red in the packet is `tests / nightly-status`, which is not in `merge_train.py owed-reds` (`ev/owed-reds.txt`), so it is owed no answer. The body's `## Red checks: none` stands.
- `cloud_dispatch.py --self-test`: 166 checks, 0 failed at the head and 153 checks, 0 failed at the base, matching the body (`ev/selftest-head.txt`, `ev/selftest-base.txt`).
- Mutation proof: the body's 27 named mutants plus M0 were re-run alone at the head (`ev/mutants-part.txt`). `RESULT mutant=M0 failed=0 verdict=null-ok`; all 27 `verdict=killed`; `RESULT mutants=27 survived=0`, rc=0. The full 56-mutant drive was not re-run to completion; a 220 s attempt timed out (`ev/mutants-head.txt`, rc=124), after CRASHED verdicts on parent-drop, topic-to-id, head-ignored and roster-repo-ignored, which the body names as pre-existing.
- Three-dot diff: four files (`ev/three-dot-stat.txt`). VERSION, the manifest, RELEASE_NOTES and both claim files are untouched. No `*_budgets.json` key moves. Structure ratchet: cited from CI's green `gate`, not re-run.
- Carry 9: FRUGAL_LINE at the head drops the inline allowance; the self-test pins it verbatim, and "no prompt grants an inline allowance" passes.
- Forward-carry: none named. carry_audit at the head routes the body's one Friction item to R10-REVIEW-DISPATCH-RESIDUE.
- Closing self-audit: `carry_audit.py check` rc=0, 4 items routed, 0 unrouted (`ev/carry-audit.txt`). It ran on the body's one Friction item, transcribed from the live PR body, because the seat has no `gh` to save the body file. Carry: dismissed: evidence, not a finding
