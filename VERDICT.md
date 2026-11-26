Fix review: merge 60bc4b3b3db63a345b8adc5f18c5e03aae48723b

bus-nonce: abc514b2caefea463653ff4319773f22

## Scope

Round 2, a delta review. The previous verdict, on verdict/3908 at d2873618f9, blocked a0250fc36517a51c90b2f36046ed1ca1253ca153 as mutation-survivor because pp4b and pp5 survived. `git diff a0250fc 60bc4b3b3db63a345b8adc5f18c5e03aae48723b` is one hunk of `tools/pr/prepr.sh`'s self-test (`ev/delta.diff`). It touches no production code (`custom_components/`), so the scope is not widened. The packet's `## Review scope: full` line exists only because it was rendered with `--reviewed-head` set to this head; the dispatch fixes the scope as the delta.

## Findings

- Residual: `summary_end`'s elapsed field is pinned at a single clock value. Mutant pp4c replaces `elapsed=${SECONDS}s` with the constant `elapsed=1000s`, the fixture's own value, and survives: rc=0, 576 passed, 0 failed (`ev/mut/pp4c.*`). The new check's text says "so a constant fails", but that holds for every constant except 1000. The main-flow line is driven at two clocks, and pp5c (constant `730s`) is killed by the SECONDS=40 check (`ev/mut/pp5c.*`). So the same two-value pair on `summary_end` would close this residual. It does not block: the only surviving value is the fixture's own arbitrary literal, which no realistic edit writes, and the round-1 failure mode (a plausible constant such as 2) is killed. Carry: dismissed: test-tuned constant only; the realistic constant mutant pp4b is killed and the two-clock pattern is in the same hunk for any later hardening

## Evidence

- RESULT: the live PR head is 60bc4b3b3db63a345b8adc5f18c5e03aae48723b, which is what was measured (`ev/HEAD.txt`). Its parents are a0250fc365 and 0d8cac00c7, and `git log a0250fc..60bc4b3b3db63a345b8adc5f18c5e03aae48723b` adds 6403d46419 and two merges. The delta is `tools/pr/prepr.sh` alone: 12 lines added, 2 deleted.
- RESULT: `git merge-tree --write-tree origin/main 60bc4b3b3db63a345b8adc5f18c5e03aae48723b` gives rc=0, a clean merge against origin/main d66452586467 (`ev/merge-tree.txt`).
- RESULT: on the unmutated head (null control), `bash tools/pr/prepr.sh --self-test` gives rc=0, 576 passed, 0 failed (`ev/mut/null.log`). That is 574 plus the 2 net new checks. The body's 574 figure is stated at d2fbbf2d00, not at this head.
- RESULT: pp4b, the round-1 survivor (`summary_end` `elapsed=2s`), is now killed: rc=2, 575 passed, 1 failed, FAIL `and the result line carries the run's elapsed read from the clock: SECONDS set to 1000 ...` (`ev/mut/pp4b.*`).
- RESULT: pp5, the round-1 survivor (main-flow `PRE-PR:` line without ` elapsed=${SECONDS}s`), is now killed: rc=2, 574 passed, 2 failed, on the SECONDS=730 and SECONDS=40 checks (`ev/mut/pp5.*`).
- RESULT: pp5c (main-flow constant `elapsed=730s`) is killed: rc=2, FAIL on the SECONDS=40 check. pp4c survives; see `## Findings`.
- RESULT: the main-flow check extracts the line with `sed -n '/^echo "PRE-PR: /p'` over `$flow`. That pattern matches exactly the flow's line 5061, and deleting the line leaves `$pl` empty, which fails both checks.
- RESULT: each mutant was run alone and in sequence in one worktree of the head, with the file restored between runs (`ev/mut/*.diff`, `ev/mut/summary.txt`).
- CI: `merge_train.py classify 60bc4b3b3db63a345b8adc5f18c5e03aae48723b --pr 3908` read WAIT from 14:28 UTC and GREEN at 14:57:56 UTC: `GREEN 60bc4b3b3db63a345b8adc5f18c5e03aae48723b pending: none red: none` (`ev/classify.txt`).
- Red checks at this head: `gate` job 139957989183 failed with "run(s) [45830476060] at this head are still being judged; their gate decides". That is the aggregator's sequencing exit, not a defect, and later `gate` jobs succeed (`ev/gate-red.txt`). `tests / nightly-status` is red but is not in `owed-reds` (`ev/owed-reds.txt`), so no answer is owed.
- Not re-derived: the body's C4 wall-clock figures. They are unchanged by this delta and were cited, not re-run, in round 1.
