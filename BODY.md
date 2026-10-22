R10-RCA-BODY-LINT: a root-cause seat's countermeasure for a recurring class. Cloud fixers' PR bodies were first linted at `open_pr.sh` (prepr step 7, `policy_lint.mjs --pr-body`), so every defect cost an orchestrator repair round. There were five on 2026-10-22: #2524 `ae1b71ed` and `0854e390`, and R10-CURRENCY `8f8ed571`, `d19baa85` and `bf227ff6`. The record is `dev/audit/rca/R10-RCA-BODY-LINT.md`, with class `N-body-lint-bounce` in `dev/audit/config/bugclasses.json`. The process state is (c) for the missing body gate and (d) for the session link.

What changes:

- **`tools/pr/prepr.sh --body-check <abs body>`** runs step 7's `body_line` alone, offline, against `origin/main`, and prints every `ERROR`. It is an early-exit mode beside `--version-edit`, so the check is prepr's own function and not a copy.
- **`tools/audit/seat/body_push.sh`** decides from `handoff/<topic>` on origin:
  - if `handoff/<topic>` is this checkout's HEAD, the body is a PR body; it runs `--body-check` and refuses the push with the lint's own words;
  - if `handoff/<topic>` is at another head, the push is refused ("push the code, then the body");
  - if there is no `handoff/<topic>`, the body is a result (probe, design or verdict) and is not linted.
- **`FRICTION_TRAILER_RE`** in `tools/policy/policy_lint.mjs` drops the cloud harness's session-link line, `https://claude.ai/code/session_<id>` alone on a line, on #1238's argument: a pasted line is not friction. It is pinned in `tests/entities.py`.

## Head

`5b27a11aa74a8edc3bcaf9c51c68c6e387e4b21c`, one commit on `origin/main` `86425b9ad471c752baca652b9189f75b78514931`. Everything below was measured at this head unless a line names the pre-merge commit `4d407a35f` base.

## Mutation proof

Each mutant was committed in its own worktree, and `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh --self-test` was run there (base `4d407a35f`):

| mutant | change | result |
|---|---|---|
| BP-SKIP | `body_push.sh`: the lint call becomes `if false && ...` | `335 passed, 2 failed` (refusal arm, session-link push arm) |
| BP-HEADEQ | `body_push.sh`: the head-equality refusal becomes `true` | `336 passed, 1 failed` (not-the-head arm) |
| RE-SESSION | `policy_lint.mjs`: the session-link alternative removed | `336 passed, 1 failed` (session-link push arm) |
| LOG | `prepr.sh`: `body_line`'s `BODY_LOG` copy removed | `336 passed, 1 failed` (the arm requiring both ERROR lines) |

Replay of the five refused bodies, each through `body_push.sh` in a throwaway clone whose origin is a throwaway bare repository holding `handoff/<topic>` at the head the body's `## Head` names:

| body | `origin/main` `body_push.sh` | fixed | fixed, lint with the trailer change |
|---|---|---|---|
| `ae1b71ed`, `0854e390` (pusher-reap) | rc 0, pushed | rc 1, "`## Forward-carry` names no destination file" | rc 1 |
| `8f8ed571`, `d19baa85` (currency) | rc 0, pushed | rc 1, carry and session link (2 ERROR lines) | rc 1, carry only |
| `bf227ff6` (currency) | rc 0, pushed | rc 1, session link | rc 0, pushed |

## Null control

- `a4c998f1`, the repaired `r10-currency` tip, still pushes through the fixed `body_push.sh` (rc 0).
- The self-test arm "a topic with no handoff/<topic> is a result body" passes, so probe and design pushes are unchanged.
- In `tests/entities.py`, the session link followed by prose is still a Friction entry and still refused. The `junk_only` and mid-evidence controls stay as they were.

## Figures

- `bash tools/pr/prepr.sh --self-test`: `338 passed, 0 failed` (base `4d407a35f`); at this head `337 passed, 0 failed` (main moved the arm count).
- Scoped gate: `MODE: SCOPED -- 2 script(s) run`. At base `4d407a35f`, `tests/harness_headers.py` passed (`ALL 109 HARNESS HEADER CHECKS PASSED`). `tests/entities.py` reported `4 of 2397 ENTITY CHECKS FAILED`; all four were heartbeat py-spy control arms (`hb:positive_control`, "the control rests between tries") at load 19, which this diff does not reach. The three trailer checks passed. `tests/layout.py` refused this branch's usage line citing `tools/audit/prepr.sh`; that line was fixed and `layout: GUARD: 0 refusal(s)`. At this head the same: `4 of 2397 ENTITY CHECKS FAILED` (the same four hb arms), `ALL 109 HARNESS HEADER CHECKS PASSED`, layout passes; `1 TEST SCRIPT(S) FAILED` is entities on those hb arms.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 43 policy file(s)`. `ci_predict.py --base origin/main`: no closures or fast red predicted.
- `prepr.sh --body-check` took 1.47 s, 2.19 s and 2.05 s at load 19.

## Red checks

None: this head has no CI yet. The body was pushed through the changed `body_push.sh`, so `--body-check` ran on this very body.

## Forward-carry

- Prepr step 7a, `figure_lint.mjs --pr-body`, is the same shape (a pure function of the body, first run at the open). 6 of 152 handoff-body tips fail it in `origin/main`'s tree; this was not measured at each head and is not built here. It lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-MACHINERY

## Friction

- `defect-root-cause`: unenforced: R10-HANDOFF-PREPR-BOUNCE had a body-lint bounce (DEEPLINK) in its own table and costed only a full prepr in `body_push.sh` (M1, refused). The 2 s body step was never costed on its own. Carry: dismissed: built here as the countermeasure
