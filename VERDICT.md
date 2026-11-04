Fix review: merge ece7a86a2668f158b8f7e4fe2e7c6c090c3800d6

bus-nonce: db9f5e8b8e39dc13ca23d61a61463735

Round 2 of the fix review of #3186 (R10-LIVE-BUNDLE-READS). This is a delta review at head ece7a86a2668f158b8f7e4fe2e7c6c090c3800d6, against the head I blocked before, b2399a08527bf850507753b43a96d3ad56fef655 (verdict/3186: class-open on `dev/audit/rounds/round10/D15/s1/intake.py`). The authored code head is df48d4e7a3d0698bce3002023767bc3d6bc6b1fe. The head then merges origin/main 616868bdc5ca54d9555cfc89715f05a33527661e, which is now the merge base. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I used is current. I worked from detached worktrees at a9c2f90fc77b (the round-1 base), at 616868bdc5ca (the current merge base) and at the head. The finder's harness is `intake.py`, and every figure came from the synthetic download `debug_ingest._download(debug_ingest._tail_repeat_bundle())`, with the bare `_tail_repeat_bundle()` as the null control. I read no real bundle. Counts only.

## Findings

- Surviving mutant, carried from round 1 and re-confirmed at this head: dropping the `"schema" not in doc` guard in `unwrap_download` leaves gate_checks() at 8/8 and moves no intake.py figure (ev/mutants.txt R4). The body dismisses it as equivalent on the bundle's reachable domain, and I agree: every bare bundle carries `schema` and none has a top-level `data`. Carry: dismissed: equivalent mutant on the bundle's reachable domain

## Evidence

- The block is settled: the class is closed. I re-ran the body's rule `git grep -n "load_bundle" tools tests dev` at the head (ev/class_rule.txt), and it returns 18 lines.
  - All 18 fall within the body's disposition list: debug_ingest.py (lines 56, 249 and 295), debug_replay.py:198, intake.py (header lines 10 and 18, code lines 224, 225, 230 and 231), JUDGE-INPUT.json (2 lines), normalised-reports.json (2), reports-B11.json (2) and wave-r10-groups.json (1).
  - No seat is undispositioned. The round-1 caller list named `dbg_bundle_gen.py` in error; the body corrects it.
- The second rule, `git grep -n "bundle_unwrapped\|perturb unwrap\|D15/s1/intake"`, returns these files: intake.py, REPORT.md, JUDGE-INPUT.json, normalised-reports.json, reports-B11.json, tests/closures.json and `dev/audit/rounds/round10/judge-batch-1.json` (5 `"harness":` lines).
  - The body does not name judge-batch-1.json. It is a judge record naming the harness path, not a reader, so it falls under the body's "a record, not a reader" disposition. The omission is wording only, and I am not blocking on it.
- RESULT finder_harness, the repaired intake.py from the head, run from each tree's root (ev/finder_harness_intake.txt):
  - base a9c2f90fc77b, S: bundle_unwrapped=1, ingest_fails_wrapped=6, ingest_fails_unwrapped=1, bias_delta_tail=0.25, bias_delta_by_t=0.0, store_docs=1, store_off_domain_fields=0. No traceback.
  - base a9c2f90fc77b, S, `--perturb unwrap`: ingest_fails_wrapped=1. This is the finder's documented 6 -> 1.
  - merge base 616868bdc5ca: the same figures as a9c2f90fc77b in all four runs.
  - head, S: bundle_unwrapped=1, ingest_fails_wrapped=0, ingest_fails_unwrapped=0, bias_delta_tail=0.0, bias_delta_by_t=0.0. The store metrics print.
  - head, S, `--perturb unwrap`: ingest_fails_wrapped=6, so it moves 0 -> 6.
  - Null control, the bare bundle, at all three trees and with and without `--perturb unwrap`: bundle_unwrapped=0, and the wrapped arm equals the unwrapped arm (1 at both bases, 0 at the head). The perturbation moves only when a wrapper exists.
  - Every figure in the body's Figures section re-derives exactly, and so does the M4 store-metric repair (`store_name`).
- The wrapped arm measures the tool again. I mutated the head's debug_ingest.py and re-ran both gate_checks() and intake.py on S (ev/mutants.txt; each mutant restored, `git status` clean):
  - R1, the body's own mutant (`read_download` unwraps): gate 7/8, failing "read_download keeps the wrapper the harnesses measure", and intake.py's bundle_unwrapped drops to 0. The new pin bites, as the body says.
  - R2, `load_bundle` without unwrap: gate 7/8, failing the wrapped-download arm. intake.py's ingest_fails_wrapped goes 0 -> 6, and its unwrap perturbation flips it to 0. The harness now sees a regression of the fix, which the committed harness at b2399a08 could not.
  - R3, `unwrap_download` reduced to the identity: the same as R2.
  - R5, the intersection replaced by the union: KeyError crash, so the gate goes red.
  - R6, last-wins dedupe: gate 7/8, failing the tamper arm.
  - R4 survives; see Findings.
- RESULT gate_checks_head=8/8 ok, matching the body.
- Round-1 mutants M1-M3 and failing-first stay as verdict/3186 recorded them. The code delta from b2399a08 to df48d4e7 touches only `read_download`/`load_bundle` in debug_ingest.py and the intake.py repair (`git diff --stat`: 2 files, +29/-16).
- Merge with main: I ran `git merge-tree --write-tree origin/main ece7a86a2668f158b8f7e4fe2e7c6c090c3800d6` against origin/main 8e90d81443317f76f22602a89651f7ca17c633f9. It exited rc=0 with tree 832c3772359e5ab7e97f84f57d147e45b7af52fc. tests/closures.json was resolved by its ledger driver (`LEDGER-MERGE: resolved`, no refusal), and no other path conflicted (ev/merge_tree.txt).
- VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched: the three-dot diff over them is empty. No file under custom_components changed, so no golden can drift.
- Forward-carry: the R10-ROUND-PLAYBOOK item from R10-LIVE-BUNDLE-READS is present in dev/programme/rosters/wave-r10-groups.json at 4d89ce26ccfd20bbfc8fc0b675245370ead6deb3 (line 7591), and that commit is an ancestor of origin/handoff/audit-r10-roster. Its text holds bundle-derived figures, so this verdict does not quote them.
- CI, read as the whole check-run set: total_count 40 on one page. tests / fast (3.14) succeeded. Its log shows `tests/entities.py` ran (448 s) and `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN` (ev/ci_fast_summary.txt).
  - The only failure is tests / nightly-status. The body answers it: main's nightly, and the diff reaches nothing it reads.
  - tests / mutation is green. This diff writes production lines only under tools/replay, and my targeted mutants above stand in for it.
- Not re-derived: the round-1 live-bundle figures the body cites by reference (handoff-body ref 9ab3e10c). No real bundle is available to this seat, and none may be read here. They are the fixer's, unverified by me, and this round does not restate them.
- New instrument `dev/audit/harnesses/d15_bundle_reads.py` is the fixer's own, unchanged since round 1. It was verified then, and CI's harness_headers passed (112 checks).
- merge_train classify exited 0 at 2026-11-04T11:41:43Z: `GREEN ece7a86a2668f158b8f7e4fe2e7c6c090c3800d6 pending: none red: none` (ev/classify.txt).
- Head re-read before return: refs/pull/3186/head still reads ece7a86a2668f158b8f7e4fe2e7c6c090c3800d6.
- carry_audit.py check returned rc=0 with 1 routed, 0 unrouted. I ran it with the body's Forward-carry and Friction sections as the body file and this verdict as the comment.
