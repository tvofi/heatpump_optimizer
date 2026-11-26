Fix review: merge 8d38554ab6116e74519b08c6f7256e275e078953

bus-nonce: 7e94e57de465e230476790be9a560125

## Scope

Round 1, full review (no prior verdict names this head). Diff (three-dot from merge base e91329c2): `tests/stress_budgets.json` one value, `summer/1z/space/valve.rss_attrib_mb` 0.2 -> 0.4, plus the PR's own `dev/programme/delivery/3909.md` row. No `custom_components/` line, no check logic, no `tests/stress.py` line moves.

## Evidence

- RESULT reading: the three CI readings the body cites re-read from the job logs (ev/ci-valve-readings.txt): job 139744456641 `attributable 0.4 MiB` (RSS peak 124.0, baseline 123.6) and the FAIL line naming this row vs recorded 0.2; job 139068952639 `0.1 MiB` (peak 120.3); job 139717939394 `0.0 MiB` (peak 123.0). All three match the body.
- RESULT mutation: `rss_attrib_fail_threshold`, `memory_stale_axes`, `attributable_reads_the_tree`, `stale_cheap_verdict` extracted verbatim from tests/stress.py at the head by AST and evaluated on each ref's record (ev/mutation-threshold.txt). Old record 0.2 -> threshold 0.3: 0.4 FAIL. New record 0.4 -> threshold 0.6: 0.0, 0.1, 0.4 pass. Reverting the one value (the mutant) reproduces main's red; the change is earned by the record, not by the instrument.
- RESULT docstring remedy: `rss_attrib_fail_threshold`'s docstring (tests/stress.py:2182-2199) says the record is the maximum over contexts and to "re-record with the gate draw folded in when a red names a scenario whose record is thinner", and refuses an additive floor. Folding the CI draw 0.4 in, and no higher, is that remedy; the threshold stays `recorded * MEMORY_BUDGET_FACTOR`, unchanged.
- RESULT no check logic: `git diff e91329c2...8d38554a` touches only the two paths above; VERSION, manifest and RELEASE_NOTES untouched.
- RESULT stale side on CI: CI probe watermarks 120.3-124.0 MiB sit above the 76.3 record, so `attributable_reads_the_tree` declines the stale arm there (the red log prints 54 of 54 probes declined); the raise cannot turn CI's stale arm red.
- RESULT Raise justification: `python3 tools/audit/archscore/score.py --diff e91329c2c2 HEAD` at the head prints `Architecture score: dS +0.0000 NULL` (ev/archscore.txt), matching the body. Missed-payment hunt: an additive floor on the attributable arm is refused by the docstring and the detection check; a deeper `--record-memory` re-record is a measurement, not a code payment; no code-side payment found.
- RESULT merge: `git merge-tree --write-tree origin/main 8d38554a` exits 0 (tree f128a261), origin/main at 1d307773.
- Figure not re-derived: the body's "import floor ... up to 0.5 MiB for this row" -- the three logs read show 0.0-0.4 for this row; 0.5 is the cross-scenario spread in the `attributable_reads_the_tree` docstring. Paperwork, not blocking; the new threshold 0.6 clears 0.5 either way.
- RESULT CI: `merge_train.py classify 8d38554a --pr 3909` rc=4 (ev/classify.txt): `APPROVAL-OWED 8d38554ab6116e74519b08c6f7256e275e078953 1 budget raise(s), first tests/stress_budgets.json: summer/1z/space/valve.rss_attrib_mb: 0.2 -> 0.4 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`; judged GREEN, the only red is the raise's approval, which follows this verdict.
- Red checks: `budget-raise-gate / budget-raise-gate` is the raise's approval, answered in the body; `tests / nightly-status` is red and outside the owed-reds set (ev/owed-reds.txt), so it is neither answered nor a block.
- Forward-carry: the body's root-cause carries to #3885 (detectors a and b); carry_audit at the head routes both.

## Findings

- Residual: the raise makes the stale-cheap arm fire on the record platform. A probe whose watermark sits below the 76.3 MiB record (the macOS context the row was recorded in) and reads 0.1 MiB attributable is now `stale` (0.1 < 0.4/3.5 = 0.114), where at 0.2 it was not (ev/mutation-threshold.txt, peak 76.0 case). CI is unaffected (its watermarks are above the record, so the arm is declined), so the gate stays green; a local macOS full stress run may red on this row. The fuller remedy is a deeper multi-context `--record-memory` sample or detector (b)'s noise-floor rule over sub-MiB rows. Carry: #3885
