Reviewer's own instrument (fix-review.md step 9: disclosed as the reviewer's, not the finder's).
reviewer_differential_inject.py is spliced into a throwaway copy of
tools/audit/seat/queue_pre_flight.py (tools/audit/seat/_rev3401_pf.py, deleted after the run)
immediately before the line "# The train judges a mandated raise's body against the gate's measured score",
reusing the self-test's fake world. For each world it prints the pre-flight's answer
(PreFlight.entry under the train's --mandate) beside the REAL path's (Train.policy_approve
posting into the fake, then Train.policy_gate re-reading, exactly as Train.land does),
and flags a SLIP where the pre-flight PASSes and the real path parks.
Run: python3 tools/audit/seat/_rev3401_pf.py --self-test  (at head f0b7564596d2725f87090f921e0d3ceb51ceec8b)
reviewer_differential.txt: 23 worlds, 0 slips (54 checks, 0 failed).
reviewer_differential_a17.txt: the same plus A17 (train's gh account not the owner): 1 slip.
Fixture limit: the fake answers every /issues/comments/<id> read with the one mandate comment,
so A4 (a stale approval citing another mandate id) is not meaningful and is not relied on.
