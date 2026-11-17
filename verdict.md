Fix review: merge 32b899c1234f180de7ccf8e7f2cd809bc271098f

bus-nonce: b8bf921c1f3e35b4be61b3f0f7fc3f7a
pending-ci: gate

Round 2 (delta review over the reviewed head 5356706e02cd174793004a041059c090eb15efba). Scope: the packet's `## Review scope` reads `delta`; the delta is one self-test row in `tools/audit/seat/orchestrator_tick.py`, nothing under `custom_components/`, so the review is not widened.

## Findings

- The `m.group(2) != head and` conjunct of the P657 arm still survives deletion (body table S2: 375 checks, 0 failed), unchanged from round 1: a merge verdict at the head is bucketed `verdicted` by the later arm anyway. Carry: dismissed: equivalent mutant, no behaviour differs

## Evidence

- Round-1 block resolved: deleting `m.group(1) == "merge" and` at `tools/audit/seat/orchestrator_tick.py:1008` now fails "P657 merge guard: a carried *blocked* verdict at an older head is not verdicted, still RED-UNOWNED" (375 checks, 1 failed); inverting it to `!= "merge"` fails that row and the existing P657 arm (375 checks, 2 failed); restored, 375 checks, 0 failed (ev/mutants.txt, ev/selftest-head.txt).
- The new row also asserts `cvb_asked == []`, so it pins that the carry predicate is not consulted for a non-merge verdict; the existing P657 arm with the same accepting predicate stays `verdicted`, so the pair separates on the verdict kind alone (null control as the body states it).
- Body figures re-derived at this head: orchestrator_tick 375 checks, 0 failed; verdict_audit 18 checks, 0 failed; `tests/structure.py` STRUCTURE RATCHET PASSED. The body's figures are stated at a56af234d8da872e6463859d32019398544580ff; this head is the merge of a56af234d8 into 5356706e02 and `git diff a56af234d8 <head>` is empty, so they hold at this head. The body's `## Head` names this head.
- The other body mutants (M8, M6, M9, M5, M5b) were re-run and killed in round 1; the production code they target is outside this delta and unchanged.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 (tree f5130d2b85, `LEDGER-MERGE: resolved tests/closures.json`), origin/main 54cb721164. Role-contract diff merge-base...origin/main is empty, so the contract is current (ev/ci-and-merge.txt).
- The three-dot diff touches no VERSION, manifest, RELEASE_NOTES, golden or claim file and nothing under `custom_components/`.
- Finder's harness: none named; the carries' self-test pins are the harnesses, as in round 1.
- CI at this head: `merge_train.py classify 32b899c1234f180de7ccf8e7f2cd809bc271098f --pr 3689` printed `WAIT ... pending: gate red: none` (rc 3) on every run from 23:51 to 00:21 UTC, about 30 minutes, so the verdict returns with `pending-ci: gate` (ev/classify.log). No check is red, so no `## Red checks` answer is owed.
- Head re-read before return: the branch tip is still 32b899c1234f180de7ccf8e7f2cd809bc271098f (ev/HEAD.txt).
- Closing self-audit: `carry_audit.py check` over the verdict and the PR body's Head, Repair, Red checks, Forward-carry and Friction sections (as read via the GitHub API at this head) prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry-audit.txt).
