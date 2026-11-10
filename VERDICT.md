Fix review: merge a7f37e665413650685c3930ccaf635b7c83eeb9c

bus-nonce: a4cb6498fbb10cbacb4eb8ec814838b5

## Verdict
Round 1 of this review. Head measured: a7f37e665413650685c3930ccaf635b7c83eeb9c (ev/HEAD.txt). A root-cause document against root-cause.md and defect-root-cause.md: reproduced cause, one state, reach search, cost test with numbers, built countermeasure shown to detect.

- Reproduction: `replay` re-run: index `drop-carry G 1` applied twice removes 2 entries; `--match` form removes 1 and the replay refuses (control). Re-derived.
- Census `43495fb61..c444a6995` re-run: `RESULT drops=32 replays=18 replays_restored=14 replays_unrestored=4 firsts=14 firsts_restored=0`, matching the body and the bugclasses subject; the control (0 of 14 first drops restored) holds.
- State: exactly one, (d), with the process quoted (9969e3ca8 index form for a run-once caller; first automatic re-runner 0a98a0173 / #3197). The doc argues why not (c) and (b). Cited commits resolve with consistent dates.
- Reach search: table of other apply-then-record runners, each dispositioned.
- Cost test: numbers given (600 s lower bound, 3 episodes in 10 days, 8/14 replayed, 0.071 us/line re-measured, 120 s requeue; break-even 0.2 vs 0.57).
- Countermeasure demonstrated: `replay_unsafe` refuses index drop-carry/mark-carry and passes `--match` forms (GATE lines); `roster_queue.py --self-test` 65 checks, 0 failed; `mutants`: 4 of 4 killed, baseline clean.
- No VERSION, manifest, golden or notes changes in the diff; commit messages carry no trailer.
- Merge with origin/main: `git merge-tree --write-tree` rc=0, no conflict.
- Forward-carry: carry_audit 2 routed, 0 unrouted, 0 bad destination.

## Evidence
- RESULT mutants=4 killed=4; RESULT replay_unsafe_us_per_line=0.071; RESULT ref=c444a6995 entries=1690 contained_in_a_sibling=23.
- CI: `merge_train.py classify a7f37e665413650685c3930ccaf635b7c83eeb9c --pr 3415` exit 0: GREEN, pending none, red none. owed-reds output in ev/owed-reds.txt.
- Not re-derived: the kill reason and local queue/roster-done.json (host-local); the doc discloses this in its section 7.
- The mutation lane's GREEN on a change that is one production file plus self-test was not re-run (CI cited).

## Findings
- Follow-up: the bugclasses `process_state` string names (d) and also "(c)" for the replay half, though the doc commits to exactly (d); a reader keying on the field could read two states. Wording only, no change to the countermeasure. Carry: dismissed: the document body states (d) as the one state and assigns the (c) half to the hotfix R10-HOTFIX-ROSTER-DRAIN-REPLAY.
- Follow-up: a queue line written by index before this merge is now marked `#refused` and the beat records it as done, so an intended index op is dropped without retry (visible in the digest, requeue with `--match` owed by the writer). Documented in the doc's section 6; the 23 entries `--match` cannot name still go by hand. Carry: dismissed: accepted trade in the cost test (at most one 120 s requeue per index line), disclosed in the document.
