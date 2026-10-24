# Fixer, round 2, PR #2639 (R10-FLY-GH-READ-RETRY, PR 2 of 2), topic r10-fly-gh-read-retry-2. PR head 5907408d6918c618e35c6cb202dc2d9b9cd1be9e (branch fix/r10-fly-gh-read-retry-2)

Main's opener was refused at prepr: `instrument-self-tests` is red at the PR head, and the body does not answer it. On main (0d859d31 and later) the same job is green. So this diff causes the red.

The job log is check-run 120184592953 (run on 5907408d). Read it once and cache it. Its FAIL lines:
- `merge_pr self-test: 18 checks, 1 failed`: "FAIL null control: the merge records the reviewed head (STALE: a re-run did not clear #42's head)"
- `pr_args self-test: 93 checks, 1 failed`: "FAIL the pusher census: the rule returns exactly the dispositioned paths, and every runner reaps", which appears twice, at log lines ~5582 and ~5719.

Your diff touches tools/audit/seat/merge_train.py, record_row.py, queue_pre_flight.py, gh_read.py (new) and tools/pr/app_approve.sh. Likely causes:
- the new gh_read.py, or app_approve.sh's changed `gh api` calls, adds a pusher or runner path that the pusher census does not disposition;
- the merge_train retry path changes what merge_pr's null control reads.

Find the cause in the code, never by inference, and fix it architecturally:
- disposition the new path in the census rule rather than loosening the census;
- keep the null control honest.

Failing-first is the CI red itself. Show each self-test green after the fix, plus a mutant that turns it red again.

Then:
- run every instrument self-test the diff touches;
- run `PYTHONPATH=tests/hastub python3 tests/entities.py` and tests/structure.py;
- run the scoped gate with PREPR_SKIP_CLOSURES=1.

Re-take the body completely, and answer any remaining red under `## Red checks`.

Follow dev/governance/roles/fixer.md and CLAUDE.md from main. Merge origin/main first.

Output:
1. Push the code fast-forward from 5907408d to refs/heads/handoff/r10-fly-gh-read-retry-2.
2. Push the body with `bash tools/audit/seat/body_push.sh r10-fly-gh-read-retry-2 <body.md>`. That is the return signal.

No Claude footers, Co-Authored-By trailers or session links anywhere.
