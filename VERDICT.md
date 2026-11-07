Fix review: merge fe40be9853d509116f14b5e9e3fc96fb075b678f

bus-nonce: f02d72a2d8d4b78de7c41b937a9fe50f

## Scope

Round 2, under the orchestrator's ruling: head fe40be98 is a46e4d02 plus the bot commit `fe40be985 ci: pin killed mutants`. This round reviews that pin commit and re-checks the round-1 ci-red (tests/mutation refused 14 unpinned sites). The code, which is unchanged since a46e4d02, is not re-reviewed.

## Evidence

- The pin commit touches only the ledger. `git diff --stat a46e4d02f fe40be98` reads 17 files changed, 102 insertions, all under `tests/mutation_ledger/killed_by/` (ev/pin_commit_stat.txt). Excluding that path, the diff prints nothing. No custom_components file, test script, budget, golden, VERSION, manifest or RELEASE_NOTES.md is changed by this commit.
- The pins are real kills, re-derived independently. For each of the 17 pins, ev/killcheck.py located the pin's `old` line inside the function its anchor names (exactly one match in that scope), replaced it with the mutant text the pin's reason records, ran the pin's `killed_by` script with PYTHONPATH=tests/hastub in a detached worktree at fe40be98, and restored the file. Result: 17/17 KILLED (rc=1), 0 survived, 0 ambiguous (ev/kill_results.txt). The worktrees were clean afterwards.
  - 13 pins were killed by tests/features.py, 3 by tests/entities.py, 1 by tests/manual_plan.py.
  - Some kills stop the script on an exception rather than a failed check: `billed_windows` GUARD_OFF ×2 and RETURN_DEL, `_window_partition` RETURN_DEL, `_window_starts` RETURN_DEL, `sensor_trajectory` RETURN_DEL, and `_evidence_attributes` RETURN_DEL. Each still exits rc=1.
  - Where checks failed, my counts are each exactly one under the pin's recorded `failed=` (1/2, 2/3, 3/4, 33/34). The offset is uniform, consistent with the pin counting the summary line. It is not a discrepancy in what was killed.
- Null control: the unmutated head passes each killed_by script. tests/features.py rc=0 (587 s), tests/entities.py rc=0 (526 s), tests/manual_plan.py rc=0 `ALL 132 manual plan checks PASSED` (ev/null_controls.txt, ev/null_*.log).
- The pins cover the round-1 sites. The 14 sites the body's `## Unpinned sites` lists as pinned map one-to-one onto pin files in fe40be985. The three extra pins are `_evidence_attributes GUARD_OFF f450751c`, `_window_partition CLAMP_DROP 80efca0b` and the second `billed_windows GUARD_OFF`. The remaining site, `tariff.py:877 CMP_BOUND`, keeps its triage `billed_windows.CMP_BOUND.0a51dd45.json` (equivalent). I re-read it at the head: with `<=`, equal sizes take the branch, `np.concatenate([factors, np.ones(0)])`, which gives the same values, so the product is bit-identical. The triage holds.
- Extra probe on the two-site CLAMP_DROP anchor (my own construction, beyond the pin): dropping the inner clamp, `max(dt_hours * 60.0, 1e-6)` -> `(dt_hours * 60.0)`, at tariff.py:545 leaves tests/features.py at `ALL 4883 FEATURE CHECKS PASSED` (ev/kill_clamp_inner.log). That guard only matters at dt_hours == 0, which no plan step has, so it is an equivalent-in-practice guard, not a missing pin. The pin's own mutant (outer clamp) is killed, as stated above.
- The round-1 ci-red is repaired. Live `merge_train.py classify fe40be98 --pr 3273` reads `GREEN fe40be9853d509116f14b5e9e3fc96fb075b678f pending: none red: none`, exit 0, at the start and again at the end of the review (ev/classify.txt, ev/classify_final.txt). The packet's gate digest shows `tests / mutation` (128392104017) and `gate` (128392446234) at success.
- Merge with origin/main: `git merge-tree --write-tree origin/main fe40be98` exits 0 at origin/main 28d46c4918285d36c409c1fb2f72eb77e04e569e (tree 5a5eb824), so the merge is clean (ev/merge_tree_final.txt). The body's `## Head` names 08fd676e as origin/main's latest. Main has moved again since; the merge is still clean, and that line is a snapshot, not a defect.
- `## Red checks` agrees with what I read. It names the two concluded reds at a46e4d02 (`tests / mutation` refusing 14 added unpinned sites, and the `gate` edit-run deferral R10-HOTFIX-GATE-BUSY-DEFER that waited on it). It states none at fe40be98, which matches classify's `red: none`.
- Review packet: refusals none, advisories none, CARRY-AUDIT 2 routed, 0 unrouted.

## Findings

none

## Friction

- The killed_by scripts import `homeassistant` and need PYTHONPATH=tests/hastub. The brief does not say so; the session-start env lines do not set it, and tests/README.md documents it. Carry: dismissed: already documented in tests/README.md, nothing owed
