Fix review: blocked 036d2a7ff405b55e9178de65b2cbd14ec50d57b8 class-open: r10_flow_dispatch_mutants.py pins brief-drop and part-line-dropped match nothing at this head and abort the harness

bus-nonce: 6d76fbedb58ed7967ee9d1d4da4905b6

## Block

The previous block is resolved, but its class is still open. The step-8 rule in the body is `git grep -l '"<basename>"'`. It misses harnesses that name the file by a path constant, such as `REL = "tools/audit/seat/cloud_dispatch.py"`. A broader `git grep -l -e cloud_dispatch -e cloud-setup -- dev/audit/harnesses` returns two more mutant harnesses:

- `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
- `dev/audit/harnesses/r10_hotfix_delta_review_mutants.py`

`r10_flow_dispatch_mutants.py` pins two `cloud_dispatch.py` lines that this diff rewrites into the single `brief=group_brief(...)` / `+ "".join(f"\n{ln}\n" for ln in (dline, pline) if ln)` expression (`tools/audit/seat/cloud_dispatch.py:700-701` at this head):

- `brief-drop`, pattern `brief=group_brief(group, roster, fixer=role == "fixer") +`
- `part-line-dropped`, pattern `(f"\\n{pline}\\n" if pline else "")`

At the merge base 174e78cebf each pattern occurs once, and both mutants run: `RESULT mutant=brief-drop failed=11 verdict=killed`, `RESULT mutant=part-line-dropped failed=2 verdict=killed`, `survived=0`, exit 0 (ev/r10_flow_pins_base.log).

At this head each occurs 0 times. `main()` returns 2 on the first such pin, so the whole harness aborts with `abort: brief-drop's pattern occurs 0 times`, exit 2, after only `M0` and `tree-skip`. Its other 60 rows never run (ev/r10_flow_head.log, ev/r10_flow_pin_*_head.log). Every other pin of that harness counts the same at both ends (ev/flow_pin_counts.txt). No CI lane runs these harnesses, so CI cannot see this.

The production predicates are still pinned by the self-test. I planted both intents on the new spelling by hand at this head, then restored:

- `brief=group_brief(...)` → `brief=""` gives FAIL rows on designer, design-reviewer and fixer payloads (ev/plant_brief.txt).
- `(dline, pline)` → `(dline,)` gives `181 checks, 3 failed` (ev/plant_part.txt).

So the repair is the same as round 1's: re-spell the two pins to this head's lines, re-run both to `killed`, and widen the step-8 rule to path spellings. No production change is owed.

`r10_hotfix_delta_review_mutants.py` at this head: `MUTANTS: 9 run, 0 not as required`, exit 0 (ev/r10_hotfix_head.log). It is not stale.

## Findings

- The two stale `r10_flow_dispatch_mutants.py` pins above are the block itself, owed by this PR's fixer before re-handoff. Carry: dismissed: this verdict's block, owed by this PR's own fixer before merge, not a later stage's
- `r10_cloud_setup_mutants.py`'s null control fails in a plain temp directory. Its `M0` prints `FAIL 0/3` and the harness exits 1 even when every mutant is killed. That is because `self_test` copies `cloud-setup.sh` alone into a temp dir, and the script sources `../../../tests/throwaway_git.sh` and a sibling `pr_args.sh` relative to its own path. Both lines are on main (174e78cebf lines 67 and 191; the first from 27cb73cdaa), so this is not this diff's defect. The body's `M0 null 0 of 3 failed` reproduces only with `PR_BOUND=1` and a `TMPDIR` three levels under the repository root (ev/r10_setup_M8_head*.log). Carry: dismissed: present on main before this diff and outside its lines; the harness's own M0 row prints FAIL and exits 1 wherever it breaks, so its next run names it

## Evidence

Round 2, a delta review over the reviewed head 3099d416f40cf3e5468b6d93b6c410394cbbdfb2. Measured from detached worktrees at 036d2a7ff4, 3099d416f4 and the merge base 174e78cebf.

Contract and head:

- `git diff 174e78cebf...origin/main -- dev/governance/roles/` touches only `architect-planner.md` and `plan-review.md`. `fix-review.md` is unchanged, so the contract read is current.
- The PR body's `## Head` names 036d2a7ff405b55e9178de65b2cbd14ec50d57b8, the head measured.
- The delta `git diff 3099d416f4 036d2a7ff4` touches only two harness files. It has no production delta, so the scope is not widened.

RESULT lines:

- RESULT classify `GREEN 036d2a7ff405b55e9178de65b2cbd14ec50d57b8 pending: none red: none` (ev/classify.final). `owed-reds` does not include `nightly-status`, the packet digest's only red, so no `## Red checks` answer is owed (ev/owed_reds.txt).
- RESULT merge-tree origin/main head: rc=0, no conflict (ev/merge_tree.txt).
- RESULT, previous finding: `r10_seat_selftests_mutants.py` at this head prints `cloud_dispatch-15 ... KILLED rc=1` and `cloud_dispatch-16 ... KILLED rc=1` (ev/r10_seat_head.log). Resolved.
  - In the same run, `-8` and `-10` print `NOT RUN ... PATTERN FOUND 0 TIMES`. The body records both as identical at the merge base.
  - The run was stopped after those rows, because my hand-planted mutants shared its worktree. Rows after `-16` from that log are not relied on.
- RESULT `M8` re-spell: the old pattern occurs 1 time at 174e78cebf, and 4 times at 3099d416f4 and at this head. The new pattern occurs once at all three.
  - With `PR_BOUND=1 TMPDIR=<three under the root>`, `r10_cloud_setup_mutants.py M8` gives `M0 none: PASS 3/3`, `M8 ... KILLED 3/3 runs red`, `RESULT survivors=0`, exit 0 (ev/r10_setup_M8_head_bound.log). This matches the body.
  - Round 1 missed this third stale pin. The fixer's sweep found it.
- RESULT VERSION, manifest and RELEASE_NOTES: not in the delta. Round 1 found them untouched over the three-dot diff.
