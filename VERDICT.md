Fix review: merge 8aa2f5177d3d03db9139a42741fa4a46782e11e0

bus-nonce: 3cea03274e60de362641a35e9f9078ee

## Findings

- The tie-break for a shared key is unpinned. Mutant M5 (`cell.prs >= prior.prs`) passes 105/105. When two kinds have the same PR count, it changes which row's `entries` the stale-issue report shows. It cannot change the threshold decision, because that reads only `prs`, and the line is unchanged since 6fd6c0c1. Carry: dismissed: only a displayed entries count can change, the prs-vs-threshold decision is unaffected, and a fixture for it costs more than it protects

## Evidence

- This is round 2, a delta review of 6fd6c0c1..8aa2f517 after the mutation-survivor block in issue comment 6400708867.
- Check (1), the block is fixed. The new `twoKindsLater` fixture puts the larger count second (verdict class 1, then friction rule id 3) and asserts prs 3. I re-ran the counts myself. RESULT real: 105 passed, 0 failed. RESULT M3 first-write-wins: 104 passed, 1 failed, on the new later-row assertion. RESULT M2 last-write-wins: 104 passed, 1 failed, on the earlier-row assertion. These match the fixer's 105/1/1. ev/mutants.txt, ev/real.txt, ev/m3_first_write_wins.txt, ev/m2_last_write_wins.txt.
- Check (2), the scope. `git diff 6fd6c0c1..8aa2f517` is one hunk, `@@ -1077,0 +1078,5 @@ export function selfTest()`, which adds 5 lines (a comment, the fixture and one assertion). It touches no other file, and production logic is byte-identical to 6fd6c0c1. The delivery row did not move. ev/delta.diff.
- Check (3): the delta does not touch the root cause or the short-parse refusal (`censusRows !== declared`), so I did not reopen them.
- The three-dot diff against merge base da12aa37 still touches only tools/policy/friction_issues.mjs and dev/programme/delivery/2820.md. VERSION, the manifest and RELEASE_NOTES.md are untouched. The delta has no host or home paths.
- Merge: `git merge-tree --write-tree origin/main 8aa2f517` exits 0 with no conflict (origin/main dfcd8d9be). ev/merge_tree.txt.
- CI on this head at review time: the check-runs API shows prelude, refresh and cancel-superseded queued, one cancel-superseded success and arm skipped. No test job has reported on this head yet, so CI's result is not measured here. ev/ci_on_head.txt.
- The PR is open at this head (merged=false, mergeable_state blocked). ev/pr_state.txt. The head is in ev/HEAD.txt.
