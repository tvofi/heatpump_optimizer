# BLOCKED: r10-hotfix-codeql-headroom, repair round 2

**Result first: the measurement refutes the PR's premise.** Two `workflow_dispatch` CI runs at `f0b215af2447` both ran a real `codeql / Analyze (python)`, and both were **cancelled at the 45-minute cap**. Main's job at the same merge base (`a37c58e5f321`, job 128423079820) took 26m27s.

| job | features.py | entities.py | closure.py / structure.py (null) | queries done | duration |
|---|---|---|---|---|---|
| main 128423079820 | 739494 ms | 314673 ms | 1769 / 2257 ms | 52/52 in 12m42s | 26m27s |
| head 128428511054 | 1333896 ms | 208291 ms | 2215 / 2585 ms | 6/52 | 45m05s, cancelled |
| head 128440898484 (replicate) | 2008646 ms | 310210 ms | 3228 / 4606 ms | 6/52 | 45m06s, cancelled |

Main's job with null-control times matching the replicate (127995766058, 3231 / 4117 ms) read `features.py` 1389484 ms. The wrapping makes `features.py` slower and the query phase much slower. Only `entities.py`'s half gains. The full body, which passes `prepr.sh` (rc=0 at `0d5934cbbbf8`) and `--body-check`, is at `refs/heads/handoff-wip/r10-hotfix-codeql-headroom-body`. The code head is pushed to `refs/heads/handoff/r10-hotfix-codeql-headroom` = `0d5934cbbbf8f4343e0c766f0051049fde5fc466`.

## The block

`tools/audit/seat/body_push.sh` refused the return push:
`CARRY-LANDED: 3 missing` -- "a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body".

The roster branch is outside the refs this seat may write, so I did not land them. Question for the orchestrator or standing-roster: land these ops (from `carry_audit.py land-ops --body <body> --pr '#3266' --topic r10-hotfix-codeql-headroom`), then rerun `body_push.sh r10-hotfix-codeql-headroom <body>` with the body from the -body ref. Or rule that the group is closed on this measurement.

```
append-carry R10-HOTFIX-CODEQL-HEADROOM 'From #3266 (r10-hotfix-codeql-headroom), body item 6e003ed3: The premise fails: per-statement wrapping of module-scope `try` slows `features.py`'\''s CodeQL extraction and query evaluation, and the python job no longer fits its cap. The group'\''s design has to change before any fix lands, and only `entities.py`'\''s half measured a gain. Carry: R10-HOTFIX-CODEQL-HEADROOM (items 6e003ed3)'
append-carry R10-HOTFIX-CODEQL-HEADROOM 'From #3266 (r10-hotfix-codeql-headroom), body item 93aad749: A fixer cannot dispatch `ci.yml` with `pr=<N>` from its own ref. The prelude refuses any ref that is not the PR'\''s head. Dispatch with inputs empty, the batch-proof form, which still analyzes. A brief asking a fixer for a CodeQL figure should name that form. Carry: R10-HOTFIX-CODEQL-HEADROOM (items 93aad749)'
append-carry R10-HOTFIX-CODEQL-HEADROOM 'From #3266 (r10-hotfix-codeql-headroom), body item e017bcd8: fixer-codeql-dispatch: contradiction: the brief named dispatch inputs `pr=3266`, `base=main`, and the prelude refuses them for any ref but the PR'\''s head, so the first run (42380280230) went red at the prelude. Carry: R10-HOTFIX-CODEQL-HEADROOM (items e017bcd8)'
```
