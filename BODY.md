#2965 section 3, item C5 (owner, 2026-10-29: "It should be clear I want all the optional changes as well"). Refs #2965; it does not close it, because #2965 tracks the owner-only catalog submission.

Today `hassfest.yml` and `validate.yml` run only as `ci.yml` units, and only when the prelude's `workset` names them. So `main` can go weeks without a current run for the catalog PR to link. The new `.github/workflows/marketplace.yml` calls both unit files every week (cron `41 3 * * 1`, Mondays 03:41 UTC) and on `workflow_dispatch`, the same way `ci.yml` does: the caller id is the file's stem, the job grants `contents: read`, and it passes no inputs and no secrets. The job bodies, the pinned action SHAs and hassfest's image-pull warm-up retry are therefore the ones CI runs, not a copy. A schedule runs `main`'s tree. Nothing sets `continue-on-error`, so a scheduled red shows up as a failed run. `tools/ci/gate.py` reads only `ci.yml`'s runs (`actions/workflows/ci.yml/runs` at the head SHA), so a run of this file is never a source for `gate`.

**Code-owned:** this diff touches `.github/workflows/`, so it needs `@tvofi`'s approving review.

**C6 (D10.md Marketplace-readiness item) is NOT in this diff. It is blocked on a budget raise that only the owner can confirm.** `dev/governance/config/policy_budgets.json` caps `D10.md` with zero headroom, at 43 lines (`files`) and 574 tokens (`files_tokens`), exactly its size at `e5ddba1fa`. The drafted item adds 24 lines; `policy_lint.mjs` reports 67 lines and about 937 tokens against those caps. No payment is available. The brief forbids rewriting the owner's words in D10.md, and a per-file cap cannot be paid from any other file. No mandate is in force either: the one HANDOVER.md records, 6175172275 (scope `all`), ended 2026-10-28T18:14Z. CLAUDE.md rule 2 and fixer.md require the owner's confirmation before pushing a raise, so I am asking for it here instead of pushing one. The C6 change, when confirmed, is policy: **this changes what a seat must do**, and it needs the owner's approving review. It would add step 4 to D10.md's Method and leave steps 1-3, the owner's brief quote and the developers.home-assistant.io URL untouched. It would also raise D10.md's `files` and `files_tokens` caps to the measured size, giving the reason in the commit message. The draft step 4 has five checks: the downloaded archive (the release asset when `zip_release` is set, else the tag archive) unpacked, against HACS's `MAX_DOWNLOAD_SIZE` (100 MiB) and the 50,000-file limit; `manifest.json` `categories` (one to three known values); every `hacs.json` key documented upstream; the HACS action and hassfest green at the round's baseline (a `marketplace.yml` run, or `ci.yml`'s units, at that SHA); and the catalog listing state. Its citations still have to satisfy `policy_lint.mjs`'s citation class: `marketplace.yml` must be cited by its full path, and `zip_release` / `MAX_DOWNLOAD_SIZE` need an upstream anchor.

## Head

`aa59012563e5dc2a43b87eae6ddf0fd1723f0b14` on `handoff/r10-marketplace-extras`, one commit on `origin/main` `e5ddba1fad5e6eccfeceaeaaa249bc459963405b` (merge base; 0 commits behind when measured, 2026-10-29).

## Mutation proof

Production line mutated: `marketplace.yml`'s `uses: ./.github/workflows/hassfest.yml` was changed to `uses: ./.github/workflows/hasfest.yml`. This is the brief's "wrong workflow path", and it breaks the schedule's call. Run in a detached worktree at the head with `PYTHONPATH=tests/hastub python3 tests/entities.py`: `1 of 2473 ENTITY CHECKS FAILED`. The one failing check is `marketplace.yml runs CI's own hassfest and validate units weekly and on dispatch, read-only, a red never hidden (#2965 C5)`, with `defects=['hassfest: uses ./.github/workflows/hasfest.yml']`. Restored, the same command passes all 2473. The check also carries seven in-file plants that it must each name: a wrong workflow path, a caller off its stem, no schedule, a monthly cron, `continue-on-error`, a widened grant, and inherited secrets. A plant the reader misses reddens the check (`_MP_PLANT_MISSED`).

## Null control

At the head, unmutated, `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2473 ENTITY CHECKS PASSED`, including `ok marketplace.yml runs CI's own hassfest and validate units …` and `ok marketplace.yml is not a gate file, and is classified`. On the mutant above, the same check fails and no other check moves.

**The brief's dispatch control could not be run before merge.** `actions_run_trigger run_workflow marketplace.yml --ref handoff/r10-marketplace-extras` returns `404 Not Found`. `list_workflows` does not list `marketplace.yml`: GitHub registers a workflow for dispatch only from the default branch, and this head was pushed to a ref that fires none of its triggers. I did not dispatch `ci.yml` at this head as a substitute: `gate.py` reads `ci.yml` runs at a head SHA, so a stray run there would become a gate source for this PR. Owed after merge, by the orchestrator: `gh workflow run marketplace.yml --ref main`, then cite the run id and the `hassfest / hassfest` and `validate / validate-hacs` conclusions on #2965 for the catalog PR.

## Figures

Environment: the default `python3` was 3.11, which cannot parse `tests/entities.py`; every script below ran in a 3.13 venv built from `tests/requirements-ci.txt`.

- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; run = `tests/entities.py`, `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (python 3.13 venv from `tests/requirements-ci.txt`): `ALL 2473 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, wave-script or instrument red predicted against e5ddba1fad5e`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/brief_lint.mjs`: rc 0 at the merge base and at the head. The only output difference is one archived W1-G14 citation's "found at line" number, which moves because `tests/entities.py` grew (an error that already existed at the base).
- `node tools/policy/policy_lint.mjs`: output identical to the merge base's with C6 left out. With the C6 draft applied: the 2 budget errors and 4 citation errors quoted above.
- Class rule (step 8): every caller of the two unit files is enumerated by `grep -rn "workflows/\(hassfest\|validate\).yml" .github/workflows/`. The callers are `ci.yml` (`hassfest`, `validate`; pinned by the umbrella checks) and `marketplace.yml` (`hassfest`, `validate`; pinned by the new check). There are no others.

## Red checks

none

## Forward-carry

none

## Friction

none
