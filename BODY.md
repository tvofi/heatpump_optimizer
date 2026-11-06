R10-OUTSIDE-INTAKE. The owner's ruling (tvofi 2026-11-06), verbatim: "the plan html for an ongoing round should be made publically available from a suitable place in the developer documentation on the repo. During future audit rounds, issues, PRs or other posts from outside users should be regularly checked, triaged/designed and planned. Fold this shape into the repo machinery. When the plan html is done, and any outside submission is on the roster, the plan HTML should be linked in an answer to the outside submission."

**Policy and developer docs change: this merges only on tvofi's approving review** (`orchestrator.md` section 5, `standing-dispatch.md`, `dev/programme/HANDOVER.md`). The ruling gives approval in principle; the review is the approval.

What lands, by the brief's three parts:

1. **Public plan page.** `tools/audit/seat/plan_public.py stage` takes `PLAN.html` from the newest `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of` owns) and writes `plan/index.html`. `.github/workflows/pages.yml` runs it from the dispatched ref's tree. It then checks out the newest `v*` tag for the docs and adds the page, so the page is served at `https://tvofi.github.io/heatpump_optimizer/plan/` (`plan_public.PLAN_URL`, the one spelling of the URL). The beat's `plan-beat` row dispatches `pages.yml` on `main` after each state push that landed, so the page refreshes at each sweep that moved the plan. The developer docs link it from the head of the Round 10 section of `dev/programme/HANDOVER.md`; no user doc links it. A page `ref_privacy` reads a host path, account name, uid, scratch root or a tool's attribution in is refused (rc 1, red deploy, nothing published). Between rounds there is no state ref (rc 2): the site deploys without a plan and warns.
2. **Intake as machinery.** `tools/audit/seat/outside_intake.py list` lists threads (issues, pull requests, discussions, one number space) with activity at or after a cursor by an author outside `OURS` and not a bot. It prints the `OUTSIDE #N owed=triage|answer|reply` lines owed this turn. Disposition is read from the roster (`issues`/`fixes`, wired by `roster_edit.py wire-issue`) and from marker comments by our accounts, never from memory. A new beat row, `outside-intake` [1800 s], runs it with a cursor under the digest's `state/` and writes its lines to the digest the sweep reads. Sweep step (5b) in `sweep_template.md` names the action per line. `orchestrator.md` section 5 and `standing-dispatch.md` each carry the short obligation.
3. **Answer step.** `outside_intake.py answer --issue N` posts the plan link through `tools/pr/gh_comment.py post`, whose read-back is the proof. It marks the comment, and refuses a thread already answered or refused, so none is answered twice. It also refuses a thread on no roster group, one while the plan page does not answer, and a discussion. `refuse --issue N --reason-file F` records a refusal the same way.

Alternatives, and why each lost (`fixer.md` step 17):

- **A committed path under `docs/`.** It would need a commit to `main` at every sweep, each a pull request through the gate, for a generated file.
- **Pages from a push to the state ref.** Workflows run from the pushed commit's own tree, and the orphan state ref carries no `.github/`, so a `push:` trigger there never fires.
- **A `schedule:` trigger.** It runs 48 deploys a day whether or not the plan moved, and it changes the trigger set `tests/entities.py` pins to release tags plus dispatch.

The dispatch keeps that pinned set. One existing behaviour changes: a dispatch now serves the newest release's docs rather than the dispatched ref's. That matches the workflow's stated design ("the served page is the release HACS installs") and keeps a plan refresh from publishing main's unreleased docs. The owner may prefer otherwise; this is the change to review.

## Head

9a865c7bc2cf3b2a5e43c369064d3bf8ac5c8260. It is the merge dbc10bf73e68d6792e6608ea00920d34154cba73 of `origin/main` at 28482eceeb6b9809e44b12d80fc994282cc21645 (2026-11-06T21:55:18Z) into the branch, plus one commit that only adds the three new files to `tests/closures.json`'s `inert_reads` (`python3 tools/pr/ci_predict.py --base origin/main --apply-inert`). Every figure below was taken at the merge head, which has the same tree outside that file, unless it names another.

`tools/pr/prepr.sh` passed at this head (`PRE-PR: 9a865c7bc2cf3b2a5e43c369064d3bf8ac5c8260 ... rc=0`), and `origin/main` had not moved from 28482eceeb6b at the handoff, so no second merge or run was owed.

## Mutation proof

Every arm is pinned by an in-tree mutant that its own self-test runs, so CI re-runs each one; the `tests/entities.py` check was mutated by hand.

- `python3 -I tools/audit/seat/outside_intake.py --self-test`: 11 mutants in `outside_intake_selftest.py` `MUTANTS`, each killed by its named case. Two examples: `answer_twice` (drop `or t.answered` from the already-disposed refusal) is killed by "answer: an answered submission is refused and no longer listed (never answered twice)"; `forged_marker_read` (read a marker in the submitter's own comment) is killed by "list: a marker in the submitter's own comment disposes of nothing (#3226 owes triage)".
- `python3 -I tools/audit/seat/plan_public.py --self-test`: 4 mutants (`string_order`, `leak_published`, `attribution_published`, `absent_refused_red`), each killed by its named check.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: 5 new mutants (`pages_never_dispatched`, `pages_always_dispatched`, `pages_refusal_silent`, `outside_lines_dropped`, `outside_rc2_clean`), and `plan_rc1_silent` re-keyed to the restructured predicate. The run prints `136 checks, 0 failed`; a surviving or stale mutant is a failed check.
- `tests/entities.py` "the Pages workflow stages the round's plan page before it checks out the newest release, and adds it under plan/ only when one was staged": its function was driven over three mutants. With `--sort=-v:refname` changed to `--sort=-refname` it reads "the release checkout took 'v1.9.0' (rc=0), not v1.10.0". With the add step's `if [ -f ... ]` changed to `if true` it reads "with no staged page, the add step put something at _site/plan". The step as first written (`cmd; rc=$?` under the runner's errexit) reads "the plan stage step exits 2 when plan_public.py exits 2".

## Null control

- At the merge base, `pages.yml` has none of the three plan steps. The new entities check, driven over `git show origin/main:.github/workflows/pages.yml`, returns `a plan step is missing: [...]`, and over the head returns `[]`.
- No outside activity: `listing` over an empty world prints nothing and moves the cursor to now (case "list null").
- An already-current state ref dispatches nothing (case "plan-beat null").
- A clean page is staged with rc 0 ("a clean page at the newest state ref is staged"). `stage` over the live round-10 state ref printed `plan_public: round 10 PLAN.html from origin/handoff/audit-r10-plan -> plan/index.html`, which is the production page passing the privacy refusal.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- Scoped gate: `GATE_SCOPE=auto bash tests/run.sh` at this head: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, `ALL 2638 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, rc 0.
- `python3 -I tools/audit/seat/outside_intake.py --self-test`: `outside_intake self-test: all checks passed` (18 cases, 11 mutants).
- `python3 -I tools/audit/seat/plan_public.py --self-test`: `plan_public self-test: all checks passed` (9 checks, 4 mutants).
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 136 checks, 0 failed`.
- `python3 -I tools/audit/seat/beatd.py --self-test`: `beatd self-test: 119 checks, 0 failed`, run at the pre-merge head, after the job row was added.
- `python3 -I tools/audit/seat/sweep_render.py --self-test`: `sweep_render self-test: 34 checks, 0 failed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `119 self-testing, 119 wired, 0 unwired` and `0 index gap(s)`. Both new instruments are indexed in `INSTRUMENTS.md` and wired in `governance.yml`'s `instrument-self-tests` job.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget moved.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`, run at the pre-merge head.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. With `--budgets`, `orchestrator.md` reads 292 lines and ~4234 tokens against caps of 295 and 4251, and `standing-dispatch.md` reads 37 lines and ~507 tokens against 39 and 509.
  - The new obligations were paid for, not raised for. `orchestrator.md` dropped two motivation-only passages (the 2026-09-07 anecdote under "Your process is not", and the hand-rolled-loop history under "Look the instrument up"), which is `fixer.md` step 9's delete-on-sight class.
  - `standing-dispatch.md` dropped a clause restating that `set-stage` refuses unknown stages, and shortened two sentences.
  - Section 5b was kept, because RCA records cite it.
- `python3 -I tools/audit/seat/ref_privacy.py --check` and `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused` each. The fixtures spell the host paths they plant in split form.
- First live intake pass, read-only. `outside_intake.py list --repo tvofi/heatpump_optimizer --since 2026-11-01T00:00:00Z` at the pre-merge head printed three lines:
  - `OUTSIDE #3224 owed=triage pr by=Bankaifan since=2026-11-05T09:45:08Z`
  - `OUTSIDE #3226 owed=triage pr by=Bankaifan since=2026-11-05T11:36:11Z`
  - `OUTSIDE plan-page UNAVAILABLE URLError; 1 answer(s) wait`

  The wait is #3225, which is in R10-COMBI-TANK's `issues` on the roster ref. This environment's proxy refuses `tvofi.github.io` and the numeric-ID pagination links GitHub returns, so the run went through a scratch `gh` shim that pages by `&page=N`. The readings:
  - #3224 (adopted via #3231) and #3226 (adopted via #3232) owe triage because neither number is wired into any roster group. Their adoption PRs merged under groups whose `issues` do not name them. The sweep's action is `roster_edit.py wire-issue <group> 3224` and `... 3226` through the roster seat; this PR edits no roster.
  - #3225 waits for the page. Once this merges and a dispatch deploys it, `answer --issue 3225` is owed.

## Red checks

`tests/entities.py` went red locally at the head 36313431c. The check was "no errexit `run:` block reads `$?` after a bare producer" (R10-RCA-HOTFIX-BATCH-ERREXIT A), on the new "Stage the round's plan page" step. It was fixed in this branch before any pull request existed. The cheaper detector already exists: it is that census, and it ran in the scoped gate as intended, so no new countermeasure is owed. The plan check now also drives the step under `-eo pipefail`.

## Unpinned sites

none: the diff touches no `custom_components/` file, the only tree step 6d inventories; the `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at this head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
