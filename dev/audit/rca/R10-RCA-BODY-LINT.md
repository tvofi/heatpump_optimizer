# R10-RCA-BODY-LINT: a fixer's PR body reaches `open_pr.sh` before anything lints it

Root-cause seat, `dev/governance/roles/root-cause.md`, 2026-10-22, mandate
6329234399. Measured at `origin/main` `4d407a35f`; every figure below comes from
this seat's own runs, and the one estimate is marked as one.

The trigger is the recurrence clause: on 2026-10-22 the orchestrator's
`open_pr.sh` / `update_pr.sh` refused cloud fixers' bodies at prepr step 7
(`policy_lint.mjs --pr-body`) at least five times in about two hours, each costing
a repair round:

- #2524 (`handoff-body/r10-pusher-reap` `ae1b71ed`, then `0854e390`): `## Forward-carry`
  names no destination file (bare `Carry: R10-UPDATE-PR-SIGNALS`).
- R10-CURRENCY (`handoff-body/r10-currency` `8f8ed571`, `d19baa85`, `bf227ff6`):
  a Forward-carry with no path, and a `## Friction` line that does not parse: the
  `https://claude.ai/code/session_...` line the cloud harness appends.

## 1. The counts, reproduced

`git ls-remote origin 'refs/heads/handoff-body/*'` named 152 refs holding 519 body
commits (one per `body_push.sh` call, 2026-10-14 to 2026-10-22). Each commit's
`BODY.md` was run through the same function prepr step 7 runs,
`node tools/policy/policy_lint.mjs --pr-body`, offline (no token), with
`--paths-file` the topic's three-dot diff and the topic's `handoff/<topic>` tree as
the index (`GIT_INDEX_FILE`), so a carry path resolves where the head has it.

| set | body commits | topics |
|---|---|---|
| all | 519 | 152 |
| lint rc 0 | 463 | |
| lint rc 1, a content error (Forward-carry, Friction, empty or bare `n/a`) | **36** | **22** |
| lint rc 1, only missing sections | 20 | 15 |

The 20 missing-section commits are mostly not PR bodies: design notes, design
verdicts, a probe result (`mrbatch`) and CI-LAYOUT unit reports pushed on the
same transport. Three are early versions of real PR bodies. They are not counted
below.

The 36 content errors, by kind (one commit can carry two):

| kind | commits |
|---|---|
| `## Forward-carry` names no destination file | 10 |
| `## Forward-carry` names a file not in the tree | 14 |
| `## Friction` line does not parse, the session link | 8 (5 topics) |
| `## Friction` line does not parse, other | 10 |

Per day: 2, 2, 1, 3, 3, 6, 7, 12 (10-15 to 10-22). Four topics are still failing
at their tip: `r10-pusher-reap`, `r10-setpoint-power`, `r10-ci-layout-p2a`,
`r10-ci-layout-p2a-u9c`. For the 18 topics that later pushed a passing body, the
time from the first failing commit to the first passing one has a median of
81 min. That figure includes fixer, relay and idle time, so it is an upper bound
on the repair, not the repair itself.

Caveats. The lint is today's, and the tree is each topic's current head rather
than the head each version described, so a few `not in the tree` results may have
resolved at their own head. `--head` was omitted, because the head a superseded
version described is not recorded. Whether each failing commit actually reached
`open_pr.sh` is not recorded anywhere. So 36 is an upper bound on bounces and the
five named above are a lower bound.

The instruments are `measure.sh`, which lints tips with `--head`, and
`measure_hist.sh`, which lints every commit. They live in the seat's scratch.

## 2. Named cause

**The handoff instrument checks the code and not the body.** `body_push.sh` is the
handoff (`fixer.md` step 6). Since R10-TICK-DRIVERS it runs
`tools/pr/ci_predict.py`, which is countermeasure M2 of R10-HANDOFF-PREPR-BOUNCE.
It runs nothing over the body it publishes. The first run of `checkPrBody` on a
body is prepr step 7 inside the orchestrator's `open_pr.sh`, after the branch is
frozen and often after the cloud seat has ended.

`fixer.md` step 5 does say "the body passes `tools/pr/prepr.sh`". But the cloud
fixer payload (`tools/audit/seat/cloud_dispatch.py`, role `fixer`) says "write the PR
body and run `body_push.sh`", and a full prepr costs 9.6 min on average
(R10-HANDOFF-PREPR-BOUNCE section 5).

**The session link is a trailer the closed list predates.** `FRICTION_TRAILER_RE`
(#1238) drops the lines a tool pastes under `## Friction`: the Claude Code
attribution, `Co-Authored-By:`, and the closing keywords. The cloud harness adds a
line of its own, its session link alone on a line, to commits and bodies. That
line opens a `https:` near-miss entry under `FRICTION_NEAR_MISS_RE` and is refused
as unparseable. 297 commit messages on every ref since 2026-10-10 carry the link.
The seat did not write it, and #1238's own argument covers it: refusing a pasted
line charges every body a repair round.

**Forward-carry without a path is a grammar mismatch, not carelessness.**
`carry_audit.py` accepts `Carry: <GROUP>` with no file. The PR template's
`## Forward-carry` asks for "the path it lands in **and** `Carry: <dest>`", and
`checkPrBody` refuses a section that names no path token. A body written to
satisfy `carry_audit.py`, which `pr-contract` and the train both run, can still
fail the lint. Only an earlier run of the lint surfaces the second half.

## 3. Process state

**(c): the process was followed and did not produce the intended result.** The
process here is the handoff gate, `body_push.sh` M2, and it ran and passed on
every one of the five named pushes. The replay in section 6 shows `origin/main`'s
`body_push.sh` exiting 0 and publishing all five.

The gap is in the gate's unit. R10-HANDOFF-PREPR-BOUNCE already had a body-lint
bounce in its own table (DEEPLINK, 2026-10-15) and classed it as a different
cause. It then costed only M1, a full prepr in `body_push.sh` at 9.6 min a
handoff, and refused M1 on the cost test. The body step alone costs about 2 s
(section 5) and was never costed apart from M1. Telling fixers harder to run prepr
would be a (b) countermeasure for a (c) state.

The session link is **(d)**: the trailer list was sound for the local harness, and
fixers moved to the cloud harness, which appends a line shape the list never
named.

## 4. How far the class reaches

The same shape is any prepr step that is a pure function of the body and first runs
at the open:

- **step 7a, `figure_lint.mjs --pr-body`**: 6 of 152 tips fail it when run in
  `origin/main`'s tree. This is unverified at each head, so it is not counted and
  not built here.
- **`preflight.sh`**: needs the intended-issue list, which only the orchestrator
  has, so a seat cannot run it.
- **`carry_audit.py check --body`**: the dispatch already tells seats to run it.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- **cost(defect), one bounce**: about 20 min, taken from R10-HANDOFF-PREPR-BOUNCE
  section 5: a refused prepr run of 9.6 min (measured there) plus a fixer round
  trip of 10 min (an estimate there).
- **P(recurrence)**: from 5 bounces a day (the five named today, the lower bound) to
  12 a day (today's measured failing commits, the upper bound). That is 100 to
  240 min a day.
- **cost(countermeasure)**: `prepr.sh --body-check` ran in 1.47, 2.19 and 2.05 s
  at load 19, plus one `git ls-remote`. It runs only for a topic with
  `handoff/<topic>` on origin. At the measured 65 body pushes a day (519 over 8
  days), the upper bound is 65 x 2.2 s = 2.4 min a day.

2.4 min a day against at least 100 min a day: **build**. The session-link trailer
costs nothing at run time. It is one more alternative in an anchored regex.

## 6. Countermeasure, built (state (c) and (d))

1. **`prepr.sh --body-check <abs body>`**: step 7 alone, on `body_line` itself, so
   the predicted budget red rides along. It runs over the checkout's HEAD against
   `origin/main`, offline, and prints every `ERROR` and then the verdict line. It
   is an early-exit mode beside `--version-edit`, so the function is prepr's own
   and not a copy.
2. **`body_push.sh`** reads `handoff/<topic>` from origin:
   - if it is absent, the body is a result (probe, design or verdict) and is not
     linted;
   - if it is not this checkout's HEAD, the push is refused: push the code, then
     the body;
   - otherwise it runs its sibling `prepr.sh --body-check`, and a refusal is the
     push's, with the lint's own words.
3. **`FRICTION_TRAILER_RE`** gains the cloud harness's session link alone on a line,
   pinned in `tests/entities.py` beside the #1238 trailers. The null control: the
   same link followed by prose is still an entry, and is still refused.

**Demonstration (`root-cause.md` step 5).** `replay.sh` builds a throwaway clone
whose origin is a throwaway bare repository holding `handoff/<topic>` at the head
each body's `## Head` names, and replays the five bodies:

| body | head | `origin/main` `body_push.sh` | fixed, head's own lint | fixed, lint with the trailer |
|---|---|---|---|---|
| pusher-reap `ae1b71ed` | `2d5d6be11` | rc 0, pushed | rc 1, Forward-carry names no destination file | rc 1, same |
| pusher-reap `0854e390` | `a0cb0cdd7` | rc 0, pushed | rc 1, same | rc 1, same |
| currency `8f8ed571` | `701448f90` | rc 0, pushed | rc 1, carry and session link (2 ERROR lines) | rc 1, carry only |
| currency `d19baa85` | `23392d5d6` | rc 0, pushed | rc 1, carry and session link | rc 1, carry only |
| currency `bf227ff6` | `23392d5d6` | rc 0, pushed | rc 1, session link | **rc 0, pushed** |
| currency `a4c998f1` (the repaired tip; null control) | `23392d5d6` | | **rc 0, pushed** | |

Self-test arms in `prepr.sh --self-test`, which is in `pr-contract`'s run:

- a topic with no `handoff/<topic>` is not linted (null);
- a PR body with a pathless carry and an unparseable Friction line is refused,
  both `ERROR` lines are printed, and nothing is pushed;
- a passing body with the session-link line pushes;
- a checkout that is not the head at `handoff/<topic>` is refused.

The run printed 338 passed, 0 failed.

Mutants, each committed in its own worktree with the self-test run there:

| mutant | change | result |
|---|---|---|
| BP-SKIP | `body_push.sh`: the lint call becomes `if false && ...` | 335 passed, 2 failed: the refusal arm and the session-link push arm |
| BP-HEADEQ | `body_push.sh`: the head-equality refusal becomes `true` | 336 passed, 1 failed: the not-the-head arm |
| RE-SESSION | `policy_lint.mjs`: the session-link alternative removed | 336 passed, 1 failed: the session-link push arm |
| LOG | `prepr.sh`: `body_line`'s `BODY_LOG` copy removed | 336 passed, 1 failed: the arm requiring both `ERROR` lines |

All four are killed; the unmutated tree is 338 passed, 0 failed.

## 7. A second shape: the local check runs the branch copy, CI runs the base copy

The orchestrator reported that R10-CI-LAYOUT-P2a hit this shape; this seat did
not reproduce P2a's instance. `governance.yml`'s `wave-script` job restores every
pinned grader from the base commit ("Restore the check source from the base
commit") before it runs `check-wave-script.mjs` and the agreement lane. The pinned
graders include `tools/policy/*.mjs`, `tools/policy/*.py`, `tools/pr/*.sh` and
`tests/entities.py`. `tools/pr/prepr.sh` runs the branch's own copies:
`check-wave-script.mjs` at line 3013, and `agreement_py.py` and `agreement.mjs` at
lines 2936-2942.

So a branch that edits a pinned grader is graded locally by its new copy and in
CI by the old one, and prepr's `ok` can be CI's red. Only the budget gate is
already run from the base (`raise_red`, "THE BUDGET RED IS THE BASE'S GATE",
line 697).

The cause is the same kind as section 2: the cheaper detector runs a different
check from the gate it stands in for. The mechanism is different: the body here
was linted, but by a different copy of the grader. So it is recorded here and
carried, not counted as an instance of `N-body-lint-bounce`.

This pull request edits two pinned graders, `tools/policy/policy_lint.mjs` and
`tests/entities.py`. Run CI's way, the base copy and the branch copy agree on
this pull request: `ci_wave_base.sh` restores the pinned list from the merge base
as `governance.yml` does.

| head | `wave-script` | agreement lane |
|---|---|---|
| `0ae5eb25c`, class not yet registered | 201 passed, 1 failed (`class_guess`) | DIVERGENT `N-body-lint-bounce` |
| the registered head | 202 passed, 0 failed | `AGREEMENT ok` |

The branch copy gave the same two answers. The class id is now registered in
every reader the lane names: `bugclasses.json`; the `finding.schema.json`
`class_guess` enum, appended before `new` as `fold_ledger.py fold` does; and
`audit-find.js` `CLASS_GUESS`, written by `fold_ledger.py sync`.

## 8. Residuals

- Step 6d's unpinned sites are not fed to `--body-check`, so a predicted
  `mutation` red is still caught only at the open.
- The red history (check runs) is read only at the open; `--body-check` runs
  offline.
- A fixer who runs `body_push.sh` before pushing the code is not linted. It prints
  `a result body`, and the open still refuses. The fixer contract orders the code
  push first.
- The head's own lint decides. A head cut before the trailer change merges still
  refuses the session link until it merges `origin/main`; that refusal is correct
  for that head and cheap now.
- Step 7a (figures) is the next candidate; its count at each head is not measured.
