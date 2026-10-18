Fix review: blocked c83ae12acc074a16af424879b09b151d07726e52 carry-stale: R10-TICK-DRIVERS gains the codeql_scope -> closure.changed_between delegation carry that #2406's round-4 review (6252146172) and #2406's own body say is done in #2406 and must be dropped; #2406's head d1becac2b already delegates, so the carry dispatches finished work

bus-nonce: d2409544ec4698f4b72b59b961e051f1

PR: #2417 (R10-ROSTER). Round 1 (no earlier `Fix review:` comment on the PR).
Reviewed head: c83ae12acc074a16af424879b09b151d07726e52 (the PR's head when read; `ev/HEAD`). Merge base c8cc75ea90a3bb38dbc6b8dbb7d27d9cce74cdd0. origin/main 106af95a33f89f88f948ea9c49c4632fe74b9416.
Contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current (`ev/roles-diff-lines.txt`).
Reviewer: a cloud seat with no access to the out-of-tree briefs or bus evidence under `~/hpo-*`. Every check below was read from the tree, the check-runs API or the source review comments.

## Blocking: carry-stale (step 10, finding-propagation.md)

The second carry this PR appends to R10-TICK-DRIVERS reads: "From R10-ROSTER-FASTPATH (#2406): after #2405 and #2406 both merge, make tools/pr/codeql_scope.py's changed subcommand delegate to tests/closure.py changed_between ...".
- That carry matches #2406's round-3 review (6251656756), but round 3 is not the latest review. #2406's round-4 review (6252146172, step 10) says: "The body says the CodeQL delegation carry is done here, and it is, by M3. But that carry is still in `R10-TICK-DRIVERS.carry` ... Dropping it is the orchestrator's roster edit at merge, or a later seat will redo finished work."
- #2406's current body says the same thing in `## Forward-carry`: "The CodeQL delegation carry is done in this PR, so the orchestrator drops it from that group."
- Measured: at #2406's head d1becac2b (origin/fix/r10-roster-fastpath), `tools/pr/codeql_scope.py:93` is `return _closure().changed_between(base, head, cwd=cwd, env=env)` (`ev/codeql_scope-at-2406-d1becac2b.txt`). The carry's own precondition ("after #2405 and #2406 both merge") is therefore the state in which its work is already done.
- So this carry contradicts the newest review it came from. It would dispatch the R10-TICK-DRIVERS seat to repeat the work #2406 lands. Remedy: drop that carry from R10-TICK-DRIVERS (roster_edit.py), or restate it as a check that the delegation landed with #2406. Then cite #2406's round-4 review as the source.

## What holds

- Carries in the roster at this head (step 10; `ev/three-dot.diff`). Every destination the body names exists at this head, every group is at `resume.stage: not-started`, and every carry comes from #2411 or #2406:
  - R10-SAV-COMFORT (new group, `after: R10-SAV-BASELINE`): one carry. It matches #2411's round-1 item 2 and round-2 review figure for figure: null 10.83 % head / 43.66 % base; gap 13.9 kWh (128.4 / 114.5); comfort 6.6 kWh, about 5 points; room 18.79 vs 20.44 C; timing +17.27 %; stored +23.7 kWh_th / about 13.3 kWh_e; `const` arm timing +0.00 %, gap 15.6 = 5.1 + 10.1; summer_dhw_only -12.74 % / -3.17 %, 1.95 % at the caps, away_setback 60.71 %.
    - It carries its control (the `const` arm), states the acceptance as a precondition (comfort matched, `const` arm settled reads about 0, the varying arm reads the timing term, not 0), and gives a re-measure instruction.
    - It closes round-1's carry-missing for O13 with an in-tree destination.
  - R10-ADVISOR: the restated null, which carries the `const` arm as its control and stored-heat settlement as its precondition, plus the row semantics. Both match #2411 round 1 items 1 and 2.
  - R10-SCORES: the row semantics. This matches round 1 item 1 ("the R10-SCORES and R10-ADVISOR roster briefs do not hold the row semantics").
  - R10-TICK-DRIVERS, first carry: the state-docs beat restart. It carries its control (the memo holds two SHAs, and a roster-only commit regenerates within one beat) and its precondition (after #2406 merges). This matches #2406 round 2 and round 3.
- `node tools/policy/brief_lint.mjs` (the default run, at the head): rc 0, `TOTAL: 0 error(s) across 47 file(s)`. Its ERROR lines all come from `tools/policy/fixtures/*`, the negative controls it expects (`ev/brief_lint.txt`).
  - Instrument finding, not this PR's (the same code is on main): the default run never reads `dev/programme/rosters/`. `workflowFiles` lists only `.claude/workflows` and `dev/programme/carries`, so the default rc 0 says nothing about `wave-r10-groups.json`. `brief-citations.md` also still names `.claude/workflows/wave-*-groups.json` as the roster path.
  - Run on the roster by name, `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` gives rc 0 and `TOTAL: 0 error(s) across 1 file(s)` at the head, the same as at the merge base. The one warning (R10-RCA-FRICTION, `fix-review.md:29`, no anchor) is present at both ends (`ev/brief_lint_r10_head.*`, `ev/brief_lint_r10_base.*`).
  - CI's `briefs` job is green.
- Step 13: `git merge-tree --write-tree origin/main(106af95a3) c83ae12ac` exits 0 with empty stderr (tree a115167503ac). There are no `MERGE-CLAIM` lines because neither claim file is touched (`ev/merge-tree.*`).
- Step 11: the check-runs API at this head shows 43 runs, all completed: 26 success, 16 skipped, 1 neutral (CodeQL) and 0 failures (`ev/checkruns-head.txt`). The body's `## Red checks: none` holds at the head. pr-contract is green.
- Step 5: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`ev/version-untouched.txt` is empty). Steps 1 to 4, 6, 14 and 15: n/a. The diff is roster state plus this PR's delivery row, with no production, test, budget, closure or claim file.
- Step 7: the body names c83ae12ac as the head, and it is the head.

## Not blocking

- The R10-SAV-COMFORT carry writes "gap 15.6 = comfort 5.1 + start drawdown 10.1". The parts sum to 15.2. #2411's round-2 review noted that the `const` arm closes only to 0.4 kWh. The carry should say "about" or name the 0.4 kWh residual.
- #2406's round 3 notes that the beat restart is an orchestrator action gated behind R10-TICK-DRIVERS's `after: R10-REF-PRIVACY`. A post-merge beat item would reach it sooner. That is not carried here.
- `origin/handoff/audit-r10-roster` has moved past 97344315a (9a487b732, R10-ARCHSCORE-COVERAGE for #2415). Those commits are not in this PR's head and were not reviewed.

## Not verified by me

- No figure in the carries was re-measured. They are checked against the source review comments, not re-derived (step 8). The harnesses' evidence directories are out of tree.
