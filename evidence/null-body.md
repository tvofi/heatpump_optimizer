ARCH2-s2 P1 (round 10, D7): the four standing configuration notices (grid fee magnitude, grid fee sign, lower-floor modelled, comfort-band contradiction) had four coordinator flags and four hand-copied create/clear blocks. `setpoint_check.ConfigNotices` now owns the rule once: raise once per offending value, clear unconditionally. Touches only the config-notice fields in `coordinator.py`; `issues.set_issue` gains a `persistent` option. No issue closed here; Part of the ARCH2-s2 group.

Alternatives considered: the finder's patch put the create/delete calls (an `ir` import) inside `setpoint_check`; that hunk did not apply to main and the import broke `architecture.md`'s HA-boundary counts, so the owner goes through the existing `issues.set_issue`/`clear_issue` edge instead (one owner per edge, the existing mechanism). `clear_issue` is best-effort (it logs a failed delete), a small change from the bare delete.

This head adds one commit to the PR's code: `tests/structure_budgets.json`'s `seam_cut_total` goes back to main's 420. The previous merge of main (2f5bf7257) wrote 413 by hand-carrying this branch's delta measured under the OLD seam-cut definition (710 -> 703) onto main's 420, which #2711 re-recorded under a NEW definition (distinct (seam, attribute) and (seam, callee) pairs, O19). Under the current definition this branch measures 420, exactly what origin/main measures: folding four flags into one `ConfigNotices` slot moves the owned-attribute counts (learning 37 -> 36, grid 27 -> 24) but no seam crossing. The 413 was never earned, so nothing was owed; the three-dot diff of the budget file no longer touches `seam_cut_total`, and against the base this is no raise. The reason is in that commit's message (`--record --allow-regression`).

## Head

`9a3bbaa751b71a9b6c75a4c152b9c96d4f5a92a1` merges origin/main `21a1e04a7` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Body-only re-issue (r3): the code head stays `6e4e274a4afc889228f867b8ac41edd2adc646c8`, re-pushed unchanged as handoff/r10-config-notices-r3; the only change is the Friction item's `Carry:` (its named group, R10-POLICY-FIXER-MD, is done). Re-taken at origin/main 7138516b4b03764b4e76afbfdf183bab2cb1396b, 2026-10-25T06:34Z: `python3 -I tools/audit/carry_audit.py check --body <this body>` (main's checkout) prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`; the previous body printed `BAD-DEST body item c8bac42d: R10-POLICY-FIXER-MD: R10-POLICY-FIXER-MD is done (resume.stage done)`. No figure below was re-taken.

`6e4e274a4afc889228f867b8ac41edd2adc646c8` merges the authored code head `d7017b683923008651481b37dd9d7f3d67d9393b` and then merges origin/main `ab00437c9` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

d7017b683923008651481b37dd9d7f3d67d9393b, on base 662a3809ced43b41dba2166f04277f2d3c95e991 (origin/main's tip, committed 2026-10-25T01:02:53Z, merged into the branch, never rebased; measured from 2026-10-25T02:06Z).

## Mutation proof

The five sites this diff adds were pinned under `tests/mutation_ledger/killed_by/` by an earlier local `--pin-killed` run; at this head each was re-driven with `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor "<anchor>" --scripts tests/features.py --jobs 2` (records nothing). Four printed `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced`, killed by `tests/features.py`. The fifth, `issues.py:set_issue GUARD_OFF 266bc37b`, the instrument refused ("MUTATION TABLE REFUSED -- no full-line comment in any file in the pool, so the run has no null control"): its pool is `issues.py` alone. That one was re-proved by hand: `issues.py` line 54 `if persistent:` -> `if False:`, then `PYTHONPATH=tests/hastub python3 tests/features.py`: rc=1, "2 of 4359 FEATURE CHECKS FAILED" (the two named below), then `git checkout` restored the line and `git status --short` printed nothing. The checks each mutant reds:

- `setpoint_check.py` `if offending is None:` -> `if False:` (the reload-leak defect, a clear gated on instance memory): "ConfigNotices: a fresh instance (entry reload) still clears the notice", plus the four audits' existing "corrected configuration clears" checks.
- `setpoint_check.py` `if self._raised.get(issue_id) == offending:` -> `if False:`: "ConfigNotices: the same offending value is created once, persistent WARNING" (it keys on the issue record's identity, because the stub replaces a re-created issue in place and a count cannot see a repeat).
- `issues.py` `if persistent:` -> `if False:`: the same check's `is_persistent` clause, and the existing "a stored negative rule raises the sign notice" check.
- `coordinator.py` `worst > fee_bound(currency)` -> `>=`: "fee audits: a zero fee and a fee exactly at the bound raise nothing; 1% above raises the magnitude notice".
- `coordinator.py` `lowest < 0.0` -> `<=`: the same check's zero-fee clause (a `<=` would warn every installation with a zero fee).

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 4` at this head: "PIN KILLED: nothing to pin" (0 new unpinned sites against the base).

## Null control

Each `--anchor` drive's own controls (which also serve the hand mutant, run with the same driver on the same head): baseline `tests/features.py` at this head rc=0 failed=0, and the comment-only null mutant `coordinator.py:510 NULL_COMMENT` survived `tests/features.py`. For the budget restore: `python3 tests/structure.py` in a detached worktree of origin/main at 662a3809ced43b41dba2166f04277f2d3c95e991 prints `seam_cut_total = 420` and `ok seam_cut_total 420 <= 420`; at this head it prints `seam_cut_total = 420` too, so the restored value is main's own measurement, and the merged tree before the restore commit (budget 413, carried from 2f5bf7257) printed `FAIL seam_cut_total 420 > 413 (+7)`.

## Figures

- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at this head (exit 0). Per-seam rows (its seam table) differ from origin/main's only in the owned-attribute column: learning 37 -> 36, grid 27 -> 24; xattr, xmeth and cut equal per seam; seam_cut_total 420 at both.
- `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/structure_budgets.json`: only class_excess_loc 18209 -> 18110, coordinator_attrs 146 -> 143, coordinator_multiassigned_attrs 114 -> 110, max_class_loc 8449 -> 8350 and recorded_at; every row moves down, none up.
- `python3 tools/audit/archscore/score.py --diff 662a3809ced43b41dba2166f04277f2d3c95e991 HEAD`: `Architecture score: dS +0.0611 IMPROVES` (coord_footprint 2463 -> 2446, coordinator_multiassigned_attrs 114 -> 110); null control `--diff` of the base against itself: `dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --diff 662a3809ced43b41dba2166f04277f2d3c95e991` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out.`; `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=662a3809c ./tests/run.sh` with `PYTHONPATH=tests/hastub` passed every script but two: `tests/entities.py` (the BASH_ENV shadowing, see Friction) and `tests/harness_headers.py`, which never ran (`gate_lock: flock-wrap refused ... holds no lease`: this seat set `HPO_GATE_LOCK_LABEL` without taking a lease). Re-run with `BASH_ENV` unset: `tests/harness_headers.py` ALL 112 HARNESS HEADER CHECKS PASSED and `tests/entities.py` ALL 2429 ENTITY CHECKS PASSED, at this head and identically at origin/main.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` (BASH_ENV unset): "no closures, fast, wave-script or instrument red predicted against 662a3809ced4".
- Finder's harness (`dev/audit/rounds/round10/D7/arch2-s2/`) was not re-executed; the architecture score above is the instrument it reads, re-run here at both ends.

## Architecture score

Architecture score: dS +0.0611 IMPROVES (coord_footprint and coordinator_multiassigned_attrs fall; no gate metric rises).

## Red checks

- `tests / fast (3.14)` at 2f5bf7257: `python3 tests/structure.py` refused `seam_cut_total 420 > 413 (+7)`. Not a regression of this diff: the merge of main hand-carried a delta measured under the retired definition onto #2711's re-recorded 420; this head restores 420 (see the paragraph above the Head). Cheaper detector: `python3 tests/structure.py` on the merge commit before the push, which `fixer.md` step 5 already requires ("runs before every push") and `prepr.sh` runs; it would have printed this exact FAIL in seconds. It did not catch it because the merge was resolved by carrying the branch's recorded numbers rather than re-recording after the merge, and the ratchet was not re-run on the merged tree. No new detector is owed: the existing one, run, catches it.
- `gate` ("still being judged") and its following reds at 2f5bf7257: the codescan wait race (R10-RCA-CODESCAN-WAIT #2756; R10-GATE-DEFER #2770 fixes it), not this diff.
- `pr-contract` at 2f5bf7257: the body's `## Red checks` did not name `tests / fast (3.14)`; this body names it.

## Forward-carry

none

## Friction

environment: cost: the seat's BASH_ENV toolchain hook shadows the stand-in python3 that two tests/entities.py workflow-step checks put on PATH, so entities.py and prepr's closures step fail on an untouched tree until BASH_ENV is unset. Carry: R10-POLICY-FIXER-MD

## Unpinned sites

Re-derived at this head with `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: none. The five sites the diff adds are pinned, each re-verified at this head (four by `--anchor`, `set_issue` by hand; Mutation proof), killed by `tests/features.py`:

- custom_components/heatpump_optimizer/coordinator.py `_audit_grid_fee` CMP_BOUND (the `grid_fee_magnitude` bound): pinned.
- custom_components/heatpump_optimizer/coordinator.py `_audit_grid_fee` CMP_BOUND (the `grid_fee_sign` bound): pinned.
- custom_components/heatpump_optimizer/issues.py `set_issue` GUARD_OFF (`if persistent:`): pinned.
- custom_components/heatpump_optimizer/setpoint_check.py `ConfigNotices.report` GUARD_OFF (`if offending is None:`): pinned.
- custom_components/heatpump_optimizer/setpoint_check.py `ConfigNotices.report` GUARD_OFF (`if self._raised.get(issue_id) == offending:`): pinned.
