Fix review: blocked f1a32a3648f9d7d72330ccd7df885b2227fa0399 root-cause-unanswered: nightly-status went red, unanswered; the arm's trigger output is unpinned (R2, R3 survive) and the arm never ran in CI
bus-nonce: 7b331bc5c141db64065a92acdfdc7a33

Round 1. #1863 (R9-F11.7, Closes #1757). I measured the head f1a32a3648f9d7d72330ccd7df885b2227fa0399, and it is still the live head at posting. Merge base 1abfef56d081146d7a38828047d790a23ffcac27. `git merge-tree --write-tree origin/main <head>` (origin/main 687e15b6f) exits 0. The diff leaves VERSION, the manifest, RELEASE_NOTES.md and tests/golden/ untouched. `fix-review.md` is unchanged between the merge base and origin/main.

## Blocking

1. **nightly-status is red at the head, and the body says it is not.** Check-run 111022420278 failed with `NIGHTLY ABSENT: nothing failed, but mutation-ledger, mutation-ledger-push did not run in that scheduled run`. Its run is 36984959667, the same run the body cites as `success`. The run's own conclusion was success, but the reporter keys on missing schedule-only lanes. `## Red checks: none` is therefore false. This diff edits tests.yml, the workflow that holds the nightly-status job and the lanes it watches, so the body owes the answer. Name the check and answer the trigger: either the main-wide ABSENT cause (#1848's ledger jobs postdate main's last nightly) with no cheaper detector, or the detector and its cost. Every other latest check-run at the head is success, skipped, or neutral (CodeQL). See `check_runs_<head>.tsv`.

2. **The arm can be disconnected while every check stays green.** I re-ran the fixer's mutants with `tests/entities.py` in full (venv python, `PYTHONPATH=tests/hastub`), restoring after each.
   - RESULT M1 (tests.yml at the merge base): rc=1, 2 of 2077 failed, both new checks. This reproduces the fixer's result.
   - RESULT M2 (field_coverage `run: true`): rc=1. The first new check fails, then the pre-existing `_pin_unhashed_installs` crashes on the bool `run`. This matches the body.
   - RESULT M3 (record-predicate dropped from the trigger): rc=1, 1 failed, the pathspec check.
   - RESULT M4 (`!cancelled() &&` dropped from the policy_lint step): rc=1, 1 failed, the first check.
   - RESULT R1 (field_coverage step loses its `GITHUB_TOKEN`): rc=1, 1 failed. Killed.
   - RESULT R5 (`GITHUB_TOKEN` added to the policy-docs `rules_sync.mjs` step, a new token-bearing pinned grader): rc=1, 1 failed. Killed, so the class predicate is live.
   - **RESULT R2 (the else branch writes `governance=false`, so the arm never fires): rc=0, ALL 2077 PASSED. SURVIVES.**
   - **RESULT R3 (the three steps keyed on `governance == 'false'`): rc=0, ALL 2077 PASSED. SURVIVES.** `_pt_armed` checks only the prefix `${{ !cancelled() && steps.changed.outputs.governance`.
   - RESULT R4 (the job-level `if:` loses its leading `!cancelled()`): rc=0, survives. That line predates this diff. Nothing pins it, though, and with `needs: [coverage]` a red coverage would skip the arm silently. Pinning it is advised, not blocking.
   - RESULT R6 (trigger short-circuited to always fire): rc=0, survives. This is the over-fire direction, so it costs only time. Not blocking.

   R2 and R3 are the under-fire direction, the one that reopens #1721. The second check claims "the arm fires on exactly the pathspec policy-docs restores". It pins the pathspec's text, not that a non-empty diff sets `governance=true`, and not that the steps key on `'true'`. Fix: pin the output wiring, i.e. the else branch writes `governance=true` and each armed step's `if` compares to `'true'`. Better still, run the trigger script on a planted diff.

3. **The arm has never run in CI, and the body says it was green.** At this head, graders-head-copy (job 111031359110) took the `governance=false` branch, because the diff touches no restored path. Steps 8–10 (setup-node, policy_lint, field_coverage) are **skipped**; see `graders_head_copy_job.log`. "At this PR's own head, the same steps are green" is false. `defect-root-cause.md` requires a detector to be shown failing on its defect and passing once it is fixed, with both runs reported. That is owed before merge, not after. Local runs cannot show the CI wiring: `gh` picking up `GITHUB_TOKEN`, checkout with tags, node, and the real Actions-token view. See "CI demonstration" below.

## Verified (not blocking)

- **The #1721 reproduction under the Actions-token view** (my own instrument, `gh_actions_view_shim.sh`). It is a `gh` wrapper that deletes `bypass_actors` from any `/rulesets/` read, run with the seat's token. It is an emulation of the Actions view, not that token. The fixer's demo used `field_coverage --ruleset-json` with a jq-stripped file. Mine also drives `policy_lint.mjs` through its real `gh api` path.
  - RESULT field_coverage(ruleset) tree=main(1abfef56d) view=admin rc=0; view=actions rc=0 (read=37 refused=0)
  - RESULT field_coverage(ruleset) tree=demo(39b07c75b) view=admin rc=0 (read=43); **view=actions rc=1, REFUSED "unperturbed, is already red"**
  - RESULT policy_lint tree=main view=admin rc=0; view=actions rc=0 (the bypass_actors skip line is printed)
  - RESULT policy_lint tree=demo view=admin rc=1; view=actions rc=1. The demo is red in **both** views. In the admin view the failure is `FIXTURE VACUOUS: a recorded field the live read omits produced 3 finding(s) and 0 skip line(s)`, a local self-test that has landed since #1721. So on today's tree, policy_lint already catches this one-token perturbation for a seat. Only field_coverage separates the principals, and it is the half of the demonstration that carries the claim. The body's expectation that the policy_lint step is "red on required-contexts drift" holds, but that step's red is not principal-specific.
- **Class enumeration.** I enumerated independently (a token-bearing step env in any job that restores from `$PINNED`, then the programs it runs). It gives the same six programs as `_PT_SEAMS`: policy_lint.mjs, field_coverage.mjs, policy_lint_envmatrix.mjs, budget_raise_gate.py (two workflows), contract_rerun.py, and tests/nightly_status.py. No job-level token env exists in any workflow. The autofix push steps carry GH_TOKEN but run no pinned program. pr-contract's token steps run only inline `gh api`. Class closed for this shape.
- **Exemptions.**
  - `policy_lint_envmatrix.mjs`: the substance holds.
    - Its rows run policy_lint.mjs and policy_lint_mutants.mjs under the inherited token. RESULT policy_lint_mutants view=admin rc=0 0 SKIP/ACCEPTED/CRASH; view=actions rc=0, 0 SKIP/ACCEPTED/CRASH, output identical except a random SHA.
    - Its one principal-dependent row, `pr / nothing skipped`, uses `unexpectedSkips`/`TOKEN_HIDDEN_SKIP_RE`. Reviewer mutant E1 rewords the emitted skip line (`UNCHECKED on this run`): RESULT E1 policy_lint view=admin rc=1, view=actions rc=1, `FIXTURE VACUOUS: the token-hidden skip line no longer matches TOKEN_HIDDEN_SKIP_RE`. So the arm's policy_lint pins env-matrix's contract.
    - The reason text is loose. Every shape inherits the real token; the explicitly token-bearing since-ref shape uses a fixture token and reaches no network. Worth rewording; not blocking.
  - `budget_raise_gate.py`: it reads reviews and the mandate issue's comments (public objects) and, on `--rerun-stale`, POSTs a rerun. It does not read the ruleset. Its job has `pull-requests: read, issues: read`, which graders-head-copy lacks. The reason holds but omits the rerun path.
  - `contract_rerun.py`: it reads runs and POSTs a rerun, and grades nothing. The reason holds.
  - `nightly_status.py`: its job has `actions: read`; graders-head-copy has `contents: read` only. The reason holds and matches the pre-existing tests.yml comment.
- **Permissions parity.** graders-head-copy and policy-docs both run on the workflow floor `contents: read`, so the arm sees what policy-docs sees.
- The fixer's head instrument: RESULT entities head rc=0 ALL 2077 ENTITY CHECKS PASSED (97 s).
- Not re-run: the gate and the mutation table (CI's runs cited: mutation success, fast success); env-matrix in full; structure.py; harness_headers.py.

## CI demonstration

Yes, a CI demonstration is needed. The arm is a detector that has never executed, and the property it exists for (the Actions-token view) cannot be produced locally, only emulated. Suggested throwaway draft:
1. From this head plus a comment-only edit to `.claude/workflows/counts.mjs`: expect `governance=true` and both arm steps **green**.
2. Then push the demo perturbation (`handoff/r9-f11-governance-7-demo` at 39b07c75, which also deletes `docs/delivery/1863.md`; ignore delivery noise): expect the field_coverage arm step **red** with ruleset REFUSED, and policy-docs green.

Both run links go in the body. Close the draft unmerged.

Evidence: `evidence/` (matrix.txt, fc_*/pl_* outputs, E1_*, mut_*.txt, mutants.py, mutants.out, graders_head_copy_job.log, nightly_status_job.log, check_runs_<head>.tsv, gh_actions_view_shim.sh).
