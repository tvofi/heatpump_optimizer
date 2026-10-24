`tools/pr/ci_predict.py` now runs the layout guard that the `fast` job runs. This is #2554's forward-carry, item 4ddebe42. Part of #2505 (R10-FLY-CIPREDICT-LAYOUT, carved out of R10-ORCH-MACHINERY's row G).

`body_push.sh` refuses a handoff only on what `ci_predict.py` predicts, plus the pr-body lint. `prepr.sh` already ran `tests/layout.py --guard` (`moved_line`), but `ci_predict.py` did not. So a head that re-added a moved path, or added a line citing one, passed the handoff and turned red on `tests / fast (3.14)` after the push. The guard runs in seconds; the CI red took about 30 minutes to show (`prepr.sh`'s comment above `moved_line`, from #2065).

The fix adds a fifth refusing arm, `layout_preds(root, base)`. It calls `tests/layout.py`'s own `guard` and does not restate the rule. It reads the commit `HEAD` against the merge base and uses `HEAD`'s `tests/layout.json`, so the prediction covers what is pushed. CI runs the guard on a checkout of that commit, whose index is the commit. The arm uses the guard's `rev` form, which `--replay` uses too. Each refusal prints as `PREDICT tests / fast (3.14) LAYOUT <guard line>` and sets rc 1. A guard that raises prints `LAYOUT UNREADABLE` and also sets rc 1, the way the carry arm handles an unreadable roster. A tree with no `tests/layout.py` predicts nothing for this arm, as `prepr.sh`'s `moved_line` skips. `repairs()` gains the arm's repair line, worded like `moved_line`'s hints.

Alternatives considered:
- Have `body_push.sh` call `prepr.sh`'s `moved_line`. That puts a second refusal path into the handoff script, outside the predictor. Every other static CI red is predicted in one place (the predictor), and `prepr.sh` step 6d already reads that place.
- Re-implement the guard's three refusals inside `ci_predict.py`. `tests/README.md` says a restated rule pins nothing, and the other arms call CI's own functions (`closure.orphan_files`, `mutation_table`, `carry_audit.audit`).

## Head

`6965c36b492af09aec9b7161802b4f877a6a9766`, cut from `origin/main` `145bfe197b9e7c09eb90bedadec44c6bc19d679d`, which is also the merge base. Every figure was taken at this head on 2026-10-24 from 10:31Z, while `origin/main` was at `145bfe197b9e`. `origin/main` moved to `e8a08cf9efef` before the handoff; its 23 changed files include nothing this diff reads (`git diff --name-only 145bfe197b9e...origin/main`), so the head was not merged forward. Python 3.14.7 at `/opt/hpo/venv-ci`.

## Mutation proof

The self-test was written first. Its two red cases failed before the arm was written (the worktree, uncommitted: the merge base plus the self-test alone): `ci_predict self-test: 2 failed`, with `FAIL a file re-added at a path whose move landed is predicted red (rc 0)` and `FAIL a new line citing a landed path is predicted red (rc 0)`.

Each mutant is one single-occurrence replacement in `tools/pr/ci_predict.py`. Each run executes `python3 -I tools/pr/ci_predict.py --self-test` and then restores the file (the driver printed `restored`).

| mutant | replacement | rc | failing checks |
|---|---|---|---|
| NULL | none | 0 | none |
| M1 arm not called | delete `preds += layout_preds(root, base)` in `predict` | 1 | `a file re-added at a path whose move landed is predicted red`, `a new line citing a landed path is predicted red` |
| M2 findings dropped | `layout_preds` returns `[]` in place of its findings | 1 | the same two |
| M3 guard on the index | `layout.guard(root, manifest, base)` in place of `..., base, "HEAD")` | 1 | `the re-added path staged and not committed is predicted green (null control)` |
| M4 repair line dropped | `if False:` in place of the LAYOUT test in `repairs` | 1 | the two red cases (their `CI PREDICT: a LAYOUT refusal is repaired` line is missing) |
| M5 wrong job | the arm files under `mutation` (a warning that never sets rc) | 1 | the two red cases (rc 0) |

M3 survived a first version of the self-test. The staged-and-not-committed null case was added to kill it. M1 is also the base end of the measurement below: the base has no layout arm.

## Null control

- The self-test's two nulls run in the same throwaway clone as the plants. One is a comment that cites nothing, appended to `tests/wood_advisor.py`. The other is the placement plant staged but not committed. Both print no `LAYOUT` line and exit with rc 0.
- On this head's own diff, the predictor prints no LAYOUT line: `CI PREDICT: no closures or fast red predicted against 145bfe197b9e`. CI's guard agrees: `layout: GUARD: 0 refusal(s) against 145bfe197b9e`.
- Both ends against CI's own command. The same three plants were committed in a throwaway clone of this head (`throwaway_git_clone --shared`) on a base commit that holds either the base's or the head's predictor. Each was then run through `python3 -I tools/pr/ci_predict.py --base <that commit>` and through CI's `python3 -I tests/layout.py --guard --base <that commit>`. The plant path is the first `retired` entry in `tests/layout.json` that has a `new` path, is a file and no longer exists in the tree. At this head that is `.claude/workflows/agreement.mjs`.

  | end | plant | predictor rc | predictor LAYOUT lines | CI guard rc |
  |---|---|---|---|---|
  | base | re-added path | 0 | 0 | 1 |
  | base | citation | 0 | 0 | 1 |
  | base | comment (null) | 0 | 0 | 0 |
  | head | re-added path | 1 | 1 | 1 |
  | head | citation | 1 | 1 | 1 |
  | head | comment (null) | 0 | 0 | 0 |

  At the base, the predictor and CI disagree on both plants. At the head, they agree on all three rows. This probe was a one-off driver in the seat's scratch directory and is not landed: the in-tree self-test reproduces the head end, and mutant M1 reproduces the base end.

## Figures

- `python3 -I tools/pr/ci_predict.py --self-test` -> `ci_predict self-test: 0 failed`, with 4 layout cases and 3 carry cases `ok`, and `every JOB value is a name gate.REQUIRED owes`. `governance.yml`'s step "Show the CI predictor" runs this command. A depth-1 clone of this head passes it too (`git rev-parse --is-shallow-repository` -> `true`).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `CI PREDICT: no closures or fast red predicted against 145bfe197b9e (a data-file read is not seen)`, rc 0. The output has no `ADDED UNPINNED` line.
- `python3 tests/closure.py select --diff 145bfe197b9e --workdir "$D"` -> `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` The only changed file is `tools/pr/ci_predict.py`, and no measured closure lists it. Its check is the `governance.yml` self-test step above.
- `run_always` lines: `python3 tests/env_drift.py --claims-only origin/main` -> `claims hygiene: origin/main ok`; `python3 tests/closure.py selftest` -> `ALL 117 closure shrink pins PASSED`; `python3 tests/layout.py` -> `layout self-test: ok`. `tests/harness_headers.py` was left to CI because no harness changed.
- `python3 tests/closure.py affected` over the same diff names 2 closures to re-derive, `tests/entities.py` and `tests/harness_headers.py`, because both read `tools/pr/ci_predict.py` as text (`inert_reads`). Both pass when run plainly at this head: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2425 ENTITY CHECKS PASSED`, rc 0 (the same at the base, in a worktree at `145bfe197b9e`); `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0.
- `bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 6965c36b492a... 000000000000000001000000`, rc 1. Its only refusal is the closures step: `failed while being recorded: tests/entities.py (exit 1)`. This is not this diff (see `## Red checks`). Every other step is `ok` or `skip`, including `ci predict`, `layout guard`, `throwaway git` and `claims hygiene`. `prepr.sh --body-check` -> `pr-body ok: PR-BODY: 0 error(s)`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` -> `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`.
- `python3 -I tests/layout.py --guard --base 145bfe197b9e` -> `layout: GUARD: 0 refusal(s) against 145bfe197b9e`.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 145bfe197b9e` -> `Architecture score: dS +0.0000 NULL`.
- `python3 -I tests/throwaway_git.py --check` -> `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`. The self-test's clone goes through `throwaway_git_clone`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -> `tmp_paths: 0 refused`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `selftest_wiring: 93 self-testing, 93 wired, 0 unwired`.
- The class census (fixer step 8). The class is a CI command that `prepr.sh` runs before the PR exists but the handoff (`body_push.sh` = `ci_predict.py` plus `prepr.sh --body-check`) does not predict. The rule that lists its seams is `grep -nE '^[a-z_]+_line\(\) \{' tools/pr/prepr.sh`, which returns 9 functions. Dispositions:
  - `moved_line` (the layout guard, `fast`): closed in this diff.
  - `predict_line`: this is `ci_predict.py`.
  - `body_line`: run by `body_push.sh` through `prepr.sh --body-check`.
  - `closures_line` (scoped recordings): `ci_predict.py`'s closures arms already predict it statically, by design. A recording cannot be done statically, and `closures-autofix` repairs it after the push (`ci-autofix.md`).
  - `unpinned_line` and `reds_line`: body-side checks that read `open_pr.sh`'s red history and step 6d's site file, and only exist at the open (`--body-check`'s comment).
  - `copies_line` (`tests/closure.py no-copies`, the `closures` job), `throwaway_line` (`tests/throwaway_git.py --check`, `governance.yml`) and `claims_line` (the claim-file check, `tests/env_drift.py`, a `run_always` line of `tests/run.sh`): **open seams** that this diff does not close, carried below.

## Unpinned sites

n/a: `ci_predict.py --base origin/main` prints no `ADDED UNPINNED` line for this diff (prepr step 6d's arm).

## Red checks

No pull request or CI run exists for this head yet. Locally, one step went red: `prepr.sh`'s closures step, which records `tests/entities.py` under strace (`tests/derive_closures.sh --single tests/entities.py --record-only`). The recording exits 1 with `2 of 2425 ENTITY CHECKS FAILED`. The two failures are both final tries of `hb:positive_control`: under the strace recorder, `py-spy dump` times out or does not name the spin. Null control: the same recording at the base `145bfe197b9e`, in a worktree without this diff, also exits 1 with `2 of 2425 ENTITY CHECKS FAILED` and the same two final-try `hb:positive_control` failures, while the plain `entities.py` run passes at both ends. So this is the seat's recorder environment (two ptrace users on one process), not this diff. CI's `closures` job does the recording that counts. The cheaper detector would be the recording at the merge base, which costs the same ~20 min as the recording itself; I have not built one, and the condition is carried below under `## Friction`. The self-test's red before the arm existed was the failing test, written deliberately before the fix. `main`'s possible push-CI red on `tests / ci-ratchet` is not this diff's: this diff touches no ratchet file, and a hotfix is in flight, as the dispatch states.

## Forward-carry

- Three CI commands that `prepr.sh` runs before the PR still have no arm in `ci_predict.py`, so `body_push.sh` hands off a head they refuse: `tests/closure.py no-copies` (`copies_line`, the `closures` job), `tests/throwaway_git.py --check` (`throwaway_line`, `governance.yml`) and the claim-file check (`claims_line`, `tests/env_drift.py`). Control, as for this arm: for each one, a planted violation must make `ci_predict.py` predict red, and a null plant must keep it quiet. They belong in R10-FLOW-JIDOKA's error-proofing before handoff. Carry: R10-FLOW-JIDOKA
- `prepr.sh` runs the layout guard twice: in step 6d through `ci_predict.py`, and on its own through `moved_line`. This is only a duplicate print, not a disagreement, because both call the same `guard`. `moved_line` stays because its self-test pins the refusal hints and a tree with no predictor. Retiring it is a `prepr.sh` change outside this one-module group. Carry: R10-FLOW-JIDOKA

## Friction

- gate-scoping: cost: on this cloud seat, `prepr.sh`'s closures step refuses any diff that reaches `tests/entities.py`, because `hb:positive_control`'s `py-spy` sample fails under the strace recorder. The base reproduces the same 2 of 2425 failures, so the refusal says nothing about the diff, and each occurrence costs a ~20 min recording to show that. Carry: R10-POLICY-GATE-SCOPING
