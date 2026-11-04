Fix review: blocked a615a76f16aa76f49a436ae16b65b3ba63214aba root-cause-detectable: tests / closures

bus-nonce: 8ba45417cba8b44ad106112fe4ea9aab

Round 1. Reviewed head a615a76f16aa76f49a436ae16b65b3ba63214aba (doc and harness under dev/audit only). The PR head is now 79ac5afb80a921f3b4b13be6800dadf77ec7bec9, a bot "ci: re-record closures" commit on top; `review_carry.py` prints CARRY for it (ev/review_carry.txt), so this verdict stands for the PR as it is now.

## Block

The body's `## Red checks` says "none". At this head's run `tests / closures` went red (UNDER-SCOPED): the five new .py files under `dev/audit/harnesses/r10_gate_stale_jobs/` were in no measured closure, and the ci-autofix commit 79ac5af added them to `tests/closures.json` (ev/closures-autofix.diff). The body also states that `tests/closure.py`'s INERT list covers them, and that is wrong: `dev/audit/` is on INERT (tests/closure.py:321), but these files are measured, as the bot's re-record shows.

`pr-contract` is red at 79ac5af for exactly this: `ERROR [pr-body] check `tests / closures` is red and `## Red checks` does not name it` (job 126817495961); `gate` is red on that one reason, `FAIL pr-contract / pr-contract: failure (this run)` (job 126817908140). Both are the push-time and later runs of the head's workflows, concluded. `ci-autofix.md` makes `UNDER-SCOPED` answerable by naming it, which the body does not do.

A cheaper detector existed: `tests/closure.py` / `prepr.sh` predict the red before the handoff, and a repair before the handoff was owed. Fix: add `tests / closures` under `## Red checks` naming UNDER-SCOPED and the 79ac5af repair, and correct the INERT sentence. No code change needed.

## Findings

- The body's INERT sentence and its "Scope: 0 script(s) run" line misdescribe the new files, which are measured closure members; correct them with the Red checks answer. Carry: dismissed: owned by this PR's own body edit above, not a later stage
- Residual: the doc's "about 47 min" (section 4) re-derives as 45 min under my reading (13 attempt-1 attempts that only the lag reasons explain, each at its largest lag rounded up to 60 s); 39.7 min unrounded. Same order, same verdict (build); say which rounding. Carry: dismissed: the cost-test verdict does not move
- Follow-up: the doc's handoff-column results (3 of 9, section 5) and the body's `a6305aa29` figures were not re-run: that SHA is not fetchable from origin by abbreviation, so only the main column was verified. Carry: R10-HOTFIX-GATE-STALE-JOBS
- Follow-up: the doc's two fail-open readers (`codescan_wait.py` own-run path, `pr-contract.yml` red list at line 306) are unmeasured and carried; the body's carry routes resolve on origin/handoff/audit-r10-roster (CARRY-AUDIT: 3 routed, 0 unrouted). Carry: R10-HOTFIX-GATE-STALE-JOBS

## Evidence

- Re-derived from `reasons.jsonl` with `tally.py` (ev/tally.txt, ev/rederive.txt): 1000 scanned runs, 383 red gate attempts; only-PENDING 6 (3 false, 3 hid a real failure), only-prelude-None 12 (10 false, 2 true), ABSENT 1 (false), PENDING-plus-other 2; class 21, false reds 14. Matches the doc. 37 unread runs (jobs-read errors) and 0 log-read errors match; the tally's own "read errors 175" counts 175 error records over 138 runs, 101 of which a later pass scanned.
- By incident (symmetric 66 min window, read_at): 11 inside, 8 within, 2 outside (41289450679 at 20 s, 41061779792 at 23 s): 19 of 21 as stated. Lags: 28 lines, 22 on attempt 1, 2 over 660 s: as stated.
- Harness at the head tree and at origin/main d7582ed40 (ev/harness-head.txt, ev/harness-main.txt): `mismatches 4 of 9`, rc 1, identical rows to the doc's main column; both nulls PASS/FAIL with 0 s waited.
- The 170 min 4 s recovery and the 224 min figure: the nine listed durations sum to 170:04, plus 54:05 is 224:09; `recover.py` needs gh auth, which this seat lacks, so the per-run times themselves are not re-derived.
- merge-tree of origin/main with the head: clean (ev/merge-tree.txt). VERSION, manifest version and notes heading untouched (pr-contract's own line). No production code changes, so no mutation proof beyond the body's two harness mutants, which I did not re-run.
- Not verifiable here: `tests/entities.py` needs homeassistant, absent in this seat. `tests / nightly-status` is red on the run but this diff reaches nothing it reads.
- CI at the reviewed head: classify RED (gate) (ev/classify.txt); at 79ac5af RED (gate) (ev/classify-79ac.txt), reason as above.
- Head reviewed: a615a76f16aa76f49a436ae16b65b3ba63214aba (ev/HEAD.txt).
