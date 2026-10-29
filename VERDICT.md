Fix review: blocked a5b8603b2fd49196105b4238a205b39a038f6944 ci-unconcluded: tests / mutation refused 9 added unpinned sites and both mutation-pins shards were still running 3.5 h after the push

bus-nonce: d83aee5bc851ad16a2e522c6b295aa0a

## Block

Round: fix review 2 of this group (fix review 1 blocked `fa6eb482b` class-open).

This blocks on CI that has not concluded. It does not block on a defect in the authored work: every check I ran on the authored change passes (see `## Evidence`). `fix-review.md` step 11 says a red check can be judged only once all of the head's workflows have concluded. At 2026-10-29T00:51Z, at head `a5b8603b2fd49196105b4238a205b39a038f6944` (unchanged since dispatch), the head's CI read:

- `tests / mutation` (job 123109077767): `MUTATION TABLE REFUSED -- 3760 unpinned site(s) against 3758 at the ratchet base b0b2d7697f8c..., 9 of them added by this diff`. The 9 include `optimizer.py:536 GUARD_OFF` and `thermal_model.py:1772 GUARD_OFF`, which the body lists as "Open, survivor on CI".
- `tests / mutation-pins (1)` (job 123111705393) and `(2)` (job 123111705308): `in_progress` since about 21:27Z, and still running at 00:51Z. These shards decide whether CI kills those two survivors. No `mutation-autofix` commit has landed.
- `prelude` (job 123103594775): `FAIL run(s) [40769797152] still adding sources after 8700 s`. `gate` (job 123169165710): `FAIL prelude: failure`.

Re-review owes only a CI read. Once the pin shards conclude, either:

- (a) `mutation-autofix` pins the killed sites and the mutation lane goes green on the bot head, and `prelude`/`gate` go green on a re-run; that is a merge, or
- (b) a pin shard still reads `536 GUARD_OFF -- lives` or `1772 GUARD_OFF -- lives`. That contradicts my local kill below and is a real block: those sites need a CI-reachable killing check.

## Findings

- The body no longer describes the head. `## Head` describes `ff71ecaa8` as the authored code head and never mentions `6ff573112`, the commit that adds `single-zone valve: the reference charges the tank onto its curve, never past it` to `tests/features.py`. `## Unpinned sites` and `## Red checks` still say `optimizer.py:536 GUARD_OFF` and `thermal_model.py:1772 GUARD_OFF` are open CI survivors and "this check stays red at this head until each has a killing check or a triage". At this head both have a killing check: I killed both with it (Evidence). The error runs in the safe direction: the head is better than the body says. The `## Red checks` account of `tests / mutation` should name `6ff573112` when the body is next re-taken. Carry: R10-BUFFER-STORE (the fixer's body at its next head)
- Instrument false positive: `tools/audit/seat/review_packet.py render` refused `host-path` and wrote no packet. Its message was `dev/audit/rca/R10-RCA-BUFFER-STORE.md:9: home-directory in an added line`, and line 9's only match is the substring `/root` inside `dev/governance/roles/root-cause.md`. This seat's `$HOME` is `/root`, and `ref_privacy.py`'s host-identity match takes `$HOME` verbatim with no path-boundary check. So on any cloud seat whose home is `/root`, every diff citing `roles/root-cause.md` refuses the packet. I did not work around it: no packet was rendered, and the review ran by hand from the PR body and the live checks. Carry: R10-REF-PRIVACY

## Evidence

- Head measured: `a5b8603b2fd49196105b4238a205b39a038f6944`, which is the PR head at dispatch and at 00:51Z (`ev/checks_at_verdict.txt`). Merge base `b0b2d7697`, which equals `origin/main`. The `dev/governance/roles/` diff from the merge base to `origin/main` is empty, so this contract is current.
- Merge: `git merge-tree --write-tree origin/main a5b8603b2` exits 0 with tree `79a984f46` and no conflicting path (`ev/merge_tree.txt`).
- Step 1, mutation proof at this head. Each mutant was applied to a `git archive` of the head and run through `tools/audit/seat/features_block.py` under the CI venv (numpy 2.4.6, scipy 1.17.1; `ev/mut.sh`, `ev/mut2.sh`):
  - RESULT null rc=0
  - RESULT opt536 rc=1 (`optimizer.py:536` -> `if False:`): 29.4493 C against the 26.6000 C curve
  - RESULT tm1772 rc=1 (`thermal_model.py:1772` -> `if False:`): 27.1364 C
  - Over the rework block (13 checks):
    - RESULT null2 rc=0
    - RESULT m8 rc=1 (`1756` headroom clamp dropped): `refused 14.094 kW`, the body's figure
    - RESULT m3 rc=1 (`1824` cap dropped): `refused 0.000 kW; the tank ended at nan C`, the body's figure
  - Files: `ev/mutants.txt`, `ev/mutants2.txt`.
- Step 2, the finder's harness. `dev/audit/harnesses/r10_setpoint_boost.py` has sha1 `878ce05bcd06` at both ends. I ran it unmodified from each tree's archive, at the base `b0b2d7697` and at the head. Both rc=0, `failures 0`.
  - Base: every 750 L plan hash equals its 0 L twin's (`identical plan` 8 spread, 14 flat), so the finding reproduces.
  - Head: no 750 L hash equals its twin's.
  - Null: all 16 no-buffer rows are byte-identical between the two ends.
  - Files: `ev/setpoint_base.txt`, `ev/setpoint_m_null.txt`.
- Body figures I did not re-derive at this head:
  - `savings` on the 750 L cells now reads 8.85, 1.68 and 3.11 for the body's three cells. The body quotes 8.83, 1.66 and 2.88, taken at `baff727d1` and labelled so.
  - The 1.7 flat set-point cells read -9.35 and -8.52, against the -6.89 that the dismissed "understated savings" carry quotes. The direction (understated) holds, but the size is this head's figure, not the body's.
- Step 3, null control: `r10_buffer_store.py reference` (harness sha1 `1ed68fea6f69`) at both ends, rc=0 both (`ev/harness_reference.txt`).
  - Unvalved reference: 8.15 / 9.00 kWh at both ends.
  - Valved reference: 8.15 / 14.92 at the base, 8.10 / 7.99 at the head.
  - Refused heat: 0.00 everywhere.
  - All of these match the body's figures at `baff727d1`.
- Step 4, claims: `GOLDEN_MODE=drift GOLDEN_REF=b0b2d7697 tests/golden.py` reads `NO UNCLAIMED DRIFT: 56 scenario(s) checked against b0b2d7697` and `NO STALE FIXTURE` (`ev/golden_drift.txt`). `claims-for: 7.0.5` equals `VERSION`. `card_claimed_drift.txt` is untouched.
- Step 5: the three-dot diff touches none of `VERSION`, `RELEASE_NOTES.md` or `manifest.json` (`ev/static.txt`).
- Step 6, class: I ran the body's rule, `git grep -n "\.simulate_step(\|compute_cop(" -- custom_components` (`ev/ratchet_census.txt`). Every hit is either named in the body or falls under its blanket clause. `coordinator._capacity_caps`, `_max_pump_rise` and `flow_meter.space_reference_cop` price at outdoor COP in every zoning at the base too, and none sizes a valved step's power. No seam is open.
- Step 10: the carries are present on `handoff/audit-r10-roster` at the SHAs the body names (`ev/carries.txt`): the two R10-STORE-RACES carries (35 L fallback; over-booking residual) at `5704c4048`, the CPU carry at `b5ea7fda7a9e`, and the R10-FLOW-POSTMERGE carry at `c0dbb4585d68`. The CPU carry is quoted there at the earlier head `173b71ba4` (2.5x).
- Step 14: every budget move in the three-dot diff is downward:
  - `class_excess_loc` 18037 -> 17981
  - `functions_cc_over_15` 28 -> 27
  - `methods_over_200` 9 -> 8
  - `stress_budgets` `summer/2z/space/wood-two-tank` ratio 7.64 -> 2.2
  - `tests/structure.py` at the head reads `STRUCTURE RATCHET PASSED`. No raise, so there is no budget-raise to judge.
- CI at this head, other than the block above: 32 check runs `success`, including `tests / fast (3.14)`, `pr-contract`, `arch-score`, `tests / closures` and `tests / coverage`. `prelude` failed on the "still adding sources after 8700 s" scheduling timeout, which the body already answers at `cd731ff0d`. It is a CI wait, not this diff.
