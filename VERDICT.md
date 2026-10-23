Fix review: merge 05b9c1d5383cf9ca7e2cd5310914897960244301

bus-nonce: c978149a1d6a175005643361cd8a54bf

Round 3, a re-check of round 2's single block (carry-missing). Head measured: 05b9c1d5383cf9ca7e2cd5310914897960244301 (ev/HEAD.txt), unchanged since round 2. Code is unchanged from round 2, which found it ready.

1. Head unchanged: `git fetch origin 05b9c1d5…` resolves to the same SHA, and the PR API reports that head.
2. Roster carry: at f65126e9d (an ancestor of handoff/audit-r10-roster) the roster holds exactly one drop-edge carry, on R10-CI-LAYOUT-P2 (ev/roster_carry.txt). It says a window straddling a job-graph change refuses only when both jobs survive, and that a rename or removal is a silent no-op, so the median mixes two graphs. This matches the body's second Forward-carry. No roster carry reads "refuses rather than mixing".
3. `carry_audit.py check --body` (roster-ref f65126e9d, and again at the branch tip): `5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit.txt).
4. pr-contract on the edited event (05:26:20Z to 05:26:42Z): success. This comes from one bulk check-runs read, 44 runs. The only red check is nightly-status, which grades main's scheduled runs and which the body answers. `fast (3.14)` is now green (the red in the body was round 1's head).
5. Merge: `git merge-tree --write-tree origin/main <head>` exits 0 with no conflict. Main has moved on (c26499e0). The diff touches no VERSION, manifest, notes heading or golden file.

Not re-run: the mutation proofs and figures (round 2 reviewed them; the code is unchanged). CI's heavy runs are cited from the check-runs read, not re-run.
