Fix review: blocked afabd5b6a6e2da5bb42eaad5f6697837491c5556 carry-missing: not carried to R10-CEILING-PROBE (the idle-absorbs-compressor control and the set-point-to-draw gain identification are routed there by Carry: lines but absent from its brief on origin/main and on handoff/audit-r10-roster)

Round: 2 of R10-SETPOINT-BOOST (round 1 at 345cdf58 blocked carry-missing). Not yet the fourth, so a repair is owed, not a re-cut.
Head measured: afabd5b6a6e2da5bb42eaad5f6697837491c5556; the PR head was re-read just before return and is unchanged. origin/main at review: 2bd48adfa. Contract: dev/governance/roles/ on the checkout equals origin/main (empty diff).

## Blocking

- **carry-missing (step 10, finding-propagation.md "Enforcement": "the reviewer opens that, not the claim").** `carry_audit` now reads `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` against origin/main, and `pr-contract` is green on this head. That shows the markers resolve to live groups. It does not show the content landed. I opened each destination's `brief` in `dev/programme/rosters/wave-r10-groups.json` at origin/main; it is the same text on `origin/handoff/audit-r10-roster` (`ddd4d1c7c`):
  - R10-DEMAND-OVERBOOK, R10-BUFFER-STORE and R10-COP-PARTLOAD: each brief is written from this PR's finding ("Found by R10-SETPOINT-BOOST's ...") with its controls. Carried.
  - R10-CEILING-PROBE (ev/ceiling_probe_brief_origin_main.txt, 956 chars, `carry: []`): the brief covers the ceiling probe, the configured-5-kW vs believed-3-kW maximum, and ceiling-commanded evidence. The body's "Reaching the real maximum" item is therefore carried. **Two items routed there are not:**
    1. **The idle draw absorbs compressor draw.** The forward-carry says "The ceiling probe's controls should include a gate-held draw above idle", with the measured 24/72 drop and the low end moving 1.35 -> 1.8 kW. The brief's controls are the comfort/price gates, a synthetic pump with a known maximum, duty-cycling unchanged and a flat-price null. Neither "idle" nor "gate-held" appears. That is exactly the kind of control the rule says to carry: it narrows what the probe stage may trust.
    2. **The set-point-to-draw gain is unidentified at levels between the floor and the ceiling** (the "mapping reads the water temperature only at the floor" limitation). The body says identifying that gain is CEILING-PROBE's. The brief asks only for a ceiling-set-point probe, so nothing in the tree tells that seat to measure draw against set-point minus water temperature at intermediate levels.
  - Repair: a `roster_edit.py` (or equivalent) edit of R10-CEILING-PROBE's `brief`, or its `carry`, on `handoff/audit-r10-roster` (or main), stating both items with their controls as preconditions and read back by `brief_lint.mjs`. The body should then name that roster SHA. No production or test change is needed.

## Verified at this head (RESULT lines)

- RESULT merge-tree: `git merge-tree --write-tree origin/main(2bd48adfa) afabd5b6` exit 0, tree 76b57d69; `LEDGER-MERGE: resolved tests/closures.json` (inert_reads merged as a set). No MERGE-CLAIM lines: neither claim file is touched (ev/merge_tree.txt).
- RESULT mutation M0: `ALL 69 FEATURES BLOCK PASSED` (block "# -- live power clamp, 7a" .. "# --- #1956"). The mutants are my own string replacements of the body's named edits (ev/mutants.py), each on a `git archive` copy of the head, through tools/audit/seat/features_block.py:
  - M1 and M2 fail 2 checks each.
  - M3, M4, M5, M6, M7, M8, M9, M11, M12, M13 and M14 fail 1 each, and each failing check is the one the body's table names.
  - M10 fails 3: the fractional-inlet check, "a floor rounds up, a ceiling down ..." and "a Fahrenheit entity is quantised in Fahrenheit ...".
  - **M15**, which drops `lo=min(floor_c, heat_c)` in `_flow_target`, fails exactly 1: the fractional-inlet check, with `[30.0 31.0 31.0]`. The 25.3 arm goes red; the 25.9 arm and the whole-26 null stay 31 under the mutant, as a null should. The round-1 R16 survivor is killed (ev/mutants_summary.txt, ev/M*.txt).
- RESULT features: `ALL 4248 FEATURE CHECKS PASSED` in a git worktree at the head (ev/features_full_worktree.txt). In a `git archive` copy it reads 1 of 4248 failed. That one is "#363 resolvable recorded_at" = 'unknown', because the copy has no .git. It is environmental, not this diff's (ev/features_full.txt).
- RESULT structure: `STRUCTURE RATCHET PASSED`, seam_cut_total 719 <= 719 (ev/structure.txt). No `*_budgets.json`, claim file, VERSION, manifest or RELEASE_NOTES change in the three-dot diff.
- RESULT harness --no-solves (dev/audit/harnesses/r10_setpoint_boost.py, the head's copy run in both trees). Every body figure matches (ev/harness_nosolves.txt):
  - head: floor 155 cells / 0 at or below the gate; window plan `engaged False observed (0.8999999999999999, None) idle 0.3`; probe `engaged True observed (2.94.., 3.0)`.
  - merge base 4a3cbcf62: 63 at or below the gate; window plan `engaged True observed (0.9, 2.034)`; the probe is the same.
- RESULT harness with solves (ev/harness_solves_m0.txt, ev/harness_solves_mb.txt): every per-plan sha1 line is identical at head and merge base (the full outputs differ only in the 3 no-solve lines). Spread: lower 8 / higher 0 / identical 8; near-floor-dear 0.000 on 16/16; cheap-quarter 0.948-1.000. **Flat on this machine: lower 2 / higher 0 / identical 14 at both trees**, on cells (0.6, 750, False, True) and (0.6, 0, False, True), each with relaxed-delta -1.814. This is the round-1 reviewer's figure. The body states both the fixer's 0/16 and this 2/14 and attributes the difference to the solver environment, with base and head byte-identical on each machine. Confirmed. `failures 0` at both trees.
- RESULT carry_audit vs origin/main: 6 routed, 0 unrouted, 0 bad destinations (ev/carry_audit_origin_main.txt). pr-contract: 2 runs on this head, both success.
- RESULT CI on afabd5b6 (check-runs API, ev/check_runs.tsv) when this was written:
  - `mutation` is failure. The body answers it under `## Red checks` (sites unpinned until mutation-autofix runs; ci_predict names them locally). Answered.
  - `arch-score` (x2), pr-contract, typing, coverage, browser, env-matrix, instrument-self-tests and the rest: success.
  - `closures`, `fast (3.14)` and `mutation-pins (1-12)` were still in progress at the last read, so they are not cited as green.
  - The body states the round-1 `pr-contract` red as "stays red until the roster PR merges". That is stale: the roster PR #2467 has merged and pr-contract is green. Not blocking.

## Judged disclosures

- **`_SP_READ` fixture (27/29/32/36 from 22/24/26/31): sound.** Under fix A, any anchor at or below the 25 C gate floors at 30, so the old readings would no longer separate the rungs by their own lift. Moving them above the gate keeps the #2445 check's intent (the floor follows the anchor read). The check text moved with it (29 C -> 34), and the sub-gate case is pinned separately by "an 18 degC tank writes the gate plus the lift ...".
- **repairs.py disinfection write up to 0.22 K low on a degF entity: accepted.** It now goes through `write_setpoint` at nearest on step 1.0. The floors come from `_number(35, 55, 1)` / `_number(55, 70, 1)`, so they are whole degC. On every whole floor 40-79 C the round trip errs at most 2/9 K = 0.222 low, which is under `MIXING_VALVE_WRITE_EPSILON` 0.25, so `setpoint_check._dhw` does not re-raise. A non-integer floor could reach 5/18 = 0.278 K (above the epsilon), but the selectors make that unreachable from configuration.

## Notes, non-blocking

- Harness provenance (step 9): the finding is the owner's report, with no committed finder harness. `dev/audit/harnesses/r10_setpoint_boost.py` is the fixer's own and lands in this diff. I ran it, unmodified, at both trees and built no instrument of my own beyond the hand-mutant script in ev/. Carry: dismissed: provenance note on this review, no later stage changes
- The private export aggregates (54 samples, 41 at p_min, 25.0 written) were not re-derivable here: the export is the owner's and private. Not verified. Carry: dismissed: private data, not re-derivable by design

bus-nonce: 0f1f8919bff09df03e399b56241f22ab
