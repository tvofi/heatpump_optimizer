Question: R10-START-COUNTER-EDGES is already delivered; should this dispatch be retired, or is there a further item the payload did not name?

Pull request 3598 merged into main at cb19070965 (main 31117b1029, the head this seat was given), and its head
d9e3d1550f already carries the refresh-held start that owner ruling D1 (carry 2) asked for
(eddba039c3 failing S7 check first, then fbe6b63a3a..d9e3d1550f). The reviewer's six-offset harness,
`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/start_counter_edges.py`, at
origin/main 31117b1029 prints s7_60s=0, s7_30s=0, s7r_60s=0, s7r_30s=0 (0 false starts at every offset; the
verdict measured 5 of 6 at ca0e06eb3d46) and control=3, perturbed=4, restored=8, s7r_real=6.

Carry 3 (pull request 3602's running_now read) assumed 3602 merges first. It has not merged; this group merged
first, so the one-line change to running_signal.running_now(running_signal.signal_for(coord)) with the
executing-step fallback falls on 3602's own rebase, not on this group.

No code was written, nothing was pushed to handoff/ or handoff-body/, and no pull request was opened.
