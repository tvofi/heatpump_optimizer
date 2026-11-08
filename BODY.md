Instrument half of R10-CLOSEOUT-CLEANUP's carries (closeout exemptions, worktree_gc, prune_refs). Merge base is origin/main 73365699a135, unmoved since my last prepr run (no second run owed).

Note: the round's final --apply run stays with R10-CLOSEOUT-CLEANUP. Two readings to confirm: "host" is resume.host as a group id; class E derives the topic from the seat directory name less a leading seat-.

## Head

fe7d2e21dcb53e67e812def87e42910d455a32ff

## Mutation proof

Each fix's predicate was broken in place and its self-test run:
- closeout exemption dropped (`exempt = set()` in roster_blockers): `python3 tools/audit/seat/closeout.py --self-test` -> 4 failed, first "a fixture roster with only the post-stamp owner step open proceeds".
- carry 1, cwd gate restored to the `onremote` condition: `bash tools/audit/worktree_gc.sh --self-test` -> FAIL "carry 1 (a): class B with a holder keeps"; gate removed from class A -> FAIL "carry 1 (c)" and the topic-seat cwd arm.
- carry 0, topic mapping removed -> 7 failed (merged/closed topic seats kept); class-E PR check bypassed -> FAIL "copies of an open topic stay".
- carry 2, per-sha aliasing disabled: `python3 tools/audit/seat/prune_refs.py --self-test` -> FAIL "a tag held at another sha ...", "...the old tag is left at the old sha", "a re-plan after a lease refusal archives the moved tip under a per-sha tag".

## Null control

Fixture arms that must keep or must not change: a not-started group still refuses beside the exempt ones; an unwired issue still blocks step 4; a seat with one unpushed commit, a dirty tree, a live cwd, or an open fix/<topic> PR stays; class B without a holder still removes; copies with a .git or an open topic stay; an unmoved ref archives under the plain tag name (no alias).

## Figures

- Carry 0 worktree_gc: all of the above covered by `bash tools/audit/worktree_gc.sh --self-test` (132 checks, 0 failed; 105 at the merge base).
- `python3 tools/audit/seat/closeout.py --self-test` 35 checks, 0 failed; `python3 tools/audit/seat/prune_refs.py --self-test` 77 checks, 0 failed; `python3 tools/audit/seat/roster_lib.py --self-test` 67, `python3 tools/plan/replan.py --self-test` 0 failed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, runs tests/entities.py.
- Mutant run (prepr diff-mutant step): the diff changes no file the mutants lane reads, so it skipped; closeout.py's own self-test served as MUTANT_CMD. Survivors: 0 reported, wall time not measured (step skipped).
- Rule for the exemption: roster_lib.closeout_exempt = open post-closure groups (replan's rule, moved to roster_lib) plus their wired issues, plus refused/refuted groups whose resume.host is not an open group. Carry 1/0/2 verified not already delivered at the merge base (grep of worktree_gc.sh, prune_refs.py).

## Red checks

tests/entities.py fails 3 checks that fail identically on an untouched origin/main worktree in this sandbox (coverage-job cache key, release ZIP build, Pages workflow probe); a 4th it showed (bare array expansion in worktree_gc.sh) was mine and is fixed. Consequently prepr's closures step refuses here and is left to CI. Non-required.

## Forward-carry

none

## Friction

none
