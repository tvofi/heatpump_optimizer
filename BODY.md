R10-RCA-BODY-LINT, a root-cause seat's countermeasure for a recurring class.

Cloud fixers' PR bodies were first linted at `open_pr.sh`, in prepr step 7 (`policy_lint.mjs --pr-body`). Every defect in a body therefore cost an orchestrator repair round. There were five on 2026-10-22:
- #2524: `ae1b71ed` and `0854e390`;
- R10-CURRENCY: `8f8ed571`, `d19baa85` and `bf227ff6`.

The record is `dev/audit/rca/R10-RCA-BODY-LINT.md`, and the class is `N-body-lint-bounce`. Process state: (c) for the missing body gate, (d) for the session link.

What changes:

- **`tools/pr/prepr.sh --body-check <abs body>`** runs step 7's `body_line` alone. It runs offline against `origin/main` and prints every `ERROR`. It is an early-exit mode beside `--version-edit`, so the check is prepr's own function, not a copy.
- **`tools/audit/seat/body_push.sh`** reads `handoff/<topic>` on origin:
  - at this checkout's HEAD: the body is a PR body. It runs `--body-check` and refuses the push with the lint's own words.
  - at another head: the push is refused ("push the code, then the body").
  - absent: the body is a result (probe, design or verdict) and is not linted.
- **`FRICTION_TRAILER_RE`** in `tools/policy/policy_lint.mjs` drops the cloud harness's session-link line, `https://claude.ai/code/session_<id>` alone on a line. This is #1238's argument: a pasted line is not friction. It is pinned in `tests/entities.py`.
- **The class id is registered in every reader the agreement lane names.** The readers are:
  - `dev/audit/config/bugclasses.json` (the class and its `_rca` entry);
  - `dev/audit/config/finding.schema.json`'s `class_guess` enum, appended before `new` as `fold_ledger.py fold` does;
  - `.claude/workflows/audit-find.js`'s `CLASS_GUESS`, written by `python3 tools/audit/fold_ledger.py sync`.

Code-owned paths in the diff: `.claude/workflows/audit-find.js` and `tools/audit/fold_ledger.py`'s outputs. Approval is under mandate 6329234399.

## Head

`2fe11ffbc87966eba52410dcead117224a26e04e`, one commit on `origin/main` `fd9914851f063bc03bb44d4050ad30d6d0052f8d`.

## Mutation proof

Each mutant was committed in its own worktree. `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh --self-test` was then run there, at base `4d407a35f`. The mutated files have not changed since.

| mutant | change | result |
|---|---|---|
| BP-SKIP | `body_push.sh`: the lint call becomes `if false && ...` | `335 passed, 2 failed`: the refusal arm and the session-link push arm |
| BP-HEADEQ | `body_push.sh`: the head-equality refusal becomes `true` | `336 passed, 1 failed`: the not-the-head arm |
| RE-SESSION | `policy_lint.mjs`: the session-link alternative is removed | `336 passed, 1 failed`: the session-link push arm |
| LOG | `prepr.sh`: `body_line`'s `BODY_LOG` copy is removed | `336 passed, 1 failed`: the arm requiring both ERROR lines |

**Class registration**, run CI's way. `ci_wave_base.sh` restores the pinned graders from the merge base as `governance.yml`'s `wave-script` job does, then runs `check-wave-script.mjs` and the agreement lane:

| head | `wave-script` | agreement lane |
|---|---|---|
| `0ae5eb25c`, before registration | `201 passed, 1 failed` (`class_guess is exactly the tools/audit/bugclasses.json ids plus "new"`) | `DIVERGENT finding-class-id "N-body-lint-bounce"` |
| registered | `202 passed, 0 failed` | `AGREEMENT ok` |

The branch copies give the same two answers.

**Replay** of the five refused bodies, each through `body_push.sh`. It ran in a throwaway clone whose origin is a throwaway bare repository holding `handoff/<topic>` at the head the body's `## Head` names:

| body | `origin/main` `body_push.sh` | fixed | fixed, with the trailer change in the head's lint |
|---|---|---|---|
| `ae1b71ed`, `0854e390` (pusher-reap) | rc 0, pushed | rc 1, "`## Forward-carry` names no destination file" | rc 1 |
| `8f8ed571`, `d19baa85` (currency) | rc 0, pushed | rc 1, carry and session link (2 ERROR lines) | rc 1, carry only |
| `bf227ff6` (currency) | rc 0, pushed | rc 1, session link | rc 0, pushed |

## Null control

- `a4c998f1`, the repaired `r10-currency` tip, still pushes through the fixed `body_push.sh` (rc 0).
- The self-test arm "a topic with no handoff/<topic> is a result body" passes, so probe and design pushes are unchanged.
- In `tests/entities.py`, the session link followed by prose is still an entry and still refused. `junk_only` and the mid-evidence control are unchanged.

## Figures

All at this head, `origin/main` `fd9914851`:

- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`: rc 0, `PRE-PR: 2fe11ffbc87966eba52410dcead117224a26e04e 0000000000000000000000000000`, with `agreement lane` `AGREEMENT ok` and `wave-script` `202 passed, 0 failed` (this run was on this body before this line was filled in, and again after).
- Its self-test step: `337 passed, 0 failed`.
- Scoped gate, `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=<merge base> ./tests/run.sh`: `MODE: SCOPED -- 2 script(s) run`; `ALL 109 HARNESS HEADER CHECKS PASSED`; `4 of 2397 ENTITY CHECKS FAILED`. All four failures are heartbeat py-spy control arms (`hb:positive_control survives one hung py-spy sample`, `the control rests between tries`, and two more), and `tests/entities.py` at `origin/main` `fd9914851` fails the same four (`4 of 2397 ENTITY CHECKS FAILED`), so they are main's on this Mac, not this diff's. The three trailer checks print `ok`.
- `python3 tools/audit/fold_ledger.py check`: `fold_ledger: 0 violation(s)`.
- `prepr.sh --body-check` took 1.47 s, 2.19 s and 2.05 s at load 19 (base `4d407a35f`).

## Red checks

None. This head has no CI yet.

## Forward-carry

- Prepr runs the branch copy of pinned graders; CI runs the base copy.
  - `tools/pr/prepr.sh` runs `check-wave-script.mjs` (line 3013) and the agreement lane (lines 2936-2942) from the branch.
  - `governance.yml`'s `wave-script` job restores every pinned grader from the base before running them.
  - So a branch that edits a pinned grader can pass prepr and go red in CI. P2a hit this.
  - The fix shape is `raise_red`'s (line 697): run the base's copy offline, beside the branch's.
  - It is recorded in `dev/audit/rca/R10-RCA-BODY-LINT.md` section 7. It is not counted as an `N-body-lint-bounce` instance, because the mechanism differs: the check ran, but on another copy.
  - It lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY
- Prepr step 7a, `figure_lint.mjs --pr-body`, has the same shape as this class: a pure function of the body, first run at the open. 6 of 152 handoff-body tips fail it in `origin/main`'s tree. This is not measured at each head and not built here. It lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY

## Friction

- `defect-root-cause`: unenforced: R10-HANDOFF-PREPR-BOUNCE had a body-lint bounce (DEEPLINK) in its own table, but it costed only a full prepr in `body_push.sh` (M1, refused). The 2 s body step was never costed on its own. Carry: dismissed: built here as the countermeasure
