Fix review: blocked e1e3197e3aff48ee7afd6d43db153e232f7b6134 tests-gap: --open-cards output untested and silently empty on unmarked cards

bus-nonce: 5222f6bae840a95f8da6548601e6d793

Round 1 (first review of this PR). Head reviewed: e1e3197e3aff48ee7afd6d43db153e232f7b6134. Merge base b880dc914f3ba2590b7ce655d7419678b1c4968e. Role contract unchanged on main since the merge base.

## Block

- `--open-cards` is P3's input (architect-planner.md, Inputs and step 3: "none is dropped silently"). Two problems, one fix:
  1. **Nothing tests its output.** Mutant M11 survives the full `check_scopes.py --self-test` (rc 0, `evaluation arms: 59/59 held; --open-cards rc=2`). M11 drops the `out` argument in `main()` (`evaluation_gaps(a.round, tree, show, merged, anc, changed, out)` -> `evaluation_gaps(a.round, tree, show, merged, anc, changed)`), so `open_cards` is always `[]`. The only `--open-cards` arm covers the case where no evaluation is tracked (rc 2). No arm runs the CLI on a record that has a PARALLEL card and checks that the card is listed. Evidence: `ev/mutants-full.txt`.
  2. **It silently prints an empty list on a record whose cards are unmarked.** `--open-cards` throws away every gap `evaluation_gaps` returns, including the new "carries no boolean gates_finders" gap. On the real round-11 evaluation (origin/eval-review/r11-4 = f6d35cf73f) as written, 43 accepted cards are unmerged and none has `gates_finders`. `python3 tools/audit/check_scopes.py --repo . --ref f6d35cf73f19a053c99e6627071984ff4190aa04 --round 11 --open-cards` prints `{"round": 11, ..., "open_cards": []}` and exits 0 (`ev/open-cards-r11-4.txt`). The architect would read "no open cards". The body already applies the opposite rule to part 2's groups (an unmarked group is flagged `UNMARKED` and the listing exits non-zero) and to an untracked evaluation (exit 2, "never an empty list"). Unmarked cards need the same treatment.
- Wanted: `--open-cards` refuses (non-zero exit, naming the cards) when any accepted card lacks a boolean `gates_finders`. Add a self-test arm that runs the CLI path on a record with one non-gating unmerged card and asserts that card is listed, which kills M11. Add another arm asserting an unmarked card is refused rather than omitted.

## Findings

- none open beyond the block, which this PR settles.

## Evidence

- CI: `merge_train.py classify e1e3197e3aff48ee7afd6d43db153e232f7b6134 --pr 3620` printed `GREEN e1e3197e3aff48ee7afd6d43db153e232f7b6134 pending: none red: none`, rc 0 (`ev/classify-1.txt`). No red, so no `## Red checks` answer is owed. The body's `none` stands.
- Merge with main: `git merge-tree --write-tree origin/main e1e3197e` rc 0, no conflict (`ev/merge-tree.txt`).
- VERSION, manifest and RELEASE_NOTES.md are untouched in the three-dot diff. The diff touches 4 files (`ev/diffstat.txt`).
- Self-test at the head: `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` printed `evaluation arms: 59/59 held; --round 1 rc=1; --open-cards rc=2` and `SELF-TEST passed`, rc 0 (`ev/selftest-head.txt`). This matches the body's figure.
- Mutation proof, re-run with my own driver (`evaluation_self_test` at HEAD, exits 1 on any failing arm; `ev/mutants.txt`). NULL held 59/59. Killed: M1 (isinstance -> False), M2 (-> `gating is None`), M3 (merged guard dropped), M4 (`elif False`), M5 (no append), M6 (no `continue`), M7 (old `norm(ev.get(k, ""))`), M9 (an unmerged non-gating card still checked as a gap). This confirms the body's M1 to M7. M8 (`not gating` -> `gating is False`) survives and is equivalent, since `gating` is a bool on that branch. In the full self-test, M10 (`--open-cards` exit 2 -> 0) is killed and M11 survives (see Block).
- Null control, re-derived with my own driver (`ev/null-written.txt`, `ev/null-true.txt`) on f6d35cf73f. As written: 92 gaps, 43 of them "no boolean gates_finders" and 43 "not merged". With every accepted card true: 49 gaps (43 not merged) and 0 PARALLEL. Those 49 lines are identical, as an ordered list, to `check_scopes.py --round 11` run on main's code (origin/main e0ad8b2bd3) at that ref (`ev/main-round11.txt`, `ev/null-compare.txt`). The body's figures hold.
- Not re-derived: the third null-control arm (31 true / 12 false -> 36 gaps, 12 PARALLEL). The gating list is held outside this PR, so I could not rebuild it.
- Policy text: architect-planner.md's new holdout pointer, "the first five fitness functions step 7 names", resolves to step 7's structure budgets, gate-only tripwires, behaviour inventory, mutation kill rate and change coupling. That is the list it replaces. "read-only on code" is covered by the remaining "writing only the plan" and "You do not write production code". These policy edits still need the owner's approving review (or one under the mandate) before merging. That is not this verdict's to give.
- The body's head and code-head SHAs match the head I measured. When I re-read before posting, `refs/pull/3620/head` had moved to 9b6adde88a8049f4cd5f9b7ad81879b226affafb. That commit is one non-merge commit, `record: the delivery row for #3620`, and adds only dev/programme/delivery/3620.md. `review_carry.py e1e3197e 9b6adde8` prints CARRY (`ev/head-moved.txt`). check_scopes.py did not change, so every number above and the block hold at both heads. This verdict names e1e3197e, as dispatched.
- The body's `Carry: R11-PRE-ROUND-CHECK-GATE` part-2 carry: the packet's carry_audit reports it routed to origin/handoff/audit-r10-roster.
