Fix review: blocked 0c563c12e1ace15d5e2c73dc0a19f9fca1953f2b ci-unconcluded: pr-contract never read the body at this head (GitHub API rate limit); five other red checks hit the same limit and three jobs were still running at 06:33Z

bus-nonce: b3556ac8bcb1d8243375ea138f87fe38

## Block

The roster content passes every check below. The PR is blocked only on CI state at this head. That state is outside the diff, and re-running the jobs clears it with no code change.

- `pr-contract` (job 119675443456) is red. Its first step, "Read the body off the API", got `gh: API rate limit exceeded for installation (HTTP 403)`, so `/tmp/pr-body.md` never existed. The figure lint, the preflight and the carry_audit steps all failed reading that missing file. No body check has run at this head.
- `arch-score` (both jobs 119675393295 and 119675399560) and `validate-hacs` (119675441309) failed on the same rate limit (`GitHubRatelimitException` / HTTP 403). `env-matrix` (119675679118) failed one outcome of 16: `pr / nothing skipped in a full clone -- the GitHub API is unreachable`. `nightly-status` (119675836542) printed `NIGHTLY UNREADABLE ... HTTP 403 (rate limit exhausted)`.
- `closures`, `fast (3.14)` and `instrument-self-tests` were `in_progress` at 06:33:19Z.
- fix-review.md step 11 posts `root-cause-unanswered` only after all of the head's workflows conclude and a `pr-contract` run that started after the last red checks the body. Neither has happened, so I am not blocking on that class. I am also not returning `merge` over a required body check that never ran. The body's `## Red checks` reads main's tip, not this head, and could not answer these reds, because they appeared after the body was written.
- To clear: once the rate limit resets, re-run the failed jobs at this head (no new commit is needed). If `pr-contract` then reads the body green and the other checks go green, this verdict's content checks still hold, because the head has not moved. Any red that remains owes a body answer under step 11.

## Findings

- R10-RCA-FRICTION goes to `stage: done` at 3976515a, but its `resume.next_step` still says "dispatch a fixer once every after group is done". Its `resume.note` still says "Owed: merge current main, re-take the body and open the pull request". Both are left over from the in-progress stage. `stage` and `commit` are the fields the tooling routes on, and both are correct. Carry: dismissed: descriptive history text only; stage and commit are correct and brief_lint passes; a later roster op can tidy it, and it does not justify another round on this PR.
- brief_lint's path:line check is anchor-text only. A planted citation `coordinator.py:1083` lints clean (`ev/mutant_1083.txt`, TOTAL 0 errors), but line 1083 is in a different function. So the lint does not prove that the repaired citation lands in `_scores_view`. I checked that by hand: line 10309 is inside `_scores_view` (def at 10299). Carry: dismissed: a known limit of an anchor-text lint; the body itself states 1083 is the wrong function, and the citation this PR writes is correct.

## Evidence

- HEAD reviewed: `0c563c12e1ace15d5e2c73dc0a19f9fca1953f2b` (ev/HEAD.txt). At 06:33Z it was still the head of `fix/audit-r10-roster-8`. origin/main is `16a8240f179d8a6a1ecaae2b284f6ec5a0f04eab`, which is also the merge base, so the branch is 0 behind. This is review round 1.
- Roles contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Roster diff against main (ev/roster_diff.json, ev/changed_groups.diff): 144 groups at main, 147 at head. The 3 new groups are R10-RCA-FRICTION-RESIDUE (issues 2428, 2429, 2436, 2437, 2438 and 2593), R10-NIGHTLY-PYSPY-RETRY and R10-TRAIN-OVERLAP-GRADE, each `queued`. None removed. Five groups changed, exactly as the body lists:
  - R10-SCORES: the only change is the citation `coordinator.py:10293` → `coordinator.py:10309`.
  - R10-RCA-FRICTION: stage done at commit 3976515a08228598ea3863f4f36dc4c7c4846865, and issues 2428, 2429, 2436, 2437 and 2438 removed (five unwired; they reappear on the RESIDUE group).
  - R10-FLOW-DESIGN-POLICY: stage done at 6077bf70e.
  - R10-FLOW-BOARD: one carry appended (orchestrator_tick owner-gate count under a mandate).
  - R10-FLY-GH-READ-RETRY: one carry appended (PR 1's proof owed by PR 2 and PR 3, control r10_gh_read_retry_mutants.py, 17 survivors at fd1e3f6c and 0 at 37cffb09).
  - R10-TRAIN-OVERLAP-GRADE carries #2595's RCA item as its one carry.
  - Top-level keys other than `groups` are identical. The group order is unchanged apart from the three groups appended. No other roster op is present. The second file is the delivery row `dev/programme/delivery/2598.md` (1 line).
- Body figures re-derived: null control `git diff --exit-code origin/main 306a96d5f -- <roster>` rc=0. `306a96d5f..562015181` is 15 commits, 1 file, 146 insertions and 13 deletions. Groups 144 → 147. 3 new, 0 removed, 5 changed. The PR shows 147/13 over 2 files, which is the 146/13 roster diff plus the 1-line delivery row (ev/git_checks.txt).
- Done SHAs: 3976515a (merge of #2561) and 6077bf70e (merge of #2586) are both ancestors of origin/main.
- R10-FLOW-DESIGN-POLICY checklist at 6077bf70e, all six items met:
  - (1) `designer.md` and `design-review.md` exist under dev/governance/roles/.
  - (2) orchestrator.md lines 129-133 dispatch the designer when the last predecessor dispatches, the design reviewer at the design's head, and the fixer only after `Design review: approve`. The approved note is the architect note.
  - (3) fixer.md step 17 says "architect note followed; a departure is raised, not made".
  - (4) fix-review.md step 15 says "from the architect or approved design note".
  - (5) CLAUDE.md lines 118 and 119 name both contracts.
  - (6) decision 0014 exists. 0012 reads "Status: Revoked 2026-10-21" and "Revoked by decision 0014-...".
  - policy_budgets.json `corpus_tokens` went from 61026 to 62892, plus per-file caps for both new files.
- R10-SCORES citation at origin/main: `ctx._thermal_params.heat_loss_coefficient` is at coordinator.py:10309, inside `_scores_view` (def at 10299). Line 1083 is in a different function (a two-zone helper that returns `params.heat_loss_coefficient`).
- brief_lint: `node tools/policy/brief_lint.mjs` at head with no argument gives TOTAL 0 errors across 47 files (ev/brief_lint.txt). That default set does not include the r10 roster, so I ran it on the roster explicitly: `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` gives TOTAL 0 errors and 1 warning (R10-PLAN-ARTIFACT plan.json, also present on main) (ev/brief_lint_r10.txt). Main's roster gives 1 error: R10-SCORES `coordinator.py:10293`, `heat_loss_coefficient` not found near there (ev/brief_lint_main_roster.txt). That confirms the body's statement that this was the refusing error.
- carry_audit over the body: `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt), run on the body as fetched over REST (ev/body.md), because `gh pr view` hit a GraphQL 403 (ev/gh_err.txt).
- merge-tree: `git merge-tree --write-tree origin/main 0c563c12e` exits 0, tree 92edf10dcb333d8bc76d453c616534294af27182, no conflict (ev/merge_tree.txt).
- Mutation proof: n/a. There is no production or test code. VERSION, the manifest version and the notes heading are untouched; CI's pr-contract version-edit step printed "no version edit".
- CI at head, read twice from the check-runs API (ev/check_runs_head.tsv at 06:32:20Z, ev/check_runs_head_2.tsv at 06:33:19Z): 16 success, 17 skipped, 1 neutral (CodeQL), 6 failure (pr-contract, arch-score ×2, validate-hacs, env-matrix, nightly-status) and 3 in_progress. I read the job logs for all six failures (ev/red_job_logs.txt), and every one is a GitHub API rate-limit 403. nightly-status's own log says it is not one of the required contexts on `main-protect` and does not block a merge.
- Not re-derived: the body's account of main tip 16a8240f1's check-runs at its own read time. Those runs have since changed, and the block does not depend on them.
