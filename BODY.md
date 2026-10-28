R10-ORCH-BEATD arm (a): the supervised beat's engine, `tools/audit/seat/beatd.py`, and the beat jobs' git, `tools/audit/seat/beatd_shims/git`, with their `INSTRUMENTS.md` entries and the self-test's CI step. This is the first of three serial arms of #2505 (concern B). It does not close the issue, because (b) and (c) follow.

The approved note is `dev/programme/designs/R10-ORCH-BEATD.md` on `design/R10-ORCH-BEATD` at 32e249d2ed66bd8dfd7f158efedeb93b306edac5 (`Design review: approve 32e249d2ed66bd8dfd7f158efedeb93b306edac5`, design-verdict at 4c15decb07c645eb54d543f1d4c8a12f14b7d7b9). Its §2 is built as written. For (b) and (c), the round-3 reference text is f0f0469294c95f39b399c1392c1d393bebc4985c §3 and §6.

Scope, as §2 sets it:
- no job row (`beatd.jobs.json` does not exist yet, so `run` without `--jobs` refuses with rc 2);
- no edit to any existing script;
- no policy text;
- both claim files byte-identical, and no golden fixture touched.

The only edit to an existing file outside `INSTRUMENTS.md` is one `governance.yml` step. `selftest_wiring.py --check` refuses an unwired self-test, so that step is required.

What the engine does:
- **Table.** It refuses a malformed table (rc 2, zero jobs run).
- **Single instance.** It holds `beatd.lock`; a second `run` exits 75.
- **Jobs.** Each job runs under its own lock and process group, with SIGTERM at `timeout_s` and SIGKILL 10 s later.
- **Class lock.** It takes the `orch-checkout` class lock, waits at most `class_wait_s` (default 60), and then records `busy`.
- **Journal.** It writes the journal.
- **`status`.** It reports `late`, `idle` and `DOWN`, plus `ALERT lock-owner-dead`, `ALERT pulse-silent` and `STALE-CODE behind=`.
- **`held`.** This is `beatd.lock`'s one reader for other scripts.
- **Real git.** It resolves the real git once and refuses rc 2 when that git is a shim or does not answer `git version` (carry dr4-real-git-validate).

The shim resolves the real git from `HPO_REAL_GIT` only when that is a regular executable file that is not a shim (carry dr4-real-git-validate: a directory falls back to the PATH walk). Otherwise it walks `PATH` and skips every copy that carries the line-2 marker, read with builtins. With no real git it exits 127. It retries a `fetch` or `pull` that fails on `cannot lock ref`.

Arm (a)'s three carries are closed here: dr3-shim-discovery, dr3-bash32 and dr4-real-git-validate. The (b) and (c) carries stay on the roster group, as the note and the verdict assign them.

Two repairs followed the first open's prepr refusal (code f1f34cd61):
- **throwaway git.** The self-test's fixture repositories were raw `git init` and `git clone` calls. They are now built with `tests/throwaway_git.py` (`throwaway_git_init` / `throwaway_git_clone`), so auto-maintenance is off in both the environment and each repository's config. The race's fetches still run under the beat's own env.
- **policy_lint `named-docs`.** The bare-name pass resolved the word `git` in `.claude/rules/claim-files.md` prose to the tracked extensionless file `tools/audit/seat/beatd_shims/git`, the only tracked file with that basename. It reported that file as an uncapped document. The shim must be named `git` to be found on `PATH`, and it is an executable, not prose.
  - The exclusion is the data file's: `dev/governance/config/corpus_excluded.json` gains the path, and its `_comment` the reason.
  - An earlier head (f008c2b75) put the same entry in `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. That passed locally but went red on #2916, because `governance.yml`'s policy-docs and env-matrix jobs restore pinned check sources from the base before grading. That is the case `corpus_excluded.json`'s own `_why_data_not_source` describes. That edit is reverted, so `policy_lint.mjs` is byte-identical to main and no existing program is edited.
  - `policy_lint_mutants.mjs` exited 1 for the same cause, because its entry point is `policy_lint.mjs` on the corpus as it stands.

## Head

c991d64cdaef342d282d1a8e991dadc2671f917d

## Mutation proof

The self-test plants each mutant in a temp copy of `beatd.py` and `beatd_shims/git`, runs that case against the copy, and requires the named check to go red. The plants are the `MUTANTS` table in `beatd.py`. Every plant is a predicate change, and the self-test pins each anchor to occur exactly once in production text. Run at f008c2b75, every plant below turned its check red (`mutant <name> turns (<case>) '<check>' red` printed `ok`):

- `m1_parse_defaults_to_zero_jobs`: (1) `unreadable`
- `m1b_unknown_key_accepted`: (1) `unknown key`
- `m2_no_instance_flock`: (2) `second run exits 75`
- `m3_no_killpg`: (3) `its process group was killed`
- `m4_serial_jobs`: (4) `fast passes while slow runs`
- `m5_class_ignored`: (5) `class jobs never interleave`
- `m6_retries_zero`: (6) `race: B through the shim exits 0, origin/main current, a retry logged`
- `m6_no_shim_prepend`: (6b) `beat job B exits ok through the shim`
- `m6_drop_C_skip`: (6) the same race check
- `m6_string_compare` (round 3's rule, f0f046929 spike `shims/git`): (6) `discovery relative: rc 0 within 5 s`
- `m6_marker_via_head`: (6) `discovery no-real-git: rc 127, one line`
- `m6_real_git_dir_accepted` (dr4): (6) `discovery real-git-is-dir: rc 0 within 5 s`
- `m6_beatd_trusts_any_git` (dr4): (6) `beatd refuses rc 2 when its git is not git`
- `m7_late_without_timeout`: (7) `null: past interval, inside interval + timeout, is not late`
- `m7_no_pulse_alarm`: (7) `pulse-silent while beatd reads healthy`
- `m8_held_always_free`: (8) `held: rc 0 while held`

Failing test first: at the merge base 71fe1f7fcaeadd448a3e2213744f68b3e680e24e, `beatd.py` does not exist, so `python3 -I tools/audit/seat/beatd.py --self-test` cannot run. An earlier cut of this branch had three surviving plants, `m1b`, `m7_late_without_timeout` and `m7_no_pulse_alarm`:
- Case (7) called the parent's own `status()` instead of the copy under test.
- Case (1)'s bad job reused the good job's name, so a duplicate-name refusal masked the unknown-key one.

Both cases were fixed before this head, and all 16 plants now kill.

## Null control

Each case carries its own null in the same run, and each printed `ok` at f008c2b75:
- (1) a well-formed table runs its job.
- (2) a run after the first ends gets the lock.
- (3) an in-time job reads `ok`.
- (4) the fast job alone passes as often.
- (5) two class-less jobs overlap.
- (6):
  - B with the beat's env and no shim exits 1 with `cannot lock ref`;
  - beatd runs when the real git is first on `PATH`;
  - `git status` through the shim logs no retry.
- (7):
  - a healthy fixture prints no alarm, rc 0;
  - a live lock owner, and a pulse with nothing stopped, are no alarm;
  - past the interval but inside interval + timeout is not late.
- (8) `held` is rc 1 with no lock file, and rc 1 after release.

Wiring null: with `governance.yml` restored to the merge base, `selftest_wiring.py --check` printed `UNWIRED tools/audit/seat/beatd.py` and `100 self-testing, 99 wired, 1 unwired`.

## Figures

- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused` at d72c4a982 and after. Null: at f1f34cd61 it printed `3 raw git init or clone site(s) refused` (beatd.py:668, :758, :824).
- `node tools/policy/policy_lint.mjs` at c991d64cd, with main's copy of the linter (`git diff origin/main -- tools/policy/policy_lint.mjs` is empty): `TOTAL: 0 error(s) across 50 policy file(s)`, rc 0. Null: at d72c4a982, without the exclusion, it printed `TOTAL: 1 error(s)` with the `[named-docs] tools/audit/seat/beatd_shims/git` error, rc 1. #2916's policy-docs job at e09b123f9 printed the same error.
- `node tools/policy/policy_lint_envmatrix.mjs "$PWD" <dir> "$(git rev-parse HEAD)"` (CI's argv) at c991d64cd: `16 declared outcome(s) held, 0 did not, across 6 environment shape(s)`. Null: #2916's env-matrix job at e09b123f9 failed `pr / policy_lint rc=0 and every pin earned` and its push-main, no-remote and shallow siblings, each on the same named-docs error.
- `node tools/policy/policy_lint_mutants.mjs`: `MUTANTS ok`, rc 0 at c991d64cd. Null: prepr at f1f34cd61 refused it with `the entry point exited 1 on the corpus as it stands`.
- `python3 -I tools/audit/seat/beatd.py --self-test` at f008c2b75 (macOS, /bin/bash 3.2.57, git 2.38.1): `beatd self-test: 84 checks, 0 failed`. That is 68 case checks, 16 anchor checks and 16 mutant checks, the anchor checks counted by `MUTANTS`. Measured 2026-10-28T16:40Z; the same count at f8bb14aad before the throwaway_git change.
- `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh BODY.md` at f008c2b75 (before the named-docs move to the data file; see `## Red checks` for why its policy_lint step passed there): `PRE-PR: f008c2b75478f2f2c1722810a5983ee30fbe809f`, rc 0, with 32 ok, 6 skip and 0 REFUSE.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired` (null above).
- `python3 tools/audit/archscore/score.py --diff 71fe1f7fcaeadd448a3e2213744f68b3e680e24e HEAD`: `Architecture score: dS +0.0000 NULL`. The note's target is dS = 0; `vector.py` reads only `custom_components/heatpump_optimizer`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff 71fe1f7fcaeadd448a3e2213744f68b3e680e24e`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/entities.py` and `tests/harness_headers.py`. The new files sit under `tools/audit/`, which is on `tests/closure.py`'s INERT list, and inside `tests/layout.json`'s `tools` group (`tools/audit/seat/**`).
- `git diff --stat 71fe1f7fcaeadd448a3e2213744f68b3e680e24e...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION custom_components`: empty.
- Measured against origin/main f844df1fe750d5e420af0d1555f4b9472a740413 at 2026-10-28T15:33Z: `git merge-tree --write-tree origin/main HEAD` reports no conflict.

- `tests/closures.json` has one INERT READS entry: `tests/entities.py` reads `tools/audit/seat/beatd.py`. It was written by `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --apply-inert`, and after it the predictor printed `no closures, fast, wave-script or instrument red predicted`. 

## Red checks

- **`governance / env-matrix`** and **`governance / policy-docs`** at e09b123f9 (#2916). Both are the one `[named-docs] tools/audit/seat/beatd_shims/git` error. Fixed at this head through `corpus_excluded.json`; figures and nulls are above.
  - **Cause.** The exclusion was written into `tools/policy/policy_lint.mjs`. Both jobs restore that pinned program from the base before grading, so the branch's own copy never ran in CI.
  - **Root-cause trigger.** The trigger applies: a cheaper detector exists.
    - The check that fired runs locally in seconds (`node tools/policy/policy_lint.mjs`).
    - `tools/pr/prepr.sh`'s `policy_lint` step ran it and printed ok at f008c2b75, because prepr grades the head's own copy of a pinned program, while CI grades the base's.
    - The cheaper detector is prepr running each `PINNED` check source from the merge base, the way `governance.yml`'s "Restore the check source from the base commit" step does. Its standing cost is one `git show <base>:<path>` per pinned file on each prepr run.
  - **Process state.** (c): prepr was followed and passed, and did not model CI's restore.
  - **Not built here.** It is a change to `tools/pr/prepr.sh`, which is outside arm (a). It is owed to a root-cause seat under `defect-root-cause.md`.

## Forward-carry

none

## Friction

none
