Fix review: blocked 10805aa975d9c6ba62f9fe669f8d288c431a6468 root-cause-unanswered: tests / replay

bus-nonce: a506f168523411261eb556fded560a3d

## Head

I measured 10805aa975d9c6ba62f9fe669f8d288c431a6468, still the head (`git ls-remote origin refs/pull/3170/head` read it at the end). This is a delta re-check of round 4's block at 5ee2be2db0abefd7988a4465b4f431334925895e. I did not re-review the host-zone code, as the brief says. The merge base with main is clean: `git merge-tree --write-tree origin/main 10805aa975d9c6ba62f9fe669f8d288c431a6468` exits 0 (tree 8d98e5a3, ev/merge_tree.txt).

## Block

Round 4's two grounds, by the brief's steps:

- (a) Delta: `review_carry.py 5ee2be2d 10805aa975d9c6ba62f9fe669f8d288c431a6468` prints **CARRY**. The two branch-only commits (0cac0fe2, 10805aa9) are both main merges. No fresh review is owed (ev/review_carry.txt).
- (b) Carry-missing is settled. The TOCTOU text is on origin/handoff/audit-r10-roster. Group R10-GATE-LEASE-TOCTOU was appended at 7f6468d1ce071e988cdb1a401da183e4e2035bc9 (line 16813). Its brief states the `_free_slot` check-then-act race and names the delay-only plant (a 30 ms sleep after the read, no logic changed; 8 of 10 red) as its precondition control ("the fix must turn it green"). Roster commit 51525ad2 added the same fact to the group's `carry`, and both are ancestors of the roster tip 7a0acfe0 (ev/roster_7f6468d1.txt, ev/roster_tip_carry.txt). The body's `## Forward-carry` names 7f6468d1 and ends `Carry: R10-GATE-LEASE-TOCTOU`. The plant evidence the carry cites, gl_toctou.py and gl_head_toctou.txt, exists on the verdict/3170 ref (ev/plant_on_verdict_ref.txt). Minor: the body calls that ref "review/3170" in one place and "verdict/3170" in another. Both refs exist.
- (c) Root-cause-unanswered stays open for one check. The head's concluded reds, read across all 41 check-runs (one page; ev/check_runs.tsv), are four:
  1. `tests / replay` (job 127191893386, concluded failure 10:41:12Z). **The body does not name it.** The log reads `4 of 194 replay checks FAILED`: the `cycle_cost` arms on synthetic-dhw-only.json read `runner class unknown: ref_ms 21.91 lies in no band of COST_RUNNER_CLASSES [(22.64, 25.53), (28.72, 32.69), (42.99, 49.51), (49.6, 56.78)]; no budget is assumed`. `## Red checks` says only that 5ee2be2d's replay red (cpu_ratio) "did not recur", and that the merged head "has no CI yet". This head now has CI and the replay red is its own run. The diff touches no replay or cost code (the only workflow it changes is nightly.yml). The cause looks inherited: it is the same runner-class-unknown failure as main's scheduled nightly (job 126971378040, ref_ms 40.1, no band). But the body must say so, naming the cause and the base, and it does not. Rule 11 gives `root-cause-unanswered`.
  2. `governance / delivery-status` (127191611689): `DELIVERY STATUS OVERDUE — 10 rowed, 11 pending, 13 overdue`. The overdue rows are other merged PRs (#3193, #3181, #3191, #3201 and others); #3170 is open and not listed. The body names it and the answer is correct (inherited from main's ledger; the log says the check is not a required context).
  3. `tests / nightly-status` (127191611616): `NIGHTLY FAILED: slow failed last night`, scheduled run 41943946464 at 499162c8. The cause I read in the slow job's log (126971378040) is the replay lane: `5 of 181 replay checks FAILED`, `runner class unknown: ref_ms 40.1 lies in no band of COST_RUNNER_CLASSES`. The body's answer is correct as far as it goes (the failing night predates this PR's nightly step, by ancestry) but it did not read the log and names no cause. The cause is the same replay cost-band miss as item 1. I take this as answered on the brief's own standard (the trigger, not the answer), but item 1 is the same cause and is not answered at all.
  4. `governance / policy-docs` (127109349298 at the old head) is **green now** at this head (127191611673). The inherited `machinery_budgets.json` red is cured by the main merge, as the body says.

The still-running checks are `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `tests / arch-instrument`, `governance / instrument-self-tests` and `codeql / Analyze (python)`. `merge_train.py classify 10805aa975d9c6ba62f9fe669f8d288c431a6468 --pr 3170` read `WAIT ... pending: gate red: none` (rc 3) at the end. I judged none of the pending checks. This block rests on item 1 alone.

To clear it: add the head's replay red to `## Red checks`. Name `tests / replay` (job 127191893386), its cause (ref_ms 21.91 below the lowest COST_RUNNER_CLASSES band 22.64, so no budget is assumed), and that it is the same cause as main's nightly. State whether the diff touches the closure (it does not: only nightly.yml among workflows). Name the base ancestry where main is red, or give the finding that no cheaper detector exists. The host-zone class and the carry need no more review at this head if the head stays a main-merge delta (`review_carry.py` prints CARRY).

## Findings

- The replay lane's `COST_RUNNER_CLASSES` bands miss the runners CI assigns (ref_ms 21.91 on this head's replay, 40.1 on main's 2026-11-05 nightly), so `cycle_cost` refuses on its own arms with no budget. It is red on main's nightly and on this head, whatever the diff. The PR neither causes nor fixes it, and no roster group or issue is named for it in the body. Carry: R10-REPLAY-COST-BUDGET
- Round 4's other finding, the `_free_slot` TOCTOU, is carried and verified at 7f6468d1 (above). Carry: R10-GATE-LEASE-TOCTOU

## Evidence

- RESULT delta: `review_carry.py 5ee2be2d 10805aa975d9c6ba62f9fe669f8d288c431a6468` = CARRY (ev/review_carry.txt).
- RESULT merge: `git merge-tree --write-tree origin/main 10805aa975d9c6ba62f9fe669f8d288c431a6468` rc 0 (ev/merge_tree.txt); origin/main at 0ae75bf3 when read (ev/HEAD.txt).
- RESULT carry: 7f6468d1 and 51525ad2 are ancestors of origin/handoff/audit-r10-roster (7a0acfe0); the group's brief and `carry` hold the TOCTOU and its plant control (ev/roster_7f6468d1.txt, ev/roster_tip_carry.txt).
- RESULT check-runs: all 41 listed for 10805aa975d9c6ba62f9fe669f8d288c431a6468; reds are replay, delivery-status and nightly-status; policy-docs is green; six checks pending (ev/check_runs.tsv, read live; the run was 42011494510).
- Not re-derived: the body's host-zone figures (the brief said not to re-review the code); round 4 verified them at 5ee2be2d and the delta is main merges only.
