Fix review: blocked 21b920ba64892ade1446b8c7e804461cfb12b41b mutation-vacuous: tools/ci/sweep.py:400 (judge's `or run["id"] in self.deferred_ids` guard), tools/ci/sweep.py:463 (completion's `v["status"] != "completed"` clause)
bus-nonce: 11ef1d499411e7039e8468fa0020807c

Round 1, full scope (the packet names no reviewed head). Measured at 21b920ba64892ade1446b8c7e804461cfb12b41b, which is the head the body names.

RESULT self-tests at head: sweep 145/0 failed, prelude 162/0, gate 133/0 (evidence/selftests.txt).
RESULT reviewer mutants, 9 run (evidence/mutants.txt): undefer ignoring busy, attempt cap, stale pin; busy_sources ignoring judging, and failing open: each killed by 1-3 rows.
RESULT survivors:
- tools/ci/sweep.py:400: dropping `or run["id"] in self.deferred_ids` from `Sweep.judge` leaves all 145 rows passing. The module doc states that "a deferred run's gate is never re-run alone", and no row pins it. I checked that the case is reachable with evidence/probe_deferred_gate.py, which uses the self-test's own World and run helpers. The world is a deferred run 1, a busy run 5 and a green V 9. At the head the sweep posts nothing. With the guard removed it posts `jobs/10/rerun`, so it re-runs run 1's gate alone while its sources are busy. Carry: #3885
- tools/ci/sweep.py:463: dropping `v["status"] != "completed"` from `Sweep.completion` leaves all 145 rows passing. I did not probe whether the case is reachable: a sweep-self of a V still in progress would return True and skip `settle`. Add a row that pins it, or record it as equivalent with the reason. Carry: #3885
- Two equivalent mutants, not blocking. The `rerun_ids` skip in `undefer` is equivalent because undefer runs first and rerun_ids is empty at that point. The prelude-conclusion clause in `deferred` is equivalent because a failed step fails its job. Carry: dismissed: equivalent mutants
RESULT finder's harness: dev/audit/harnesses/ci3885_queue.py `fetch 2026-11-26` stopped on an HTTP 502 from GitHub, so there is no base reading. The head reading is an after-merge census by construction. Carry: dismissed: evidence, not a finding
RESULT merge-tree origin/main HEAD: rc 0. VERSION, the manifest version and the notes heading are not touched.
Note: root-cause-unanswered: there are two `gate` runs at this head. In the edit run 45955022697, the gate is red because it deferred to code run 45955023499. That run's gate went green at 08:41Z, and a gate-sweep (45967617920) was still queued when I read it at 08:44Z. Required `gate` should clear once that sweep runs. `tests / nightly-status` is red and not required. Carry: dismissed: evidence, not a finding
