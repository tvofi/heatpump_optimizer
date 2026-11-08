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

`df0ffdf5e0ac56832a65818b7a31b7ac00c185fc`: round 7 repair, one commit on `c95c3b4b2e5875103fd5944c766d9e954f5b8a90` (the conflict-resolution head, which contains `0ac370fa281804336ba3444b3c867dacf48505ff`). It changes only `tools/audit/seat/beat_jobs_selftest.py`: two `plan_beat` cases and their two `MUTANTS` entries. No production line moved. `git merge-tree --write-tree origin/main HEAD` reported no conflict, so main was not merged; origin/main had not moved since the last prepr run (merge base `7c9c4c154cda514f938fd503cde2779716caf251`).

The previous head `0ac370fa2` was a conflict resolution by merge: one merge commit whose parents are the previous head `33c3dd998d2413452fa6aec5c331a0a7e9c0c579` and `origin/main` at `8a1358e8448e6734ed16982f25da6aae223ba8b9`. No re-cut, squash or rebase. The merge conflicted in `tools/audit/seat/beat_jobs.py`, `tools/audit/seat/beat_jobs_selftest.py` and `tools/audit/seat/instruments/beat_jobs.py.md`; `tests/closures.json` and `sweep_template.md` merged without a conflict. Review only the resolution delta and the round 7 test commit: `git show --cc 0ac370fa2`, which prints just the hunks that differ from both parents.

Resolution delta:
- `beat_jobs.py` docstring: `plan-beat` keeps main's `PLAN MOVED` sentence, then this branch's `pages.yml` dispatch sentences. The `gantt` and `verdict-audit` docs are main's.
- `beat_jobs.py` `ROWS` and the dispatch table: main's `gantt` and `verdict-audit` plus this branch's `outside-intake`.
- `beat_jobs.py` `plan_beat`: one `lines` list. A non-zero rc gives this branch's `PLAN UNAVAILABLE` or `REFUSED` line. On rc 0, main's page-hash `PLAN MOVED` line is added when the page changed. A state push that landed (`pushed ` on rc 0 or 1) dispatches `pages.yml`, and a refused dispatch adds `PAGES NOT DISPATCHED`. A single `write_job` call writes the list.
- `beat_jobs_selftest.py`: the `plan_rc1_silent` mutant uses this branch's predicate (`    if rc != 0:
        said = `). Main's `plan_moved_every_pass` mutant still matches the merged source, and `pages_*` mutants are unchanged.
- `instruments/beat_jobs.py.md`: main's text, with the `pages.yml` dispatch added to the `plan-beat` description.

Previous head `33c3dd998` was itself at `8eac7a704` plus the round-6 review fixes; the earlier history in this section is unchanged and superseded by this merge. The merge base with `origin/main` is now `8a1358e8448e6734ed16982f25da6aae223ba8b9`.

## Mutation proof

**Round 7 (beat_jobs).** The round-7 reviewer's two surviving mutants of the resolved `plan_beat` lines (`verdict/3262` `evidence/reviewer-mutants-resolution.txt`; probes `reviewer-probe-moved-and-pushed.txt`, `reviewer-probe-rc1-page.txt`) each survived `beat_jobs.py --self-test --no-mutants` with rc 0 at `c95c3b4b2`. Two cases now pin them, and both mutants are in `beat_jobs_selftest.py`'s `MUTANTS`:
- `moved_early_return` (`lines.append(PLAN MOVED ...)` becomes `return write_job(...)`) is killed by "plan-beat: a moved page whose push landed is PLAN MOVED and still dispatches Pages, once": `state_docs` writes a changed page and prints `pushed ...` at rc 0; the case requires the PLAN MOVED line and exactly one `gh workflow run pages.yml`.
- `moved_on_rc1` (`if rc == 0:` becomes `if rc in (0, 1):` before the page read) is killed by "plan-beat: rc 1 with a re-rendered page is PLAN UNAVAILABLE alone, no PLAN MOVED, no page memory": at rc 1 with a re-rendered page the digest starts `PLAN UNAVAILABLE rc=1`, has no PLAN MOVED, and `plan-page.json` stays empty.
- Null control: the unmutated head passes both cases (`175 checks, 0 failed`). The mutant stage applies each entry to a copy and requires its named case to fail, and an entry whose edit does not apply is refused as stale; the run prints `ok   mutant moved_early_return killed by: ...` and `ok   mutant moved_on_rc1 killed by: ...`.

**Earlier rounds (plan_public, outside_intake).** **Failing test first.** At `b6feee85e~1`, I applied the new `MUTANTS` entries alone, without the new cases.
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
- `python3 -I tools/audit/seat/plan_public.py --self-test` and `outside_intake.py --self-test`: rc 0 after the merge.
- `tools/pr/prepr.sh` at `df0ffdf5e0ac56832a65818b7a31b7ac00c185fc` (`PREPR_SKIP_CLOSURES=1` since CI re-records closures; `MUTANT_CMD` set to the beat_jobs self-test): `PRE-PR ... rc=0`. The diff-mutant step reports 11 survivors against main; each is answered in the Unpinned sites section. The resolved `plan_beat` lines DO form a new control-flow site: main's early `return write_job` for PLAN MOVED and this branch's Pages dispatch were folded into one `lines` list. The round-7 review found two survivors there, now pinned by the two cases under Mutation proof. The earlier sentence saying the resolution had no new site was wrong.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test` at this head: rc 0, `175 checks, 0 failed` (171 before: +2 cases, +2 mutants); `moved_early_return` and `moved_on_rc1` each print `ok   mutant ... killed by`.

## Red checks

At `c95c3b4b2` (the resolution head) two checks concluded red, per the round-7 verdict:
- `gate` 128581122145: `FAIL run(s) [42424058362] at this head are still being judged; their gate decides`. An edit-run deferral to the code run, which was still running; not a defect of this diff.
- `pr-contract / pr-contract` 128578752551: `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`. A timing fail-close in `codescan_wait.py` while CodeQL python was still running; its body lanes were clean. It re-runs once CodeQL finishes.

At this new head nothing has run yet, so no red has concluded; both are owed a re-read at the relayed head. The reds of the older head `b9b6af686` (a cancelled `gate`, the unrequired `tests / nightly-status`) are superseded.

Carry: R10-HOTFIX-GATE-BUSY-DEFER (the edit-run gate deferral recurs).

## Unpinned sites

The diff touches no `custom_components/` file. The diff-mutant step reports 11 survivors on the added lines against main, all in the beat_jobs pair and none in the round-7 lines:
- `beat_jobs.py:583-584` (`GUARD_OFF`, `RETURN_DEL`): the `outside-intake` row's guard from an earlier round of this PR; not new in round 7. Disposition: left to `mutation-autofix`/triage if the row is touched.
- `beat_jobs_selftest.py:127, 391-394, 401, 414, 471-472` (`CONST_SWAP`, `CALL_DEL`, `GUARD_OFF`, `RETURN_DEL`): test-fixture constants and null-case inputs. A mutated fixture is not production behaviour; the production mutants for these cases are the `MUTANTS` entries. Disposition: value checks, no pin owed.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
