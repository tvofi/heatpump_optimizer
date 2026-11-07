R10-OUTSIDE-INTAKE. The owner's ruling (tvofi 2026-11-06), verbatim: "the plan html for an ongoing round should be made publically available from a suitable place in the developer documentation on the repo. During future audit rounds, issues, PRs or other posts from outside users should be regularly checked, triaged/designed and planned. Fold this shape into the repo machinery. When the plan html is done, and any outside submission is on the roster, the plan HTML should be linked in an answer to the outside submission."

**Policy and developer docs change: this merges only on tvofi's approving review** (`orchestrator.md` section 5, `standing-dispatch.md`, `dev/programme/HANDOVER.md`). The ruling approves the shape in principle. The review is the approval.

What lands, by the brief's three parts:

1. **Public plan page.** `tools/audit/seat/plan_public.py stage` takes `PLAN.html` from the newest `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of` owns) and writes `plan/index.html`. `.github/workflows/pages.yml` runs it from the dispatched ref's tree. It then checks out the newest `v*` tag for the docs and adds the page, served at `https://tvofi.github.io/heatpump_optimizer/plan/` (`plan_public.PLAN_URL`, the one spelling of the URL). The beat's `plan-beat` row dispatches `pages.yml` on `main` after each state push that landed. `dev/programme/HANDOVER.md` links the page from the head of its Round 10 section; no user doc links it. If `ref_privacy` reads a host path, account name, uid, scratch root or a tool's attribution in the page, it refuses the page (rc 1: the deploy goes red and nothing is published). With no state ref, or no `PLAN.html` at the newest one, it stages nothing (rc 2): the site deploys without a plan and warns. A closed round's state ref stays the newest until `closeout.py --apply` deletes it, so the closed round's page is served until then. `plan_public.py`'s docstring and the `pages.yml` header now say so (round 6).
2. **Intake as machinery.** `tools/audit/seat/outside_intake.py list` lists threads (issues, pull requests and discussions, which share one number space). It lists a thread when it has activity at or after a cursor by an author who is outside `OURS` and not a bot. It prints the `OUTSIDE #N owed=triage|answer|reply` lines owed this turn. Disposition is read from the roster (`issues`/`fixes`, wired by `roster_edit.py wire-issue`) and from marker comments by our accounts, never from memory. The new beat row `outside-intake` [1800 s] runs it with a cursor under the digest's `state/` and writes its lines to the digest. Sweep step (5b) in `sweep_template.md` names the action for each line. `orchestrator.md` section 5 and `standing-dispatch.md` each carry the short obligation.
3. **Answer step.** `outside_intake.py answer --issue N` posts the plan link through `tools/pr/gh_comment.py post`, whose read-back is the proof. It marks the comment. A marker is read only from a comment by an account in `OURS`, and only `saw()` moves a thread's outside activity, so a third-party bot's comment is neither ours nor outside activity. It refuses a thread already answered or refused, so none is answered twice. It also refuses a thread on no roster group, any thread while the plan page does not answer, and a discussion. `refuse --issue N --reason-file F` records a refusal the same way.

Alternatives, and why each lost (`fixer.md` step 17):

- **A committed path under `docs/`.** It needs a commit to `main` at every sweep, each a pull request through the gate, for a generated file.
- **Pages from a push to the state ref.** A workflow runs from the pushed commit's own tree. The orphan state ref carries no `.github/`, so a `push:` trigger there never fires.
- **A `schedule:` trigger.** It runs 48 deploys a day whether or not the plan moved. It would also change the trigger set `tests/entities.py` pins (release tags plus dispatch).

The dispatch keeps that pinned set. One existing behaviour changes: a dispatch now serves the newest release's docs rather than the dispatched ref's. That matches the workflow's stated design ("the served page is the release HACS installs"), and it keeps a plan refresh from publishing main's unreleased docs. The owner may prefer otherwise; this is the change to review.

## Re-cut note

Round 6. This is a minimal re-cut of the round-5 block (`verdict/3262`, ci-red). The block is cured by a fresh head, and this round also takes the four findings that verdict carried to R10-OUTSIDE-INTAKE. The plan_public.py lines the round-5 reviewer found cured are untouched: the CLI case, the `host_ident_dropped` and `main_rc0` mutants, and the runner.

- **A fresh head.** `10bd5426d`, `f6a7b52fe` and `8eac7a704` are clean merges of `origin/main`, the last at `364353e670f666be6c97a5942ffa0bea9132b5ce`, so the head's runs start anew.
- **The false sentence is corrected.** In both `plan_public.py`'s docstring and the `pages.yml` header, "between rounds there is no page" now reads like this:
  - A closed round's state ref stays the newest until `closeout.py --apply` deletes it, so its page is served until then.
  - The page is absent only when there is no state ref, or no `PLAN.html` at the newest one.
  - Source: `closeout.py`'s `refs` step (2) is the only step that deletes remote branches, and it runs only under `--apply`.
- **`main_url_rc1` is killed.** A new `plan_public.py` case, "url prints PLAN_URL alone, rc 0", runs `main(["url"])` and requires rc 0 and stdout of exactly `PLAN_URL` plus a newline. The mutant `main_url_rc1` is entered in `MUTANTS`.
- **`scan_disc_kind` is killed.** A new `outside_intake_selftest.py` case, "discussions: a discussion opened before the cursor, its new outside comment listed as a discussion", covers discussion #3262. It was opened before `SINCE`, and an outside comment came after it. The case requires the line `OUTSIDE #3262 owed=triage discussion by=asker since=2026-11-06T10:00:00Z`; the mutant prints `comment`.
- **`owed_reply_ge` is killed.** A new case, "reply: outside activity in our answer's own second owes nothing; one second later owes a reply", drives `owed()` on two threads. In the first, outside activity falls in the same second as our answer and owes `None`. In the second it falls one second later and owes `reply`.
  - **This case encodes a design choice** (`fixer.md` step 11). GitHub stamps to the second, so a same-second outside comment cannot be ordered against our answer.
  - The choice is that only activity strictly after our latest comment owes a reply. The alternative, `>=`, would owe a reply on that tie. Both directions are defensible. This one keeps the production predicate unchanged, and the case names the tie, so a later seat that reads the tie the other way is reversing a stated choice rather than fixing a bug.
- Both new entries go in `outside_intake_selftest.py`'s `MUTANTS`.
- **Carry 1 is not this PR's work.** It is the group's part 2, prototyped at `handoff-wip/r10-outside-intake-p2`, and the carry itself says it starts after #3262 merges. This round leaves it untouched.

## Head

`8eac7a7049082315693abbedf6c2f5ed2e19babc`. It sits on the round-5 PR head `b9b6af68683febf678907b19d7e73be453bc5bb7` and adds four commits:

- `10bd5426d`: a clean merge of `origin/main` at `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76`.
- `b6feee85e`: the round-6 change above, 3 files, +36 and -4.
- `f6a7b52fe`: a clean merge of `origin/main` at `aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98`. Main moved while the body was being written after the first clean `prepr.sh` run, which was at `b6feee85e`.
- `8eac7a704`: a clean merge of `origin/main` at `364353e670f666be6c97a5942ffa0bea9132b5ce`. Main moved during the clean `prepr.sh` run at `f6a7b52fe` (18:05:31Z to 18:17:34Z). This merge touches none of the round's four files (`git diff --quiet HEAD~1 HEAD -- <the four>`).

The merge base is `364353e670f666be6c97a5942ffa0bea9132b5ce`. The figures below were re-taken at `8eac7a704`, except the mutation proof's `HEAD~1` arm, which was taken against `b6feee85e`'s parent before the last merge. That merge touches none of the three files the round changes. `origin/main` was `aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98` before and after the final `prepr.sh` run (see `## Figures`), so no further merge was owed.

## Mutation proof

**Failing test first.** At `b6feee85e~1`, I applied the new `MUTANTS` entries alone, without the new cases.
- `python3 -I tools/audit/seat/plan_public.py --self-test` gave rc 1: `FAIL mutant main_url_rc1 killed by: url prints PLAN_URL alone, rc 0`.
- `outside_intake.py --self-test` refused both new entries as stale, because their cases did not yet exist: `FAIL mutant scan_disc_kind: stale` and `FAIL mutant owed_reply_ge: stale`.

**Direct survival proof.** A scratch driver applies each `outside_intake.py` mutant by hand and runs `outside_intake_selftest.cases()` on the mutant copy:

| run | at `b6feee85e~1` (27 cases) | at this head (29 cases) |
|---|---|---|
| null | no case fails | no case fails |
| `scan_disc_kind` | no case fails (SURVIVES) | fails "discussions: a discussion opened before the cursor, its new outside comment listed as a discussion" |
| `owed_reply_ge` | no case fails (SURVIVES) | fails "reply: outside activity in our answer's own second owes nothing; one second later owes a reply" |

At `b6feee85e~1` the result matches the round-5 reviewer's cases-only record (`verdict/3262` `evidence/reviewer-mutants-casesonly.txt`).

**At this head, both self-tests pass and print each kill:**
- `plan_public.py --self-test`: rc 0, ending in `ok   mutant main_url_rc1 killed by: url prints PLAN_URL alone, rc 0` and `plan_public self-test: all checks passed`.
- `outside_intake.py --self-test`: rc 0, with these lines:
  - `ok   mutant scan_disc_kind killed by: discussions: a discussion opened before the cursor, its new outside comment listed as a discussion`
  - `ok   mutant owed_reply_ge killed by: reply: outside activity in our answer's own second owes nothing; one second later owes a reply`
  - `outside_intake self-test: all checks passed`

The round-5 survivors `mark_old_restored_EQUIV`, `has_disc_ignored` and `plan_live_200` (`outside_intake.py`) were not in the findings carried to this round, and this round leaves them untouched. The same holds for `html_case_sensitive`, `rc_ignored_refs`, `show_rc_ignored`, `empty_text_published` and `main_print_stdout` (`plan_public.py`), which the round-4 and round-5 verdicts classed as equivalent, near-equivalent or cosmetic.

## Null control

- The unmutated module at both ends: the hand driver's `NULL` row fails no case at `b6feee85e~1` (27 cases) or at this head (29 cases). Each kill above therefore belongs to its mutant, not to the case set.
- The pass arms of `owed_reply_ge`'s case are not vacuous. The one-second-later thread must owe `reply`, so a predicate that never replies fails it too.

## Figures

- `python3 -I tools/audit/seat/plan_public.py --self-test`: rc 0. It prints 20 `ok` lines (`grep -c '^ok'`): 13 cases and 7 `mutant` lines.
- `python3 -I tools/audit/seat/outside_intake.py --self-test`: rc 0. It prints 52 `ok` lines (`grep -c '^ok'`): 29 cases and 23 `mutant` lines.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` The two scripts are `tests/entities.py` and `tests/harness_headers.py`.
- The scoped scripts, each run with `PYTHONPATH=tests/hastub`:
  - `python3 tests/entities.py`: `ALL 2646 ENTITY CHECKS PASSED`.
  - `python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No `*_budgets.json` is in the three-dot diff (`git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c budgets.json` prints 0).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- Path and wiring checks at the head:
  - `python3 tools/audit/seat/ref_privacy.py --check`: `0 refused`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`.
  - `python3 -I tools/audit/seat/selftest_wiring.py --check`: `120 self-testing, 120 wired, 0 unwired` and `0 index gap(s)`.
  - `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are byte-identical to `origin/main`: `git diff --quiet origin/main HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo BYTE-IDENTICAL` printed `BYTE-IDENTICAL`.
- `dev/programme/delivery/3262.md` is in the three-dot diff (`grep -c` prints 1).
- Toolchain: `bash tools/audit/seat/cloud-setup.sh` was run, then `--check` gave `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. No golden was run, because the diff touches none.
- `tools/pr/prepr.sh <body>` at `8eac7a704`, run 2026-11-07T18:18:02Z to 18:38:47Z: `PRE-PR: 8eac7a7049082315693abbedf6c2f5ed2e19babc ... rc=0`. Every lane was `ok` or `skip`: `closures` was skipped (CI re-records), `diff mutants` because `MUTANT_CMD` was unset, and `unpinned sites` because the diff adds none. The `push order` WARN names the push to `handoff/` that followed. Earlier clean runs were at `b6feee85e` (17:08:33Z to 17:19:34Z) and `f6a7b52fe` (18:05:31Z to 18:17:34Z), each followed by a main move and a merge. `origin/main` was `364353e670f666be6c97a5942ffa0bea9132b5ce` at the start and the end of the last run.

## Red checks

**At the new head, nothing has run, so no red has concluded.** `gh api "repos/tvofi/heatpump_optimizer/commits/8eac7a7049082315693abbedf6c2f5ed2e19babc/check-runs?filter=all&per_page=100"` gives `total_count` 0 (one page), and `actions/runs?head_sha=` gives `total_count` 0. Both were read at 2026-11-07T18:39:12Z. The same reads gave 0 and 0 at `f6a7b52fe` (18:05Z) and at `b6feee85e` (17:50Z).
- `merge_train.py classify 8eac7a7049082315693abbedf6c2f5ed2e19babc --pr 3262` read `WAIT 8eac7a7049082315693abbedf6c2f5ed2e19babc pending: gate red: none` at 18:39:12Z. At `f6a7b52fe` it read `WAIT` at 18:05:20Z, and at `b6feee85e` it read `WAIT` at 17:20:02Z and 17:50:08Z.
- The cause: pull request #3262's head branch is `fix/r10-outside-intake`, still at `b9b6af68683febf678907b19d7e73be453bc5bb7` (`pulls/3262` `.head`). The PR moves only when the orchestrator's `tools/audit/seat/handoff_push.sh` relays `handoff/r10-outside-intake` through `app_push.sh`.
- So the brief's "make classify read GREEN before handoff" cannot be met from this seat, which may not write `fix/`. I took the option that keeps coverage: hand off with the fresh head. **The GREEN classify is owed at the relayed head before the next review.** If a fresh run is cancelled by a runner stall, that is the orchestrator's re-run.

**The old head's concluded reds** (`b9b6af686`, `verdict/3262` `evidence/reds.tsv`). This head supersedes each one:
- `gate` 128449147307 concluded `failure`, with `FAIL tests / fast (3.14): cancelled (run 42385084286)`.
- `gate` 128449368751 concluded `cancelled`.
- The cancelled jobs of code run 42385084286, cancelled at about 15:46:18Z with no re-run: `tests / fast (3.14)`, `tests / browser`, `tests / closures`, `tests / coverage`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
  - This was a cancellation, not a defect of this diff. No cheaper detector exists.
  - The two `gate` reds repeat it, and they are the same edit-run gate red class that `R10-HOTFIX-GATE-BUSY-DEFER` carries.
- `tests / nightly-status` 128443914073 concluded `failure`. It grades main's cancelled Nightly 42369836867 at `08fd676`.
  - This diff does not read that run: `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c nightly_status` prints 0.
  - The check is unrequired, red for every open PR graded against that dispatch, and its own detector.

This seat could not read the code-scanning alerts: the body check's ancestry lane reports `code-scanning/analyses page 1: HTTP 403`, fail-closed. That read is owed by a seat with that access.

Carry: R10-HOTFIX-GATE-BUSY-DEFER (the edit-run gate reds on another run's cancelled jobs recur).

## Unpinned sites

none: the diff touches no `custom_components/` file, the only tree step 6d inventories. The `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
