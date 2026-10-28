Fix review: blocked 0f77f2ecd80e59c178c66e9f9fae6cab8d363561 figure-uncited: P63 Instances 3 is carried as the orchestrator's account, not cited, and it is the figure that flips P57's DEFER to ACCEPT

bus-nonce: b96f2797f4306fdcd233e2161038f462

Round 1. Head measured: 0f77f2ecd80e59c178c66e9f9fae6cab8d363561 (PR head when read; merge base e97f5749b = origin/main). Roles diff since the merge base: empty, so the fix-review contract I applied is current.

## Block

`dev/governance/roles/proposal-triage.md` requires each ruling's `Instances:` to give "each counted instance with the command or log reference beside its figure: cite it, don't carry it", and says "an unmeasured benefit is DEFER, never ACCEPT". The P63 entry reads `Instances: 3 (roster w5/w6; the #2698 fixer against an update; dispatch w14/w15 ...). Orchestrator's account; not re-counted from logs.` That figure is carried, not cited: no log path, line, timestamp or command appears for any of the three instances. It is also the figure that decides the verdict. P57 (`s6-batch4.md`, on `origin/triage/s6-batch4`) is `DEFER; re-triage on a third instance` at 2 instances, so P63's ACCEPT rests entirely on the new third instance (w14/w15). I cannot re-derive it from the tree or from git (fix-review.md step 8), and the body does not quote it either. Every other `Instances:` line in s5-batch1, s5-batch2 and s6-batch1..3 names a PR, a run, a log line or a command (`ev/instances-practice.txt`), so this entry departs from that practice as well as from the contract. Once on main, the ACCEPT is what `roster_edit.triage_refusal` lets through (see Evidence), so an uncited count gates a roster edit.
To clear it: cite each of the three instances with its log reference (for example the dispatch w14/w15 state-dir log line and its UTC timestamp, the #2698 fixer and update times, and the roster w5/w6 refs or logs). Alternatively, rule DEFER until the third instance is cited.

## Findings

- `s6-batch5.md` refers twice to `s6-batch4.md`: "Numbering continues after `s6-batch4.md` (P62)" and "Supersedes the DEFER in P57 (`s6-batch4.md`)". That file is not on origin/main (`ev/main-triage-files.txt` lists only s6-batch1..3); it is in the open #2734 (`origin/triage/s6-batch4`, head 35cb7e8cc). If #2735 merges first, or #2734 is reworked, both references dangle, and the superseded P57 DEFER is not on main to supersede. This PR should merge only after #2734, and the body should state that order. Carry: #2734

## Evidence

- RESULT ruling_verdict(s6-batch5.md, P63) = ACCEPT; null control P99 = None (matches the body's claim). `ev/ruling.txt`
- Mutants (own, in-memory): deleting the `Verdict:` line gives `unreadable`. ACCEPT changed to DEFER gives `DEFER`, and `triage_refusal` then refuses the citation `s6-batch5.md#P63`. Unmutated, `triage_refusal` returns None. So the consumer reads the one entry, as the body says.
- Body figure re-derived: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' ... | uniq -c` gives 1 ACCEPT, matching the body (`ev/figure.txt`).
- Destination group R10-ORCH-BEATD exists in `dev/programme/rosters/wave-r10-groups.json` at the head (line 8068), so ACCEPT names an existing group as the contract requires.
- Classification: both files are under `dev/programme/`, which `tests/closure.py` lists as INERT (line 273). No code, no budgets and no claim files are touched (`ev/diffstat.txt`). Mutation proof n/a, as the body states.
- VERSION, manifest and RELEASE_NOTES untouched (`ev/version.txt`).
- `git merge-tree --write-tree origin/main 0f77f2ecd` exits 0 with no conflicts (`ev/merge-tree.txt`).
- CI on the head (check-runs API, read twice): `refresh` in run 40102048538 succeeded. The two `prelude` jobs, the two `cancel-superseded` jobs and the `refresh` job in run 40102049462 were still queued, so no workflow had concluded and no `pr-contract` result exists yet. The body's `Red checks: none` is therefore unverified at this head. The block above does not depend on CI.
- The PR body's head line names d47d5e0fe plus a row commit, and the head is 0f77f2ecd = d47d5e0fe + `dev/programme/delivery/2735.md`. That agrees with `git log`.
