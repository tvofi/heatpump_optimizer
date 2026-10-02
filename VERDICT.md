Fix review: blocked edb67c665910d30ba1fa12585d324e46d4652d7c root-cause-unanswered: mutation went red, unanswered

bus-nonce: faa7aa7f3298abd9e89ba5026626743e

PR #1845, roster group R9-EG-B5a, issue #1743. Round 1. Reviewed from a detached worktree at
edb67c665910d30ba1fa12585d324e46d4652d7c (code head dafa803c), merge base 2b6c5b87 (= origin/main
at review time). `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/`
was empty, so the contract copy is current. No earlier review material exists: the roster's
`handoff/r9-eg-dhw-closure-dedupe-review` ref is absent on origin.

## Why blocked (fix-review step 11)

The head's own check-runs show `mutation` **failure** (job 110843162592):
`ADDED UNPINNED optimizer.py:4058 RETURN_DEL` and `MUTATION TABLE REFUSED -- ... 1 of them added by this diff`.
The body's `## Red checks` reads "none". `pr-contract` (job 110857027418) is red on that exact gap:
"check `mutation` is red and `## Red checks` does not name it".

This is the ci-autofix unpinned-sites case, and it repaired itself. The pin step printed
`PIN KILLED: 2 pinned, 0 left unpinned`, and `mutation-autofix` pushed dfd383ae
(`ci: pin killed mutants`, github-actions[bot]). That commit adds two ledger rows only:
`_solve_objectives` CLAMP_DROP (comfort_band), killed by tests/env_drift.py, and
RETURN_DEL, killed by tests/doc_claims.py. So the fix is a body edit and no code change.
In `## Red checks`, name `mutation` as the ci-autofix.md unpinned-sites case and cite the
bot pin commit dfd383ae. In `## Head`, name dfd383ae. The "Mutation proof" section says one
added site was expected; that prediction was right.

**Head moved:** the live head is now dfd383aea689ae7f6a102882839655c28165a2e9. The bot made that
move, not the fixer, so this is not a `head-moved` violation. `git diff --name-only edb67c66
dfd383ae` names only the two `tests/mutation_ledger/killed_by/...` files, which the branch's own
diff does not touch. So under orchestrator.md section 11, my measurements below carry to dfd383ae.
After the body edit, a merge verdict should be a carry and needs no re-review of the code.

## RESULT lines (everything except the red-check answer holds)

Refactor equivalence. These are my own AST instruments (disclosed per step 9). The finder's
harness is the brief's: env_drift byte-identical, claim files untouched, structure rows down.
- RESULT ast-equal base._optimize_with_dhw.{_space_traj,objective,objective_batch} == head._solve_objectives.*: True True True (docstrings stripped; renames power_schedule->space_power, power_matrix->space_matrix, space_penalty->penalty)
- RESULT ast-equal base._optimize_space_only._space_traj == head: True
- RESULT ast-equal base._optimize_space_only.{objective,objective_batch} == head.*[dhw_plan_power=None] (fold the IfExp to its None arm, substitute the alias): True True
- RESULT setup statements (comfort_band, _terminal_cost, _grid_terms, _energy_cost_fn): identical under n_steps=h.n_steps, start_time=h.start_time, solar_gains_per_step=h.solar_gains. Every captured local in both base paths is a plain h.<attr> read (bindings_base_*.txt).
- RESULT late binding: no captured name is rebound after the closures in either base path. The one `h` hit (base 6149, head 6191) is a list-comprehension target, which has its own scope in Python 3, so it is a false positive.
- RESULT call-sites identical base vs head (5 calls; space path never passes a DHW plan; DHW path calls objective(optimal_space, optimal_dhw))
- RESULT undef-total 0 at head for _solve_objectives/_optimize_space_only/_optimize_with_dhw (base 0)

Perturbations, with a null control: the unperturbed head passes every instrument above. Each
perturbation is one line:
- M1, the objective drops the DHW term: dhw objective ast-equal False. Every other instrument holds.
- M2, the batch drops the DHW term: dhw objective_batch ast-equal False.
- operand swap, `dhw_plan_power + space_power`: dhw objective ast-equal False. This is numerically null for two IEEE operands, so the instrument errs toward sensitivity.
- the space path passes a plan, `objective(optimal_power, optimal_power)`: call-sites DIFFER.
- deleting `comfort_band` from the builder: undef ['comfort_band']. This is the control for the undefined-name check.
- A numeric perturbation moves a golden. CI's pin step at this head killed CLAMP_DROP on the builder's `comfort_band` with tests/env_drift.py (rc=0 -> rc=1). The fixer's M1 and M2 rows in features.py were run at 5a69e874. I could not re-run them here because this Mac has no numpy and no container. CI's `fast (3.14)` is green at this head.

Structure, with tests/structure.py run at both ends (Python 3.14, rc=0 at both):
- RESULT duplication_copies 60 -> 59, max_method_loc 386 -> 385, methods_over_200 11 -> 10, methods_over_150 18 -> 18
- method LOC: _optimize_space_only 297 -> 189, _optimize_with_dhw 386 -> 274, _solve_objectives 150. sysid.identify (385) is now the maximum. The merge commit's correction of 5a69e874's message is accurate. The reasons for the re-record are in the commit messages, as rule 2 requires.

Numeric checks, cited from CI at edb67c66 (35 check-runs). These were not re-run locally:
env-matrix, fast (3.14), closures, closure-scope, coverage, coverage-ratchet, typing and
instrument-self-tests passed; so did briefs, policy-docs, delivery-status and nightly-status.
`mutation` failed (above). pr-contract had one cancelled run and one failed run (above). Of the
two budget-raise-gate runs, one was cancelled and one passed. closures-autofix and
claims-autofix were skipped, so no closure or claim repair was owed. The body's env_drift
figure "56 scenarios, NO UNCLAIMED DRIFT" was taken at 5a69e874. At this head its coverage is
CI's green env-matrix/fast plus the mutation run's `baseline tests/env_drift.py: rc=0 failed=0`.
I did not re-derive the count of 56.

Other contract steps:
- Claims: `git diff --stat MB...HEAD -- tests/golden/` is empty, and the claim files are untouched (step 4).
- VERSION, the manifest and RELEASE_NOTES are untouched (step 5).
- `git merge-tree --write-tree origin/main HEAD` returned rc=0, with no conflict (step 13).
- The body's code head dafa803c matches the head reviewed. The body's edb67c66 is its own row commit. dfd383ae is not in the body; see above.
- Forward-carry "none" is correct. EG-B5's brief already assumes the closures stay on the optimizer, and this PR found nothing that changes that stage.
- Class: the issue names a single seam for B5a, the two duplicated closure sets. The AST comparison covers all three closures and the four setup terms. No other copy remains: structure.py's clone listing at the head shows no _solve_objectives class.

## "Part of #1743" against fixer.md step 7

"Part of" is correct, and #1743 stays owed after this PR. Step 7's "closes its issues"
covers the issues the group fixes. R9-EG-B5a's roster entry has `fixes: []`, and its brief says
"Issue #1743 (Part of)". The issue's disposition is "R9-EG-B5a (Part of) and R9-EG-B5 (Fixes)".
The issue's substance is the DHW-planner extraction, which R9-EG-B5 does (`fixes: [1743]`, after
R9-EG-B5a). A `Closes #1743` here would auto-close the issue on merge and drop the work EG-B5 still owes.

Evidence: the evidence/ directory (HEAD.txt names the head; the instruments, outputs, patches and CI excerpts are all there).
