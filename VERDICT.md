Fix review: merge e9ddfb0874f4eec7992728539dca85f398cd5084

bus-nonce: 843c2514d7e68c0d3577abb3d1937adc
pending-ci: gate

## Scope

Round 3, a delta round over reviewed head 957818d6ea3d2dee9a71e2c01f450b673dfc327b, measured at head e9ddfb0874f4eec7992728539dca85f398cd5084. `review_carry.py 957818d6ea e9ddfb0874` prints FRESH-REVIEW. The delta has three merges and no authored commit. f6f271cebd merges origin/main 5cd7b87413 onto 51f4cf4d1f. cbdfe210c1 merges f6f271cebd into 957818d6ea. e9ddfb0874 merges origin/main ee9e23372c. `git show --remerge-diff` is empty for cbdfe210c1 and e9ddfb0874. For f6f271cebd it is the ledger driver's `tests/closures.json` set-merge plus one hand resolution: a conflict hunk in custom_components/heatpump_optimizer/optimizer.py (ev/merge_and_version.txt).

The scope is widened to exactly that production resolution. Path: optimizer.py, between `_thermostat_held_state` and `_held_unreachable`. Risk: a union resolution could drop either side's functions or cut one side's body. That would silently break either the branch's held-start what-if (`_held_reference`, #2257) or main's unreachable-setpoint reference (`_held_bisected` / `_pump_unreachable`, 3588). CI would read either break only as a features failure attributed to the wrong owner.

## Evidence

- Resolution read back: `git merge-file -p` of optimizer.py, with ours 957818d6ea, base merge-base(957818d6ea, 5cd7b87413) and theirs 5cd7b87413, differs from the head's optimizer.py only in the conflict-marker lines and two blank lines. So the head keeps both sides byte for byte and adds nothing. This matches the body's sorted-line-set read-back (ev/merge_and_version.txt).
- `_held_reference` calls `_thermostat_held_state(model, state, weather, target)`. Main's 3588 kept that signature (head optimizer.py:824, origin/main :816), so the call still binds.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at the head, Linux venv-ci: `ALL 5650 FEATURE CHECKS PASSED`, rc=0, 9m20s (ev/features_head.log). The body ran this only partially (stopped at 5540 ok); this run completes it.
- Mutant A (branch side), where `_held_reference` returns `state` (ev/mutantA.diff): `11 of 5650 FEATURE CHECKS FAILED`, rc=1. The failures include "#2257: the what-if's steady figure does not move with where the live house starts" and the null control (ev/features_mutantA.log). Killed.
- Mutant B (main side), where `_pump_unreachable` returns `False` (ev/mutantB.diff): `2 of 5650 FEATURE CHECKS FAILED`, rc=1. The two are the R10-SAV-VALUATION-RESIDUE pump-too-small checks (ev/features_mutantB.log). Killed. Both sides of the resolution are therefore live and pinned at the head.
- Step 13: `git merge-tree --write-tree origin/main e9ddfb0874` gives rc=0, with origin/main at d2e7805b7c. The only driver line is `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_and_version.txt).
- Steps 4 and 5: the three-dot diff against merge base ee9e23372c touches neither VERSION, the manifest, RELEASE_NOTES.md, nor either claim file (ev/merge_and_version.txt).
- Step 7: the body's `## Head` names e9ddfb0874f4eec7992728539dca85f398cd5084, which matches.
- Prior findings: both of round 2's residuals were dismissed there (the 3481/3574 arch-score attribution, and the 3561 "read but not merged" wording). Neither owes a change, and the delta settles neither and needs to settle neither.
- Step 11: owed-reds is in ev/owed_reds.txt. The live check runs at the head were read through the PR's check-runs API. `tests / nightly-status` is a concluded failure and is outside owed-reds, so it is not this PR's. The 18:34Z `gate` failure (job 132546035640) is the aggregate gate concluding before its inputs did; classify reads `red: none` for it. CI state: `merge_train.py classify e9ddfb0874 --pr 3582` printed WAIT (rc=3) on every poll from 18:39:11 to 19:12:28 UTC; the last line was `WAIT e9ddfb0874f4eec7992728539dca85f398cd5084 pending: gate red: none` (ev/classify.log). No required check was red while polling, so the verdict carries `pending-ci: gate`.
- Step 12: the head was still e9ddfb0874f4eec7992728539dca85f398cd5084 at 19:12 UTC (`git ls-remote` of fix/r10-arch-docs-delta, ev/head_at_post.txt).
- Step 1 for this group's own diff: n/a. The authored change is one docs row, already reviewed in rounds 1–2. The only production lines in the delta are the merge resolution, mutated above.
- Not re-derived: the body's macOS golden / env_drift / prepr.sh lines for merges 1 and 2 (heavy runs; CI's are cited instead), and the 32/92 importer counts (re-derived in round 1, untouched by this delta).

## Findings

- Residual: the body's `## Head` has two paragraphs that each call a different SHA "this PR's head": e9ddfb0874 (correct) and f6f271cebd (stale, from before the orchestrator's merge of ee9e23372c). Carry: dismissed: a stale paragraph in a body; the first paragraph names the measured head and the delta past f6f271cebd is a clean merge.
