Fix review: merge 879dd65becbc34403458628b0614ccdb43063e9f

bus-nonce: e3d895bb6b5d1579556abb097fe179dc

This is round 3, a delta re-review. The brief asks two things: do the new commits dispose roster carries 10 and 11, which round 2 blocked on as `carry-undisposed` at `859b74ba8`, and is the gate-defer red rechecked. I measured head `879dd65becbc34403458628b0614ccdb43063e9f` and re-read it from the PR API just before writing; it has not moved. The merge base is `a260e563086a85dcd2f1bc0ffaf033c93a01e783`. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract I read is current.

## Findings

- The body's `## Red checks` still says "No CI has run at this head yet". It was written before CI ran. At this head one `gate` job is red, 120968381381. It is a deferral, not a failure: its log reads "FAIL run(s) [40126133450] at this head are still being judged; their gate decides". That run's `gate` (120972924063) is green. A `pr-contract` run (120972809938) started at 19:59:48Z, after that red concluded at 19:40:11Z, and it is green. The deferring workflow's `gate` was also re-run (120973056574), and it is green. No red check is owed an answer. Carry: dismissed: the red is a gate deferral that its deciding run settled green, and a later pr-contract run is green; the stale sentence binds no stage

## Evidence

- RESULT carry 10 applied (tvofi 2026-10-24 card 3, roster `313643643`, an ancestor of `handoff/audit-r10-roster` `1558cf55f`). `fixer.md` lines 7 to 9 tell a fixer to wait on CI through one `seat/ci-watch.sh` or `seat/proof_watch.py`, with the 60 s API floor kept inside the script. The fixer is woken once by the watcher's exit and never sleeps and polls. Past the handoff, the fixer does not wait. `fix-review.md` line 8 points a reviewer's long job, or wait on CI, at the same preamble. Each clause of the card is present: one watcher, the 60 s floor inside the script, woken once, no sleep-and-poll, no wait after the handoff. Both scripts exist at the head. Neither file had a poll-every-5-minutes sentence at the merge base, so the amendment is an addition (`ev/grep-head.txt`, `ev/carries-10-12.txt`).
- RESULT carry 11 applied (card 2, amended twice; roster `3454d6cc3`). `fixer.md` line 9 to 10 says to rotate to a fresh context between stages (rca, fix, handoff) through refs, never mid-task, by about 150 k tokens (S, M) or about 300 k (L, XL). `fix-review.md` line 8 says between rounds, never mid-review, by about 150 k. That is one sentence per file, as the card asks. The orchestrator's 500 k cap is not added, as the card says.
- RESULT carry 12 applied (#2709, roster `8ecacecb1`, 16:48Z). `fixer.md` step 2 names `exit $?` to `exit 0` under `set -e` as equivalent, and gives `|| true; exit 0`.
- RESULT R10-ORCH-BEATD at roster tip `1558cf55f` keeps R10-POLICY-FIXER-MD in its `after` list. The seat-side rule its after-edge rests on is now in this diff, so merging this PR orphans neither owner card. That was round 2's block.
- RESULT the payments: no budget moved. `policy_lint.mjs --budgets` at the head reads `fixer.md 314 315 5214 5216`, `fix-review.md 140 140 2448 2451` and `finding-propagation.md 101 101 1332 1336`. `TOTAL: 0 error(s) across 50 policy file(s)`, `RULES-SYNC ok`, `check-wave-script 209 passed, 0 failed`. At the merge base it reads `312/315 5169/5216`, `139/140 2420/2451`, `100/101 1335/1336` (`ev/head-checks.txt`, `ev/mb-budgets.txt`). All of these match the body.
- RESULT mutant B, re-run by me: `fix-review.md` at `859b74ba8` plus only the new preamble sentence gives `fix-review.md 140 140 2482 2451` and `TOTAL: 1 error(s)`. That matches the body, so the fix-review cuts are needed. The worktree was restored clean (`ev/mutantB.txt`). I did not re-run mutant A, which the body states as `fixer.md 318 315 5293 5216`.
- The cuts in `e1af66910` remove motivation only:
  - the `pre-edit.sh` instance in step 2;
  - step 10's "because" clause;
  - #948's narrative in step 15, condensed to its figures, with the production-width condition and the CPython `sum` rule kept;
  - fix-review's `preflight.sh` aside;
  - #1144's narrative, with its citation kept.
  I read each one against its parent, and no operative clause is lost. No added sentence loosens a binding.
- Mutation proof (step 1): the new sentences are prose that no checker reads, and the body says so. The only kill to check is the payment, shown by mutant B above.
- The two merges into the head, `ea1bc9347` and `879dd65be`, have empty `--remerge-diff`, so neither hides a resolution (`ev/remerge.txt`). The authored change since round 2 is `e1af66910`, which touches only `fixer.md` and `fix-review.md`. The PR's own diff at the head is 6 files, 76 insertions and 69 deletions (`ev/diffstat.txt`).
- RESULT merge-tree: `git merge-tree --write-tree origin/main 879dd65be` exits rc=0 against origin/main `2636ce9e9` (`ev/merge-tree.txt`).
- Step 11, CI at this head, read with all check runs listed, not the latest per name (`ev/check-runs.txt`, `ev/ci-code-run.txt`):
  - The only red is `gate` 120968381381, the deferral recorded under Findings.
  - Run 40126133450 (CI code) concluded `success`, including `tests / coverage` and `coverage-ratchet`.
  - Its `gate` and the later `pr-contract` are green.
  - Every other check is success or skipped.
- Step 5: no change to `VERSION`, the manifest or `RELEASE_NOTES.md`.
- Step 14: `policy_budgets.json` is not in the diff.
- Item 11, mutants 1 to 3 and the forward-carries stand from rounds 1 and 2. This delta touches nothing they read.
- Step 12: the head is `879dd65be`, re-read from the PR API at writing.
