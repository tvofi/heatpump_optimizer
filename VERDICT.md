Fix review: blocked 5640ad9d03e8a9bd9b5f8cae7701887170e70713 class-open: field coverage step 3f3 is a heavy_skip-gated heavy step that runs unleased and the body does not disposition it; closures_owes_slot survives its own deletion

bus-nonce: fb2bd131e471e08d662d6779020bcc62

## Round

First round. Reviewed head `5640ad9d03e8a9bd9b5f8cae7701887170e70713`, which is still `refs/pull/3191/head` at the time of writing. Merge base `616868bdc`. `dev/governance/roles/` on main has not changed since the merge base, so the contract I followed is current.

## Block

1. **class-open: step 3f3 `field coverage`.** Carry 26, as the PR body's own index counts it, asks for the slot to be taken "just before the first heavy step that heavy_skip/selftest_owed/the scoped gate does not skip". `heavy_skip` gates three steps: 3a `mutants`, 3f3 `field coverage` and 3f5 `register check`. The diff calls `take_slot` before 3a, 3h, 6b and 6d', but not before 3f3 or 3f5. 3f5 measures about 0.5 s per call, so leaving it unleased is defensible, but the body does not say so. 3f3 is the most expensive step that is now unleased:
   - `node tools/policy/field_coverage.mjs` takes **234 s on an idle machine**, against 184 s for the mutants drive that the PR does lease (measured under load; `ev/step-timings.txt`, `ev/fieldcov-seam.txt`).
   - Plant: a one-line change to `.github/workflows/arch-score.yml` on this head. `heavy_skip mutants` returns skip (rc 0) and `heavy_skip "field coverage"` returns run (rc 1), with the reason "field coverage reads .github/workflows/arch-score.yml". The plan's case is `scoped` with 0 scripts (`ev/fieldcov-seam.txt`).
   - So a workflow-only diff, or any diff reaching `tests/structure.py`'s closure but not the mutants read-set, runs a ~4-minute step outside the four-slot cap. That reverses the old behaviour, where 1b leased the whole run. The body neither leases 3f3 nor rules it light, and the self-test pins exactly four call sites, so it holds that omission in place.
   - Repair: call `take_slot` in the else-arm of 3f3 (and of 3f5, or state why 3f5 is light). Update the four-call-site count row, and add a driven row: a plan where mutants skip and field coverage runs takes the slot before 3f3.

2. **mutation-vacuous: `closures_owes_slot`** (prepr.sh:773-783, new in this diff). This predicate alone decides whether the scoped recorder (`derive_closures.sh`, the step that P208 measured at 40 minutes) runs inside a slot. No self-test row drives it; `grep -n closures_owes_slot` shows only the definition and the one call site.
   - Mutant A: `return 1` as the first body line, so the recorder never takes a slot. Result: **477 passed, 0 failed** (`ev/mutant-A.diff`, `ev/mutant-A.summary`).
   - Mutant B: `[ "$k" = scoped ]` changed to `[ "$k" = full ]`. Result: **477 passed, 0 failed** (`ev/mutant-B.*`).
   - The "calls take_slot at ... (4)" row counts text only, so it stays green with the predicate gutted.
   - Repair: drive `closures_owes_slot` the way the 6b rows drive `closures_line` (a stubbed `closure.py affected` workdir). Cover scoped with scripts → 0, skip → 1, full → 1, `closures_records_here` false → 1, and a scoped but empty `affected.scripts` → 1 as the null control.

## Findings

- Follow-up: carry 26's "Measure before and after: slot-wait minutes per prepr over a day" is not measured. The body discloses this under `## Figures` ("Not measured"), and the "after" half can only be taken once the change is live. It is owed after the merge: count slot waits over one day of prepr logs with fixer logs included (carry 25's caveat), and compare them with the 29-of-35 baseline. Carry: R10-PREPR-CAP
- Follow-up: in `take_slot`, deleting `SLOT_TAKEN=1` survives (mutant C, 477 passed, 0 failed, `ev/mutant-C.*`). The idempotence row only drives a successful take, where the exported `HPO_SLOT_LABEL` makes the second call join anyway. On the WARN path (failed take), each later heavy step would retry `slot-take` and queue again, and append another `slot-unleased` marker. Add a row that drives two calls with a failing `slot-take` stub and asserts one attempt. Carry: R10-PREPR-CAP

## Evidence

- RESULT selftest-head: `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` at the head printed `477 passed, 0 failed` with rc 0, in 8 min 43 s (`ev/selftest-head.tail`). This matches the body's figure.
- RESULT mutants: A (`closures_owes_slot` returns 1) survived; B (scoped→full) survived; C (no `SLOT_TAKEN=1`) survived. Each run was in place in its own detached worktree, so it is not affected by the /tmp-copy runner artefact the body mentions.
- I did not re-run the body's three named mutants (unconditional take, per-target interpreter in 6g, `if false` in 1a3). The rows they name exist at the head, and I read them as consistent with the claims.
- Carry 6 being built at the merge base is confirmed: `git grep` at `616868bdc` shows 6g triggering on `pinned_touched "$CR.paths" "$CLAIMS_READS"` at line 4119.
- Merge: `git merge-tree --write-tree origin/main 5640ad9d…` returned rc 0, with no conflict (`ev/merge-tree.txt`).
- `VERSION`, the manifest and the notes heading are not in the diff (6 files: three gate-scoping copies, nudge.md, delivery row, prepr.sh).
- `## Head`: the body names `5640ad9d03e8a9bd9b5f8cae7701887170e70713`, the head I reviewed.
- CI: `merge_train.py classify … --pr 3191` was still `WAIT … pending: gate red: none` when this verdict was written (`ev/classify.txt`). The block does not depend on CI. The packet's red `tests / nightly-status` is not this PR's: the diff does not reach what it reads.
- Not re-derived: the body's 4/4-slot pool figure and the 90 s `timeout` null control (main stalls at rc 124, branch finishes at rc 0). I could not re-derive them here without a live four-holder pool, and did not build my own instrument to stand in for them.
- No finder's harness is named. The packet says `none named`, and the roster carries an out-of-PR `dev/audit/harnesses/r10_prepr_cap_lease_mutants.py`, which I did not run.
- Approval: the policy edits (gate-scoping.md, nudge.md) still need tvofi's approving review whatever this verdict says.

## Friction

- The session's frugal-routing hook refused inline reads after five operations and forced a scout delegation just to read background-task output files.
