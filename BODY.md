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

**Round 2 repair (fix review blocked, mutation-vacuous).** The block was on the inner `outside()` guard in `Thread.mark`'s non-OURS branch. `4bb24d609` added the failing case first ("identity: a third-party bot's comment after our answer owes nothing; an outsider's owes a reply") and its mutant `thirdbot_moves_out`. `9ffed3f2a` deleted the outsider branch in `Thread.mark`, which was dead code: `saw()` is the only writer of `last_out` for outside activity. Round 3 found that cure holds.

**Round 4 repair (round-3 fix review blocked, mutation-vacuous; verdict `c652d217` on `verdict/3262`).** The block: in `one_thread`, the read of a pull request's review comments (`if r["kind"] == "pr":`, L210) was unpinned. The mutant `if False:` survived the cases. Under it, `dispose` refuses #3240 with `REFUSED: #3240 has no outside activity`. This round makes one change, in `tools/audit/seat/outside_intake_selftest.py`:

- A new case, "refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)". In the self-test's fixture world, #3240 is a pull request opened by `hpo-author[bot]`, and its only outside activity is a review comment by `reviewer-x`. The case runs `dispose(Fake(w), "o/r", 3240, roster(), LIVE, "Not in scope: reason.\n", False, poster)`. It asserts rc 0 and exactly one post, to #3240, that starts with `REFUSED_MARK`.
- A new mutant, `one_thread_pr_reviews_drop`: `        if r["kind"] == "pr":` becomes `        if False:`. It names that case.
- The reviewer's plausible findings `scan_disc_kind` and `owed_reply_ge` are left out of this round, as the brief directs. They stay where the round-3 verdict (`verdict/3262`, `## Findings`) records them, under this PR's own group R10-OUTSIDE-INTAKE. This seat's brief forbids writing the roster branch, so this body carries neither. No production line changed.

## Head

`28f9f11bb0e302cfd4920bb1e50384c4db9633a6` is the head everything below was measured at. It is the reviewed head `0fd9bc6da6a5f562c7104c1e4d921189f492cff1` plus four commits. The first is a merge of `origin/main` at `0e9c508c1260220e49c049753b011e6e140f0e9c` (`e3304b4f4`, clean). The second is the one round-4 commit above (`b83f2f43c`), which touches only `tools/audit/seat/outside_intake_selftest.py`. The third is a merge of `origin/main` at `812bb874708a348ed603009191f151aa0a06c6d5` (`da54a710d`, clean), because main moved after the first `prepr.sh` run. The fourth is a merge of `origin/main` at `62bcca76ee043e68544a7f7042e9bb3ff5502aa7` (`28f9f11bb`, clean), because main moved again during the second. Every figure below was re-taken at `28f9f11bb`. The merge base is `62bcca76ee043e68544a7f7042e9bb3ff5502aa7`.

## Mutation proof

Run with `python3 -I tools/audit/seat/outside_intake.py --self-test`. All 21 mutants in `outside_intake_selftest.py` `MUTANTS` are killed at the head, each by its named case (`ok   mutant <id> killed by: <case>`). A surviving or stale mutant is a failed check. This round adds one mutant:

| mutant | edit | command | red at mutant | green on null control |
|---|---|---|---|---|
| `one_thread_pr_reviews_drop` | `one_thread` L210: `if r["kind"] == "pr":` made `if False:` (the round-3 reviewer's mutant) | applied in place, then cases only: `cd tools/audit/seat && python3 -I -c 'import sys; sys.path.insert(0,"."); import outside_intake_selftest as t; sys.exit(t.run(False))'` | rc 1: `FAIL refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)` and `1 self-test check(s) failed`, with that case the only failure | source restored (`git status` clean for `outside_intake.py`): the same command rc 0, `outside_intake self-test: all checks passed`. In-tree, `--self-test` prints `ok   mutant one_thread_pr_reviews_drop killed by: refuse: a pull request whose only outside activity is a review comment is refused, marked (#3240)` |

The kill is counted on cases only (`run(False)`), the counting the round-3 reviewer adopted, so the self-test's own stale-mutant check cannot stand in for a case.

The first draft of this case reused the `Poster` variable `p` that the next case ("refuse: a refused submission owes nothing until the submitter writes again") reads. Under the mutant, that draft also failed the next case, so the red was not this case's alone. The case now uses its own `Poster`. The table above is from that final form, where the new case is the only failure.

**Class rule (step 8).** The rule that enumerates the readers of a thread's comments is every `rows(` call in `one_thread` and `scan`. `one_thread` has two: the issue comments, and the PR review comments that this round pins. `scan` reads review comments through the `pulls/comments` endpoint pair, which `review_comments_unread` already pins.

## Null control

- The unmutated self-test runs rc 0 at the head (`outside_intake self-test: all checks passed`), and so does the cases-only run, so the kill above is the mutant's.
- At the head, #3240's listing line is unchanged (`OUTSIDE #3240 owed=triage comment by=reviewer-x since=2026-11-06T08:00:00Z`, in the fixture world's `want`). That line comes from `scan`, which the mutant does not touch. So the new case is what separates `one_thread`'s read.
- The existing refusal of a thread with no outside activity (#3251, #9999) still holds. So the new case's rc 0 is not an unconditional dispose.

## Figures

- `python3 -I tools/audit/seat/outside_intake.py --self-test` at `28f9f11bb`: `outside_intake self-test: all checks passed`, with 48 `ok` lines. That is 27 cases and 21 `mutant` lines. Round 3 had 26 and 20.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- Scoped scripts: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `ALL 2643 ENTITY CHECKS PASSED` (rc 0). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gives `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget moved, and no `*_budgets.json` is in the three-dot diff (`git diff --name-only origin/main...HEAD | grep -c budgets.json` prints 0).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`. `python3 -I tools/audit/seat/selftest_wiring.py --check`: `120 self-testing, 120 wired, 0 unwired` and `0 index gap(s)`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` are byte-identical to `origin/main` (`git diff --quiet origin/main HEAD -- <those> && echo BYTE-IDENTICAL` printed `BYTE-IDENTICAL`).
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check`: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. No golden was run, because the diff touches none.
- `tools/pr/prepr.sh <body>` at `28f9f11bb`, run 2026-11-07T09:24:11Z to 09:38:11Z, with `origin/main` at `62bcca76ee043e68544a7f7042e9bb3ff5502aa7` both before and after: `PRE-PR: 28f9f11bb0e302cfd4920bb1e50384c4db9633a6 ... rc=0`. Its lanes include `carry ok` (2 routed, 0 unrouted), `pr-body ok`, `figures ok`, `merged structure ok`, and `ci predict` with no red predicted. Main had not moved at the end of the run, so no further merge was owed. The two earlier runs, at `b83f2f43c` and `da54a710d`, were rc 0 too; main moved after each of them. `tools/pr/prepr.sh --body-check <body>`: rc 0.
- These round-1 figures are unchanged, because this round edits no file they read:
  - the `plan_public.py` self-test (4 mutants) and the `beat_jobs.py` self-test (136 checks);
  - the `policy_lint --budgets` caps on `orchestrator.md` and `standing-dispatch.md`;
  - the first live intake pass.

## Red checks

The final head `28f9f11bb0e302cfd4920bb1e50384c4db9633a6` has no check runs: it has not been pushed to the PR. Its reds, if any, are named at the next read.

At the round-3 head `0fd9bc6da6a5f562c7104c1e4d921189f492cff1` (the reviewer's `filter=all` read across both pages, 200 runs; my latest-only read at about 08:15Z returned 68 runs, all success or skipped):

- **`gate` 128304775378, 128316374818 and 128324526998 concluded `failure`.** Each log says `FAIL run(s) [42339563999] at this head are still being judged; their gate decides`. Class: the edit run's ordering deferral to code run 42339563999, which was still in progress. It is not a defect of the authored code. That code run's own `gate`, 128330158424, concluded success at 06:44:00Z. Answer: R10-HOTFIX-GATE-BUSY-DEFER, which removes this deferral red, is MERGED. The cheaper detector is the gate itself once the code run concludes, so no new countermeasure is owed.
- **`gate` 128305369003 and `arch-score / arch-score` 128304887981 concluded `cancelled`.** Class: superseded by a later attempt or run at the same head (`cancel-superseded`). Their replacements concluded success: `gate` 128330158424 and 128331018038, and `arch-score / arch-score` 128322484672 and 128331044271. Answer: no defect, so no countermeasure is owed.
- **`governance / instrument-self-tests` 128304160651 (04:45:23Z-05:15:38Z) and 128314670086 (05:30:48Z-06:01:03Z) concluded `cancelled`, each at the 30-minute job timeout.** Class: the job's wall time, which is the owner's standing line. Answer: R10-HOTFIX-SELFTEST-TIMEOUT, cured by R10-PROCESS-SLIM (#3245). Attempt 3, 128322483648, concluded success at 06:35:48Z. This PR's own self-test (`outside_intake`) runs in well under a minute locally, so it is not the cost.
- Every other run concluded success, skipped or neutral.

At the round-2 reviewed head `3189559b21ddf1d5517ea7ec34f0df470c480103`, `gate` 128272376901 concluded `failure` with `FAIL run(s) [42329336154] at this head are still being judged; their gate decides`. It is the same deferral with the same answer. That code run's `gate` concluded success.

At the round-1 head `48acc104f97cf88bf0ec28a3f6ec01438e169bb5`, four `gate` runs concluded `failure`, all the same ordering deferral: 128203011639, 128206299696, 128215975302 and 128215984338. They were named in round 1 and are answered the same way.

The earlier local red stands as recorded. `tests/entities.py` reported "no errexit `run:` block reads `$?` after a bare producer" on the new "Stage the round's plan page" step at 36313431c. It was fixed before any pull request existed, and the existing census caught it, so no countermeasure is owed.

## Unpinned sites

none: the diff touches no `custom_components/` file, the only tree step 6d inventories. The `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
