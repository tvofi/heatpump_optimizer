Fix review: merge b62c1aa5d9069e025d2b2a5b5e8b0e7ee2d0a902

bus-nonce: f1b7824b82f53ccab06a0e8761ba3eb6

Round 3, a delta review of a2a7b9ef..b62c1aa5. I measured head `b62c1aa5d9069e025d2b2a5b5e8b0e7ee2d0a902` from a detached worktree. `git ls-remote origin refs/pull/2843/head` returned that SHA at 07:49Z, just before writing, so the head did not move. `dev/governance/roles/` has no diff between the merge base `11b7a9d73` and origin/main `5fb83393`, so the contract is current. Round 2 blocked on `harness-nondeterministic`. That block is cleared.

## Findings

- **`## Red checks` answers reds this head does not have.** I read the check-runs API at `b62c1aa5`. It shows 55 runs, every one success or skipped, and none red or in progress (`ev/check_runs_at_head.txt`). Both `pr-contract` runs and both `gate` runs passed (07:29Z to 07:39Z). The section still answers round 2's reds from `a2a7b9ef` (rate-limit 403s, nightly-status). It also says "No run exists yet for `9f62bb70`", which was true when the body was written at 06:15Z and is stale now. Nothing at this head owes an answer, so this does not block (step 11). It is a body-only edit and does not move the head: say that the head's runs are all green or skipped, or drop the earlier-head list. Carry: R10-996-RUNNER-CLAIMS
- **The owner's approving review is owed before merge.** `dev/governance/rules/claim-files.md` and its generated copies are code-owned policy, and the blobs are unchanged since round 1. The body's `## Approval` states this. Carry: R10-996-RUNNER-CLAIMS
- **Equivalent mutant R10** (the `path.startswith(prefix)` guard in `shaped_leaves`): SURVIVED again, as expected. Carry: dismissed: an equivalent mutant; `_diff_leaves` always prefixes the path with `<fixture>.`

## Evidence

- **What the delta changes.**
  - The only authored commit since `a2a7b9ef` is `41c0cdc36`. It touches only `dev/audit/harnesses/r10_shape_grammar_mutants.py`. The child now runs as `[sys.executable, "-B", "-c", CHILD]` with `PYTHONPYCACHEPREFIX` set to a fresh temp directory.
  - The rest of the delta is merges: `babae3204`, `708b55bab` (origin/main `11b7a9d73`), `9f62bb70d` and `b62c1aa5d`. `git show --remerge-diff` is empty for `9f62bb70` and `b62c1aa5`, so no merge has a hand resolution.
  - The trees of `9f62bb70`, `708b55bab` and `b62c1aa5` are identical (`f9df546b`).
  - `tests/env_drift.py`, `tests/entities.py`, the three claim-files rule copies, `r10_shape_claim_controls.sh`, `tests/closures.json` and `dev/programme/delivery/2843.md` have the same blobs at `a2a7b9ef` and at the head. Round 2's pin, finder-harness (band census blob `893c3957` at `996b54cf1`: `scenarios=50 susceptible=15 failures=0`) and real-capture evidence therefore carries unchanged. I did not re-run the band census.
- **Check 1: the documented invocation at the head** (`ev/grammar_mutants_intree_head.txt`). `python3 dev/audit/harnesses/r10_shape_grammar_mutants.py`, in-tree and unmodified, printed `M0 RESULT pins=16 fails=0`, R1 to R17 KILLED except R10, `RESULT mutants=17 killed=16`, `exit=0`, in 12.0 s wall.
- **Check 1: `R10 R11` repeated.**
  - At the head, 5 runs (`ev/grammar_R10_R11_x5_wt.txt`): R11 KILLED 5 of 5, exit 0 each time.
  - At `a2a7b9ef` in its own worktree, 5 runs (`ev/grammar_R10_R11_x5_prev.txt`): R11 SURVIVED 4 of 5, exit 1 on those 4.
  - The body's own 10-run loop at the head with no planted cache (`ev/figures_before_after_x10.txt`): the `a2a7b9ef` copy gave 7 SURVIVED / 3 KILLED (7 × exit 1). The head's harness gave 10 KILLED (10 × exit 0). The body quotes 8/2 against 10/0. The "before" column is nondeterministic by nature, and 7/3 against 8/2 is the same finding. The "after" column matches exactly.
- **Check 1: every child is bytecode-free.**
  - The harness has three subprocesses. Two are `git` (`rev-parse --show-toplevel`, `diff --quiet`), and neither is Python.
  - The one Python child carries `-B` plus an empty `PYTHONPYCACHEPREFIX`, so it neither writes to nor reads from `tests/__pycache__`.
  - The parent imports no project module.
  - The sibling `r10_shape_claim_controls.sh` (outside check 1's harness) runs `python3 tests/env_drift.py --all` without `-B`. That is not the same hazard: every arm copies the same `env_drift.py` bytes, and the null arm's production change appends a line, which changes the file size. A stale `.pyc` cannot stand in for different code there.
- **Check 1: null control with a stale cache** (`ev/plant_pyc.py`, my own instrument; `ev/null_control_stale_pyc_{wt,prev}.txt`).
  - Before each run I planted an UNCHECKED_HASH `tests/__pycache__/env_drift.cpython-314.pyc` compiled from the R10 mutant. Any reader of that cache loads the mutant whatever the source says.
  - At the head: R11 KILLED 3 of 3, exit 0.
  - At `a2a7b9ef`: R11 SURVIVED 3 of 3, exit 1. The plant was live, and only the head's prefix and `-B` ignore it.
  - `ev/figures_x10_with_planted_pyc.txt`: with the plant still present, the `a2a7b9ef` copy gave 10 of 10 SURVIVED and the head's harness 10 of 10 KILLED.
  - The fix, not luck, turned it green.
- **Check 2: CI at the head** (`ev/check_runs_at_head.txt`). Of 55 check runs, none is red. `tests / nightly-status`, `governance / env-matrix`, `validate / validate-hacs`, `arch-score`, `refresh` and `prelude` all concluded success at this head. `tests / mutation` is green, but the delta writes no production line, so it draws no mutant. I did not re-run the gate or the mutation table.
- **Check 3: the body** (live body read at about 07:45Z).
  - The headings are the template's (`## Head`, `## Mutation proof`, `## Null control`, `## Figures`, `## Red checks`, `## Forward-carry`, `## Friction`), plus `## Approval`, which `checkPrBody` requires for a policy path (`tools/pr/prepr.sh:627`). There is no history narrative.
  - `## Head` names the merge head `b62c1aa5` and the authored head `9f62bb70`. It says `9f62bb70` is origin/main `11b7a9d73` merged into `41c0cdc36`, with merge base `11b7a9d73`, and that is true. Its account of `b62c1aa5` is right in substance: the parents are `708b55bab` (the previous head line plus main) and `9f62bb70`, with identical trees.
  - `## Forward-carry` has two bullets; the third (the `-B` bullet) is gone, and so is the matching `## Mutation proof` carry.
- **Check 3: figures re-taken at this head** (`ev/cheap_checks.txt`, 07:45Z, origin/main `5fb83393`):
  - `STRUCTURE RATCHET PASSED`.
  - `Architecture score: dS +0.0000 NULL` (archscore `--diff 11b7a9d73 HEAD`).
  - `TOTAL: 0 error(s) across 50 policy file(s)` (`ev/policy_lint_total.txt`).
  - `RULES-SYNC ok`.
  - `CLAIMS-VERSION-UNTOUCHED`.
  - `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 11b7a9d739db`.
  - `tmp_paths: 0 refused`.
  - `claims hygiene: origin/main ok`.
  - All match the body.
- **Not re-derived by me:** the scoped-gate figure (`MODE: SCOPED -- 6 script(s) run`, `2 of 2461`, and the `2 of 2449` control). I cite CI's green `gate` and `tests / closures` at this head instead; the contract tells reviewers not to re-run the gate.
- **Check 4: hygiene.**
  - `git merge-tree --write-tree origin/main HEAD` exits 0, against origin/main `5fb83393`, tree `88a47db0`.
  - VERSION, the manifest, `RELEASE_NOTES.md` and both claim files have no three-dot diff.
  - `dev/programme/delivery/2843.md` is present and reads `**open**`.
  - `python3 -I tools/audit/carry_audit.py pr 2843`: `2 routed, 0 unrouted, 0 bad destination(s)`.
  - `ref_privacy --check`: `0 refused`, exit 0.
  - The claim-files change is policy; the owner's approving review is still owed (Findings).
- **Round:** this is round 3, so it is not yet a re-cut round.
