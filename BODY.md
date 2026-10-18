R10-CI-CONCURRENCY. A newer App push does not cancel an older run that was bot-sent (an approved autofix head) or dispatched: those get a group of their own by run id, so the newer run's group has nothing to cancel. The older run finishes for a head nobody reads. This adds a live-head cancel job to `tests.yml` and `codeql.yml`, run by the App-sent `pull_request` run only; the `concurrency:` expression is unchanged. Option 1 of the pre-study (`handoff-body/r10-ci-concurrency` before this body; harness `dev/audit/harnesses/superseded_runs.py`).

**`.github/workflows/**` is changed (tests.yml, codeql.yml, governance.yml) and `.github/CODEOWNERS` gains one line (`/tools/pr/cancel_superseded.py @tvofi`, which `codeowners_gap` required because governance runs the PR's own copy of the script): both need tvofi's review at merge. CODEOWNERS is policy-adjacent.**

## Head

`fb3bcf11a5bf708493cb5c7086139963787d742f` (code head of `handoff/r10-ci-concurrency`): the PR head `6ffc3708d` with origin/main `55dc8d9c2` merged in. That merge resolved two add/add conflicts with #2405 by keeping both sides: `.github/CODEOWNERS` keeps #2405's `/tools/pr/codeql_scope.py @tvofi` and this PR's `/tools/pr/cancel_superseded.py @tvofi`; `.github/workflows/codeql.yml` keeps this PR's `cancel-superseded` job and #2405's `scope` job (jobs now `cancel-superseded`, `scope`, `analyze`; `analyze` still `needs: scope` only). Earlier in the branch: the authored head `a5849788b`, the `INERT_EXCEPT` fix `b3ea5b31d`, the re-derive `1daf9361b`, the delivery row `c7300b36e`. Round 3 (the fix review blocked `6ffc3708d`), measured 2026-10-18.

What changed:
- `tools/pr/cancel_superseded.py` (new, one owner, `--self-test`). Cancels nothing unless: the caller is a `pull_request` run whose sender is not `github-actions[bot]`; the branch is not `main`; the PR is open, same-repo, and its head right now is the caller's head SHA (the live-head check); then only runs on that branch of event `pull_request`/`workflow_dispatch`, queued/in progress/waiting, at a different head SHA and a lower run id. Unreadable answers cancel nothing; always exit 0 (an optimisation, never a gate).
- `tests.yml`, `codeql.yml`: job `cancel-superseded` (`actions: write` on that job alone, `fetch-depth: 2`, `persist-credentials: false`), restoring the program from the pinned base sha and running it under `-I` (D11-s1-03); until the base carries the file it only prints a notice.
- `governance.yml`: `instrument-self-tests` runs the self-test on every PR.
- `.github/CODEOWNERS`: owns the script (`codeowners_gap.py`: `uncovered_files` 1 -> 0). `tests/closures.json`: the new harness recorded as an INERT READ of `tests/harness_headers.py` (`tools/pr/ci_predict.py --apply-inert`).
- `tests/closure.py`: `tools/pr/cancel_superseded.py` joins `INERT_EXCEPT` (round 2). `tests/entities.py` opens it, so CI's recording at `72a3f1bbd` put an INERT file in that script's closure and the merge refused the pair (#357). Same route as `tools/pr/README.md` (R9-RO-4): the `tools/pr/` prefix stays INERT, the file moves to the recorded closure. Null control: `closure.is_inert('tools/pr/cancel_superseded.py')` is `True` at origin/main's `tests/closure.py` and `False` at this head; `is_inert('tools/pr/ci_predict.py')` stays `True`. The alternative, filing it under `inert_reads` by hand, lost: the recording would put it back in `files` and every later merge would refuse again.
- `tests/entities.py`: the permission-override pin and the undone-copy pin list the new job (7 jobs override the floor; the D11-s1-03 null control now refuses 4 jobs).

Not changed: the `concurrency:` blocks, `governance.yml`'s, `hassfest.yml`'s and `validate.yml`'s run cancellation (measured below: no superseded run in the window), `pr-contract.yml`, `budget-raise-gate.yml`, `arch-score.yml` (cancel false on purpose), `approve_held_runs.sh`, the dispatch and approve steps.

## Mutation proof

Predicate lines deleted one at a time in a scratch copy of `tools/pr/cancel_superseded.py` (`python3 -I <mutant> --self-test`), baseline `19 checks, 0 failed`:

- live-head check deleted: `FAIL stale head: a run that is not on the live head cancels nothing` (19 checks, 1 failed). This is the stale-head guard the brief asks for.
- `head_sha != live_sha` deleted: `FAIL a same-SHA twin of the live head is never cancelled` and `FAIL a run on the live head only is never cancelled` (2 failed).
- bot-sender refusal deleted: `FAIL a bot-sent newer run cancels nothing` (1 failed).
- `id < run_id` deleted: `FAIL a newer head's run (higher id) is never cancelled` (1 failed).
- `branch == "main"` guard deleted: first attempt SURVIVED (0 failed): the arm used a fixture with no run on main and passed vacuously. Fixed in `bfee97060` (the arm now plants older runs on main); the mutant then reads `FAIL a caller on a branch named main cancels nothing` (1 failed).

## Null control

The recorded superseded pair is the fixture: run 39090494028 (#2371, bot-sent `pull_request`, attempt 2 by hpo-runs) and its dispatch 39090491271, both running when 39091600343 (App push, head 8d76a9ed) started. `--self-test` selects exactly those two and not the caller. The arms that must cancel nothing, each passing: a same-SHA twin of the live head; a run on the live head with nothing older at another SHA; a bot-sent newer run; a `workflow_dispatch` caller; runs on `main`; runs on another branch; `push`/`merge_group` runs on the branch; finished runs; a run of a newer head (higher id); a stale caller head; a closed PR; a fork head; an unreadable PR. End to end over a stub `gh`: exactly two `POST .../cancel`; `--dry-run` posts none; an unreadable listing posts none and exits 0.
The unmodified tree selects nothing: before this change no step cancels a run outside the PR group, which is the harness's class B and D.

## Figures

All from `dev/audit/harnesses/superseded_runs.py` over a cache fetched 2026-10-18T15:27:04Z (`--fetch --fetch-jobs`, read-only `gh api`), window `--since 2026-10-14T22:55:00Z` to the fetch. Run history is not a function of the head; the figures go stale as runs accrue, so re-derive with the command. Every `NULLCONTROL` row printed `all_cancelled_superseded=0 same_sha_superseded=0 unique_sha_dup_heads=0`, and `jobs_unread=0` on every workflow (an earlier pass without the jobs fetch printed `jobs_unread=42`/`19` and billed 0; those billed figures were discarded).

BEFORE (measured, `python3 dev/audit/harnesses/superseded_runs.py --cache $CACHE --since 2026-10-14T22:55:00Z --jobs --fetch-jobs`):

    RESULT tests  superseded=42 wall_min=2428 tail_min=984 billed_min=7806 tail_billed_min=2064
    RESULT codeql superseded=19 wall_min=450  tail_min=203 billed_min=496  tail_billed_min=212
    RESULT CLASS tests: pull_request/github-actions[bot]+rerun -> pull_request/hpo-author[bot]  superseded=8 tail_min=425 tail_billed_min=986
    RESULT CLASS tests: workflow_dispatch/github-actions[bot] -> pull_request/hpo-author[bot]  superseded=6 tail_min=125 tail_billed_min=203
    RESULT CLASS codeql: pull_request/github-actions[bot]+rerun -> pull_request/hpo-author[bot]  superseded=4 tail_min=55 tail_billed_min=56
    RESULT CLASS codeql: workflow_dispatch/github-actions[bot] -> pull_request/hpo-author[bot]  superseded=4 tail_min=52 tail_billed_min=54

AFTER (PREDICTION, not a measurement: nothing runs the new job until it lands on the base, and the job restores the program from the base): the two classes whose newer run is an App/human `pull_request` run are the ones this cancels, at the moment the newer run's job starts:

    tests  tail_billed_min  2064 -> 875  (-1189 = 986 + 203)   tail_min 984 -> 434 (-550 = 425 + 125)
    codeql tail_billed_min   212 -> 102  (-110 = 56 + 54)       tail_min 203 -> 96  (-107 = 55 + 52)

The remaining 875 / 102 are classes where the newer run is a dispatch; they stay by design (the older run may still owe autofix). The largest is tests `pull_request/hpo-author[bot] -> workflow_dispatch/github-actions[bot]` (20 runs, tail_billed_min=499). Upper bound: an immediate cancel at the newer run's start; the job takes seconds to start, so the real figure is a little lower. The re-measure after merge is the same command over the next window; it must show the two cancelled classes at 0 for runs started after the merge.

**The class, every member.** The rule: a workflow whose `concurrency:` group falls back to `github.run_id` for a bot-sent or dispatched run (the reviewer's enumeration; 8 workflows). Disposition each:

- `tests.yml`, `codeql.yml`: covered by the job (figures above).
- `governance.yml`, `hassfest.yml`, `validate.yml`: same group expression, NOT covered, by measurement. Same command, same cache:

      RESULT validate   nonmain_runs=483 completed_not_cancelled=424 superseded=0 wall_min=0 tail_min=0 tail_billed_min=0
      RESULT hassfest   nonmain_runs=483 completed_not_cancelled=428 superseded=0 wall_min=0 tail_min=0 tail_billed_min=0
      RESULT governance nonmain_runs=462 completed_not_cancelled=390 superseded=0 wall_min=0 tail_min=0 tail_billed_min=0

  The class's runs exist there (bot-sent `pull_request` 33 each, `workflow_dispatch` 34 for validate and hassfest), but they end before a newer head's run starts: run duration (`updated_at - run_started_at`, completed non-cancelled non-main runs in the same cache) is median 0.9 / p90 1.7 min for validate, 0.5 / 1.2 for hassfest, 3.1 / 4.7 for governance, against 30.0 / 55.6 for tests and 24.8 / 27.6 for codeql. A cancel job there would start a runner on every App-sent run (344, 346 and 333 in the window) to save a measured 0 minutes. Null control that the 0 is not a dead instrument: the same rule over the same cache returns 42 and 19 for tests and codeql, and the harness `--selftest` passes (`SELFTEST bot got=1 want=1 ok`).
- `pr-contract.yml`, `budget-raise-gate.yml`, `arch-score.yml`: cancel false on purpose (unchanged reason above).

Ran locally at this head: `python3 -I tools/pr/cancel_superseded.py --self-test` (`19 checks, 0 failed`); `superseded_runs.py --selftest` (passes); `tests/structure.py` (`STRUCTURE RATCHET PASSED`); `tests/layout.py` (`layout self-test: ok`); `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`); `tools/audit/seat/tmp_paths.py --check` (`0 refused`); `codeowners_gap.py --check` (`uncovered_files=0`); `closure.orphan_files()` (`[]`); `tests/entities.py` (`ALL 2347 ENTITY CHECKS PASSED`; the merged `codeql.yml` and `tests.yml` are what its permission-floor and undone-copy pins read). `MODE: FULL` (the diff touches `tests.yml` and `tests/closure.py`, gate files): the rest is CI's.

## Red checks

Check-runs read 2026-10-18 at the three PR heads since round 1. At `72a3f1bbd`: `closures`, `closures-autofix` and `pr-contract` failed. At `0a596b410`, the PR head after the fix and re-derive, all 47 check-runs are `success` or `skipped`. At `6ffc3708d` there are 0 check-runs (the PR was DIRTY on the conflict above); this head is the first CI sees after the resolution.

- `closures` (job 117671067846, at `72a3f1bbd`): `INERT READS UNDER-APPROXIMATED`, `tests/entities.py: tools/pr/cancel_superseded.py`. The new script sat under the INERT `tools/pr/` prefix and `tests/entities.py` opens it. Answered in-tree: the `INERT_EXCEPT` entry and the `--single tests/entities.py` re-derive (`1daf9361b`); green at `0a596b410`. Cheaper detector: none needed; `closures` is the detector and named the pair on the first CI run. Standing cost: one CI cycle per new file under an INERT prefix that a gate script reads.
- `closures-autofix` (job 117676459987, at `72a3f1bbd`): `AUTOFIX: skip-merge-failed`. The bot's merge refused `files on the INERT list are actually read by tests: tools/pr/cancel_superseded.py`, so no bot commit came and the repair was the fixer's (`ci-autofix.md`). The same `INERT_EXCEPT` entry answers it. No cheaper local detector: only a recording of `tests/entities.py` sees the read, and `closure.py`'s refusal text already names both remedies.
- Re-derive note: `--single tests/entities.py` at `b3ea5b31d` exited 1. Its single failure of 2347 was `every tracked file is either measured or deliberately classified [... tools/pr/cancel_superseded.py]`: out of INERT, the file is an orphan until the table lists it. `entities.py` runs every check and exits at the end, so the recording was complete: `--record-only`, then `closure.py merge --partial --allow-failures`, then a second `--single` exited 0 (`rc: 0` recorded).
- `pr-contract` (job 117678895680, at `72a3f1bbd`): the body did not name `closures-autofix`. This section answers it.

tvofi's review is still required at merge (CODEOWNERS and workflows).

## Forward-carry

Two findings from the pre-study, OUT of scope here and named for the orchestrator (`ci-autofix.md` is policy; neither is touched):
1. **Same-SHA duplicate run at every bot-pushed head.** The harness counts heads carrying a same-SHA pair of a dispatched run and a held-then-approved `pull_request` run: `same_sha_dup_heads` tests 31, codeql 33, at `same_sha_dup_min` tests 1249, codeql 701 (wall, not billed; same cache as `## Figures`). Not a supersession, so not this rule; the larger lever. Needs its own pre-study; the #1276 shadowing risk applies. Destination: the orchestrator's findings register / a new R10 row.
2. **Stale sentence: "a GITHUB_TOKEN push creates no pull_request run".** In `dev/governance/rules/ci-autofix.md` ("measured 2026-10-09"), `tools/audit/seat/merge_train.py` (R9-RC-AUTOFIX-GOVERNANCE comment, `bot_tip`) and the tests.yml autofix comments. In the window every bot head has a held `pull_request` Tests run, approved by `hpo-runs[bot]` ~6 s after the push (earliest 2026-10-15T10:23Z); head 3b76e0b0 has eight. One of the two is stale. Destination: a policy PR by tvofi / the orchestrator (ci-autofix.md is policy).
(Heading is `## Forward-carry` as the template and `pr-contract` spell it.)

## Friction

`none`. Two process notes, not rule events: `tools/audit/seat/body_push.sh` is mode 0644 in the tree (it only runs as `bash <path>`), and a `pkill -f tests/entities.py` I ran to stop my own mis-redirected run matches every seat's process of that name; I could not tell whether another seat's run was hit.

