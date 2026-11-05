R10-RAISE-GATE-SHIM (issue 3128), repair round 4: the round-3 fix review blocked on `body-stale` (the body described code head `289fe24b`, not the deny-by-default shim). This body is retaken whole for the head below, and the three cheap findings the review measured are closed in the code.

Closes #3128

## Head

Code head `88d809f841a1fadc7ccdb34badc142dc65ef522e` (`handoff/r10-raise-gate-shim`): the PR head `6b416a18fc8752eaa3c10404cec43f896df3ed60` plus three commits of this repair, merged with `725410a6b` (the round-3 seat's commit already on `handoff/r10-raise-gate-shim`: `queue_pre_flight.py`'s self-test answers the train's measured score, three added lines; kept so the handoff ref stays a fast-forward). `6b416a18` merges the authored code head `6027fe3e`, which carries `1d4ed28e4`. `origin/main` is `8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc` (`git fetch origin main && git rev-parse origin/main`, 2026-11-05) and equals the merge base (`git merge-base origin/main HEAD`), so main had not moved and no merge was needed.

The shim under review is `1d4ed28e4`: `tools/audit/seat/shims/seat-gh` carries a deny-by-default `gate()` over `api_gate`, `issue_gate` and `pr_gate` (there is no `api_hits`). A call that could write a comment on the tracking issue (#201) is refused unless the caller is python running the tree's own `tools/pr/gh_comment.py` by real path, or the call is on gh's own explicit table of calls that cannot write one: reads, `issue view/list/status/create`, `issue comment/close/...` on one plain number other than 201, `pr` with no word reading 201, `api` reads, `api` writes at paths that are neither `issues/201/comments`, `issues/comments/<id>`, an unreadable path nor a graphql mutation, and the command groups with no issue-comment surface. Everything else (an unknown subcommand, an alias, an extension, an unknown flag) is refused.

This repair changes three things on top of `1d4ed28e4`:
1. `norm()` lower-cases the api path before matching, so `repos/o/r/ISSUES/201/COMMENTS` is the tracker's (review finding: the case gap).
2. The kill word is built from fragments at runtime in `gh_calls.py` (the `planted` argv and the `gh issue comment 201` refused row) and the id is the fixture id `fixture-mandate-0000`, replacing the fake numeric id.
3. `seat_venv.sh --self-test` has a row for the installer's `gcpy=` bake (review finding: the surviving installer mutant).

No budget file, claim file, `VERSION`, manifest version or `RELEASE_NOTES.md` is touched.

The brief's four carries and where each stands:
- Carry 1 (the mandate-revoke fixer's gaps): (a) a raw `gh api` or `gh issue comment` post to #201 is refused by the shim (`1d4ed28e4`, this PR); (b) merge_train and `--check-body` check the dS value (landed in round 1; mutants M2 to M4 of the review kill it); (c) is Carry 3.
- Carry 2 (the value check re-routed from #3045): built as (b) above and unchanged by this repair.
- Carry 3 (item 870f6b21, `(c)` measured, no change needed): the `budget-raise-gate / budget-raise-gate` job against its 5-minute timeout. The round-3 seat's measurement over 31 jobs (min 19 s, median 28 s, max 48 s) is carried as it stands; this repair adds two more runs read at `6b416a18` (jobs 127348404149 and 127322514552, 29 s and 25 s). The scorer's cost on a raise diff stays unmeasured (no raise diff runs it).
- Carry 4 (item aae60647, `exec -a` argv0 spoofing): the declared residual, under Forward-carry.

## Mutation proof

All counts are `python3 tools/audit/seat/gh_calls.py --self-test` at the head, `195 checks, 0 failed`.
- Predicate `[ -n "$ok" ] || {` changed to `true || {` in the shim (the refusal never fires): `gh_calls self-test: 195 checks, 67 failed`; restored, 0 failed. (The reviewer measured 190 checks, 65 failed at `6b416a18`; the difference is this repair's own rows.)
- The lower-casing line in `norm()` deleted: 4 failed (`gh api an upper-cased issues segment is refused`, `gh api an upper-cased comments segment is refused`, `mutant killed: path segments not lower-cased` and its `(comments segment)` twin); restored, 0 failed.
- The installer's bake line in `seat_venv.sh` (`[ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l=...`) replaced by `:`: `seat_venv self-test: 27 checks, 1 failed` (`FAIL --install-shims bakes the tree's gh_comment.py path into the installed gh shim`); restored, 0 failed. The same mutation left 25 checks, 0 failed before this repair.
- The in-suite `guard_mutant` rows of `1d4ed28e4` (each kills one rule of the guard) are unchanged and pass.

## Null control

- A post to another issue with upper-case segments (`repos/o/r/ISSUES/202/COMMENTS`) reaches the real gh (stub rc 7), so the lower-casing refuses only the tracker. The existing nulls (GET of #201, posts to 202 and 2011, dot segments to 202, `%`-encoded 202, `issue comment 202`, `issue view 201`, an api read with Accept, a non-issue path write) still reach the stub.
- The unmodified shim at `6b416a18` lets both upper-case spellings reach the stub (the review's measurement); the deleted-lower-casing mutant reproduces it.
- The source `seat-gh` carries the `gcpy=@HPO_GH_COMMENT@` placeholder, asserted by its own row (the bake row's null control).
- **No control wrote to GitHub.** Every shim control ran against the self-test's local stub `gh` (exits 7, no network call); the refused rows assert the stub never ran. The only mandate id in tests is the fixture `fixture-mandate-0000`. The kill word appears whole in no added line: `git diff origin/main...HEAD | grep '^+' | grep -ci 'revok'` prints `0` (it printed 2 at `6b416a18`: the `planted` argv and the `issue comment 201` row).

## Figures

- `python3 tools/audit/seat/gh_calls.py --self-test`: `gh_calls self-test: 195 checks, 0 failed` (190 at `6b416a18`).
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `45 checks, 0 failed` (the merged `725410a6b` change).
- `bash tools/audit/seat/seat_venv.sh --self-test`: `seat_venv self-test: 27 checks, 0 failed` (25 at `6b416a18`).
- Mutants: predicate `true || {`: 67 failed of 195; lower-casing deleted: 4 failed; bake replaced by `:`: 1 failed of 27 (commands under Mutation proof).
- `git diff origin/main...HEAD | grep '^+' | grep -ci 'revok'`: `0`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `scope.run` named `tests/entities.py`, run with `PYTHONPATH=tests/hastub`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget raise.
- Claim files, `VERSION`, manifest, `RELEASE_NOTES.md` and every `*_budgets.json`: `git diff origin/main...HEAD --quiet -- <file>` exits 0 for each.
- Seam enumeration (step 8): the class is "a #201 comment write spelled so the shim cannot read the tracker". Instrument: the self-test's `refused` table plus the review's offline controls (33 of 38 refused as required). Seams returned and dispositions: upper-case path segments (closed here); PATCH of a comment by id, graphql mutations and `gh pr comment` (already refused at this head: rows `a PATCH of a comment by id`, `a graphql mutation`, `gh pr comment 201`); PATCH of `issues/201` (an issue body, not a comment; not read by the gate); `pulls/201/comments` (#201 is not a PR); `exec -a` (the residual under Forward-carry).
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` read `OK`; `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` printed `2.5.4 1.18.1`, equal to `tests/requirements-ci.txt`. No golden or solver measurement is in this diff.
- `tools/pr/prepr.sh <body>` at `88d809f8` (detached, committed tree; main unmoved since the last run): `PRE-PR: 88d809f841a1... rc=0`; `ci predict`: no red predicted; claim files byte-identical to origin/main.

## Red checks

Read with `get_check_runs` on PR #3223 (55 check runs, one page of 100) at the PR head `6b416a18`, base `8bf45e5dc`. The three commits of this repair have no runs until the PR head moves; they are retaken then. Concluded reds, all in run 42049714711:
- `governance / instrument-self-tests` (job 127322514778): every self-test step visible in the log passes (`local_alerts self-test: 0 failed`, `ALERT-LIST MUTANTS: every mutant refused`). The `alert_list self-test: 25 checks, 12 failed` style lines are printed by `alert_list_mutants.sh` by design (its expected outcome is "every mutant refused", each mutant must fail the self-test) and are not a red. The log the API returns holds no failing step, so the cause is not established from it; this diff touches no `tools/ci/` file. Carry: R10-RAISE-GATE-SHIM
- `governance / delivery-status` (job 127322514659): the log ends with `overdue` rows of other PRs (`#3206`, `#3189`, `#3204`, ... `#3192`, 21 to 30 commits since) and "This check is NOT a required context"; exit 1. Cause: other PRs' delivery rows on main at base `8bf45e5dc`; this diff adds only its own row. Inherited.
- `tests / nightly-status` (job 127322514282): `NIGHTLY FAILED: slow failed last night` (scheduled run 41943946464, head `499162c`, job `slow`); not a required context. Cause: a nightly lane on main outside this diff's closure. Inherited.

- `arch-score / arch-score`: red on this PR earlier, in run 41988495065 (job 127126421625) at the older head `e7126ae2`, and green in the two other runs of that head; at `6b416a18` both runs are green (jobs 127348403633 and 127322514610). This diff changes no scored module (a shell shim, a tool, an instrument note), so the flip is not this diff's. Cheaper detector: none known, standing cost nil; cause not established here (a root-cause seat owns it). Not turned by this branch.

- `budget-raise-gate / budget-raise-gate`: named by the ancestry read as red on an earlier head of this PR (the round-1 and round-2 heads, whose guard and body were different code); at `6b416a18` it is green in both its runs (jobs 127348404149 and 127322514552, 29 s and 25 s). This diff raises no cap, so the job's scorer path is not exercised. Cheaper detector: none known (the job is the detector), standing cost 25 to 30 s a run; cause of the earlier reds not re-read here. Not turned by this branch at this head.
- Code-scanning alerts could not be read from this seat (`code-scanning/analyses`: HTTP 403 through the proxy); the `CodeQL` and `codeql / Analyze` check runs at `6b416a18` are green (14 checks listed, none red).

`pr-contract` and `gate` are green at that head. No red here was turned by this branch.

## Forward-carry

- Residual, by design: the caller test reads `ps` args, which a caller writes, so an `exec -a` spoof of the parent (a process naming `gh_comment.py` as its own argv) passes the guard. The shim is a guard against a seat's habit, not an adversary (declared in the shim and the instrument note). Carry: R10-RAISE-GATE-SHIM
- `score_check` accepts a `## Raise justification` that quotes a wrong figure beside the measured one (predates this PR). Carry: R10-RAISE-GATE-SHIM
- The shim guards only a `gh` found on PATH (an absolute `/usr/local/bin/gh`, curl with a token and `tools/pr/app_comment.sh` bypass it). Carry: dismissed: the brief scopes the guard to the seat shims and the note calls it a habit guard, not a boundary.
- Carry (c), the `budget-raise-gate` job's 5-minute timeout against the scorer on a mandated path: not measurable by a seat with no CI runner (29 s on this diff, which raises no cap). Carry: dismissed: the orchestrator reads the job's duration from the next raise PR's run.

## Friction

none
