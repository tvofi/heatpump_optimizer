R10-OUTSIDE-INTAKE. The owner's ruling (tvofi 2026-11-06), verbatim: "the plan html for an ongoing round should be made publically available from a suitable place in the developer documentation on the repo. During future audit rounds, issues, PRs or other posts from outside users should be regularly checked, triaged/designed and planned. Fold this shape into the repo machinery. When the plan html is done, and any outside submission is on the roster, the plan HTML should be linked in an answer to the outside submission."

**Policy and developer docs change: this merges only on tvofi's approving review** (`orchestrator.md` section 5, `standing-dispatch.md`, `dev/programme/HANDOVER.md`). The ruling gives approval in principle; the review is the approval.

What lands, by the brief's three parts:

1. **Public plan page.** `tools/audit/seat/plan_public.py stage` takes `PLAN.html` from the newest `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of` owns) and writes `plan/index.html`. `.github/workflows/pages.yml` runs it from the dispatched ref's tree. It then checks out the newest `v*` tag for the docs and adds the page, so the page is served at `https://tvofi.github.io/heatpump_optimizer/plan/` (`plan_public.PLAN_URL`, the one spelling of the URL). The beat's `plan-beat` row dispatches `pages.yml` on `main` after each state push that landed, so the page refreshes at each sweep that moved the plan. The developer docs link it from the head of the Round 10 section of `dev/programme/HANDOVER.md`; no user doc links it. A page `ref_privacy` reads a host path, account name, uid, scratch root or a tool's attribution in is refused (rc 1, red deploy, nothing published). Between rounds there is no state ref (rc 2): the site deploys without a plan and warns.
2. **Intake as machinery.** `tools/audit/seat/outside_intake.py list` lists threads (issues, pull requests, discussions, one number space) with activity at or after a cursor by an author outside `OURS` and not a bot. It prints the `OUTSIDE #N owed=triage|answer|reply` lines owed this turn. Disposition is read from the roster (`issues`/`fixes`, wired by `roster_edit.py wire-issue`) and from marker comments by our accounts, never from memory. A new beat row, `outside-intake` [1800 s], runs it with a cursor under the digest's `state/` and writes its lines to the digest the sweep reads. Sweep step (5b) in `sweep_template.md` names the action per line. `orchestrator.md` section 5 and `standing-dispatch.md` each carry the short obligation.
3. **Answer step.** `outside_intake.py answer --issue N` posts the plan link through `tools/pr/gh_comment.py post`, whose read-back is the proof. It marks the comment (a marker is read only from a comment by an account in `OURS`; a third-party bot's is neither ours nor outside activity), and refuses a thread already answered or refused, so none is answered twice. It also refuses a thread on no roster group, one while the plan page does not answer, and a discussion. `refuse --issue N --reason-file F` records a refusal the same way.

Alternatives, and why each lost (`fixer.md` step 17):

- **A committed path under `docs/`.** It would need a commit to `main` at every sweep, each a pull request through the gate, for a generated file.
- **Pages from a push to the state ref.** Workflows run from the pushed commit's own tree, and the orphan state ref carries no `.github/`, so a `push:` trigger there never fires.
- **A `schedule:` trigger.** It runs 48 deploys a day whether or not the plan moved, and it changes the trigger set `tests/entities.py` pins to release tags plus dispatch.

The dispatch keeps that pinned set. One existing behaviour changes: a dispatch now serves the newest release's docs rather than the dispatched ref's. That matches the workflow's stated design ("the served page is the release HACS installs") and keeps a plan refresh from publishing main's unreleased docs. The owner may prefer otherwise; this is the change to review.

## Head

`296bc921d0023a52d194c1f8d16d5afa418c098f` is the head everything below was measured at, unless a line names another. It is the PR head `48acc104f97cf88bf0ec28a3f6ec01438e169bb5` with `origin/main` at `f2a015142714383722bf49d7ab20d8398ec9674c` merged in (clean, no conflict; stamped 2026-11-07T02:06Z) and one repair commit for fix review round 1 (blocked, mutation-vacuous). That commit touches only `tools/audit/seat/outside_intake.py` and `tools/audit/seat/outside_intake_selftest.py`.

Round 1 repairs:

1. **The plumbing is pinned.** Two self-test cases now cover it. "main list: ..." drives `main(["list", ..., "--cursor", tmp])` over the fixture world twice, the second pass with a later `--since` that the cursor must override, and once more over the empty world. "post: ..." drives `post()` with a recording runner: it asserts the `tools/pr/gh_comment.py post` argv, the body file, `--dry-run` passed when asked and absent otherwise, and that runner rc 1 comes back as rc 1. Six new mutants pin these lines: `main_cursor_unread`, `main_cursor_now`, `main_list_rc0`, `post_rc_dropped`, `post_dry_dropped` and `post_wrong_script`.
2. **Markers come only from `OURS`.** `Thread.mark` reads a marker only from a comment whose login is in `OURS`. A third-party bot's comment is neither ours nor outside activity. The discussion projection appends the `[bot]` suffix that GraphQL leaves off a bot's login, so our App's marker in a discussion is still read. Without that, the OURS test would have stopped reading our App there. Two mutants pin this: `marker_any_bot` and `graphql_bot_suffix`. The existing `forged_marker_read` mutant was re-targeted to the restructured guard and is still killed.

`tools/pr/prepr.sh` ran at this head: `PRE-PR: 296bc921d0023a52d194c1f8d16d5afa418c098f ... rc=0`, and `origin/main` had not moved from f2a015142714 at the handoff, so no second merge or run was owed.

## Mutation proof

Run with `python3 -I tools/audit/seat/outside_intake.py --self-test`. All 19 mutants in `outside_intake_selftest.py` `MUTANTS` are killed, each by its named case (`ok   mutant <id> killed by: <case>`). A surviving or stale mutant is a failed check. The 8 new ones, with the case that kills each:

- `main_cursor_unread` (the cursor read becomes `pass`), `main_cursor_now` (`{"since": keep}` becomes `{"since": utc()}`) and `main_list_rc0` (`return 1 if lines else 0` becomes `return 0`): killed by "main list: rc 1 with owed lines, the cursor persisted at the earliest owed activity and read back next pass".
- `post_rc_dropped` (`runner(argv); return 0`): killed by "post: a failed gh_comment read-back (rc 1) is a non-zero answer".
- `post_dry_dropped` (drop `+ (["--dry-run"] if dry else [])`): killed by "post: gh_comment.py post is run with the body file, --dry-run passed, rc 0 kept".
- `post_wrong_script` (the script path becomes `tools/pr/gh_comment_missing.py`): killed by "post: ... --dry-run absent, rc 0 kept".
- `marker_any_bot` (the `OURS` test becomes `outside()`, which is the old behaviour): killed by "identity: a third-party bot's marker disposes of nothing (#3225 still owes the answer)". **Failing test first:** at `48acc104` this case fails (`FAIL identity: a third-party bot's marker ...`, rc 1).
- `graphql_bot_suffix` (the suffix is not appended): killed by "discussions: our App's marker is read (GraphQL names a bot without its [bot] suffix)".

**The finder's harness at both ends.** I re-ran the reviewer's mutants from `evidence/reviewer-mutants.txt` on `verdict/3262`, one by one, each applied in place, `--self-test` run, then restored. That is 13 mutants: the 12 lines on file, with the cursor-write mutant run once, plus the script-path line. At `48acc104`, 6 survive with rc 0: cursor read, cursor write, post rc, `--dry-run`, script path and list rc. At `296bc921d0023a52d194c1f8d16d5afa418c098f`, all 13 are KILLED with rc 1. I re-ran the reviewer's marker drive (`evidence/marker-trust.txt`: `Thread.mark` and `owed` on #3225, with one ANSWER_MARK comment):

- `renovate[bot]` (Bot): at `48acc104` `answered='2026-11-06T00:00:00Z' owed=None`; at `296bc921d0023a52d194c1f8d16d5afa418c098f` `answered='' owed=answer`.
- `hpo-approver[bot]` (Bot): `owed=None` at both ends, still disposing.
- `Bankaifan` (User): `owed=answer` at both ends.

The other in-tree mutant sets are unchanged and green: `plan_public.py` has 4, and `beat_jobs.py` has 5 new plus `plan_rc1_silent`. The by-hand mutation of the `tests/entities.py` Pages check in the previous round still stands, because neither `pages.yml` nor that check moved in this round.

**Class rule (step 8).** I enumerated with `grep -rn "ANSWER_MARK\|REFUSED_MARK\|\.answered\b\|\.refused\b" --include=*.py .` (selftest excluded). Only `Thread.mark` writes `Thread.answered` or `Thread.refused`. Every other hit only reads them (`owed`, `dispose`) or defines a marker or projection. Both thread readers, `scan` and `one_thread`, route every comment through `mark`. The class is closed in this diff.

## Null control

- The unmutated self-test runs rc 0 at both ends (`outside_intake self-test: all checks passed`), so each kill above is the mutant's.
- `Bankaifan` (User) still owes the answer and `hpo-approver[bot]` still disposes of it, at both ends (marker drive above).
- `main list null`: an empty world gives rc 0 and prints nothing, so rc 1 is not unconditional.
- At the merge base, `pages.yml` has none of the three plan steps. The entities check returns `a plan step is missing: [...]` over `git show origin/main:.github/workflows/pages.yml` and `[]` over the head. That figure is from the previous round and unchanged.
- No outside activity: `listing` over an empty world prints nothing and moves the cursor to now ("list null").

## Figures

- `python3 -I tools/audit/seat/outside_intake.py --self-test` at `296bc921d0023a52d194c1f8d16d5afa418c098f`: `outside_intake self-test: all checks passed`. That is 25 cases and 19 mutants, counted as the `ok` lines without and with the `mutant` prefix. At `48acc104`: rc 1, `FAIL identity: a third-party bot's marker disposes of nothing ...` once the new cases are applied.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- Scoped scripts: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `ALL 2641 ENTITY CHECKS PASSED` (rc 0). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gives `ALL 112 HARNESS HEADER CHECKS PASSED` (rc 0).
- `python3 -I tools/audit/seat/plan_public.py --self-test`: `plan_public self-test: all checks passed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 136 checks, 0 failed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `120 self-testing, 120 wired, 0 unwired` and `0 index gap(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget moved, and no `*_budgets.json` is in the diff.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` gives `OK python3 is /opt/hpo/venv-ci/bin/python3`, and numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`. No golden was run, because the diff touches none.
- `VERSION`, `RELEASE_NOTES.md`, `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are byte-identical to `origin/main` (`git diff --quiet origin/main HEAD -- <those>`).
- These figures from the previous round are unchanged, because this round edits no file they read: the `policy_lint --budgets` caps on `orchestrator.md` (292/295 lines) and `standing-dispatch.md` (37/39), and the first live intake pass, which printed #3224 and #3226 owed=triage and #3225 waiting on the plan page. I did not re-run the live pass this round. The marker change can only make a thread owed that was disposed before, never the reverse, and that pass printed no disposed thread among #3224 to #3226 to move.

## Red checks

I read every check run at the previous head `48acc104f97cf88bf0ec28a3f6ec01438e169bb5`, all pages, with `filter=all`: 94 runs. Exactly four are concluded reds, all named `gate`: 128203011639, 128206299696, 128215975302 and 128215984338. Each concluded `failure` with `FAIL run(s) [...] at this head are still being judged; their gate decides`. That is the gate's ordering deferral to code runs still in progress at that head, not a defect of the authored code. The last two name each other's workflow runs (42309082852 and 42308039479), which is two gate runs racing. Every other run concluded success, skipped or neutral (CodeQL). The cheaper detector is the gate itself, re-run once the code runs conclude: no new countermeasure is owed. At `296bc921d0023a52d194c1f8d16d5afa418c098f` no check has run yet, because it has not been pushed to the PR. Its reds, if any, are named at the next read.

The earlier local red stands as recorded: `tests/entities.py` "no errexit `run:` block reads `$?` after a bare producer", on the new "Stage the round's plan page" step at 36313431c. It was fixed before any pull request existed, by the existing census, so no countermeasure is owed.

## Unpinned sites


none: the diff touches no `custom_components/` file, the only tree step 6d inventories; the `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none

