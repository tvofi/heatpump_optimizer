_Requested by **tvofi**_

Make cancellation of a superseded CI run mechanical. Part of the CI-efficiency request of 2026-10-02; no issue.

Every pull-request workflow's `concurrency` block already cancels per PR. But 14 jobs in `.github/workflows/tests.yml` carried a job-level `if: always() && (...)` (`closures` a bare `always()`). GitHub keeps running a job whose `if` is true through `always()` after the run is cancelled, so a superseded run kept `fast`, `coverage`, `mutation` and the rest going and the newer run sat `pending` in the group (34 min on #1845). `always()` was there because `needs: [recheck-gate]` / `[closure-scope]` are skipped outside `workflow_dispatch` / `pull_request`; `!cancelled()` keeps that skipped-dependency behaviour and honours the cancel.

Change: job-level leading `always()` becomes `!cancelled()` in `fast`, `browser`, `briefs`, `typing`, `coverage`, `coverage-ratchet`, `mutation`, `mutation-nightly`, `slow`, `graders-head-copy`, `closures`, `closures-autofix`, `claims-autofix`, `mutation-autofix` (14). Single-line forms are written `${{ !cancelled() ... }}` because a plain YAML scalar cannot start with `!`. Step-level `if: always()` (artifact upload, cache save, report steps) is untouched. `tests/entities.py` gets one new check, and its `_if_under` reader learns `!cancelled()` (it would otherwise read the required contexts as undecidable and fail the merge-queue and `edited` checks).

Other workflows: `governance.yml`, `pr-contract.yml`, `codeql.yml`, `validate.yml`, `hassfest.yml` and `budget-raise-gate*.yml` have no job-level `always()`, only step-level; nothing to change there.

The three `*-autofix` jobs: skipping them on a superseded head loses no repair. Each is gated on `needs.<job>.result == 'failure'`; a cancelled upstream job has result `cancelled`, so under `always()` they were already skipped on a cancelled run, and `!cancelled()` changes nothing for them except stopping the case where only the autofix job itself is still queued. Their repairs push as `github-actions[bot]`, which the top-level `concurrency` puts in a group of its own keyed on `run_id` with no cancel, and the newer head's run re-runs the same check and repairs it itself. `ci-autofix.md` is unaffected.

## Head

179a8c2a45c7496332f2e5b7a58d820719eaea9e

## Mutation proof

Predicate mutated, not the tail: `fast`'s `!cancelled()` put back to `always()` in `tests.yml`, the new check's predicate run over the parsed workflows. Run on the Mac (no numpy, so the whole of `entities.py` cannot run locally) by extracting the check's own `_ca_bad`, `_if_under` and the `_RC_DOCS` loading from `tests/entities.py` text and executing them over `.github/workflows/*.yml`:

- head: `bad []`, `!cancelled()` jobs 14.
- `fast` reverted: `bad ['tests.yml:fast']`, 13 jobs: the check "no job-level `if` leads with `always()`" goes red.
- restored: `bad []`, 14.

The full `entities.py` run is CI's.

## Null control

At `origin/main` every one of the 14 jobs leads with `always()`, so the new check fails there (the reverted-`fast` line above is the one-job case). The check's own null control feeds `always() && a` and `${{ always() }}` (both refused) and `!cancelled() && a` (accepted). `_if_under` reads `fast` as True under `pull_request`, `push` and `merge_group`, and `closures` as True, so the required-context checks still see them as running.

## Figures

- 14 jobs: `grep -nE '^\s+(always\(\)|!cancelled\(\)|if: \$\{\{ !cancelled)' .github/workflows/tests.yml` against the job list; the check pins `>= 14`.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Code-owned CI wiring (`.github/workflows/tests.yml`, `tests/entities.py`). Needs tvofi's approving review at the head above; no mandate is claimed here.

## Verification after merge

Owed to the orchestrator, not run here: open a scratch PR and push twice in quick succession. Expected: the first run's `fast` ends `cancelled` within about a minute, and the second run does not sit `pending` in the group.

Not run locally: `tests/entities.py` in full and the scoped gate (no numpy on this Mac; CI is the authority).
