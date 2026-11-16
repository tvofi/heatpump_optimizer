Fix review: merge af7d2813775aa51f817135b7df4edc55fcfa2046

bus-nonce: 301775d67d2ae498b558829cf07f0680

Round 1 (first round, full scope). Base b94425b94f0d25a02576e98fa10a8ff324974a0c; role contracts current (`git diff <mb>...origin/main -- dev/governance/roles/` empty).

## Evidence

- Mutation proof (step 1): reverting the fix line `orchestrator_tick.py:1730` to the bare `SEAT_WINDOW_MIN` makes `python3 tools/audit/seat/orchestrator_tick.py --self-test` exit 1 with `NameError: name 'SEAT_WINDOW_MIN' is not defined` via `plan` (ev/selftest-mutant-bare-name.txt, ev/mutant-bare-name.diff). Killed.
- Value mutant (step 14): pointing the window at `owatch.FIRE_GRACE_MIN` fails exactly `OUTSIDE-CHAIN-IDLE: null control: a path ending in a seat ref inside the window prints nothing`, 368 checks, 1 failed (ev/selftest-mutant-fire-grace.txt). The body's claim that the null-control row pins the value is confirmed.
- Both ends (steps 2-3): base file self-test rc 1 with the same NameError (ev/selftest-base.txt); head `orchestrator_tick self-test: 368 checks, 0 failed`, rc 0 (ev/selftest-head.txt). The finder's harness here is the self-test itself; no separate harness is named, and the defect is a crash, so the self-test is sufficient.
- Class (step 6): an undefined-global enumeration (my own symtable script, ev/undefined-globals-*.txt; the body's `ruff --select F821` was not available here) lists `SEAT_WINDOW_MIN` as the base file's only undefined module name and none at the head. Across `tools/audit/seat/*.py` at the head, the only other flagged file is `gh_calls.py`, whose names are function locals (a symtable false positive, not this class). This is a one-seam class.
- Driver: `mutant_run.py --diff <mb>...HEAD --list` prints one mutant, `orchestrator_tick.py:1730 STMT_DEL pass` (ev/mutant_run-list.txt), which matches the body. The run itself exited rc 0 and printed no KILLED/SURVIVED line here (ev/mutant_run.txt). I therefore did not re-derive the body's "killed, 0 survived" from the driver, only from my own mutant above.
- Step 4: no golden or claim files are in the diff. Step 5: VERSION, the manifest and RELEASE_NOTES.md are untouched (ev/version-untouched.txt).
- Step 7: the body's head is af7d2813775aa51f817135b7df4edc55fcfa2046, the head measured. Step 13: `git merge-tree --write-tree origin/main <head>` rc 0, tree 572c8b1a46 (ev/merge-tree.txt).
- Figures: the self-test figures were re-derived. The `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` scope line and the prepr rc 0 were not re-run (cite CI). The live-tick BOARD line comes from the orchestrator's state dir and cannot be re-derived from this seat.
- Carry: the body's forward-carry to R11-CLOSEOUT-CLEANUP passes carry_audit at the head (packet: 1 routed, 0 unrouted).
- CI: see ev/classify.log; the last classify line is quoted below.
- CI (step 11): `merge_train.py classify af7d2813775aa51f817135b7df4edc55fcfa2046 --pr 3661` final line `GREEN af7d2813775aa51f817135b7df4edc55fcfa2046 pending: none red: none` (ev/classify.log). The re-rendered packet has no refusals and shows `governance / instrument-self-tests` success at the head, so no introduced red (ev/review-packet-final.md). The only red is `tests / nightly-status`, which is not in the `owed-reds` set, so it owes no answer and blocks nothing.
- Step 12: the head was re-read before return (ev/head-recheck.txt).
