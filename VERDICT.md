Fix review: merge 0e9d90eaa3af4f227def7e090463760fcfcbc807

bus-nonce: 66b56db4963f64c6b3bf0d04cff75621
reviewer: local-reviewer-s10
round: 2 (round 1 blocked 0d6c82965 null-control; its record is in r1/ beside this file, and it is not published)
measured head: 0e9d90eaa3af4f227def7e090463760fcfcbc807, code 43e474b3a, merge base f844df1fe. The head was re-read before posting and had not moved. The worktree survived the 12:42Z power loss clean at 0d6c82965 and was moved to the new head.

All harnesses are the reviewer's own (`ev/nullsweep.py`, `ev/detect.sh`, `ev/mutants.py`, `ev/pins.sh`), not the fixer's `ev/nullsweep2.py` or `ev/pin6d.sh`.

## Round 1's block is repaired

**Null sweep, re-derived** (`ev/nullsweep-head.txt`). The head's own `self_test_hosts` and `self_test_reads` ran over every tracked self-testing file, each treated as changed alone:

    RESULT listed-pairs-any-table=74
    RESULT self-testing=95 hosted-files=8 pairs=8
    (ci_ratchet, archscore/gate, record_row, roster_lib, state_docs, tools/ci/gate, ledger_merge, stamp)
    RESULT total-preds=0      (record 0.2 to 41.8 s a file; state_docs 41.8 s)

- `budget_raise_gate.py` and `selftest_wiring.py` are no longer hosted. My sweep matches the body's 8 pairs and 0 predictions.
- The rule now reads `closures` alone and excludes the file as its own host. Both changes are in `8ad983385`.

**Detection, re-run** (`ev/detect-results.txt`). The head's `ci_predict.py` was copied into detached worktrees of #2883's heads and run against `6349205b6`:

    RESULT head=8f05b74d4 mode=arm rc=1   INERT tests/entities.py: tools/audit/merge_throughput.py
    RESULT head=71987ff1e mode=arm rc=1   INERT tests/entities.py: critical-path.json, wave-r9-groups.json
    RESULT head=7b071dbd7 mode=arm rc=0   quiet, "unless a changed file's own self-test makes it" (now printed under --only too)

These are the same pairs CI named, as in round 1.

## Mutants and pins

**My mutants** against the arm's self-test (`ev/mutants-reviewer.txt`):

| mutant | result |
|---|---|
| R2, window 0 | killed, 4 fails |
| R3, round 1's inert_reads union restored | killed, 3 fails |
| R4 | killed, 1 fail |
| R5 | killed, 4 fails |
| R6, file as its own host | killed, 2 fails |
| R8, no self-test word needed | killed, 2 fails |
| R7, window 10000 | survives |
| R1, record not re-keyed to the host | survives |

- The three round-1 survivors, R2, R3 and R6, are now killed.
- **R7 survives.** The window's upper side is pinned only by the "one past the window" null host at 13 lines. That host is also caught by the self-test word plus a name on separate lines, so a huge window would need a separate plant. This is minor.
- **R1 survives, newly.** It was killed in round 1. Round 2's plant makes the file a closures key of its own (`f: [f]`), and grading under the file's own key then coincides with grading under the host's.
  - On real detection at 71987ff1e it still gives rc 1 with the same three reads, so the outcome holds.
  - Only the label degrades, to `tests/entities.py: tools/audit/seat/roster_lib.py: <path>` (`ev/detect-71987ff1e-R1.txt`).
  - It is not blocking. It is worth a plant where the host's closure and the file's own key differ.

**The prepr wiring pins** (`ev/pins.txt`). I drove both predicates over three wiring mutants myself:
- Dropping 6d's `record` trips pin6d.
- Deleting the `rec=` line trips pinmap.
- Dropping `$rec` from the command line trips pinmap.
- The clean copy passes both.

On CI, instrument-self-tests 122942992153 at this head concluded success. That is the pins' first run: both print `ok`, and `ci_predict self-test: 0 failed` includes the reworded arm.

## Other checks

- **Local self-test.** `ci_predict --self-test` at the head fails the same 5 AGREEMENT arms as at round 1's base, an identical FAIL set (`ev/fail-head.txt`). They are environmental and pre-existing. CI shows 0 failed.
- **Cost test, redone.** It now counts round 1's 4 false reds and states 0 false reds for the closures-only rule. My sweep supports the 0. I did not re-derive "15 of 300 PRs", "63.4 s", the 4 historical reds or the ~85 min per occurrence. The verdict "Build it" follows on the stated numbers.
- **Process state (c)** is unchanged from round 1. It is consistent with root-cause.md section 2.
- **Identities** (`ev/identities.txt`). The PR's non-merge commits are 80cf79c2c, 8ad983385 and d2e0d88f7, all Tvofi2/hpo-fixer noreply, plus the tvofi record commit 0d6c82965. They carry no Claude trailers. The `Claude <noreply@anthropic.com>` commit b9a66d28d in the range is main's #2903, merged forward, not this PR's.
- **CI.** `tests / closures` at this head is success (122943233136). At post time, coverage, codeql/python and prelude were still in progress, and none was red. No red gate check, so no root-cause trigger is owed.
