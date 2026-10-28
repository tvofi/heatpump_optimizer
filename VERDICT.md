Fix review: merge b9c96f4fa3fb1f556186bb8557050461b00d7a7e

bus-nonce: 80c4e712c89af74673e4a2b468396526

Round 1. Measured at head b9c96f4fa3fb1f556186bb8557050461b00d7a7e (base beb570c817c4efcae0d5f6f4bba52f3383baf8db = origin/main). The diff is two new markdown files: dev/programme/triage/s6-batch54.md and dev/programme/delivery/2927.md. No production code.

## Findings

- The roster carry for P265 is not on handoff/audit-r10-roster (b7e25cf06d1d1c13b298a3f94c791dbd2fd395bf) and cannot be written before this file lands: roster_edit's triage gate reads the ruling from the roster branch or origin/main, so the orchestrator must append the carry citing `triage: dev/programme/triage/s6-batch54.md#P265` to R10-ORCH-LEDGER after the merge, and read it back (finding-propagation.md). Carry: R10-ORCH-LEDGER

## Evidence

- ev/mutation.txt: roster_edit.ruling_verdict reads P265 as ACCEPT on the committed file. With the verdict rewritten to DEFER in a copy, triage_refusal returns "#P265 is not an ACCEPT ruling (DEFER)". With the file absent it returns "the triage ruling ... is not on the roster branch or origin/main". This matches the body's mutation proof and null control; I used the gate's own functions, not the fixer's text.
- Figures re-derived (ev/figures.txt): verdict/2906 tip is "blocked fb2f3de86... carry-missing", committed 2026-10-28T10:00:27+01:00 (= 09:00:27Z), refs/pull/2906/head is fb2f3de86; verdict/2917 and verdict/2919 do not exist; orchestrator_tick.py is 4066 lines, DIRTY line at 855, THROUGHPUT STALL at 1850. The "about 9 h" age and the "no new GitHub calls" design claim are proposals' reasoning, not re-derived here.
- git merge-tree --write-tree origin/main b9c96f4fa3fb1f556186bb8557050461b00d7a7e exits 0, no conflict (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES.md and tests/golden are untouched (ev/protected.txt empty); no claim file is touched, so env_drift has nothing to compare.
- carry_audit at the head (review packet): 1 finding item, 1 routed, 0 unrouted, 0 bad destination. figure_lint: 0 refused.
- Metrics/budgets: the diff moves no structure budget, closure, INERT list, golden or mutation ledger; the new files are markdown under dev/programme.
- No finder's harness exists or is claimed for a triage ruling; the body discloses its own mutation proof as its own.
- Commit messages carry no footer, trailer or session link.
- CI at read time (ev/checks.txt): prelude, refresh and cancel-superseded were queued, arm skipped, and no gate conclusion existed yet, so no red check exists to be answered; the body's "Red checks: none" is consistent with that. The merge train owns the gate conclusion.
- Head re-read: the PR head was b9c96f4fa3fb1f556186bb8557050461b00d7a7e when measured.
