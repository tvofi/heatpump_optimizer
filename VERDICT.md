Fix review: merge 7a5ca1e400da56da7cac5e64a7a675f9bbbd1115

bus-nonce: 16f4665db8175b85612d7e4e7b085f7d

Reviewer seat review-2025-r6, round 8 of PR #2025 (R9-EG-B11, #1745). This is a delta review of 9c664109..7a5ca1e4, run from the detached worktree /Users/timmalmstrom/hpo-seats/review-2025-r6/wt at the head. The live head was re-read at posting and is unchanged. Round 7's single block, the out-of-tree probe, is fixed.

## Delta

**2a7b4d0c lands the probe at `dev/audit/harnesses/eg_b11_equiv_6840.py`.**
- Ignoring machine paths, its body equals the round-7 scratch probe (sha1 3e661d15). It gains a header that states the metric, the control and the expected figures.
- The triage row's `reason` changes only in its citation: the machine path and sha1 are replaced by the tree path and its run command.
- The probe, the row and the body contain no `/Users/`, `/home/` or `/tmp/` path.

**387128bb is a one-line change** (`tests/closures.json`, +1 line). It adds `dev/audit/harnesses/eg_b11_equiv_6840.py` to `inert_reads["tests/harness_headers.py"]`, between `dual_path.py` and `eg_b7_seam_hubs.py`. The list is sorted at 387128bb (533 entries) and at the head (534 entries).

**Merges reproduce.** For 16016d5d and 7a5ca1e4 (main 0b89f781), `git merge-tree --write-tree` gives each merge's tree exactly, and the remerge-diff is 0 lines. On 7a5ca1e4 the stderr reads `LEDGER-MERGE: resolved tests/closures.json`, which is the driver.

**I re-ran the probe from the tree at the head:** `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/eg_b11_equiv_6840.py <out>`, venv-ci 3.14.7.
- `RESULT mutant: cases=552 differing=0 (flag on 0, flag off 0)`
- `RESULT control: cases=552 differing=264 (flag on 264, flag off 0)`
- `boundary cases (flag on, every step's snow 0)=276, of them with rain on some step=264`

These reproduce the row's and the body's figures, and the control moves. My independent round-7 bitwise probe (1,998,978 finite values, 0 differing) still stands, because neither `_liquid_fraction` nor `_weather_series` changed in this delta.

**Body:**
- It names 7a5ca1e4 and has no machine paths.
- It records the round-7 finding at pump_arbiter.py:572: the RETURN_DEL kill is `structure.py`'s `dead_top_level_symbols`, not behaviour. It records it as an instrument note for the pin chain.

## CI at 7a5ca1e4, settled

- **`mutation` success** (job 113364861297): `MUTATION TABLE PASSED`, 4624 unpinned against 4642 at base 0b89f781, 0 survivors of 10 evaluated, and the ledger agrees with the inventory.
- **Also success:** fast (3.14), closures, typing, env-matrix, browser, policy-docs, pr-contract (both runs), instrument-self-tests, briefs, wave-script, hassfest, validate-hacs, CodeQL and both budget-raise-gate twins.
  - coverage and coverage-ratchet are also success, though the dispatch did not require them.
- **`delivery-status`** (UNCHECKED, 78 rowed, 0 overdue) is main's window.
- **`nightly-status`** reports main's scheduled run 37753990323 at 816547e. Its failures are closures, mutation-nightly and nightly-ha. That is main's nightly, not this diff (`defect-root-cause.md`).
  - The body names the earlier nightly run, not this one. No answer is owed for a status lane this diff does not reach.

Code before 95b08306 was not re-reviewed, per the dispatch. Rounds 6 and 7 hold as recorded.

Evidence: /Users/timmalmstrom/hpo-seats/review-2025-r6/ev8. It holds:
- HEAD.txt
- mt_*.err and remerge_*.diff
- probe_tree.py, probe_run.txt and probe_out/
- cr_head.tsv and job_*.txt
- pr-body.md and pr-body-final.md
