Fix review: blocked 6fd6c0c1b1ff3250fd1d7190ed7c4d3b4abae47f mutation-survivor: the shared-key max is unpinned, first-write-wins passes 104/104

bus-nonce: 23b464eb90f111b0f7f6c0e9784bdf7a

## Block

Round 1 of this review. Mutant M3 replaces the new `if (!prior || cell.prs > prior.prs) census.set(...)` in `parseHistogram` with `if (!prior) census.set(...)` (first row wins), and `node tools/policy/friction_issues.mjs --self-test` still passes 104/104. The PR's added assertion "and the shared key keeps the larger PR count, never the smaller" only pins it in one order, because the `twoKinds` fixture puts the larger row (verdict class, 2) first. That is also the order policy_lint prints (verdict class, then rework, then friction rule id). So when a friction rule id has the higher count for a key shared with a verdict class, a first-write-wins regression would keep the smaller count, which is the false below-threshold reading the code comment says this branch exists to prevent. The repair: add a mirrored fixture where the larger count comes second (for example, the friction row `3` after the verdict row `1`) and assert prs 3. Then re-run M2 (last write wins) and M3, and both should go red.

## Findings

- A surviving mutant on added production logic: in tools/policy/friction_issues.mjs `parseHistogram`, the max rule for a shared key is unpinned for the case where the larger row comes second (M3 above). This is the block reason, owed by the fixer on this PR. Carry: #2820
- A pre-existing coverage gap, not created by this PR: mutant M6 (`censusRows < declared`, which refuses only a short parse) survives because no fixture has more CENSUS rows than the summary declares. The old `!==` comparison had the same gap. This PR does not make it worse. Carry: dismissed: an over-count needs the producer to print a row it does not count, which policy_lint's summary (the same maps' sizes) cannot do; not worth a fixture on its own, but it can ride with the O1 repair at no extra cost

## Evidence

- Check 1, the root cause is true. Hand-counting the failed job's CENSUS rows gives 67 rows (37 verdict class, 1 verdict family, 1 rework, 27 friction rule id, 1 friction family) and 66 distinct keys. The one duplicate is `harness`, which is both a verdict class (2/2) and a friction rule id (1/1). policy_lint.mjs prints the summary as a sum of map sizes, which is a row count. ev/root_cause_from_job_log.txt, ev/job121219438293_census_replay.txt.
- RESULT, base da12aa37: replaying the job's census gives ok=false with "the census summary declares 67 key(s) and 66 row(s) parsed", the live refusal word for word. RESULT, head: ok=true, census.size=66, harness.prs=2. ev/replay_both_ends.txt.
- Check 2, the null control. The same histogram with one real row removed (`defect`) and the summary still at 67 is refused at the head ("67 key(s) and 66 row(s)"), so a genuinely short parse still refuses. ev/nullcontrol_missing_row.txt, ev/replay_both_ends.txt.
- Check 3, the mutation proof. The unmutated head passes 104/104. M1 (old `census.size !== declared`) fails 2, both on the new two-kinds lines. M2 (unconditional set, last write wins) fails 1. M4 (no row increment) fails the base parse lines. M5 (`>`) fails 1. M3 and M6 survive, as described above. ev/mutants.txt, ev/mutant_fail_lines.txt.
- Check 4, the Red checks answer. The body names `governance / record` and says the cheaper detector is the filer's self-test, which now carries a two-kinds census, at nil standing cost. The trigger is answered.
- Check 5, scope. The diff against merge base da12aa37 touches only tools/policy/friction_issues.mjs and dev/programme/delivery/2820.md. Head 6fd6c0c1 is 8e20aaaac plus the delivery row only (`git diff 8e20aaaac 6fd6c0c1` touches only 2820.md). The diff has no host or home paths. VERSION, the manifest version and RELEASE_NOTES.md are untouched.
- Merge: `git merge-tree --write-tree origin/main 6fd6c0c1b1ff3250fd1d7190ed7c4d3b4abae47f` exits 0, with no conflict (ev/merge_tree.txt). Main has moved since the merge base, but only in unrelated files, and dev/governance/roles/ is unchanged on main.
- CI on this head at review time: the check-runs API shows tests / fast (3.14), closures, coverage and codeql python still in progress. governance / delivery-status is red on main's own overdue #2795; the job itself says it is not a required context and does not block. This diff only adds this PR's own row, so that red is not this PR's. ev/ci_on_head.txt.
- The brief says this hotfix "merged on a green gate". The PR is open and unmerged at this head (merged=false, mergeable_state blocked).
- The body's figures section says "none". Its "104 of 104" re-derives at the head.
- Instrument disclosure: the replay loads parseHistogram from a scratch copy of the module with only its last `run(argv)` entry line removed. That copy is my own harness, and the finder's harness is the job log it transcribes.
- The head at post time is in ev/head_at_post.txt.
