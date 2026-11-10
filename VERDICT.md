Fix review: merge f5d7df0bdf186b210bedc33c9bb4e75254aa1970

bus-nonce: 40ec412970940f0a76bc01cd6eff6403

Round: first. Measured head f5d7df0bdf186b210bedc33c9bb4e75254aa1970, base b0762725099fefd337fc74ecff161cb487a992bc; the head matches the body's `## Head` line.

## Findings

- The after-figure (the census over a window after the merge reading `token=<n>/<n>`) cannot be taken at this head, because `workflow_run` and `sweep-self` run main's and the pinned base's copies. The body's `## Figures` records it as owed after the merge, and the census harness is in the tree to take it. Carry: dismissed: owed by the body's own Figures line and taken with the in-tree harness; it changes no later stage's brief

## Evidence

- Roster carry (#3400 counter-instance): the body answers it. The App-actor decider's completion did fire gate-sweep 42738574607 (I read it via the API: event `workflow_run`, actor `hpo-author[bot]`, created 2026-11-10T01:50:15Z). That sweep's stale-pin arm dispatched run 42738604293. I confirmed that run's event is `workflow_dispatch` and both its `actor` and `triggering_actor` are `github-actions[bot]`, so its completion could fire no sweep. The fix handles that exact shape: `fresh` returns False where V is the green dispatched fresh judge, so `sweep-self` re-runs the stale red once. The required null control holds: the self-test arms `stale pin, #3400 null: the decider's own sweep, while the fresh judge runs and after it completes, re-runs nothing` and `sweep-self: a gate still running elsewhere is not waited on from inside V` both pass at the head.
- RESULT sweep self-test at head: `sweep self-test: 81 checks, 0 failed`; `gate self-test: 81 checks, 0 failed`; `RESULT self-test checks=5 failed=0` (r10_sweep_token_actor.py).
- RESULT mutants (mine, tools/ci/sweep.py, each restored and checked with `cmp`), all killed: M1 `if self.green in later:` -> `if False:` (1 failed); M2 `self.green = v["id"]` -> `pass` (1); M3 caller exclusion dropped from `finishing` (3); M4 `judging` dropped from settle's break (1); M5 SELF_JOB dropped from `sources` (1); M6 the busy-run poll arm -> `elif False` (2); M7 the green branch's `r["status"]=="completed" or success` guard dropped (2); M8 caller detection -> None (4); M9 `fresh`'s new `return False` -> `return True` (1). These match the body's mutation proof wherever the two overlap.
- ci.yml plants: I did not re-run them. `tests/entities.py` cannot run in this seat because `homeassistant` is not installed (ev/entities.txt). I cite CI instead: the `gate` check (id 129627385733) is green on the MODE: FULL closure. The `sweep-self` permissions and base restore follow the pattern of the existing `refresh` job; `persist-credentials: false`; a push or merge_group with no base runs nothing.
- Adversarial check on the stale-red re-run: the re-run's own completion fires gate-sweep, because a re-run keeps the PR run's actor. There `self.green` is the edit run, not a dispatch, so `fresh` takes the `later` arm and leaves it. No loop, as the self-test arm `stale pin, no loop` pins.
- Figures not re-derived: the census counts (other=37/37 token=0/2; token=0/1 for #3358 and #3400) and the 1,088 head-minutes cost table. The census needs `gh api` over about 590 job logs, which this seat cannot use (gh is for search only). The cost table is host-local by the RCA's own statement.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0, so it merges cleanly (ev/merge-tree.txt).
- Role contracts: the three-dot diff of dev/governance/roles/ against origin/main is empty, so the contracts are current.
- CI: `merge_train.py classify` -> `GREEN f5d7df0bdf186b210bedc33c9bb4e75254aa1970 pending: none red: none` (ev/classify.txt). Owed-reds set: ev/owed-reds.txt; none of those checks is red, so no `## Red checks` answer is owed (the body says none).
- VERSION, the manifest and the RELEASE_NOTES heading are untouched (not in the 8-file diff). The diff touches no claim files and no golden fixtures.
