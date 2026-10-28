Fix review: blocked 0d6c82965f056081c30e2cf1938597fde42dc643 null-control: the shipped host rule fires on 2 of its 10 pairs on a green tree (budget_raise_gate.py, selftest_wiring.py -> tests/entities.py); the RCA's 8-pair null sweep does not cover what the code ships

bus-nonce: b924bd8ea4ef820a31cb2b216093d7e1
reviewer: local-reviewer-s10
round: 1
measured head: 0d6c82965f056081c30e2cf1938597fde42dc643 (code head c68b62203f5e22cb881d8b4dd9ca810d0a11b8bf), merge base 0b8f8b585daf6a84ae9470389a709d5fec2a4f47. Re-read at post time, and the head had not moved.

All harnesses below are the reviewer's own (`ev/detect.sh`, `ev/nullsweep.py`, `ev/mutants.py`), not the fixer's `ev/proto.py` or `ev/nullsweep.py`. No finder harness is named, which is expected for an RCA seat.

## The block: the null control fails at the PR's own base

My sweep (`ev/nullsweep.py`) calls the head's own `self_test_hosts` and `self_test_reads` over every tracked self-testing `.py`. It treats each file as changed, alone, at the head tree (main 0b8f8b585 plus this PR):

    RESULT self-testing=95 hosted-files=10 pairs=10
    RESULT file=tools/audit/seat/selftest_wiring.py preds=1
      PRED SELF-TEST READS UNDER-SCOPED tests/entities.py: tools/audit/seat/selftest_wiring.py
    RESULT file=tools/policy/budget_raise_gate.py preds=1
      PRED SELF-TEST READS INERT tests/entities.py: dev/governance/config/policy_budgets.json
    RESULT total-preds=2          (the other 8 pairs: 0)

- **The RCA's figure is wrong for the shipped code.** Section 4 reports 8 pairs, all rc 0. The shipped rule gives 10 pairs, both at `6349205b6` (the RCA's own sweep base) and at the head (`ev/hosts-6349-vs-head.txt`). The two extra pairs are exactly the ones where the file sits only in `inert_reads[tests/entities.py]`. That means the host reads the file as text. The RCA says those are the pairs the rule exists to exclude ("a script that lists a file as text ... does not run it"). The fixer's sweep must have used a narrower definition than `self_test_hosts`, which unions `inert_reads` into the listing test.
- **Both predictions are false.** `tests / closures` is green on main 0b8f8b585 (check-run 122756539492) and on this head (122773765327). `policy_budgets.json` is absent from the CI-recorded `inert_reads[tests/entities.py]`. Changing `budget_raise_gate.py` does not make entities' run read it.
- **The false reds are frequent and costly.** In the RCA's window (since 2026-10-21, 302 first-parent merges on main), 4 merged PRs touched one of the two files: 3 for budget_raise_gate.py and 1 for selftest_wiring.py. Each would have got a prepr 6d rc 1. For the INERT one, the repair line tells the fixer to take INERT_EXCEPT plus a ~15 min `--single`. That is 4 false reds against the 2 true catches demonstrated, in the same window. Section 5's cost test counts no false-positive cost, so its "Build it" verdict is not established either.
- **What a repair looks like (the fixer decides).** Restrict hosts to scripts whose `closures` (not `inert_reads`) list the file. My mutant R3 (`closures` only) passes the arm's self-test and keeps all 8 real pairs, including roster_lib and state_docs, which are `closures`-listed. Then re-run the null sweep over what the code ships, and pin an inert_reads-only pair as a null arm in `self_test_reads_self_test`.

## What verified

**Detection, in detached worktrees of #2883's heads.** I copied the head `ci_predict.py` in and ran against `6349205b6` = `00ab2e97b^1` (`ev/detect-results.txt`):

    RESULT head=8f05b74d4 mode=arm rc=1 secs=46   -> INERT tests/entities.py: tools/audit/merge_throughput.py (state_docs)
    RESULT head=71987ff1e mode=arm rc=1 secs=58   -> INERT tests/entities.py: critical-path.json, wave-r9-groups.json (roster_lib; also state_docs for the latter)
    RESULT head=7b071dbd7 mode=arm rc=0 secs=51   -> quiet
    RESULT head=*         mode=noflag (--only under-scoped) rc=0, all three

The arm names exactly the pairs CI named. At load average about 250, its wall time is 46 to 58 s per head.

**ci_predict `--self-test`.**
- Locally, base and head both fail the same 5 AGREEMENT arms, with an identical FAIL set (`ev/fail-base.txt`, `ev/fail-head.txt`). The ok count goes from 27 to 32, so the five new arms pass.
- CI instrument-self-tests at this head (122773548310) prints `ci_predict self-test: 0 failed`, with the five new arms ok. The 5 local FAILs are environmental and pre-existing.

**My mutants** against the arm's own self-test (`ev/mutants-reviewer.txt`):

| mutant | result | consequence |
|---|---|---|
| R1, record not re-keyed to the host | killed, 2 fails | |
| R4, UNDER-SCOPED header unparsed | killed | |
| R5, `--self-test` filter negated | killed, 4 fails | |
| R2, window 0 | survives | also still detects at 71987ff1e (`ev/detect-71987ff1e-R2window0.txt`), so the 12-line window is unpinned but unexercised by these instances |
| R3, hosts from `closures` only | survives | this is the repair proposed above |
| R6, host may be the file itself | survives | minor |

**Commit identities** (`ev/identities.txt`). 80cf79c2c and c68b62203 are Tvofi2/hpo-fixer noreply. The merge-forward ef77f1be8 and the record commit 0d6c82965 are tvofi noreply, the same pattern as main's own record and merge commits (0238b7c7c, 7b071dbd7). No Claude footers or session URLs.

## Not verified, or noted

- **Process state (c).** The quoted 6d run at 71987ff1e is the fixer's artifact. Without the flag, I reproduced only the under-scoped arm quiet. The (c) reasoning is consistent with root-cause.md section 2: a check that existed in CI but in no local path.
- **The `prepr.sh` wiring is unpinned.** No prepr `--self-test` arm checks that 6d passes `record`, or that `predict_line` maps its fifth argument to `--record-self-tests`. A `git grep` finds no reference. Dropping either line disconnects the countermeasure silently. Compare the existing pin "--fill-red asks the predictor one arm". I did not run prepr `--self-test` under this load, so this is a static finding. It should get a case-pin when the block is repaired.
- **Cost-test inputs I did not re-derive.**
  - "15 of 300 PRs" and "63.4 s".
  - The 4 historical reds, and the ~85 min for each.
  - My per-file record times are 0.6 to 58.5 s at load about 250 (state_docs 58.5 s, budget_raise_gate 18.6 s). The RCA's 29 s upper bound was taken on a quieter machine.
- **Minor.**
  - Under `--only self-test-reads`, the quiet line lacks "unless a changed file's own self-test makes it", although the arm ran.
  - The `--apply-inert` re-predict drops `notes`.
- **Checks at post.** At post time, coverage, codeql/python and one prelude were still in progress. None was red.
