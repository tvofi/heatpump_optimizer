Fix review: merge 0f779c2dce6b72f5bb3fe8d448d815d20c86ec96
bus-nonce: 736714e5a81f3297a1f05605b89c0db6

Round 2. Measured at head `0f779c2dce6b72f5bb3fe8d448d815d20c86ec96`, re-read live immediately before publishing: `OPEN` at that head on `refs/heads/fix/triage-s6-batch40-pr` and in the PR body's `## Head` (`evidence/head.txt`). Worktree `~/hpo-seats/r10s6/review-2886-r2/wt`, detached at the head; the main checkout is untouched. `git diff --name-status origin/main...0f779c2dc` is exactly two added paths, `dev/programme/delivery/2886.md` and `dev/programme/triage/s6-batch40.md`; `git rev-list --count f2ac08446..0f779c2dc --not origin/main` is `2` (the authored `1a6365f16` and its merge of main). No production line is written, so there is no mutant to draw; `prepr.sh`, the gate and the mutation table were not run, per the brief's cost discipline. Evidence: `~/hpo-seats/r10s6/review-2886-r2/evidence/`, one file per arm.

## Verified — B1-B4, each re-derived here

- B1 is paid, all three citations hold. `~/hpo-orch/r10s6/seat-ledger.md:1684` records the ruling at `2026-10-27T18:43:35Z` and `:1685` the batch-40 push at the same stamp; the arrival re-measures at `2026-10-27T18:23:44Z` (`TZ=UTC stat` on `~/hpo-orch/r10s6/proposals.md`) against `:1687`'s "mtime is 2026-10-27T18:23Z on this box (19:23 local)"; and `:1687` states the stamp "runs 10 min ahead of this seat's clock", which is the same clock the file's "about 10 min ahead of this box's clock" names. The round-1 falsehood is gone: `grep -n relayed dev/programme/triage/s6-batch40.md` prints nothing, and lines 5-6 now read "18:53Z is a stamp, not an arrival" (`evidence/b1_b2_provenance.txt`).
  Carry: dismissed: re-derived at this head, all three
- B2(a), the clock caveat, is in the file at lines 3-6, not only in the PR comment: "the entry's own header stamp / reads 2026-10-27T18:53Z, about 10 min ahead of this box's clock -- the seat read and ruled it at / 18:43:35Z, so 18:53Z is a stamp, not an arrival."
  Carry: dismissed: caveat in the durable file
- B2(b), the 85-minute caveat, is in the file at lines 9-11 and states all three required things. The quote re-checks verbatim by `gh pr view 2854 --json body --jq .body | grep -o`: "when the 30-minute lease lapsed inside the 85-minute run". The caveat calls the figure "not a measurement on / this box, and it is not re-derived here", so it does not imply a measurement taken here; and it records the earlier note false: "the claim that #2854's body lacks the figure is false". The cited `updatedAt` is the one non-re-derivable clause -- see Could not establish.
  Carry: dismissed: quote verbatim, not measured here
- B3 is paid as a limitation, not as work done. Lines 73-76: "Known limitation of the carried arm: the stored sample / must be keyed to the pid and start it sampled, and re-stored when either differs, or a branch / lock re-taken by a later run compares its CPU against the earlier run's sample and prints a / false STUCK." That is round 1's NONBLOCK (`~/hpo-seats/r10s6/review-2886-r1/VERDICT.md:23-24`) in the same shape, (pid, start) plus a re-store when either differs, and it is filed under a limitation heading rather than claimed as implemented (`evidence/b3_b4.txt`).
  Carry: R10-UPDATE-PR-SIGNALS
- B4 is paid. `dev/programme/delivery/2886.md` reads `- [#2886](...) — **open**, triage: batch 40 -- rule V124 as P211/V131 ...`, `gh pr view 2886 --json state` is `OPEN`, and `governance / delivery-status` on this head is `COMPLETED SUCCESS`. The diff is exactly the two markdown files named above, both added.
  Carry: dismissed: row true at this head
- The destination and the head are both as stated. At the cited `origin/handoff/audit-r10-roster` `32b938f3e` the roster has 212 groups and `R10-UPDATE-PR-SIGNALS` has `stage: done`, `files` naming `tools/audit/seat/pr_args.sh` and `tools/audit/seat/cloud_relay.sh`, and a brief ending "wait on a condition, never a fixed window" -- the seam lines 15-19 describe. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched because no such path is in the diff.
  Carry: dismissed: destination verified at its ref
- `python3 tools/audit/carry_audit.py pr 2886` prints `CARRY-AUDIT #2886: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`; `git merge-tree --write-tree origin/main 0f779c2dc` exits 0 with no conflicting path, so `claim-files.md`'s DIRTY path is not in play.
  Carry: dismissed: audit and merge arms clean
- No red check owes an answer. No rollup entry on this head carries a failing conclusion (`FAILURE`, `TIMED_OUT`, `CANCELLED` all return nothing); the ones still without a conclusion at measurement were `tests / fast (3.14)`, `tests / coverage`, `governance / instrument-self-tests`, `governance / env-matrix` and a `prelude`, so I cite no tick and claim no green beyond the completed runs (`evidence/destination_carries_checks.txt`).
  Carry: dismissed: no red check at this head

## Could not establish

- The `updatedAt` the provenance note brackets, `2026-10-27T18:23:17Z`, does not re-derive: `gh pr view 2854 --json updatedAt` now prints `2026-10-27T19:09:27Z`, moved by a comment two minutes after the fix commit (`1a6365f16` is 19:07:18Z), and no event at 18:23:17Z exists in the PR's timeline (the nearest stamps are 02:23:17Z and 18:46:52Z). Round 1 read 18:23:17Z at `f2ac08446`, so it was a snapshot true when taken, not a wrong reading; the load-bearing claim -- the quote is in the body -- re-checks verbatim now, so nothing in the ruling turns on it.
  Carry: dismissed: snapshot, quote re-checked
- #2854's `1,919 s` and its "+3.4 s of CPU per 20 s" sampled pair, and #2876's `2,295 s`: a finished run is not re-observable. The PRs are real and the figures are declared the orchestrator's and quoted from V124, which round 1 verified as declared.
  Carry: dismissed: figures not re-observable
- CI's green: several checks had not concluded at measurement, so the train's pre-flight remains the only whole-head gate.
  Carry: dismissed: not concluded at measurement
