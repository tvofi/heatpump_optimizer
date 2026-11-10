Fix review: blocked 0884509a04003457eea9ae5d2777941ba9d00fe2 figure-wrong: phase P1 is 28 pushes with 24 cancelled, not 27 and 23

bus-nonce: 9b5dbc607bf3f24387e407e6e8eaadae

Round 1. Measured head `0884509a04003457eea9ae5d2777941ba9d00fe2`, still the PR head when this was written; merge base `0362916ac`.

## Block

- Section 1's phase table gives P1 (`ba6fd7e8b` to `3aac11dfb`) as **27** pushes, "23 `cancelled` ... 4 `failure`", and section 1 says "The 36 push runs of `ci.yml` in the window fall into three phases". Section 2d ("phase P1 hid 2a for 27 pushes") and section 5 ("Cost of this occurrence: 27 pushes, phase P1") repeat the 27. Re-derived from git alone: `git rev-list --first-parent --count ba6fd7e8b^..3aac11dfb` = **28**. The job `governance / instrument-self-tests` concluded `cancelled` on **24** of those 28 pushes and `failure` on 4. The four failures the document names (`6d660061d`, `72a2acee5`, `53f4a051b`, `b8f67a775`) are correct (`ev/p1-p3-instrument-self-tests-jobs.tsv`, one row per first-parent commit, `filter=latest` job of each push run). The document's own figures disagree with each other: 27 + 5 + 2 = 34 concluded, plus 2 in progress = 36, against its "37 pushes counting #3315's own". With 28, the sum is 28 + 5 + 2 + 2 = 37, which matches. Repair: P1 = 28 pushes (24 cancelled, 4 failure) in the table, in 2d and in section 5. "The 36 push runs ... fall into three phases" becomes 35 concluded in three phases plus the 2 in progress. The conclusions (state (c), A and B pass the cost test, no countermeasure for 2d) do not turn on the one push.
- CI on this head reads `RED 0884509a... pending: none red: gate` (`merge_train.py classify`, rc 1, `ev/classify-final.txt`). The red is the **edit** run's `gate` (check run 129680025529, run 42771199407, attempt 1): `FAIL run(s) [42771199429] at this head are still being judged; their gate decides`, exit 1 at 06:53:35Z. The code run's `gate` (check run 129688172891) concluded `success` at 07:17:11Z. This is the same deferral #3361's body answered. `pr-contract / pr-contract` (129687440137) started at 07:14:44Z, after that red, and concluded `success`, so by fix-review.md step 11 the body's `## Red checks: none` is not a root-cause block. The train still classifies the head RED, though. On the re-cut, re-run that attempt, as #3361's run 42540449051 attempt 2 did, so that classify reads GREEN at the new head. Or name the deferral in `## Red checks` as #3361 did.

## Findings

none

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 0884509a...` exits 0 with tree `235bbf2e3`, no conflict (`ev/merge-tree.txt`).
- RESULT roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT diff: two added files, `dev/audit/rca/R10-RCA-MAIN-SELFTESTS-RED.md` and `dev/programme/delivery/3410.md`. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. No golden or claim file changes, so `env_drift.py --all` has nothing to compare.
- RESULT mutation: n/a. The diff writes no production, test or check line, so no mutant can be drawn (fix-review.md step 1). `tests / mutation` is `success`.
- RESULT figure `git log --first-parent --format=%h ba6fd7e8b..0362916ac | wc -l` = 36, matching the body.
- RESULT figure `git diff --stat 2cf0f129b^1 2cf0f129b -- tools/ci/selftest_closures.json` = 26 insertions, 0 deletions, matching.
- RESULT figure: all six missed-path add commits and dates in 2a re-derive exactly.
- RESULT figure class enumerator 2 at `0362916ac` = 23 files, matching. `git grep -c "event_name == 'push'" -- .github/workflows` = 1+3+1+14 = 19 lines in 4 files, matching.
- RESULT null control 2c: `selftest_scope.py --self-test` prints `103 checks, 0 failed` at `5ab6030d7` and `FAIL the live job parses (118 steps) ...`, `103 checks, 1 failed` at `8652aa65c`, matching. Countermeasure B probe, my own driver of production `wiring_gaps(workflow_steps(root))`: 0 `[]` at `5ab6030d7`, 1 at `8652aa65c` with the UNGATED line verbatim, matching. I did not re-run the scratch-gated third case.
- RESULT null control 2b, by strace at `0362916ac`: `git show HEAD~400:tools/audit/seat/gh_read_run.py` touches the worktree path once, and `git show HEAD:...` touches it 0 times, matching.
- RESULT figure run 42758119155 (`57091a694`, push, failure), job 129637321760: `selftest_scope check: 109 gated step(s), 38 refusal(s)`, matching.
- RESULT figure run 42748431595: workflow_dispatch "CI code pr=3361" at `825f54927` (#3361's merged head, merge `8652aa65c`), failure. Its one failed job is 129632432183 `governance / instrument-self-tests`, at step "Show the self-test scope (tools/ci/selftest_scope.py) refusing its own fixtures", matching. #3361's `## Red checks` names only the `gate` deferral, matching 2c.
- RESULT figure P2 = 5 and P3 = 2 pushes, all `failure`, matching. `e3295ba46` and `0362916ac` have since concluded `failure`.
- RESULT spans: #3315 08:16Z to `57091a694` 04:47Z = 20.5 h, and to #3375 01:47Z = 17.5 h, matching.
- Not re-derived: the per-run refusal counts inside P1 (39, 47) and P2 (37 to 38), artifact ids 13737009763, 13735714488 and 13737089304, the 0.3 s / 34857-byte upload, #3393's 148 min, and the 0.79 s / 3.1 s wall clocks. These are taken as quoted.
- Carry check: the body's third forward-carry names `R10-HOTFIX-MAIN-SELFTESTS`, present in `dev/programme/rosters/wave-r10-groups.json` on `origin/handoff/audit-r10-roster`. The packet's carry_audit reads 3 routed, 0 unrouted. Carries A and B are dismissed as owner proposals.
- CI: every check at the head has concluded (`ev/check-runs-at-head.tsv`). `governance / instrument-self-tests` (129679296219) is `failure`. It is not in `merge_train.py owed-reds` (`ev/owed-reds.txt`), and main is red on the same job at the merge base (`0362916ac` push run 42759830106, failure), so this red is inherited and not this PR's.
- Harness: none. This is an RCA document with no finder's harness. All the probes above are my own commands, run in detached worktrees.
