Fix review: blocked 05b9c1d5383cf9ca7e2cd5310914897960244301 carry-missing: not carried to R10-CI-LAYOUT-P2

Round 2 of PR #2645 (R10-FLOW-TOOLKIT-MEASURE). I measured head 05b9c1d5383cf9ca7e2cd5310914897960244301 in a detached worktree. At the end of the review the PR head was still 05b9c1d5383cf9ca7e2cd5310914897960244301. Role contract: origin/main's fix-review.md. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the copy at this head is current. Group brief: origin/handoff/audit-r10-roster 8de7e22ac38c, wave-r10-groups.json.

The code is ready to merge. All four round-2 questions pass. The one blocker is a roster carry, which only the orchestrator can fix. No code round is needed.

## Blocker (step 10, finding-propagation.md)

The body's second Forward-carry corrects the `--drop-edge` wording that was already carried to R10-CI-LAYOUT-P2 at roster 5e70cc5cee. That carry says the tool "refuses rather than mixing two graphs", and the code shows that is false. The body sends the correction to "Carry: R10-ORCH-MACHINERY" and says "the roster carry is main's to amend".

- R10-ORCH-MACHINERY has `resume.stage: absorbed` on the roster at 8de7e22ac38c. Its note reads "Closed, superseded by the re-cut ... This group keeps only the no-build records and residuals as carries". `carry_audit` accepts it only because `roster_lib.DONE_STAGES` = (done, rca-done). No seat that runs CI-LAYOUT's next PR reads that group.
- R10-CI-LAYOUT-P2 is `in-progress`. Its carry still says the tool refuses (ev/roster_carries.txt). The roster holds no corrected text for either group.
- finding-propagation.md: a finding that "constrains one stage" goes to that stage's brief, and "while two copies disagree, the newer one is right and the other is the bug". Here the bug is the copy that P2's fixer will read. A P2 fixer who trusts it will take a `--last N` window across a graph change that renames or removes a job, and get a silent mixed figure (gain 0, rc=0; see ev/critpath_dropedge_and_W1.txt).
- To clear: the roster seat drops P2's 5e70cc5cee carry and appends the corrected text from the body, which states its precondition: read over runs on one side of the change and check the job names at both ends. The body then names the roster SHA as the destination. Once that SHA shows the corrected carry, this verdict can turn to merge with no re-measurement, as long as the head has not moved.
- The other carry, review_strength at or after this head, is already in the tree on R10-FLY-YIELD-GUARD (carry 6, from a7ef03069016). It is fine.

## The four round-2 questions

(a) The c10 mutant is killed, and so is the seat mutant.
- My mutant `q = ""` in `Api.runs` gives `KILLED rc=1 | ci_critpath self-test: 27 checks, 1 failed`, with `FAIL: --event and --branch reach the run-list query, and only its rows return`.
- I also ran four variants of my own, none in the PR: branch dropped, event dropped, keys swapped, and q not appended to the path. Each was KILLED with the same failing check (ev/ci_critpath_mutants.txt).
- The seat harness `r10_seat_selftests_mutants.py M0 ci_critpath-1..4 flow_metrics-1..2` prints `M0: 0 seat step(s) red` and `ci_critpath-3 ci_critpath.py: KILLED rc=1 | ci_critpath self-test: 27 checks, 1 failed`. Every other named mutant is KILLED with the body's failure counts (3/2/1/1/1/4). `RESULT survivors=0` (ev/seat_mutants.txt).

(b) c9-git-first is pinned, and c7 is rightly left alone.
- My mutant `p.stdout if False` is KILLED with `FAIL: needs at a head git holds are read from git, not the API (0 reads)`. A variant I added, `returncode != 0`, is KILLED 2 failed.
- The c7 cycle guard survives, as the body discloses (`27 checks, 0 failed`). Calling it "equivalent" is right in outcome but not literally. On a cyclic graph, head refuses with `SystemExit: ci_critpath: refused: a needs cycle through a`, and the mutant raises an uncaught RecursionError (ev/c7_cycle.txt).
- Both exit non-zero, so neither prints a wrong figure, and GitHub refuses cyclic `needs:` before a run exists. The only difference is the error text, so no check is owed.

(c) The forward-carry text matches the code.
- `analyse()` refuses only when `a in g and b in g and a not in g[b]["needs"]`, and `g` from `graph()` holds only jobs that ran (not skipped, with both timestamps).
- Run 39625218966 from the fixtures shows this. `typing:closures` (both ran, no edge) refuses rc=1. `nosuchjob:closures` and `coverage:nosuchjob` exit rc=0 with `gain 0 s` and no warning.
- The body's wording ("refuses only when both jobs ran ... the drop is a silent no-op") is accurate. The blocker above is about where that text went, not what it says.

(d) Red checks: every check at this head has concluded (ev/check_runs_head.tsv).
- The only red is `nightly-status`. Its log says it grades main's nightly ("There is no answer about the nightly yet"), and this diff does not reach nightly.yml or what it reads. The body answers it as not this PR's.
- `fast (3.14)` is green at this head. The body answers its round-1 red at ad62bf634 (`hb:positive_control`, a wall-clock spin check) and names the check's own three tries as the cheaper detector. That answers the trigger.
- pr-contract started at 04:24:23Z, after nightly-status concluded at 04:24:16Z, and passed.

## Other checks (this head)

- Self-tests: ci_critpath `27 checks, 0 failed`, flow_metrics `16 checks, 0 failed`, review_strength `100 checks, 0 failed`. These match the body. CI `instrument-self-tests` is green.
- Finder's null control, from the group carry, on the fixtures:
  - The W1 counterfactual gives `wall 2915 s (48.6 min)` → `1632 s (27.2 min)` and `2867 s (47.8 min)` → `2461 s (41.0 min)`. These match the study's 48.6/47.8 and about 27-30/about 41.
  - The archive parity harness gives `PARITY 24/24`, `NULL 9/24`, `NEEDS 40 files, 0 differ; mutant differs on 28`, rc=0 (ev/parity.txt).
- review_strength over the two study windows gives `PRs 112 verdicts 257 real 58 (0.52/PR)` and `PRs 47 verdicts 84 real 7 (0.15/PR)`. These are the study's figures. The bus total is now 684, not the body's 655, because the bus has grown since; the window figures did not move (ev/review_strength_windows.txt).
- I did not re-derive flow_metrics' FUTURE-STATE comparison. The body says those figures are on no ref it could read, and I did not search further. Carry: R10-FLOW-TOOLKIT-MODEL
- `git merge-tree --write-tree origin/main(a7cf60cfd8ac) HEAD` gives rc=0 (tree 6df74a475d49), so there is no conflict. VERSION, the manifest, RELEASE_NOTES and tests/golden are untouched (0 diff lines, three-dot).
- Lint checks: selftest_wiring `89 self-testing, 89 wired, 0 unwired`. `STRUCTURE RATCHET PASSED`. ref_privacy `0 refused`. throwaway_git `0 raw git init or clone site(s) refused`.
- I built no instrument of my own beyond the one-shot mutant drivers ev/mut.py and ev/c7.py.
- I re-ran neither the gate nor the mutation table; both are CI's and green.

bus-nonce: a96f1712ed4f4075e30975a04ce2def5
