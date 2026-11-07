R10-OUTSIDE-INTAKE. The owner's ruling (tvofi 2026-11-06), verbatim: "the plan html for an ongoing round should be made publically available from a suitable place in the developer documentation on the repo. During future audit rounds, issues, PRs or other posts from outside users should be regularly checked, triaged/designed and planned. Fold this shape into the repo machinery. When the plan html is done, and any outside submission is on the roster, the plan HTML should be linked in an answer to the outside submission."

**Policy and developer docs change: this merges only on tvofi's approving review** (`orchestrator.md` section 5, `standing-dispatch.md`, `dev/programme/HANDOVER.md`). The ruling approves the shape in principle. The review is the approval.

What lands, by the brief's three parts:

1. **Public plan page.** `tools/audit/seat/plan_public.py stage` takes `PLAN.html` from the newest `origin/handoff/audit-r<N>-plan` state ref (the layout `state_docs.state_of` owns) and writes `plan/index.html`. `.github/workflows/pages.yml` runs it from the dispatched ref's tree. It then checks out the newest `v*` tag for the docs and adds the page, served at `https://tvofi.github.io/heatpump_optimizer/plan/` (`plan_public.PLAN_URL`, the one spelling of the URL). The beat's `plan-beat` row dispatches `pages.yml` on `main` after each state push that landed. `dev/programme/HANDOVER.md` links the page from the head of its Round 10 section; no user doc links it. If `ref_privacy` reads a host path, account name, uid, scratch root or a tool's attribution in the page, it refuses the page (rc 1: the deploy goes red and nothing is published). With no state ref, or no `PLAN.html` at the newest one, it stages nothing (rc 2): the site deploys without a plan and warns. A closed round's state ref is not retired until `closeout.py --apply`, so until then the newest closed round's page is served; that is the round-4 verdict's finding (`## Re-cut note`), not a property this PR claims.
2. **Intake as machinery.** `tools/audit/seat/outside_intake.py list` lists threads (issues, pull requests and discussions, which share one number space). It lists a thread when it has activity at or after a cursor by an author who is outside `OURS` and not a bot. It prints the `OUTSIDE #N owed=triage|answer|reply` lines owed this turn. Disposition is read from the roster (`issues`/`fixes`, wired by `roster_edit.py wire-issue`) and from marker comments by our accounts, never from memory. The new beat row `outside-intake` [1800 s] runs it with a cursor under the digest's `state/` and writes its lines to the digest. Sweep step (5b) in `sweep_template.md` names the action for each line. `orchestrator.md` section 5 and `standing-dispatch.md` each carry the short obligation.
3. **Answer step.** `outside_intake.py answer --issue N` posts the plan link through `tools/pr/gh_comment.py post`, whose read-back is the proof. It marks the comment. A marker is read only from a comment by an account in `OURS`, and only `saw()` moves a thread's outside activity, so a third-party bot's comment is neither ours nor outside activity. It refuses a thread already answered or refused, so none is answered twice. It also refuses a thread on no roster group, any thread while the plan page does not answer, and a discussion. `refuse --issue N --reason-file F` records a refusal the same way.

Alternatives, and why each lost (`fixer.md` step 17):

- **A committed path under `docs/`.** It needs a commit to `main` at every sweep, each a pull request through the gate, for a generated file.
- **Pages from a push to the state ref.** A workflow runs from the pushed commit's own tree. The orphan state ref carries no `.github/`, so a `push:` trigger there never fires.
- **A `schedule:` trigger.** It runs 48 deploys a day whether or not the plan moved. It would also change the trigger set `tests/entities.py` pins (release tags plus dispatch).

The dispatch keeps that pinned set. One existing behaviour changes: a dispatch now serves the newest release's docs rather than the dispatched ref's. That matches the workflow's stated design ("the served page is the release HACS installs"), and it keeps a plan refresh from publishing main's unreleased docs. The owner may prefer otherwise; this is the change to review.

## Re-cut note

Round 5, the minimal re-cut owed past three rounds (`fixer.md`, "Past three rounds, re-cut rather than repair"): one self-test case plus two mutants, answering the round-4 block (`verdict/3262`, mutation-vacuous: `plan_public.py` stage's host identity default and `main()`'s exit status survived the self-test). The round-3 block (`one_thread`'s review-comment read) stays cured and untouched. The only production-adjacent file changed in this round is `tools/audit/seat/plan_public.py`, and only its self-test and `MUTANTS` table:

- The case "the CLI over a scratch repository" runs `main(["stage", "--out", D, "--repo", R])` with no ident, as `pages.yml` does, over a scratch repository built by `throwaway_git_init`, whose `refs/remotes/origin/handoff/audit-r10-plan` holds `handoff/round10/state/PLAN.html`. Three arms: a clean page gives rc 0 and the page staged byte-identical; a page naming another account's home gives rc 1 and nothing staged; no state ref gives rc 2 and nothing staged. An exception counts as a failed arm, so a crashing mutant fails its case instead of aborting the self-test.
- Mutants `host_ident_dropped` (`refusal`: `ident or ref_privacy.Identity.of_host()` made `ident`) and `main_rc0` (`main`: `return rc` made `return 0`).
- The mutation runner mutated only the code above the `MUTANTS` table, so `main()`, below it, could not be mutated. It now mutates everything but the table, and an old string must occur exactly once outside it.

The round-4 verdict's other findings are left out of this minimal re-cut, as the brief directs, and stay where that verdict (`verdict/3262`, `## Findings`) records them, each under its own `Carry:` line: the false "between rounds there is no state ref" sentence in `plan_public.py`'s docstring and `pages.yml`'s header (R10-OUTSIDE-INTAKE; this body no longer states it), the recurring edit-run deferral `gate` reds (R10-HOTFIX-GATE-BUSY-DEFER), and the surviving `outside_intake.py` mutants `scan_disc_kind` and `owed_reply_ge` (R10-OUTSIDE-INTAKE). This seat's brief forbids writing the roster branch that lands them.

## Head

`f69a1caf9c3de0b4d1f9ae663f58f0dbf55a534c`, on top of the round-4 code head `28f9f11bb0e302cfd4920bb1e50384c4db9633a6` (tree-identical to the PR head `aa5022f63cac715abe871d168d2ed250997261e7`). Its commits: `7a603a1f0`, a clean merge of `origin/main` at `28d46c4918285d36c409c1fb2f72eb77e04e569e`; `78389d732`, the round-5 change above; `22e1f930f`, which builds the case's scratch repository with `tests/throwaway_git.py`'s `throwaway_git_init` after `prepr.sh`'s throwaway-git lane refused the raw `git init` (`python3 -I tests/throwaway_git.py --check` now prints `0 raw git init or clone site(s) refused`); and `f69a1caf9`, a clean merge of `origin/main` at `a37c58e5f32123b4028e90983799dc2aa81816f8`, because main moved during that `prepr.sh` run. The merge base is `a37c58e5f32123b4028e90983799dc2aa81816f8`. Every figure below was taken at this head. `origin/main` was `a37c58e5f32123b4028e90983799dc2aa81816f8` before and after the clean `prepr.sh` run below, so no further merge was owed.

## Mutation proof

Failing test first: with the two `MUTANTS` entries and the runner change in place but the case not yet written, `python3 -I tools/audit/seat/plan_public.py --self-test` gave rc 1 with exactly two failures, `FAIL mutant host_ident_dropped killed by: the CLI over a scratch repository: a clean page is staged, rc 0` and `FAIL mutant main_rc0 killed by: the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written`. With the case added, the same command gives rc 0 and `plan_public self-test: all checks passed`, printing `ok   mutant host_ident_dropped killed by: the CLI over a scratch repository: a clean page is staged, rc 0` and `ok   mutant main_rc0 killed by: the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written`.

The kill is read from the case's own `FAIL` line in the mutant's cases-only output (`mod.self_test(mutants=False)`), so the stale-mutant check cannot stand in for it.

The round-4 reviewer's 18-mutant set (`verdict/3262` `evidence/mut_pp.py`), re-run with its apply step widened to mutate the whole file but the `MUTANTS` table, in a detached worktree at the head, both cases-only (`self_test(False)`) and full (`self_test(True)`):

| mutant | at round 4 | at this head |
|---|---|---|
| `host_ident_dropped` | SURVIVED | KILLED: `the CLI over a scratch repository: a clean page is staged, rc 0` |
| `main_rc0` | not applied (below the table) | KILLED: `the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written` |
| `main_repo_cwd_ignored` | not applied (below the table) | KILLED: `the CLI over a scratch repository: a clean page is staged, rc 0` |
| `int_dropped`, `max_to_min`, `regex_no_end`, `html_check_off`, `leak_off`, `attribution_off`, `refused_rc0`, `absent_rc1`, `noref_rc0`, `write_empty`, `dest_name` | KILLED | KILLED |
| `html_case_sensitive`, `rc_ignored_refs`, `show_rc_ignored`, `empty_text_published` | SURVIVED | SURVIVED |

The four survivors are the ones the round-4 verdict classed equivalent or near-equivalent, each for its stated reason: `plan_page.py` writes a lowercase `<!doctype html>`; a failed `for-each-ref` prints nothing; a failed `git show` prints nothing on stdout; an empty page moves from rc 2 to rc 1, refused either way. Every non-equivalent mutant of the set is killed. Count rule: `grep -c KILLED` over each run's output prints 14 for both runs. The runner's first-`FAIL` column for `main_rc0` names another line; applied by hand, its cases-only output fails exactly the CLI case's rc 1 and rc 2 arms, so the kill is the named case's.

## Null control

- The unmutated runner baseline: `NULL(full=False) rc=0` and `NULL(full=True) rc=0`, each `plan_public self-test: all checks passed`, so each kill above is its mutant's.
- The script driven as `pages.yml` drives it, outside the self-test (`verdict/3262` `evidence/drive_pp.sh` against this head's tree): `clean page: rc=0  staged=yes`, then `plan_public: REFUSED: round 10 PLAN.html: host-path in the page` and `leaky page: rc=1  staged=no`. The case's arms agree with the real CLI.

## Figures

- `python3 -I tools/audit/seat/plan_public.py --self-test`: rc 0, `plan_public self-test: all checks passed`, with 18 `ok` lines (`grep -c '^ok'`): 12 cases and 6 `mutant` lines. Round 4 had 9 and 4.
- `python3 -I tools/audit/seat/outside_intake.py --self-test`: rc 0, `outside_intake self-test: all checks passed`, 48 `ok` lines (`grep -c '^ok'`), unchanged from round 4 because this round edits no file it reads.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- Scoped scripts: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives `ALL 2646 ENTITY CHECKS PASSED` (rc 0). `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` gives `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No `*_budgets.json` is in the three-dot diff (`git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c budgets.json` prints 0).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tools/audit/seat/ref_privacy.py --check`: `0 refused`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`. `python3 -I tools/audit/seat/selftest_wiring.py --check`: `120 self-testing, 120 wired, 0 unwired` and `0 index gap(s)`.
- `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are byte-identical to `origin/main` (`git diff --quiet origin/main HEAD -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo BYTE-IDENTICAL` printed `BYTE-IDENTICAL`).
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check`: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. No golden was run, because the diff touches none.
- `tools/pr/prepr.sh <body>` at `f69a1caf9`, run 2026-11-07T14:11:27Z to 14:22:48Z: `PRE-PR: f69a1caf9c3de0b4d1f9ae663f58f0dbf55a534c ... rc=0`, every lane `ok` or `skip`. The first run, at `78389d732` (13:49Z-14:00Z), was rc 1 on three lanes: `throwaway git` (the raw `git init`, cured by `22e1f930f`), `self-test` (`511 passed, 2 failed`, both in the throwaway-git check's own null control, which reads the tree and went green with the same cure), and `pr-body` (a `## Forward-carry` item named a path outside the tree, re-worded).

## Red checks

The PR head `aa5022f63cac715abe871d168d2ed250997261e7` holds 160 check runs in the `filter=all` read across both pages (`verdict/3262` `evidence/check-runs.tsv`, read at about 11:30Z; the latest-only read at 13:40Z returns 68, its newest run 128389156452 the tsv's first row, so no run was added after). `python3 -I tools/audit/seat/merge_train.py classify aa5022f63cac715abe871d168d2ed250997261e7 --pr 3262` at 2026-11-07T13:38Z: `GREEN aa5022f63cac715abe871d168d2ed250997261e7 pending: none red: none` (rc 0), so every concluded red below is classified away by a later concluded success of the same check, or is unrequired. The concluded reds, by literal check-run name (`awk -F'\t' '$4!="success"&&$4!="skipped"&&$4!="neutral"'` over the tsv prints these nine rows):

- **`tests / nightly-status` 128369432665 (09:45:58Z-09:46:09Z) and 128382846793 (10:49:52Z-10:50:04Z) concluded `failure`.** Each logs `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly failed in the last verification dispatch` and `dispatched run 42357667261, ... head 62bcca7, run conclusion 'cancelled'`. It grades `main`'s Nightly dispatch, which the orchestrator cancelled to free runners; the job checks `tests/nightly_status.py` out of the pinned main commit, and this diff does not touch it (`git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -c nightly_status` prints 0). It is unrequired, red for every open PR graded against that dispatch, and the check itself is the detector that named the cause: no countermeasure owed here.
- **`governance / instrument-self-tests` 128369432606 (09:45:57Z-10:16:12Z) concluded `cancelled`** at the job's 30-minute timeout, the owner's standing line (R10-HOTFIX-SELFTEST-TIMEOUT, cure R10-PROCESS-SLIM, #3245). The same job, 128382846790 (10:49:52Z-11:17:08Z), concluded success at this tree. No cheaper detector exists.
- **`pr-contract / pr-contract` 128378515649 (10:29:02Z-10:29:49Z) concluded `failure`**: it refused an earlier body whose `## Red checks` omitted the nightly-status red. Superseded by 128382814711, 128388623658 and 128389122891, each success. The check is its own detector.
- **`gate` 128378686810 and 128378835497 concluded `failure`**, each with only `FAIL pr-contract / pr-contract: failure`: they repeat the `pr-contract` red above and cleared with it.
- **`gate` 128369699756 (09:47:09Z-09:59:21Z), 128382850917 (10:49:53Z-11:01:53Z) and 128382978616 (10:50:30Z-11:02:29Z) concluded `failure`**, each `KIND: edit` with the single line `FAIL run(s) [42361045445] at this head are still being judged; their gate decides`. This is the edit-run deferral red R10-HOTFIX-GATE-BUSY-DEFER (#3276, `cc100c275`) was meant to remove, and the base already contained it, so it recurs after that fix after a roughly 12-minute wait: a defect of the gate, not of this diff, which the round-4 verdict carries to that group. Superseded by `gate` 128388861998, 128389118396 and 128389122431, each success. The cheaper detector is the gate's own later run.

## Unpinned sites

none: the diff touches no `custom_components/` file, the only tree step 6d inventories. The `tools/` sites carry the in-tree mutants under `## Mutation proof`.

## Approval

Pending: tvofi's approving review at the head. The ruling of 2026-11-06 approves the shape in principle; the review is the approval this policy and developer-docs change merges on.

## Forward-carry

none

## Friction

none
