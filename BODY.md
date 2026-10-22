R10-CI-LAYOUT P2a, unit **U9c**: `tools/ci/ruleset_cutover.py`, the instrument tvofi runs to cut ruleset 23698884's required contexts over from the 17 to `[gate@15368]`, and back. It is built against DESIGN-REVIEW.md §4 items 1-7, PLAN.md §3's block and DESIGN-P2 §7 (plan ref `1011d6b2f`). Part of #2495. The integration seat assembles it into P2a. This seat opens no pull request and writes no delivery row.

## Unit

U9c, topic `r10-ci-layout-p2a-u9c`. `git diff --stat $(git merge-base origin/main HEAD)...HEAD`:

```
 dev/audit/harnesses/r10_seat_selftests_mutants.py |  20 +-
 tests/closure.py                                  |   5 +
 tests/layout.json                                 |   3 +-
 tools/ci/fixtures/ruleset/green.json              |  25 ++
 tools/ci/fixtures/ruleset/ruleset_23698884.json   | 124 ++++++
 tools/ci/ruleset_cutover.py                       | 510 ++++++++++++++++++++++
 6 files changed, 683 insertions(+), 4 deletions(-)
```

`ruleset_cutover.py` has 309 production lines (lines 1-309, docstring included) and a 201-line self-test (from the `# ---- self-test` marker to the end). The bound is about 400. Fixtures:
- `ruleset_23698884.json` is the live GET of 2026-10-19, copied byte for byte from `measure/p2/raw/ruleset_23698884.json` at `1371a0a6`.
- `green.json` is the all-green cut-over moment: the check runs, user, runs and pulls reads, trimmed to the fields the tool reads.

Classification:
- **`tests/closure.py`**: both paths go in `GATE_FILES`, one line each. I tried `INERT` first, and `tests/entities.py` refused it ("narrowing INERT leaves every non-audit tools/ file in the must-classify set": an INERT `tools/` file outside the named inert homes). `GATE_FILES` is the class the contract gives all of `tools/ci/`. Once U0a's `tools/ci/` prefix lands, these two lines are redundant and the integration seat may drop them.
- **`tests/layout.json`**: `tests/layout.py` refused three files "in 0 categories", so `tools/ci/**` joins the `tools` category. U0a's files need the same line, which makes this an identical-line merge.

## Interface

What this unit exports, set against EXECUTION.md §3.1:
- **Entry point.** `python3 -I tools/ci/ruleset_cutover.py` takes one of four modes:
  - `--dry-run [--staged F] [--head H] [--pr N]`
  - `--apply --rollback-file /ABS --staged F --head H --pr N`
  - `--rollback /ABS`
  - `--self-test`, which prints `ruleset_cutover self-test: 51 checks, 0 failed`.
- **Return codes.** 0 is OK. 1 is a dry-run whose preconditions fail. 2 is `REFUSED: <reason>` from any step, the fail-closed path.
- **I/O.** All of it is `gh api` as the caller, through one injectable runner, `main(argv, gh=...)`. Item 5 says the tool "uses `gh api` as the owner and is never run in CI except its offline self-test". So it does **not** import `tools/ci/ghapi.py` and imports no `urllib`. Item 2 binds only the CI-run modules, and this tool is not one of them.
- **Constants** that the glue or entities may pin: `RULESET_ID = 23698884`, `GATE_APP_ID = 15368`, `OWNER = "tvofi"`, `OLD_CONTEXTS = 17`, `NEW_CHECKS = [{"context": "gate", "integration_id": 15368}]`, `KEYS` (the six writable keys).
- **Behaviour**, against DESIGN-REVIEW §4:
  - **Item 1, fail closed.** Every step raises `Refuse`.
  - **Item 2, the rollback copy.** It is written only to a new absolute path, through a `.partial` file and `os.replace`, and only from a GET that parsed and holds exactly 17 contexts. It is re-read and asserted at 17 before any PUT. A failed GET leaves no file at all.
  - **Item 3, the five preconditions.** All five are read after the rollback GET and immediately before the PUT, and the run re-checks that the live ruleset still equals the rollback copy:
    - the six-key sha256 equals the staged JSON;
    - the newest (max id) `gate` check run at H is `success`, with `app.id == 15368` and `head_sha == H`;
    - `gh api user` reads `tvofi`;
    - no in-progress push run on main from `tests.yml`, `ci.yml` or a run named `Tests`;
    - no open PR besides `--pr`.
    A full page (100) or an incomplete `total_count` refuses rather than passes.
  - **Item 4, the two-half read-back.** Half 1: the PUT result equals the payload, and a fresh GET requires `gate` alone. Half 2: everything but `required_status_checks` in that GET equals the rollback copy.
  - **Item 5, a refused PUT.** A 4xx is reported. The tool reads the ruleset back and prints `UNCHANGED` or the diff.
  - **Item 6, the rollback triggers.** The three triggers and the order (ruleset first, then the revert) are printed after a successful apply. `--rollback` PUTs the copy's six keys and reads all six back.
- **Live read: one `--dry-run`, made with this seat's token. No write.** It read the ruleset and printed the payload. The diff removes only the 17 contexts and adds `gate`, and the rest reads `OUTSIDE required_status_checks: IDENTICAL`. Preconditions:
  - `--staged tools/ci/fixtures/ruleset/ruleset_23698884.json` gives `staged-hash: PASS -- live b6d380ac9d90f05d staged b6d380ac9d90f05d`, so the live ruleset still equals the 2026-10-19 read;
  - `caller-is-owner: PASS -- gh api user reads 'tvofi'`;
  - `main-push-idle: FAIL` (three Tests push runs in progress);
  - `queue-drained: FAIL` (nine open PRs);
  - `gate-at-head: SKIP` (no `--head`; no gate exists yet).
  The run ended `DRY-RUN REFUSED: nothing was written`, rc 1. Both FAILs are right for a day with no freeze. That makes eight API reads across two runs; no 403 or 429.

## Head

`75956eeedd4ea3640908d985cf9fa4a30e38a1f1`, on base `738d950aa981efbdf866ff369942a69c5ae7d205` (origin/main at the fetch, 2026-10-22 UTC). At the push (2026-10-22T15:27Z) origin/main read `58730d09f61f`; this head is not re-measured against it, and a later merge of main is the orchestrator's (fixer.md step 6). `git log origin/main..HEAD` holds my two commits only.

## Mutation proof

Each mutant was planted in a production line outside `self_test()`, and each turned `--self-test` red.

Command: `python3 ../mut.py`, a scratch driver that replaces one line, runs `python3 -I tools/ci/ruleset_cutover.py --self-test` and restores the line. 16 mutants, `survivors 0`, at both python 3.11 and the venv-ci 3.14:

```
half2-skipped KILLED 1 | ruleset_cutover self-test: 51 checks, 1 failed
half1-skipped KILLED 1 | ... 1 failed
staged-hash KILLED 1 | ... 1 failed
gate-conclusion / gate-app / gate-head / owner KILLED 1 | ... 3 failed each
main-idle KILLED 1 | ... 9 failed
queue KILLED 1 | ... 6 failed
assert17-live / no-overwrite / absolute / 4xx-readback / rollback-readback KILLED 1 | ... 1 failed each
payload-rsc KILLED 1 | ... 5 failed
precondition-gate KILLED 1 | ... 21 failed
```

On the first pass `4xx-readback` (`if after == six(rollback)` → `if True`) SURVIVED, because no plant drove the DIFFERS arm. A plant was added for a 4xx PUT over a ruleset that moved, and the mutant is now KILLED.

The brief's mutant, "skip the second read-back half", is pinned in the tree as `ruleset_cutover-1` in `dev/audit/harnesses/r10_seat_selftests_mutants.py`, in its own block (not at the list's end). Beside it:
- `ruleset_cutover-2` skips the first half;
- `ruleset_cutover-3` disables the staged-hash check.

The harness now names a file outside `tools/audit/seat/` from the repository root (`seat_path()`). I added a temporary `governance.yml` step, not committed, and ran `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py ruleset_cutover-1 ruleset_cutover-2 ruleset_cutover-3`. Each mutant was KILLED, rc 1, `51 checks, 1 failed`, and the result was `RESULT survivors=0`. The harness's per-mutant null, the same step on the unmutated file, passed first, or it would have printed NOT RUN.

## Null control

- **All green.** `--dry-run --staged <fixture> --head H --pr 2700` over `green.json` prints `DRY-RUN OK`, rc 0, with no PUT. `--apply` over it makes exactly one PUT. The PUT body is the GET-shaped payload: the DeployKey keeps `actor_id: null`, and without `required_status_checks` it equals the fixture's six keys. Both halves print OK.
- **Every plant is a negative.** Each refuses `--apply` with no PUT, and refuses `--dry-run` with rc 1:
  - newest gate a failure, from another app, or at another head;
  - no gate at all;
  - caller not tvofi;
  - a Tests push run in progress, a `ci.yml` push run in progress, or an incomplete runs list;
  - another open PR, or a full page of PRs;
  - a staged JSON that differs.
- **Read-back halves.** Each is planted on its own, and each refuses only on its own half. The half-2 plant flips `require_code_owner_review` in the post-PUT GET while the PUT echo is clean, so half 1 prints OK and half 2 prints FAILED.
- **The fixture filter.** `green.json` holds an in-progress `Nightly` push run on main and an older failed `gate` at H. Neither may refuse, and neither does: the main-push-idle filter and newest-by-id are each checked against their own decoy.
- **Classification.** `orphan_files()` at the base's `tests/closure.py` returns my three files. At the head it returns `[]`.

## Figures

- **Self-test.** `python3 -I tools/ci/ruleset_cutover.py --self-test` → `ruleset_cutover self-test: 51 checks, 0 failed`. The count is the number of `check()` calls executed; the instrument prints it.
- **Line counts.** Production 309 and self-test 201 are `awk 'NR<310'` and `awk 'NR>=310'` over `tools/ci/ruleset_cutover.py`, piped to `wc -l`. Line 310 is the self-test marker.
- **Mutants.** The scratch driver and the in-tree harness, as above.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` gives `MODE: FULL` ("tests/closure.py changes the gate itself").
- **Full gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=<merge-base> PYTHONPATH=tests/hastub ./tests/run.sh` was run on the first commit, with PATH on `/opt/hpo/venv-ci`. Four scripts were red:
  - `tests/entities.py` (1 of 2388: the INERT refusal above);
  - `tests/layout.py` (3 placement refusals);
  - `tests/stress.py` and `tests/harness_headers.py`: `gate_lock: flock-wrap refused, u9c holds no lease`. I had set `HPO_GATE_LOCK_LABEL` without taking the lease. That was a harness error of mine, not a check.

  After the reclassification commit:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2388 ENTITY CHECKS PASSED`;
  - `python3 tests/layout.py` → rc 0, `GUARD: 0 refusal(s)`;
  - under a taken lease, `python3 tests/harness_headers.py` → `ALL 109 HARNESS HEADER CHECKS PASSED`.

  The brief's `python3 -I tests/harness_headers.py` form fails at import (`No module named 'homeassistant'`), because `-I` drops `PYTHONPATH=tests/hastub`. The form `run.sh` uses passed.

  `tests/stress.py` was re-run under the lease on the final head: `ALL 113 STRESS CHECKS PASSED`, rc 0. Every other script in the FULL run was ok.
- **Other checks.**
  - `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
  - `python3 -I tools/audit/seat/tmp_paths.py --check` → 0 refused.
  - `python3 -I tests/throwaway_git.py --check` → 0 refused. This unit builds no git repository.
  - `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → no closures or fast red predicted.

## Red checks

- **nightly-status** is red on main's ancestry. It grades `main`, and this diff touches none of what it reads: its scripts, `tests.yml`, `nightly.yml`, `governance.yml`, the plan, `HANDOVER.md`. Under `defect-root-cause.md` no answer is owed here; it is the orchestrator's on main.
- **instrument-self-tests** (`selftest_wiring.py --check`) is predicted red on this unit alone: `UNWIRED tools/ci/ruleset_cutover.py`, 78 self-testing, 77 wired. This is by design. The contract (§3.1 item 6) gives the `governance.yml` step to the glue, and this seat may not edit it. No cheaper detector is owed: the integration seat's own `selftest_wiring.py --check` (N/N/0) is the detector, and it runs in seconds.

## Forward-carry

- **To the P2a glue (integration seat).** Add one `instrument-self-tests` step:
  ```
  python3 -I tools/ci/ruleset_cutover.py --self-test | tee "$RUNNER_TEMP/ruleset-cutover-self-test.txt"
  grep -Eq '^ruleset_cutover self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/ruleset-cutover-self-test.txt"
  ```
  Until that step exists, `r10_seat_selftests_mutants.py`'s `ruleset_cutover-N` ids assert in `step_for()`, which demands one step. A full harness run on P2a stays red until the step lands. Once U0a's `tools/ci/` prefix is in `GATE_FILES`, the two per-file `GATE_FILES` lines may be dropped. `tools/ci/**` in `tests/layout.json` is shared with U0a's files. Carry: P2a glue (integration seat).
- **To P2b and PR 2's body.** Stage the ruleset JSON with `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884 > staged.json` at H. Show `--dry-run --staged staged.json --head H --pr <PR 2>` output at H. tvofi's command is `--apply --rollback-file ~/hpo-orch/r10s3/cutover/ruleset-rollback-23698884-<UTC>.json --staged staged.json --head H --pr <PR 2>`; the tilde must expand to an absolute path. Carry: P2b brief (orchestrator).

## Friction

- `writing-for-agents`: cost: the brief prescribes `python3 -I tests/harness_headers.py`. Under `-I` that form cannot import the stubbed `homeassistant` and fails at import. `run.sh` runs it without `-I`. Carry: plans/ci-layout P2a common brief.
- `gate-scoping`: unclear: `HPO_GATE_LOCK_LABEL` set on `run.sh` without a prior `gate_lock.py take` makes `stress.py` and `harness_headers.py` fail as `>>> FAILED`, which reads like a check failure. Carry: gate-scoping.md.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01PZLsf7mySUDu2eCeGMJLDv
