Fix review: blocked b2399a08527bf850507753b43a96d3ad56fef655 class-open: dev/audit/rounds/round10/D15/s1/intake.py

bus-nonce: ebb012b8a5b5d92241bf5aa68eb59225

Round 1 of the fix review of #3186 (R10-LIVE-BUNDLE-READS), measured at head b2399a08527bf850507753b43a96d3ad56fef655, merge base a9c2f90fc77be2e7a870f3f2735dcd0f79b5f475. The roles diff from the merge base to origin/main is empty, so the contract is current.

## Block

The body states its class rule, `git grep -n "load_bundle" tools tests dev`, and dispositions what it says that rule returns: "its other callers are `debug_replay.py` (gains the unwrap) and `dbg_bundle_gen.py` (bare bundles, unchanged)". At this head the rule returns something else (ev/class_rule.txt):
- `dev/audit/rounds/round10/D15/s1/intake.py:223` calls `di.load_bundle`. It is a seam the rule returns. It is not in the diff and the body does not disposition it. It is also the finder's own committed harness for D15-s1-01 and D15-s1-03, and the body names no finder's harness. The review packet reads "Finder's harness: none named".
- `dbg_bundle_gen.py` does not call `load_bundle`, so the body's caller list does not match its own rule.

The behaviour change at that seam is measured, not inferred. I ran the finder's harness at both ends on the same synthetic download, `debug_ingest._download(_tail_repeat_bundle())` (ev/finder_harness_intake.txt):
- base: bundle_unwrapped=1, ingest_fails_wrapped=6, ingest_fails_unwrapped=1 (bias-rederived)
- head: bundle_unwrapped=0, ingest_fails_wrapped=0, ingest_fails_unwrapped=0

The fall from 6 to 0 is the fix showing in the finder's harness, which is good. But intake.py unwraps by itself after calling `load_bundle`, and at the head `load_bundle` has already unwrapped. Two things follow:
- Its M1 metric `bundle_unwrapped` now reads 0 on every real download.
- Its `--perturb unwrap` arm, documented in its header as the M3 wrapper perturbation, now does nothing: download and dbg are the same object.

Its header is EXPECTED against a live bundle, so harness_headers does not execute it and CI stays green over the drift.

Repair, either one:
- update intake.py so the wrapper metric and the unwrap perturbation still measure something (for example, read the raw file for the wrapped arm);
- or disposition the seam in the body with the reason, and correct the caller list.

Then re-state the class rule's output.

## Findings

- Pre-existing at the base as well as at the head: the finder's harness `dev/audit/rounds/round10/D15/s1/intake.py` crashes in M4 with `AttributeError: module 'heatpump_optimizer.store' has no attribute '_store_name'` (the tree now has `store_name`), so its store metrics never print (ev/finder_harness_intake.txt, both ends). The fixer is touching this file anyway to settle the block, so it is owed there. Carry: R10-LIVE-BUNDLE-READS
- Surviving mutant M5: `if isinstance(doc, dict) and "schema" not in doc:` changed to `if isinstance(doc, dict):` fails no gate check (ev/mutants.txt). The mutant is equivalent on the real domain. Every bare bundle carries `schema` (debugger.py:615, BUNDLE_SCHEMA), and no bare bundle has a top-level `data` key (debugger.py:614-639). So the guard only protects inputs the tree never makes. Carry: dismissed: equivalent mutant on the bundle's reachable domain

## Evidence

- RESULT gate_checks_head=7/7 ok (ev/mutants.txt preamble, re-run directly through debug_ingest.gate_checks()); this matches the body's "7 of 7".
- Failing first, re-derived (ev/base_failing_first.txt). With the base's `load_bundle` and `ingest` on the new fixtures:
  - the wrapped download fails 6 stages: bias-rederived, manifest-cycles, manifest-version, rows-match, schema, stores-present. This matches the body.
  - the tail-repeat bundle fails bias-rederived. This matches.
  - the tamper and disjoint negative arms fail bias-rederived at the base as well, so they are controls and not failing-first arms. The body's "three new arms" is consistent with this.
- Mutants (ev/mutants.txt), each restored afterwards, with `git status` clean:
  - M1, unwrap removed: the wrapped arm goes red. Matches the body.
  - M2, no de-duplication: the clean, wrapped and tail-repeat arms go red. Matches the body.
  - M3, `shared = sorted(held)`: KeyError crash. Matches the body.
  - M4, last-wins in place of setdefault: the tamper arm goes red.
  - M6, store bias over the whole window in place of the shared samples: the tail-repeat arm goes red.
  - M7, sample t replaced by row t: the tail-repeat arm goes red.
  - M5 survives (see Findings).
- New instrument `dev/audit/harnesses/d15_bundle_reads.py`, run without a bundle (ev/d15_harness.txt): the five EXPECTED lines reproduce exactly. `--mutant last_changed` turns age_polling_reporting_flagged to True, as the header says. This is the fixer's own instrument, disclosed as new in the body.
- tests/harness_headers.py, run locally: ALL 112 HARNESS HEADER CHECKS PASSED (ev/harness_headers.txt). This matches the body.
- `git merge-tree --write-tree origin/main b2399a08527bf850507753b43a96d3ad56fef655`: rc=0, tree dc124c20a7d9bfe484d290b8243c9439d36426e3, no conflict (ev/merge_tree.txt).
- VERSION, the manifest version, RELEASE_NOTES and both claim files are untouched. The diff is 4 files: the harness, the delivery row, closures.json and debug_ingest.py. No production file under custom_components changed, so no fixture can drift.
- Forward-carry: the body's three items for R10-ROUND-PLAYBOOK are on handoff/audit-r10-roster at 4d89ce26ccfd20bbfc8fc0b675245370ead6deb3, as the last carry of that group (ev/roster_carry_3186.txt).
- CI, read as the whole check-run set: one page, total_count 38. tests / fast (3.14) is success. Its log shows `tests/entities.py` ran (538 s) with `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN` (ev/ci_fast_summary.txt), so the entities.py run the fixer could not do locally is green in CI. The only red is tests / nightly-status. The diff reaches nothing it reads, so it is main's, not this PR's. merge_train classify exited 0 at 09:34:08Z: `GREEN b2399a08527bf850507753b43a96d3ad56fef655 pending: none red: none` (ev/classify.txt). Before this verdict, refs/pull/3186/head still read b2399a08527bf850507753b43a96d3ad56fef655. The block does not depend on CI.
- Not re-derived: every bundle-derived figure in the body's Figures section, including the live-bundle stage count, the sample and row counts, the bias deltas, the snapshot counts, the L-a and L-b readings, the scale walk and the restart-gap spacing. No bundle is in the tree or available to this seat, and the bundle is owner data, so this verdict quotes none of it. Those figures are the fixer's and remain unverified.
- Head: the PR head is b2399a08527bf850507753b43a96d3ad56fef655 at review. The body names it and its authored code head, 0623400819922e51443917996f49de671f138d34.
