_Requested by **tvofi**_

Closes #1757 (R9-F11.7, the countermeasure from the #1721 RCA, `RCA-BULK-3.md` section 1).

`policy-docs` restores `.claude/workflows/*.mjs` from the base. A changed governance grader therefore ran for the first time under the Actions `GITHUB_TOKEN` on the push to main. For #1715 that meant a comparator reading `bypass_actors`, a ruleset field this token cannot see. A seat's local run cannot detect this either, because it reads the API with the seat's own identity. `graders-head-copy` covered only `coverage_ratchet` and `delivery_status`.

Change:
- `.github/workflows/tests.yml`, `graders-head-copy`: when the three-dot diff touches the pathspec that `policy-docs` restores from the base, the pull request's own `policy_lint.mjs` and `field_coverage.mjs` now run under this job's read-only token (workflow floor `contents: read`; the job adds no `permissions` block).
  - The job stays non-required, and `HPO_JOB_GRADES: nothing` is unchanged.
  - Each arm step's `if:` is exactly `${{ !cancelled() && steps.changed.outputs.governance == 'true' }}`.
  - Checkout gains `fetch-tags: true`, because `policy_lint.mjs`'s citation resolvers ask git about tags.
- `tests/entities.py`, five checks:
  1. **Class:** it derives every program that a base-restoring job runs, from its restored pathspec, in a step whose env carries a token. Each such program needs a `graders-head-copy` step that runs it with `GITHUB_TOKEN` and is keyed exactly as above, or a recorded reason in `_PT_EXEMPT`. A stale exemption is refused.
  2. **Pathspec:** the arm's pathspec must equal the restore pathspec of `policy-docs`.
  3. **Null control:** the arm's step without its token is refused.
  4. **Trigger behaviour (round 2):** the `changed` step's own script runs on planted one-file diffs in a scratch repository.
     - `.claude/workflows/x.mjs` and `tools/audit/round6/D11/fix/codeowners_gap.py` must yield `governance=true`.
     - `README.md` must yield `false`.
     - The job's `if:` must lead with `!cancelled()`, so that a red `coverage` (its `needs`) cannot skip the arm silently.
  5. **Null control:** the same script, with its firing branch rewritten to write `false`, yields `false`.

## Head

18ae7cb0a4e6acb942867980a50b4f862701a473

This head merges origin/main `03ba7f70f` (merge base; it contains the v6.7.14 stamp `754845d0`) into the round-1 PR head `f1a32a364`, which carries the delivery row. Steps 2–8 were re-run after that merge, and every figure below is measured at this head unless a line says otherwise.

## Mutation proof

The reviewer's `~/hpo-seats/1863-review/mutants.py` was run unchanged against this head. Each mutant edits `tests.yml` or `governance.yml` in place, runs `tests/entities.py` in full (`~/hpo-seats/R9-F11.4-venv/bin/python3`, `PYTHONPATH=tests/hastub`), and restores from HEAD.

- M1, tests.yml at the round-1 merge base (arm absent): rc=1, `4 of 2086 ENTITY CHECKS FAILED`, all four new non-control checks (class, pathspec, trigger, trigger null control: the base script writes no `governance=` output).
- M2, field_coverage `run: true`: rc=1, the class check FAILs; the run then stops in the pre-existing `_pin_unhashed_installs`, which reads `run` as a string (not this diff).
- M3, `'tools/audit/record-predicate'` dropped from the trigger: rc=1, `1 of 2086`, the pathspec check.
- M4, `!cancelled() &&` dropped from the policy_lint step: rc=1, `2 of 2086`, the class and trigger checks.
- R1, the field_coverage step loses its `GITHUB_TOKEN`: rc=1, `1 of 2086`, the class check.
- **R2**, the firing branch writes `governance=false`: rc=1, `1 of 2086`, the trigger check (`.claude/workflows/x.mjs -> false`). Survived round 1.
- **R3**, the three steps keyed on `'false'`: rc=1, `2 of 2086`, the class and trigger checks. Survived round 1.
- **R4**, the job-level `if:` loses its leading `!cancelled()`: rc=1, `1 of 2086`, the trigger check. Survived round 1.
- R5, `GITHUB_TOKEN` added to the policy-docs `rules_sync.mjs` step: rc=1, `1 of 2086`, the class check.
- **R6**, `if true || git diff ...`: the condition is always true, so the trigger writes `false` on every diff (never fires). rc=1, `1 of 2086`, the trigger check. Survived round 1.
- Restored head: rc=0, `ALL 2086 ENTITY CHECKS PASSED`.

Round 1's survivors (R2, R3, R4, R6) are all killed.

Pinning killed mutants belongs to `mutation-autofix`; no local `--pin-killed` was run.

## Null control

- In-check: the token-stripped arm and the firing-branch-writes-false trigger are each refused at head (checks 3 and 5 are `ok`).
- The RCA demonstration, re-taken on the demo commits below: `field_coverage.mjs --only ruleset --ruleset-json`. The admin view is the live ruleset 23698884 read as tvofi. The Actions view is the same object with `bypass_actors` deleted (`jq 'del(.bypass_actors)'`).

| tree | admin view (null) | Actions view |
|---|---|---|
| demo (a) `3689657c1`: code head plus a comment in `counts.mjs` | rc=0, read=43 refused=0 | rc=0, read=37 refused=0 |
| demo (b) `7c4a9fbd4`: (a) plus the #1721 comparator | rc=0, read=43 refused=0 | **rc=1, refused=1** |

The admin column is green in both, which is what a seat's pre-merge run sees. The reviewer's `gh` shim found that `policy_lint.mjs` on (b) is red in both views (a `FIXTURE VACUOUS` self-test landed after #1721). So `field_coverage.mjs` is the arm step that separates the two principals.

## Figures

- Token-bearing pinned graders, the class check 1 enumerates: 6. Covered by the arm: `policy_lint.mjs` and `field_coverage.mjs`. Exempted with a reason in `_PT_EXEMPT`: `policy_lint_envmatrix.mjs`, `budget_raise_gate.py`, `contract_rerun.py` and `tests/nightly_status.py`. Instrument: check 1's failure message prints the derived set. The reviewer's independent enumeration returned the same six.
- Exemption reasons, reworded in round 2:
  - `policy_lint_envmatrix.mjs`: its one principal-dependent row pins `TOKEN_HIDDEN_SKIP_RE`, which the arm's `policy_lint` self-test drives. Its since-ref shape uses a fixture token and no network.
  - `budget_raise_gate.py`: it reads reviews and issue comments, and on `--rerun-stale` POSTs a rerun. It reads no ruleset, and it needs `pull-requests`/`issues` read, which `graders-head-copy` lacks.
  - `contract_rerun.py`: it re-requests a run and grades nothing.
  - `nightly_status.py`: it needs `actions: read`, which `graders-head-copy` lacks; `fast` already drives its copy.
- Arm cost per triggering push, timed locally (`/usr/bin/time -p`, admin token, round 1 at `68b8cb97d`): `policy_lint.mjs` 11.6 s, `field_coverage.mjs` 33.3 s. The job is non-required and off the critical path.
- Head instruments, run locally:
  - `tests/entities.py`: ALL 2086 PASSED
  - `tests/structure.py`: STRUCTURE RATCHET PASSED
  - `tests/harness_headers.py`: ALL 94 PASSED
  - `policy_lint.mjs`: TOTAL: 0 error(s) across 40 policy file(s)
  - `field_coverage.mjs`: FIELD COVERAGE ok, blind=0 dead=0 refused=0
  - `codeowners_gap.py --check`: uncovered_files=0
  - `agreement.mjs`: AGREEMENT ok
- Scope: `python3 tests/closure.py select --diff 03ba7f70f` prints `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself. The full suite is CI's.

## Red checks

- **nightly-status** (check-run 111022420278 at round-1 head `f1a32a364`) is red with `NIGHTLY ABSENT: nothing failed, but mutation-ledger, mutation-ledger-push did not run in that scheduled run`.
  - This red is main's, not this diff's. Those two schedule-only lanes came with #1848 (merged 2026-10-02T16:51Z). The scheduled run the reporter reads, 36984959667 (2026-10-02T08:36Z, head `492d84011`), predates them, so they could not have run in it.
  - The same check is red at the heads of #1862 (`a8f86edd6`), #1861 (`441adb4ae`) and #1858 (`eed5ac3fa`), none of which touch these lanes.
  - **Cheaper detector:** none exists before the next scheduled run, which is the first one that can contain the lanes. The reporter is doing its job: an absent lane is not a green one.
  - **This diff:** it adds steps only to `graders-head-copy` and changes no schedule-only lane or `REQUIRED_LANES`. The `tests/entities.py` check "the reporter watches exactly the lanes a pull request cannot see" is `ok` at this head.

## Forward-carry

none. The class rule now lives in `tests/entities.py` (`_PT_EXEMPT`, its census and the trigger's planted-diff run). A future token-bearing pinned grader is refused there until it is armed or given a reason, so no later stage's brief needs a hand-carried note.

## Friction

none

## Approval

Code-owned CI wiring (`.github/workflows/tests.yml`). It merges on tvofi's approving review at the head above, given under mandate 5951564627 through the orchestrator. No budget moved.

## CI demonstration

The arm has not run in CI. At round-1 head `f1a32a364` the diff touches no restored path, so `governance=false` and the arm's three steps were skipped. The same holds at this head.

The demonstration is owed before merge, on a throwaway draft from `handoff/r9-f11-governance-7-demo`:
- **(a)** `3689657c12aab65f80b0db84108347c1cd7c829c`: the code head plus a comment-only `counts.mjs` edit. Expected: `governance=true`, and both arm steps green.
- **(b)** `7c4a9fbd474da838631639676496bfb4d877bcec`: (a) plus the one-token #1721 comparator. Expected: the `field_coverage.mjs` arm step red (ruleset REFUSED), and `policy-docs` green, because it runs the base's copy.
- (a)'s first parent is the previous demo tip `39b07c75b`, so the ref fast-forwards. Its tree is exactly the code head plus one comment line (`git diff --stat 18ae7cb0a4e6acb942867980a50b4f862701a473 3689657c1`: 1 file, 1 insertion).

Both run links belong here once the draft has run. Close the draft unmerged.
