Fix review: blocked 51f5ce37e1ebdb5643566b0c9a062b7678ada6d2 root-cause-unanswered: governance / instrument-self-tests, pr-contract / pr-contract

bus-nonce: 7e1d7cd90ea324bb094d97525e622b5d

## Block

At head 51f5ce37e1ebdb5643566b0c9a062b7678ada6d2 the final `merge_train.py classify` exits 1 (RED, `red: gate`), and the review packet refuses on two concluded-red checks the PR body's `## Red checks` does not name: `governance / instrument-self-tests` (job 128902593488) and `pr-contract / pr-contract` (job 128914068083). The body names only `tests / fast (3.14)` at 330159042. I cannot tell whether a cheaper detector existed, so the class is `root-cause-unanswered`.

- `instrument-self-tests` failed on `.claude/hooks/stop-selfcheck.sh --self-test` ("a settings file whose PreToolUse matcher is empty-matcher passes (null control) (got 1, wanted 0)"; prepr self-tests 513 passed, 1 failed). The diff touches no `.claude` path, and I ran the same self-test at this head: 29 passed, 0 failed. It looks environmental or inherited from main, but the body must say so and name main's state.
- `pr-contract` red is likely a consequence of the unanswered red; the fix is to answer both in `## Red checks`.

The content itself held up: no fault found in the diff. After the body names both checks, re-review; `review_carry.py` should print CARRY if only the body changes.

## Evidence

- Head measured: 51f5ce37e1ebdb5643566b0c9a062b7678ada6d2 (ev/HEAD.txt). Merge with origin/main: `git merge-tree --write-tree` rc 0, clean (tree c278ee23).
- Replay at head: `RESULT replay defects=0 settle_gap=0 null_bad=0 scenes=7` (ev/replay_main.txt).
- Replay at dee8b413f tree: `RESULT replay defects=3 settle_gap=1 null_bad=0 scenes=7` (ev/replay_dee8b413.txt). Matches the body.
- Mutant (`deferred = {GATE} if busy else set()` replaced by `set()` at merge_train.py:487 of the head tree): `defects=3`, so the harness detects the wait's removal (ev/replay_mutant.txt).
- Body's "settle gap reads RED at both programs" is true only at the #3290 head. At this head, main has the settle wait (eb1081cf0), so it reads WAIT; the body's Figures section already shows `settle_gap=0`, but the record and Null control section are stale on this point. Not a blocker.
- carry_audit at head: 0 finding items. figure_lint: 2 resolved, 0 not verified. bugclasses.json parses. No VERSION, manifest, notes, budget, claim-file or ledger change; the only closures.json change adds the new harness.
- Final classify and packet: ev/classify_final.txt, ev/review-packet-final.md.
- This is round 1.
