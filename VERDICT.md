Fix review: merge 8dd2a9da51bbb06bb45d87fc93f4c3f8ec86a098

bus-nonce: 271e2316acab94c0d59211bb20b7b402
pending-ci: tests / mutation-pins (1), tests / mutation-pins (2), gate

## Summary

Round 1 review of #3875 (R11-SEAM-store Part 1 of 2), run locally from a detached worktree at the head. I reviewed the production diff (boost.py, coordinator.py, snapshots.py, store.py) and the three test files. I re-ran every mutant the body names that a single features block or one `tests/finite_boundary.py` run can decide, ran the finder harnesses at both ends, re-ran the null control and re-derived the seam enumerations. Every code, test and harness claim holds at this head. There is one paperwork note, about the null control as the body states it.

## Evidence

- RESULT head: the head I measured is `8dd2a9da51bbb06bb45d87fc93f4c3f8ec86a098` (ev/HEAD.txt), the same as the PR head at verdict time. The role contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` gives rc=0 against origin/main 24e3f37620 (ev/merge_tree.txt). It merges cleanly.
- RESULT version: VERSION, manifest.json, RELEASE_NOTES.md and tests/golden/ are untouched in the three-dot diff. No claim file moved, so there was nothing to run under step 4.
- RESULT unmutated blocks: the boost block `_bt_store = _he_store._tries()...` and the snapshot block `# D1-s1-02 ... # D1-s3-01` each print `ALL 2 FEATURES BLOCK PASSED` (ev/none_boost.txt, ev/none_snap.txt). `tests/finite_boundary.py` at the head prints `ALL 120 FINITE BOUNDARY CHECKS PASSED` (ev/finite_boundary_head.txt).
- RESULT mutants, D1-s2-06 (ev/mut_boost_*.txt): every mutant is killed by "a stored boosted sum longer than two datetimes bound reads unknown ... (D1-s2-06)".
  - Main's read restored: 3e10 and 1e14 raise OverflowError.
  - Ceiling dropped to `_Z0`: OverflowError.
  - Ceiling at `timedelta.max // 1h`, the alternative the body rejected: the `_boosted_with` arm fails. This confirms the body's reason for rejecting it.
  - The domain's floor moved to -1.0: the pre-existing negative-domain check goes red.
- RESULT mutants, D17-s3-03 and the text rule (ev/mut_snap_*.txt, ev/mut_store_textkey.txt):
  - Main's predicate (`bias is not None and ...`): the D17-s3-03 check goes red (`empty: (True, True)`).
  - `>=` at the band: the edge arm goes red.
  - Band dropped: both checks go red.
  - `if key and` removed in `in_domain`: the D1-s1-02 check goes red (`'0.3': True`).
  - A mutant of my own, `finite_float` replaced by a numbers-only read, survives (`snap_float`). It is equivalent: the `admitted("snapshots", summary)` gate in `from_dict` already refuses a text or bool bias before `best_restore` reads it. I classify it as triaged equivalent; it is not a vacuous proof.
- RESULT census mutants (`tests/finite_boundary.py`, run in separate worktrees at the head; diffs in ev/fb_mut_m*.diff):
  - Envelope loader back to `_learned_pair(entry)` (D15-s1-05): `3 of 120 FINITE BOUNDARY CHECKS FAILED`, including the round-trip check (`changed=['thermal_learning']`). This matches the body's 3 of 120.
  - `predicted_cost` back to non-null `_R` (D15-s1-04): `5 of 120 FINITE BOUNDARY CHECKS FAILED`, including the coverage check and the round-trip check (`changed=['debug']`). This matches the body's 5 of 120.
- RESULT finder harnesses at the base `1207ee13b0` and the head, with `PYTHONPATH=tests/hastub`. Each script's sha1 equals the one the body cites (ev/harness_base.txt, ev/harness_wt.txt, ev/domains_drift_*.txt):
  - boost_settle: base `restarts_raising=8 per_cell=[0, 2, 2, 2, 2]`, head `restarts_raising=0 per_cell=[0, 0, 0, 0, 0]`. `control_restarts_raising=0` at both ends.
  - domains_drift: base `sample_none_cost_admitted=0 unit_row_kept=0/1 synthetic_written_rows_kept=0/192`, head `1`, `1/1`, `192/192`. A first run under a 200 s timeout was killed at load 100+, so both ends were re-run untimed.
  - capacity_envelope: base `reloaded=0 lost=1 store_off_domain=1`, head `reloaded=1 lost=0 store_off_domain=0`. `fold_written_count_zero=1` at both ends.
  - f03_restore_unevidenced: base `restored=1 scale_after=1.0`, head `restored=0 scale_after=1.3` (refused: "No learner snapshot qualifies for restore").
  - nan_boundary `--stores accuracy,dhw_profile`: flat at both ends, as the body says for D1-s2-01 (`leaves_reaching_live=0 leaves_making_disk_undecodable=0`). Its companion check, "the boundary quarantines nan at every depth", is `ok` at both ends.
  - Every figure equals the body's.
- RESULT null control: a worktree at `1207ee13b0` with the head's three test files raises `TypeError: in_domain() takes 2 positional arguments but 3 were given` in `_domain_arm` (ev/null_control_unshimmed_typeerror.txt). I re-ran it with a signature-only shim: main's `in_domain` accepting and ignoring `key`, so main's behaviour is kept (ev/null_control_shim.diff). That run prints `6 of 120 FINITE BOUNDARY CHECKS FAILED` (ev/null_control_shimmed.txt). Five of the six are the body's five. The sixth is "each kind's shape and parse conjuncts decide alone", which is main's text-as-number reading: the "Same seam, built here" change, detected at main as it should be.
- RESULT enumerations (ev/enumerations.txt), re-run at the head:
  - `admitted(` returns 9 sites outside its definition.
  - The setdefault pair rule returns 3 seams.
  - The timedelta rule returns 82 lines, 32 of them non-literal.
  - `best_restore|undo_target` returns 3 callers.
  - All four counts equal the body's. I spot-checked the 32 non-literal timedelta lines: pump_arbiter:1525 (a constant lease), coordinator:7177 (a parameter default), wood_fuel:213 (configuration), accuracy:781 (configuration `dt_hours`). Each is dispositioned as the body says. Only boost.py:618 takes a stored document's number.
- RESULT step 6, other attacks:
  - A bool `boosted_h` still reads as unknown, because `_number` excludes bool, which replaces the deleted `not isinstance(hours, bool)`.
  - A count-0 envelope bucket caps nothing: `_capacity_caps` skips `count < CAPACITY_MIN_SAMPLES`. That is consistent with fold e.
  - `_SPAN_MAX_H` = 87649415 h. `timedelta.max` holds 273 of these spans (the store comment says "~270").
- RESULT owed reds: `tests / mutation` and `gate` read failure at this head (ev/checks_at_verdict.txt). The mutation log (ev/mutation_job_summary.txt) refuses only the 10 ADDED UNPINNED sites the body lists (9 lines, `CMP_BOUND*2` counted twice): `MUTATION TABLE REFUSED -- 1930 unpinned site(s) against 1923 ... 10 of them added by this diff`. The body's `## Red checks` names this red and its cheaper detector (prepr step 6d, `ci_predict.py`), so the trigger is answered. mutation-autofix (`tests / mutation-pins (1)`, `(2)`) is still in progress and will move the head by its pin commit (ci-autofix.md). `tests / replay` reads cancelled; it is superseded and not an owed red.
- RESULT CI: `merge_train.py classify 8dd2a9da51bbb06bb45d87fc93f4c3f8ec86a098 --pr 3875` printed `WAIT 8dd2a9da51bbb06bb45d87fc93f4c3f8ec86a098 pending: gate red: none` on every poll from 00:01Z to 01:10Z (ev/classify.log), hence the `pending-ci:` line. This merge verdict applies only once classify reads GREEN at this head, or at the autofix pin head through `review_carry.py`.
- RESULT forward-carry: the body routes carries 0 and 1 to Part 2 of 2 of this group. Both are in `wave-r11-groups.json` on `handoff/audit-r11-roster` (1609a8e97e), under R11-SEAM-store's `carry`, and each states its probe and enumerator with controls. It is a planned second part, which is a `fixer.md` own-group exception, so there is no `carry-missing` block.
- RESULT step 14: the mutation-ledger deletions are the nine `killed_by` pins whose old lines this diff rewrites, as `ci_predict.py` instructs. Nothing in `structure_budgets.json` or `closures.json` moved. I did not re-run the archscore `dS +0.0000` figure; I cite the arch-score check, which reads success.
- RESULT not re-run, cited from CI per step 11: the full gate, the mutation table, `tests/structure.py`, and the `features.py`/`entities.py`/`doc_claims.py` full runs.

## Findings

- Note: figure: the body's null control ("a worktree at `1207ee13b0` carrying the three test files ... prints `5 of 120`") does not run as stated. The head's `tests/finite_boundary.py` calls `in_domain` with three arguments, and main's takes two, so the run raises TypeError. With a signature-only shim it prints 6 of 120: the body's five plus the text-as-number kinds check (Evidence above). The control's conclusion holds and no code is affected. Carry: dismissed: paperwork figure in the PR body; the reviewer's re-derived figure is recorded in this verdict

## Friction

- The host load averaged 86 to 287 during the review, so each `tests/finite_boundary.py` run took 20 to 35 minutes, and a 200 s harness timeout killed domains_drift once. Carry: dismissed: host load, not a defect of this PR or its instruments
