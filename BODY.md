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

`0bcc7d4ecd52e6955cdff3c701735819d39fee23`, round 2: round 1's `2fe11ffbc`, `origin/main` `de69745ffcab66b566b3e75aee0b572023f80857` merged in (`0fd4c951f`, 17 commits, none touching a file this diff changes: `git diff --stat 2fe11ffbc 0fd4c951f -- <this diff's files>` prints nothing), and one commit registering `tools/pr/prepr.sh` in `tools/audit/seat/ref_privacy.py`'s `PUSHERS`.

Round 1's self-test pushes probe heads to `handoff/zz-lint` from two lines of `prepr.sh --self-test`. Both run after `git remote set-url origin "$PDX/bodies.git"` (a `throwaway_git_init` bare repository) and before the restore to `$BPO`. So the entry is `fixture`, beside `app_approve.sh` and `r9_rc_bus_fetchhead.sh`, not `guarded`: the ref is the constant `handoff/zz-lint` and nothing leaves the temp root.

## Mutation proof

Re-run at this head. Each mutant was committed in its own worktree at `0bcc7d4ec`, and `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh --self-test` was run there; the unmutated head gives `337 passed, 0 failed` (M0).

| mutant | change | result |
|---|---|---|
| BP-SKIP | `body_push.sh`: the lint call becomes `if false && ...` | `335 passed, 2 failed`: the refusal arm and the session-link push arm |
| BP-HEADEQ | `body_push.sh`: the head-equality refusal becomes `true` | `336 passed, 1 failed`: the not-the-head arm |
| RE-SESSION | `policy_lint.mjs`: the session-link alternative is removed | `336 passed, 1 failed`: the session-link push arm |
| LOG | `prepr.sh`: `body_line`'s `BODY_LOG` copy is removed | `336 passed, 1 failed`: the arm requiring both ERROR lines |

| PUSHERS | `ref_privacy.py`: the `tools/pr/prepr.sh` entry absent (the merged head `0fd4c951f`, before the round-2 commit) | `python3 tools/audit/seat/ref_privacy.py --check`: `REFUSE tools/pr/prepr.sh:2424: a push site in a file PUSHERS does not name` |

The PUSHERS row is CI's own red reproduced; with the entry, the same command no longer prints it (Figures).

**Class registration** (round 1, base `4d407a35f`; the class files are unchanged by the merge), run CI's way. `ci_wave_base.sh` restores the pinned graders from the merge base as `governance.yml`'s `wave-script` job does, then runs `check-wave-script.mjs` and the agreement lane:

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

All at this head `0bcc7d4ec`, `origin/main` `de69745ff`, measured 2026-10-22T22:15Z, under Python 3.13 (a venv from `tests/requirements-ci.txt --require-hashes`; this cloud image's ambient `python3` is 3.11, which cannot parse `tests/entities.py`):

- `python3 tools/audit/seat/ref_privacy.py --check`: `23 file(s) with a push site, 11 guarded, ... 1 refused`. The `tools/pr/prepr.sh` refusal is gone. The one left is `dev/audit/rca/R10-RCA-BODY-LINT.md:3: home-directory`, and it is this host's, not CI's: the seat runs as uid 0 with home `/root`, and line 3's `dev/governance/roles/root-cause.md` holds `/root`. That line through `ref_privacy.leaks` with `Identity.made({"/root"},{"root"},0)` returns `['home-directory']`; with the runner's `Identity.made({"/home/runner"},{"runner"},1001)` it returns `[]` (null control). CI job 120096849712 counted `1 refused`, the prepr.sh one alone.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`: rc 0, `PRE-PR: 0bcc7d4ecd52e6955cdff3c701735819d39fee23 0000000000000000000000000000`, with `agreement lane` `AGREEMENT ok` and `wave-script` `202 passed, 0 failed` (run on this body before this line was added; `--body-check` and `figure_lint.mjs --pr-body` re-run after it).
- `python3 tools/audit/seat/ref_privacy.py --self-test`: `66 checks, 0 failed`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh --self-test`: `337 passed, 0 failed`. Under the ambient 3.11 with no seat venv the same run gave `328 passed, 9 failed`, every failure step 6b's or its recorder's `no interpreter that parses the tree was found`: the environment, not the diff.
- `node tools/policy/policy_lint.mjs --self-test`: `FIXTURE ok`; `node tools/policy/policy_lint_mutants.mjs`: `MUTANTS ok`.
- Agreement lane on the BASE copy (`git show origin/main:tools/policy/agreement.mjs`, placed beside the branch copy in `tools/policy/` so its relative import and root resolve, after `python3 -I tools/policy/agreement_py.py --out`): `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`; its `--self-test`: `27 of 27 probes held`.
- Scoped gate, `python3 tests/closure.py select --diff <merge base>`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/harness_headers.py`). `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py`: `ALL 2397 ENTITY CHECKS PASSED`; `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Round 1's figures not re-taken (the files they read are unchanged by the merge): the `--body-check` timings, the five-body replay and `fold_ledger.py check`.

## Red checks

- `instrument-self-tests` (job 120096849712), at round 1's head: `ref_privacy: REFUSE tools/pr/prepr.sh:<line>: a push site in a file PUSHERS does not name`, `ref_privacy --check at HEAD: ... 1 refused`.
  - Cause: round 1's `body_push` self-test arms added two `git push -q origin ...:refs/heads/handoff/zz-lint` lines to `tools/pr/prepr.sh`, a file with no push site before and so no `PUSHERS` entry. The registry refuses an unregistered push site by design.
  - Fixed here: `tools/pr/prepr.sh` is registered as `fixture` (Head; Mutation proof row PUSHERS).
  - The cheaper detector: `python3 tools/audit/seat/ref_privacy.py --check`, offline and about a second, run before the push. Round 1 did not run it: prepr does not, and `scope.run` does not name it, because the instrument self-tests sit outside the scoped gate. It cost one CI round and this second fixer round; running it costs one command.
- `nightly-status`: main's known `NIGHTLY ABSENT`. The nightly workflow is younger than its first cron slot, so no run exists for the check to find. It is being fixed by R10-NIGHTLY-ABSENT-NEW; not this PR's, and this diff touches no file it reads.

## Forward-carry

- Prepr runs the branch copy of pinned graders; CI runs the base copy.
  - `tools/pr/prepr.sh` runs `check-wave-script.mjs` (line 3013) and the agreement lane (lines 2936-2942) from the branch.
  - `governance.yml`'s `wave-script` job restores every pinned grader from the base before running them.
  - So a branch that edits a pinned grader can pass prepr and go red in CI. P2a hit this.
  - The fix shape is `raise_red`'s (line 697): run the base's copy offline, beside the branch's.
  - It is recorded in `dev/audit/rca/R10-RCA-BODY-LINT.md` section 7. It is not counted as an `N-body-lint-bounce` instance, because the mechanism differs: the check ran, but on another copy.
  - It lands in `dev/programme/rosters/wave-r10-groups.json`, where triage P3/Q3 (s4) gives it to R10-FLOW-JIDOKA (`tools/pr/prepr.sh`). Carry: R10-FLOW-JIDOKA
- Prepr step 7a, `figure_lint.mjs --pr-body`, has the same shape as this class: a pure function of the body, first run at the open. 6 of 152 handoff-body tips fail it in `origin/main`'s tree. This is not measured at each head and not built here. It lands in `dev/programme/rosters/wave-r10-groups.json` with the prepr group (`tools/pr/prepr.sh`). Carry: R10-FLOW-JIDOKA

## Friction

- `defect-root-cause`: unenforced: R10-HANDOFF-PREPR-BOUNCE had a body-lint bounce (DEEPLINK) in its own table, but it costed only a full prepr in `body_push.sh` (M1, refused). The 2 s body step was never costed on its own. Carry: dismissed: built here as the countermeasure
