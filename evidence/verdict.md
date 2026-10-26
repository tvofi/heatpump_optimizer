Fix review: merge 07bc8000cd85b894ae65905eee065f0e15c21a68

bus-nonce: 8d7d40db6d55c1035c31425736153910

Reviewed the three-dot diff at merge base 3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f (10 files, +354/-53) from a detached worktree at the head.

Re-measured at the head (ev/selftests.txt, env -u BASH_ENV, seat venv): bus.sh --self-test 86 checks, 0 failed; ledger.py 58/0; cloud_dispatch.py 73/0; review_strength.py 116/0; orchestrator_tick.py 215/0; r10_ledger_mutants.py --self-test 88/0. These match the body's Figures.

Red check governance / instrument-self-tests (red at acc84bed4): the T3_review_owed_silent plant at the head anchors on the four-argument lg.review_owed call and is still caught: `r10_ledger_mutants.py T3_review_owed_silent` prints rc=1 fails=3 (two REVIEW OWED FAIL lines plus "verdict levels: a verdict not from the approver App is ignored"), "plants: 1, without a FAIL line: none". The body's root-cause answer holds: the cheaper detector it names exists, and tools/pr/prepr.sh contains no call to r10_ledger_mutants.py (grep), so no local path ran it; process state (a). The trigger is answered with the detector and its standing cost, which is what fix-review blocks on; see note 1.

Checked by reading:
- confirm's new replay refusal greps "$pr $tree" in posted-signed; post_verdict writes "$pr $sig" where sig=$(git rev-parse "$c^{tree}"), so the key formats agree and the refusal fires before append_commit moves verdict/<pr>.
- bus-model is taken only from a dispatched line matching pr, head and the verdict's nonce with NF>=6 and field 6 != "-"; no inference path exists.
- Registry lines stay readable by four-field readers (fields 5-6 appended).
- review_owed's carry filter fails safe: a missing predicate, a non-merge newest line, a failed fetch, or app_approve.sh --carry rc!=0 all leave the head owed.
- dispatch_group pre-renders with a probe nonce before the bus records, and reopens reviewer-fire on a publish refusal.

Non-blocking notes:
1. The Red checks section records "countermeasure not built ... for the orchestrator to route" with standing cost (~2 s) but no P(recurrence) or defect cost, so the cost test is not completed, and the line carries no destination. Wiring r10_ledger_mutants.py (and its siblings) into prepr when a planted target changes is the candidate. Carry: dismissed: the orchestrator routes the root-cause seat (defect-root-cause.md step 2), not this review.
2. blocked_rounds counts every blocked verdict on verdict/<pr> across heads, so a PR with three blocked rounds later merge-verdicted and re-dispatched after a branch-own commit also needs ## Re-cut or --past-three. That is consistent with fixer.md's round count. Carry: dismissed: matches the stated rule.
3. fixer.md edit is policy; merge still needs tvofi's approving review (body's Approval section says so).
