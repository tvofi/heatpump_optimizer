Fix review: blocked 6b416a18fc8752eaa3c10404cec43f896df3ed60 body-stale: the body describes code head 289fe24b, not the deny-by-default shim of 1d4ed28e4 at this head; its figures (146 checks), residual (PATCH, graphql, pr comment passing) and its no-literal claim are false here

bus-nonce: 5d0e85b0e5867ed57476b4154d6d7e36

## Block

Measured head: `6b416a18fc8752eaa3c10404cec43f896df3ed60` (PR #3223, R10-RAISE-GATE-SHIM, issue #3128). It was dispatched as a first-round review. The body itself records an earlier round-1 block, so by the PR's own history this is round 2. It is not the fourth round, so no re-cut is owed.

The code at this head is sound in the main: every offline control I planted behaves as the brief requires (Evidence). The body is the problem. It is the record the owner's approval reads, and at this head it describes a different code head. The body's `## Head` names code head `289fe24b`. But `6b416a18` merges `6027fe3e`, which carries `1d4ed28e4` ("seat-gh denies by default ..."). That commit rewrote the guard (+221/-57 lines in the shim, `gh_calls.py` and the instrument note), and the body never describes it. As a result, at this head:

- **The figures are wrong.** `gh_calls.py --self-test` prints `gh_calls self-test: 190 checks, 0 failed`. The body's Figures and Mutation proof quote 146, and "146 checks, 38 failed" for the predicate mutant. My re-run of that mutant (`[ -n "$ok" ] || {` changed to `true || {`) gives `190 checks, 65 failed`. The body's quoted numbers cannot be re-derived at this head (fix-review step 8).
- **The design description is wrong.** The body describes an `api_hits()` normaliser and a list of spellings. The head has no `api_hits`. It has `api_gate`/`issue_gate`/`pr_gate` under a deny-by-default `gate()`.
- **The declared residual and its forward-carry are inverted.** The body says PATCH of `issues/comments/<id>`, graphql mutations and `gh pr comment` still pass. It dismisses them under `## Forward-carry` ("names no issue the shim can read"). At this head all three are refused: my offline controls, plus the self-test rows "a PATCH of a comment by id", "a graphql mutation" and "gh pr comment 201". The head's instrument note declares a different residual: an `exec -a` parent spoof. The body never mentions it.
- **The body's no-literal claim is false.** The body says "The mandate id appearing in tests is the fixture `fixture-mandate-0000` and the kill word is never written whole in a file". The diff adds `fixture-mandate` 0 times. It adds the kill word whole, paired with the fake numeric id 1234567, in `gh_calls.py`. That is two lines: the `planted` argv and the `gh issue comment 201` refused row. 1234567 is not a mandate id (real ones are 10-digit comment ids), so no live mandate is at risk, but the body's statement is untrue.
- **The `## Red checks` section answers the runs of `e7126ae2`.** It says so itself. It names base `dad3178d`, not this head's base `8bf45e5dc`. It attributes `instrument-self-tests` to "alert_list 25 checks, 5 failed". At this head, job 127322514778's `alert_list.py --self-test` step reads `25 checks, 0 failed`. The "5 failed" lines are inside `alert_list_mutants.sh`, whose expected outcome is `ALERT-LIST MUTANTS: every mutant refused`. The `pr-contract` run 127349151366 (started 15:40:19Z, after the last red concluded at 15:22:16Z) is green, so step 11's trigger is formally answered. The account it accepted is still stale.

Repair: a body-only edit, unless the fixer takes up the findings below. Describe `1d4ed28e4` as the shim under review. Re-take the figures at the head: 190 checks, the mutant counts, and the control list now that PATCH, graphql and pr comment are refused. Replace the residual with the head's `exec -a` residual and carry it properly. Correct the no-literal sentence, or build the planted body from fragments as the brief requires. Re-answer `## Red checks` from this head's runs, naming base `8bf45e5dc`.

## Findings

- Follow-up: a path-segment case gap in the shim's api arm. `gh api repos/tvofi/heatpump_optimizer/ISSUES/201/comments -f body=x` and `.../issues/201/COMMENTS` reach the real gh (offline stub recorded the argv, ev/controls-head.txt). `api_gate` compares `issues`/`comments` case-sensitively, and a write to an unknown path passes by design. I could not check whether GitHub routes an upper-cased segment: the proxy answered 403 to unauthenticated reads, and the brief allows no live write. So this is plausible, not confirmed. It belongs to the same class the round-1 review blocked on (an unnormalised spelling). The fix is cheap: lower-case `NSEG` before matching. Carry: R10-RAISE-GATE-SHIM
- Follow-up: a surviving mutant in the installer. Replace `seat_venv.sh --install-shims`'s bake line (`[ "$l" = 'gcpy=@HPO_GH_COMMENT@' ] && l="gcpy=..."`) with `:`. Then `seat_venv self-test: 25 checks, 0 failed` and `gh_calls self-test: 190 checks, 0 failed`: nothing fails (ev/mutants.txt M5). Without the bake, an installed shim has an empty `gcpy`, so every `gh_comment.py` post to #201 on a seat is refused. That fails closed, but it would break the sanctioned posting instrument with no test noticing. A real install today does bake the line (`gcpy=/home/user/wt/tools/pr/gh_comment.py` in the installed copy). Carry: R10-RAISE-GATE-SHIM
- Follow-up: `score_check` accepts a section that also quotes a wrong figure. A `## Raise justification` holding both `Architecture score: dS +0.0012 IMPROVES` and the measured `dS +0.0000 NULL` passes `justified` and `check_body` (ev/ds-head.txt, body3045-both.md), because the test is "measured figure in the set of quoted figures". This predates this PR (`score_check` is on main), but the PR extends the same predicate to merge_train and `--check-body`. Carry: R10-RAISE-GATE-SHIM
- Out of scope: the shim guards only a `gh` found on PATH. `/usr/local/bin/gh` called by absolute path, curl with a token, and `tools/pr/app_comment.sh` (curl POST to `issues/$pr/comments`) all reach #201 without it. The brief scopes (a) to the seat shims, and the instrument note calls the shim a guard against habit, not an adversary. Carry: dismissed: the brief scopes the guard to the gh shim, and the instrument note declares it a habit guard, not a boundary
- Follow-up: carry (c), the budget-raise-gate job's 5-minute timeout against the scorer on a mandated path, is unmeasured. The body dismisses it to the orchestrator. At this head the job ran 29 s (run 42049714447, 15:39:04 to 15:39:33Z) on a diff that raises no cap, which is not the mandated path. Carry: dismissed: no seat without a CI runner can measure it, and the body routes it to the orchestrator's next raise-PR run

## Evidence

- RESULT head-measured 6b416a18fc8752eaa3c10404cec43f896df3ed60. The base is the merge base `8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc` = origin/main. `git diff <base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- RESULT merge-tree `git merge-tree --write-tree origin/main 6b416a18` rc=0 (tree ec977db65e98), no conflict.
- RESULT claim files, VERSION, manifest, RELEASE_NOTES and every `*_budgets.json` are byte-identical to origin/main (three-dot diff empty). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- RESULT self-tests at head: gh_calls 190 checks, 0 failed; seat_venv 25 checks, 0 failed; budget_raise_gate 274 checks, 0 failed; merge_train 443 checks, 0 failed (ev/selftests-head.txt).
- RESULT offline arm proven before any control. `env -i HOME=<empty> PATH=<shim>:<stub>:<symlinked tools>`. `type -a gh` lists only the shim and the stub; `/usr/local/bin` is not on PATH. `env | grep -i token` is empty. A harmless `gh --version` was recorded by the stub (ev/mkenv.sh, ev/run.sh). No control wrote to GitHub. The kill pairing used the fixture id `fixture-mandate-0000`, with the word assembled from fragments at runtime (ev/controls.py). Evidence files redact the word as `<W>`.
- RESULT controls at head: 33/38 as I predicted (ev/controls-head.txt). These are refused with an empty stub log:
  - the planted raw `gh api -X POST .../issues/201/comments` with the kill pairing, both from a python and from a bash parent;
  - trailing slash, full https and http URL, leading slash, `{owner}/{repo}`, `--method POST` with no field, `-F`, `--field=`, `--input` file and stdin;
  - graphql mutations (lower and upper case, `-F`, `--raw-field=`);
  - `gh issue comment 201` with `--repo`/`-R`/`--repo=` before or after, and `-R` before the subcommand;
  - `+201`, `0xC9`, an alias word, `gh pr comment 201`;
  - two parent spoofs: `-c` code naming the script, and `-m runpy`.

  Null controls reach the stub with their argv: GET of #201's comments, a post to #202, `issue comment 202`, `pr view`, and a graphql read query. Of the five mismatches against my prediction, two are open questions: PATCH of the issue at `issues/201` (an issue body, not a comment, so not what the gate reads) and `pulls/201/comments` (#201 is not a PR). Two are the case gap under Findings. The fifth was my own setup: `gh_comment.py` refused a body file under /tmp as a shared root.
- RESULT control: a normal post through `python3 -I tools/pr/gh_comment.py post --repo tvofi/heatpump_optimizer --issue 201 --body-file <own dir>` reached the stub. Its argv was `api /repos/tvofi/heatpump_optimizer/issues/201/comments --method POST --input /tmp/gh_comment_*.json`, then the read-back GET. The read-back mismatch is the stub's canned body (ev/control-gh_comment-head.txt).
- RESULT dS value arm, files only (ev/ds-head.txt). The #3045 round-1 body is not in the tree at 0ec244aa: that commit holds only the verdict, which quotes the body's `Architecture score: dS +0.0012 IMPROVES`. So the planted body is #3045's final `## Raise justification` with its score line set to the round-1 figure. With the measured figure `dS +0.0000 NULL`, `justified` refuses it ("claims dS +0.0012 IMPROVES, but ... measures dS +0.0000 NULL"), and `check_body` with a raise refuses it. The measured-figure body passes. With no raise, `check_body` shape-checks only (by design). This is my own reconstruction, not the finder's file.
- RESULT mutants at head, in a copy with the same offline stub (ev/mutants.txt):
  - M1, the shim refusal disabled: gh_calls 190 checks, 65 failed; my controls 6/38, and the planted post reaches the stub. Killed.
  - M2, merge_train back to `justification` (shape only): merge_train 443 checks, 1 failed ("a mandated raise whose body quotes a dS the scorer did not measure stops"). Killed.
  - M3, `check_body` shape only: budget_raise_gate 274 checks, 1 failed. Killed.
  - M4, `--check-body` passing no scorer: 274 checks, 1 failed. Killed.
  - M5, the installer bake removed: survives (Findings).
- RESULT no existing guard is weakened. `gh_comment.py`'s mandate guard and every self-test are unchanged and pass. The only pre-existing shim test edited is the `--input` skip mutant, re-pointed at the new skip line. Seat-host production writers to #201 (scout inventory): only `tools/pr/gh_comment.py`, which passes. `nightly.yml:960` posts by curl from Actions, so the shim never sees it.
- RESULT CI on this head: `merge_train.py classify 6b416a18... --pr 3223` returned `GREEN 6b416a18fc8752eaa3c10404cec43f896df3ed60 pending: none red: none` (rc 0, 15:42:05Z; ev/classify-final.txt).
- RESULT check runs at head: 55, one page of 100, read via get_check_runs. Three concluded red; none is a required gate (gate jobs 127349688309 and 127348288767 are green):
  - `governance / instrument-self-tests` (127322514778): no failing step is visible in the log the API returned.
  - `governance / delivery-status` (127322514659) and `tests / nightly-status` (127322514282): main-ancestry reds whose reads this diff does not reach. The diff adds only its own delivery row.

  `pr-contract` is green in runs 127347567197 and 127349151366, both started after the last red concluded. `budget-raise-gate` and `arch-score` are green.

## Friction

- The brief asks for a handoff-wip push at each milestone and a return "by bus.sh push-verdict". The dispatch prompt says to push nothing but the probe ref and not to run bus.sh. I followed the dispatch prompt.
