R10-OUTSIDE-INTAKE. The owner's ruling (tvofi 2026-11-06), verbatim: "the plan html for an ongoing round should be made publically available from a suitable place in the developer documentation on the repo. During future audit rounds, issues, PRs or other posts from outside users should be regularly checked, triaged/designed and planned. Fold this shape into the repo machinery. When the plan html is done, and any outside submission is on the roster, the plan HTML should be linked in an answer to the outside submission."

**Policy and developer docs change: this merges only on tvofi's approving review** (`orchestrator.md` section 5, `standing-dispatch.md`, `dev/programme/HANDOVER.md`). The ruling approves the shape in principle. The review is the approval.

What lands, by the brief's three parts:

1. **Public plan page.** `tools/audit/seat/plan_public.py stage` takes `PLAN.html` from the newest `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of` owns) and writes `plan/index.html`. `.github/workflows/pages.yml` runs it from the dispatched ref's tree. It then checks out the newest `v*` tag for the docs and adds the page, served at `https://tvofi.github.io/heatpump_optimizer/plan/` (`plan_public.PLAN_URL`, the one spelling of the URL). The beat's `plan-beat` row dispatches `pages.yml` on `main` after each state push that landed. `dev/programme/HANDOVER.md` links the page from the head of its Round 10 section; no user doc links it. If `ref_privacy` reads a host path, account name, uid, scratch root or a tool's attribution in the page, it refuses the page (rc 1: the deploy goes red and nothing is published). Between rounds there is no state ref (rc 2): the site deploys without a plan and warns.
2. **Intake as machinery.** `tools/audit/seat/outside_intake.py list` lists threads (issues, pull requests and discussions, which share one number space). It lists a thread when it has activity at or after a cursor by an author who is outside `OURS` and not a bot. It prints the `OUTSIDE #N owed=triage|answer|reply` lines owed this turn. Disposition is read from the roster (`issues`/`fixes`, wired by `roster_edit.py wire-issue`) and from marker comments by our accounts, never from memory. The new beat row `outside-intake` [1800 s] runs it with a cursor under the digest's `state/` and writes its lines to the digest. Sweep step (5b) in `sweep_template.md` names the action for each line. `orchestrator.md` section 5 and `standing-dispatch.md` each carry the short obligation.
3. **Answer step.** `outside_intake.py answer --issue N` posts the plan link through `tools/pr/gh_comment.py post`, whose read-back is the proof. It marks the comment. A marker is read only from a comment by an account in `OURS`, and only `saw()` moves a thread's outside activity, so a third-party bot's comment is neither ours nor outside activity. It refuses a thread already answered or refused, so none is answered twice. It also refuses a thread on no roster group, any thread while the plan page does not answer, and a discussion. `refuse --issue N --reason-file F` records a refusal the same way.

Alternatives, and why each lost (`fixer.md` step 17):

- **A committed path under `docs/`.** It needs a commit to `main` at every sweep, each a pull request through the gate, for a generated file.
- **Pages from a push to the state ref.** A workflow runs from the pushed commit's own tree. The orphan state ref carries no `.github/`, so a `push:` trigger there never fires.
- **A `schedule:` trigger.** It runs 48 deploys a day whether or not the plan moved. It would also change the trigger set `tests/entities.py` pins (release tags plus dispatch).

The dispatch keeps that pinned set. One existing behaviour changes: a dispatch now serves the newest release's docs rather than the dispatched ref's. That matches the workflow's stated design ("the served page is the release HACS installs"), and it keeps a plan refresh from publishing main's unreleased docs. The owner may prefer otherwise; this is the change to review.

**Round 2 repair (fix review blocked, mutation-vacuous).** The block was on the inner `outside()` guard in `Thread.mark`'s non-OURS branch: `if True:` survived the self-test. Two commits answer it.

- `4bb24d609`, failing test first. A new case, "identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply", takes #3225 answered by our App (`hpo-approver[bot]`) and then adds a later comment. With a `renovate[bot]` (Bot) comment, `listing` prints no #3225 line. With a `Bankaifan` (User) comment, the null control, it prints one `owed=reply` line. The new mutant `thirdbot_moves_out` (the guard made `if True:`) fails this case at that commit: `ok   mutant thirdbot_moves_out killed by: identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply`.
- `9ffed3f2a`, the better fix (`fixer.md` step 17). The outsider branch in `Thread.mark` was dead code. `one_thread` calls `saw()` on every outside comment before `mark()`. A comment `scan` skips has `at < since`, while the thread exists only because `saw` saw activity at or after `since`, so the comment can never raise `last_out`'s maximum. The measurement: the reviewer's `mark_no_last_out`, which deletes that move, was reported KILLED in round 2, but only as `FAIL mutant forged_marker_read: stale`. The runner counted its own stale-mutant check, not a case. Counting case failures alone, it SURVIVED at `b157d297c` (`ok` on every case). So I deleted the branch, and the guard the block named went with it; `saw()` is now the only writer of `last_out` for outside activity. The new case also drives `one_thread`/`owed` (Bot: `None`, User: `reply`). `thirdbot_moves_out` now restores an unguarded move in `mark`. `forged_marker_read` is retargeted to the early `return` that remains.
  - The alternative was to keep the branch and pin its guard, which is the brief's literal cure. It lost because the branch's own move is an equivalent mutant (`mark_outsider_moves_out` below, which restores it, survives). Keeping it would leave a line no case can pin, on a changed line, and the next mutation re-run would find it.
  - A consequence the reviewer's harness reads: `ev/thirdbot.py` calls `Thread.mark` alone, without `saw`. At `9ffed3f2a` it gives `Bankaifan/User owed=None` (at `b157d297c`: `reply`). That drive skips the reader that owns outside activity. Through the readers (`listing` and `one_thread`), the User control still gives `reply`. That is what the new case asserts, and mutant `saw_no_last_out` shows `saw` is the owner.

## Head

`9ffed3f2a80b6387bff9f41b893ac7bf804ca10c` is the head everything below was measured at, unless a line names another. It is the reviewed head `3189559b21ddf1d5517ea7ec34f0df470c480103`, plus a merge of `origin/main` at `294a880dae608502b62055775e34a5db93217b98` (`b157d297c`, clean, no conflict), plus the two round-2 commits above. Those two commits touch only `tools/audit/seat/outside_intake.py` and `tools/audit/seat/outside_intake_selftest.py`. `origin/main` was still `294a880dae608502b62055775e34a5db93217b98` at 2026-11-07T04:26Z, after the checks below ran, so no second merge or run was owed.

## Mutation proof

Run with `python3 -I tools/audit/seat/outside_intake.py --self-test`. All 20 mutants in `outside_intake_selftest.py` `MUTANTS` are killed at the head, each by its named case (`ok   mutant <id> killed by: <case>`). A surviving or stale mutant is a failed check. This round adds one mutant:

| mutant | edit | command | red at mutant | green on null control |
|---|---|---|---|---|
| `thirdbot_moves_out` | `Thread.mark`'s non-OURS early return gets `self.last_out = max(self.last_out, c["at"])` before it (at `4bb24d609`: the inner guard made `if True:`) | `python3 -I tools/audit/seat/outside_intake.py --self-test` | `ok   mutant thirdbot_moves_out killed by: identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply` (renovate[bot] gives `owed=reply`) | unmutated: that case passes, rc 0. Its User half gives `owed=reply` at the head and under the mutant, so the case's kill is the Bot half |

**The finder's harness at both ends.** I re-ran the reviewer's mutant set: `ev/mut.py` on `probe/rev-3262-990dee62`, ported to this head, each mutant applied in place and then restored. My port makes one change, and it is a correction. Each mutant runs the cases only (`outside_intake_selftest.run(False)`), and a kill counts only when a case fails. The reviewer's runner ran the full `--self-test`, so a mutant that edits text an in-tree mutant targets was counted KILLED by `mutant ... stale`. That is how `mark_no_last_out` read as killed in round 2.

- The 6 round-1 mutants (cursor read, cursor write, post rc, `--dry-run` drop, script path, list rc): all KILLED at `9ffed3f2a`.
- The reviewer's 12 changed-line mutants: `who_no_suffix`, `who_never_bot`, `who_typ_user`, `cursor_exists_guard`, `dry_always`, `post_issue_arg`, `last_ours_drop`, `keep_now` and `mark_thirdbot_moves_out` are KILLED. `cursor_write_skip` is KILLED: the main-list case's read of the unwritten cursor raises `FileNotFoundError`, and in-tree the self-test then exits non-zero.
  - `mark_revert_old` (the pre-round-1 `if outside(...): move; return`) is KILLED by "identity: a third-party bot's marker disposes of nothing".
  - `mark_no_last_out` has no line left to delete at the head. Its round-2 state is above: it SURVIVED by case at `b157d297c`.
- New at the head:
  - `mark_no_return` (the early `return` made `pass`): KILLED by "list: the fixture world gives exactly its owed lines".
  - `saw_no_last_out` (`saw` no longer moves `last_out`): KILLED by the same case. This is the null control for the claim that `saw` owns the move.
  - `mark_outsider_moves_out` (the deleted guarded move restored): SURVIVED, rc 0. That is expected and is the equivalence measurement: restoring the line changes no case.

**Class rule (step 8).** The rule that enumerates the writers of the property is every assignment to `last_out` in `outside_intake.py`: `grep -n "last_out =" tools/audit/seat/outside_intake.py`. At the head it returns `Thread.__init__` (the empty initial value) and `Thread.saw`. At `b157d297c` it also returned `Thread.mark`'s guarded move, closed in this diff by deletion. `saw` is reached only through `scan.saw` and `one_thread`, and both apply `outside()` first. The round-1 marker class (writers of `Thread.answered`/`Thread.refused`) is unchanged: only `Thread.mark`, inside its OURS branch.

## Null control

- The unmutated self-test runs rc 0 at the head (`outside_intake self-test: all checks passed`), and so does the cases-only run, so each kill above is the mutant's.
- An outsider's later comment on an answered thread still owes `reply` at the head, both through `listing` and through `one_thread`/`owed` (the new case's User half).
- `hpo-approver[bot]` still disposes of #3225 ("answer: an answered submission is refused and no longer listed").
- `main list null`: an empty world gives rc 0 and prints nothing, so rc 1 is not unconditional.
- At the merge base, `pages.yml` has none of the three plan steps. The entities check returns `a plan step is missing: [...]` over `git show origin/main:.github/workflows/pages.yml` and `[]` over the head. That figure is from round 1 and unchanged, because neither `pages.yml` nor the check moved.

## Figures

- `python3 -I tools/audit/seat/outside_intake.py --self-test` at `9ffed3f2a`: `outside_intake self-test: all checks passed`, with 46 `ok` lines. That is 26 cases and 20 `mutant` lines, counted as the `ok` lines without and with the `mutant` prefix. Round 2 had 25 and 19.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- Scoped scripts: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `ALL 2641 ENTITY CHECKS PASSED` (rc 0). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gives `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget moved, and no `*_budgets.json` is in the three-dot diff (`git diff --name-only origin/main...HEAD | grep -c budgets.json` prints 0).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `120 self-testing, 120 wired, 0 unwired` and `0 index gap(s)`.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh` then `bash tools/audit/seat/cloud-setup.sh --check`: `OK python3 is /opt/hpo/venv-ci/bin/python3`. No golden was run, because the diff touches none.
- `VERSION`, `RELEASE_NOTES.md`, `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are byte-identical to `origin/main` (`git diff --quiet origin/main HEAD -- <those> && echo BYTE-IDENTICAL` printed `BYTE-IDENTICAL`).
- These round-1 figures are unchanged, because this round edits no file they read:
  - the `plan_public.py` self-test (4 mutants) and the `beat_jobs.py` self-test (136 checks);
  - the `policy_lint --budgets` caps on `orchestrator.md` and `standing-dispatch.md`;
  - the first live intake pass.

## Red checks

The final head `9ffed3f2a80b6387bff9f41b893ac7bf804ca10c` has no check runs: it has not been pushed to the PR. Its reds, if any, are named at the next read.

At the reviewed head `3189559b21ddf1d5517ea7ec34f0df470c480103`:

- **`gate` check run 128272376901 concluded `failure`** with `FAIL run(s) [42329336154] at this head are still being judged; their gate decides`. That is the edit run's ordering deferral to code run 42329336154, which was still in progress. It is not a defect of the authored code.
  - The run that decides is that code run's own `gate`, which concluded success: 128282233458 in the reviewer's read, and 128285176170 in mine.
  - The open item R10-HOTFIX-GATE-BUSY-DEFER, which removes this deferral red, is MERGED (#3246). Its fix is in this head through the `origin/main` merge.
  - The cheaper detector is the gate itself once the code run concludes, so no new countermeasure is owed.
- I read the check runs once more at about 04:10Z (`pull_request_read get_check_runs`, `total_count` 68, every run on one page): no run concluded failure, cancelled or timed out. 128272376901 is no longer listed, because later attempts replaced it.
- **`governance / instrument-self-tests`** (128285213331) concluded success at 02:54:52Z. It was not cancelled by the 30-minute timeout, so R10-HOTFIX-SELFTEST-TIMEOUT did not fire at this head.
- Every other run concluded success, skipped or neutral.

At the round-1 head `48acc104f97cf88bf0ec28a3f6ec01438e169bb5`, four concluded reds, all `gate`, were the same ordering deferral: 128203011639, 128206299696, 128215975302 and 128215984338. They were named in round 1 and are answered the same way.

The earlier local red stands as recorded. `tests/entities.py` reported "no errexit `run:` block reads `$?` after a bare producer" on the new "Stage the round's plan page" step at 36313431c. It was fixed before any pull request existed, and the existing census caught it, so no countermeasure is owed.

## Unpinned sites

none: the diff touches no `custom_components/` file, the only tree step 6d inventories. The `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
