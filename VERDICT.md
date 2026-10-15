Fix review: blocked 25418620f9fb39304e82dceea3ce8d2114ad018f closures-red: the diff's new emitter check makes tests/entities.py read tools/coverage/coverage_tree.sh, an INERT file; closures job 116164533770 printed INERT READS UNDER-APPROXIMATED and closures-autofix 116172854754 refused (skip-merge-failed)
bus-nonce: d64afca2d7fe235ac47547e8d4a395aa
reviewer: r10-ratchet-reviewer
round: 2 (same head; round 1 was body-stale)

Head 25418620f9fb39304e82dceea3ce8d2114ad018f re-read at post time: unchanged.

Round-1 body-stale: resolved. Title is now "fix(ci-ratchet): count metrics rows only in their own lane file; stop leaking HPO_CI_METRICS to children". I re-read the whole body against the head. It lists 6 files including dev/programme/delivery/2216.md and names the M6 gap. The new claims check out: `git diff --quiet cc326217b HEAD -- <the five fix files>` exits 0, and main's job 116157526420 at c698d504a printed "window: 35", "ok script_runs_per_push: 67 (budget 68)" and "every metric at or under its budget". The body was rewritten before `closures` concluded, so it does not mention that red.

NEW BLOCK, caused by this diff. tests/entities.py's new check "every HPO_CI_METRICS emitter keeps the file from the children it runs" calls Path(p).read_text() on every `git grep -l HPO_CI_METRICS -- '*.sh'` hit. That includes tools/coverage/coverage_tree.sh, and closure.is_inert('tools/coverage/coverage_tree.sh') is True at head. CI's strace recording sees the read:
  closures job 116164533770 (run 38653583589): "INERT READS UNDER-APPROXIMATED ... tests/entities.py: tools/coverage/coverage_tree.sh", exit 1.
  closures-autofix job 116172854754: "files on the INERT list are actually read by tests: tools/coverage/coverage_tree.sh ... remove them from INERT in tests/closure.py, or except them", "AUTOFIX: skip-merge-failed -- THE REPAIR DID NOT HAPPEN".
The fix needs a deliberate classification. Either take coverage_tree.sh off INERT, or add an exception or inert_reads entry for entities.py, with closures.json re-derived. The other option is to read the emitters without a recorded open (unlikely: the check exists to read them). This changes code, so the head moves and gets a fresh review. The fixer's body must also name and answer the closures red (defect-root-cause.md trigger 2). The cheaper detector question is fair: a local `closure.py check` on the recording of entities.py would have shown it.

Carried from round 1 (code unchanged at this head, all still valid):
RESULT grade base c698d504a on run 38639862216's artifacts: GREW script_runs_per_push 69 (budget 68), rc=1. Head: ok 54, 17 rows not counted, rc=0.
RESULT rebuilt 38-artifact window: base per_push 69 and full_case_pr 67; head 54 and 54. Zero real rows dropped: every dropped row is a fixture or a nested `fast mode` line. Full-case classification is the same at base and head for all 13 PR runs.
RESULT mutants (my harness, the three checks copied verbatim): M1, M2, M3, M4, M5, M7 and M8 killed; M6 (unset left only in a comment) survived. The body now names M6.
RESULT entities.py at head (local): rc=0, ALL 2316 ENTITY CHECKS PASSED.
RESULT budgets and VERSION untouched; not a raise.
RESULT check-runs at head (API, 00:09Z): fast (3.14) success; coverage and coverage-ratchet success; pr-contract success (re-run 00:03Z after the re-body); closures FAILURE; closures-autofix FAILURE; nightly-status failure (main's, answered); composed-proof still in progress.
RESULT code-owned paths: tests/run.sh and tests/derive_closures.sh. tvofi's review is still required.
