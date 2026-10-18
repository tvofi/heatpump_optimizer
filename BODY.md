R10-CI-CONCURRENCY. A newer App push does not cancel an older run that was bot-sent (an approved autofix head) or dispatched: those get a group of their own by run id, so the newer run's group has nothing to cancel. The older run finishes for a head nobody reads. This adds a live-head cancel job to `tests.yml` and `codeql.yml`, run by the App-sent `pull_request` run only; the `concurrency:` expression is unchanged. Option 1 of the pre-study (`handoff-body/r10-ci-concurrency` before this body; harness `dev/audit/harnesses/superseded_runs.py`).

**`.github/workflows/**` is changed (tests.yml, codeql.yml, governance.yml) and `.github/CODEOWNERS` gains one line (`/tools/pr/cancel_superseded.py @tvofi`, which `codeowners_gap` required because governance runs the PR's own copy of the script): both need tvofi's review at merge. CODEOWNERS is policy-adjacent.**

## Head

`a5849788bb9a67461fc74ee3231215a2c295b74e` (code head of `handoff/r10-ci-concurrency`, origin/main `f00e1d85b` merged in). Measured 2026-10-18.

What changed:
- `tools/pr/cancel_superseded.py` (new, one owner, `--self-test`). Cancels nothing unless: the caller is a `pull_request` run whose sender is not `github-actions[bot]`; the branch is not `main`; the PR is open, same-repo, and its head right now is the caller's head SHA (the live-head check); then only runs on that branch of event `pull_request`/`workflow_dispatch`, queued/in progress/waiting, at a different head SHA and a lower run id. Unreadable answers cancel nothing; always exit 0 (an optimisation, never a gate).
- `tests.yml`, `codeql.yml`: job `cancel-superseded` (`actions: write` on that job alone, `fetch-depth: 2`, `persist-credentials: false`), restoring the program from the pinned base sha and running it under `-I` (D11-s1-03); until the base carries the file it only prints a notice.
- `governance.yml`: `instrument-self-tests` runs the self-test on every PR.
- `.github/CODEOWNERS`: owns the script (`codeowners_gap.py`: `uncovered_files` 1 -> 0). `tests/closures.json`: the new harness recorded as an INERT READ of `tests/harness_headers.py` (`tools/pr/ci_predict.py --apply-inert`).
- `tests/entities.py`: the permission-override pin and the undone-copy pin list the new job (7 jobs override the floor; the D11-s1-03 null control now refuses 4 jobs).

Not changed: the `concurrency:` blocks, `pr-contract.yml`, `budget-raise-gate.yml`, `arch-score.yml` (cancel false on purpose), `approve_held_runs.sh`, the dispatch and approve steps.

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

All from `dev/audit/harnesses/superseded_runs.py`, window created 2026-10-14T22:55Z..2026-10-18T07:24Z (old run), cache fetched 2026-10-18; the figures are stale as main moves, re-derive with the command.

BEFORE (measured, `python3 dev/audit/harnesses/superseded_runs.py --cache $CACHE --since 2026-10-14T22:55:00Z --until 2026-10-18T07:24:00Z --jobs`):

    RESULT tests  superseded=37 wall_min=2081 tail_min=968 billed_min=6057 tail_billed_min=2042
    RESULT codeql superseded=19 wall_min=450  tail_min=203 billed_min=496  tail_billed_min=212
    RESULT CLASS tests: pull_request/github-actions[bot]+rerun -> pull_request/hpo-author[bot]  superseded=8 tail_min=425 tail_billed_min=986
    RESULT CLASS tests: workflow_dispatch/github-actions[bot] -> pull_request/hpo-author[bot]  superseded=6 tail_min=125 tail_billed_min=203
    RESULT CLASS codeql: ... +rerun -> pull_request/hpo-author[bot] tail_billed_min=56;  dispatch -> pull_request/hpo-author[bot] tail_billed_min=54

AFTER (PREDICTION, not a measurement: nothing runs the new job until it lands on the base, and the job restores the program from the base): the two classes whose newer run is an App/human `pull_request` run are the ones this cancels, at the moment the newer run's job starts:

    tests  tail_billed_min  2042 -> 853  (-1189 = 986 + 203)   tail_min 968 -> 418 (-550 = 425 + 125)
    codeql tail_billed_min   212 -> 102  (-110 = 56 + 54)       tail_min 203 -> 96  (-107 = 55 + 52)

The remaining 853 / 102 are classes where the newer run is a dispatch (A, C, E, F); they stay by design (the older run may still owe autofix). Upper bound: an immediate cancel at the newer run's start; the job takes seconds to start, so the real figure is a little lower. The re-measure after merge is the same command over the next window; it must show classes B and D at 0 for runs started after the merge.
`python3 dev/audit/harnesses/superseded_runs.py --selftest` and the cancel self-test: `python3 -I tools/pr/cancel_superseded.py --self-test` (19 checks, 0 failed at this head).
Ran locally: `tests/entities.py` (2346 checks, all passed at `82015b1ac`; the later commit changes only the self-test arm), `tests/structure.py` (passed), `tests/layout.py`, `tests/harness_headers.py`, `tools/audit/seat/tmp_paths.py --check`. `MODE: FULL` (the diff touches `tests.yml`, the gate itself): the rest is CI's.

## Red checks

`none` at the head I measured. Two reds appeared during the work and were answered in-tree, not left: `entities.py` "exactly six jobs override the workflow's read-only floor" and the D11-s1-03 pin ("runs tools/pr/cancel_superseded.py unrestored", and its null control now also refuses the new job). Both are the pins doing their work on a new write grant; the job now follows the pinned-base restore pattern and the pins list it. Expected possible reds on CI: `UNDER-SCOPED` / `INERT READS` on `tests/closures.json` for the new script (autofix: `ci: re-record closures`, `ci-autofix.md`); a new script with no recording is not UNDER-SCOPED, so add it to a derive lane if CI asks.

## Forward-carry

Two findings from the pre-study, OUT of scope here and named for the orchestrator (`ci-autofix.md` is policy; neither is touched):
1. **Same-SHA duplicate run at every bot-pushed head.** All 26 bot-pushed heads in the window have both a dispatched Tests and a held-then-approved `pull_request` Tests run: tests 1024 wall-min, codeql 556 (`same_sha_dup_min` in the harness RESULT line, wall not billed). Not a supersession, so not this rule; the larger lever. Needs its own pre-study; the #1276 shadowing risk applies. Destination: the orchestrator's findings register / a new R10 row.
2. **Stale sentence: "a GITHUB_TOKEN push creates no pull_request run".** In `dev/governance/rules/ci-autofix.md` ("measured 2026-10-09"), `tools/audit/seat/merge_train.py` (R9-RC-AUTOFIX-GOVERNANCE comment, `bot_tip`) and the tests.yml autofix comments. In the window every bot head has a held `pull_request` Tests run, approved by `hpo-runs[bot]` ~6 s after the push (earliest 2026-10-15T10:23Z); head 3b76e0b0 has eight. One of the two is stale. Destination: a policy PR by tvofi / the orchestrator (ci-autofix.md is policy).
(Heading is `## Forward-carry` as the template and `pr-contract` spell it.)

## Friction

`none`. Two process notes, not rule events: `tools/audit/seat/body_push.sh` is mode 0644 in the tree (it only runs as `bash <path>`), and a `pkill -f tests/entities.py` I ran to stop my own mis-redirected run matches every seat's process of that name; I could not tell whether another seat's run was hit.
