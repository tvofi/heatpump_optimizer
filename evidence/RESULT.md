head: 827c15c8b1c4b097cfda639230b5bc09f5f83f43
round: 1 (no prior verdict on verdict/3719 or probe/rev-3719-*): full review
merge-base: 83b9012d61eb9dba11c265cf987dd1d5960c8c96; roles/ diff merge-base...origin/main empty (contract current)
diff (three-dot): tools/audit/seat/body_push.sh (+32 -2), dev/programme/delivery/3719.md (+1)

RESULT: self-test at head: 57 checks, 0 failed (selftest_head.txt)
RESULT: self-test at merge base: 49 checks, 0 failed (selftest_base.txt); the body's 49 -> 57 re-derived
RESULT: test-first: head tests over base keep_refused: 5 failed, the five the body names (selftest_testfirst.txt)
RESULT: mutation, predicate 'if false': 5 failed, same five (mut_false.txt)
RESULT: mutation, NOTE half of the predicate dropped: 1 failed (RESUME-note arm) (mut_nonote.txt)
RESULT: mutation, 'return 0' after the refusal message removed: 4 failed (mut_noreturn.txt)
RESULT: null control (the same body under another non-public host is kept): ok at head; it passes under every mutant
RESULT: judge failure (missing file): ref_privacy body-lines exits 1, so keep_refused keeps nothing (fails closed)
RESULT: tool attribution: body-lines refuses a co-author trailer, rc 1, so the class covers more than host identity
RESULT: class rule from the body: no writer of a refused body outside body_push.sh; keep_refused is the only one, closed in the diff
RESULT: VERSION, manifest and RELEASE_NOTES untouched; no claim file, budget, closures.json or INERT moved
RESULT: merge-tree origin/main vs head: exit 0, clean
RESULT: checks at head: one failure, tests / nightly-status. It grades main (merge_train NOT_GATING) and is exempt by defect-root-cause.md because the diff touches no REPORTER_INPUTS path; every other check succeeded or was skipped
RESULT: no custom_components/ change, no actuator path (step 16 n/a), no figure moved by an instrument (step 14 n/a)
RESULT: the finder's harness is the committed self-test arm (PC-1113-17); no out-of-tree instrument was used
UNCERTAINTIES: no review-packet in the dispatch, so carry_audit.py check was not run; the body's "## Head" names 827c15c8b1c4b097cfda639230b5bc09f5f83f43
Note: message-wording: when only the RESUME note fails body-lines, the stderr line still says "the refused body fails". Nothing is kept either way, so only the wording is off
