Anchor `tests/harness.py` to its own tree so a harness run from another root no longer measures the cwd's tree (Carry 3, R10-RCA-COP-UNMEASURED item 6d58568e), and settle the cloud-seat environment carries. Topic r10-suite-env-residue.

## Head

7215e37c7136142c6d6c479babf462c8f69ac569 (code head of this branch), measured on origin/main a7628041dc02e298c5399003d4c0576391dd5c4e (merged in by 628e9d3058, a clean merge), 2026-11-11T06:57Z.

## Mutation proof

Carry 3. The production change: `tests/harness.py` anchors its two `sys.path` inserts and its translations listing to `_ROOT`. The pins are in `tests/harness_headers.py`. They run `import harness, heatpump_optimizer, profiles` from a decoy cwd that holds `custom_components/heatpump_optimizer/__init__.py` and `tests/profiles.py`. `dev/audit/harnesses/learner_inputs_swap.py` imports `profiles` straight after `harness`, which is why the decoy holds that module. Three checks pin the change:

- (P1) `tests/harness.py from a foreign cwd finds its catalogues and its own tree's package`: `heatpump_optimizer.__file__` is under this tree's `custom_components`.
- (P2) `tests/harness.py from a foreign cwd resolves a module the cwd's tests/ also holds to its own tests/`: `profiles.__file__` is under this tree's `tests`.
- (P3) `tests/harness.py's sys.path inserts are exactly its own tests/ and custom_components/, absolute`: the entries `import harness` adds to `sys.path` are exactly those two absolute paths.

So each insert is pinned on its own, twice. The `tests` insert is pinned by P2 and P3, and the `custom_components` insert by P1 and P3.

The reviewer's own mutants are taken verbatim from `origin/probe/rev-3431-677c1ae0:ev/mutant-*.diff`. Each is applied with `git apply` to a `git archive` copy of 8933c424. Its `tests/harness.py` and `tests/harness_headers.py` are byte-identical at the head: `git diff --stat 8933c424 7215e37c` lists only `tests/arch_score.py`. Each copy is git-initialised before the apply so that the register-status check reads a repository. Each copy is run as `PYTHONPATH=<copy>/tests/hastub python3 <copy>/tests/harness_headers.py`, once with cwd = the copy's root and once with cwd = a directory outside it:

| mutant | cwd = copy root | cwd = outside | failing checks | vs the d710f5dd verdict |
|---|---|---|---|---|
| null (unmutated head) | `ALL 115 HARNESS HEADER CHECKS PASSED` | `ALL 115 HARNESS HEADER CHECKS PASSED` | none | null still survives |
| M1a (`tests` insert alone back to `"tests"`) | `2 of 115 HARNESS HEADER CHECKS FAILED` | `2 of 115 HARNESS HEADER CHECKS FAILED` | P2, P3 (`added=['<copy>/custom_components', 'tests']`) | **changed**: survived (113 of 113) and is now killed |
| M1b (`custom_components` insert alone) | `2 of 115 HARNESS HEADER CHECKS FAILED` | `2 of 115 HARNESS HEADER CHECKS FAILED` | P1, P3 | unchanged: killed |
| M1 (both inserts reverted) | `3 of 115 HARNESS HEADER CHECKS FAILED` | `3 of 115 HARNESS HEADER CHECKS FAILED` | P1, P2, P3 | unchanged: killed |
| M3 (`tests/harness.py` at the merge base) | `3 of 115 HARNESS HEADER CHECKS FAILED` | no result line: `import harness` raises `FileNotFoundError: ... 'custom_components/heatpump_optimizer/translations'`, rc=1 | P1, P2, P3 at the root | unchanged: killed |

Every mutant changes the production line in `tests/harness.py`; `tests/harness_headers.py` is the same file in every row. A first pass ran from plain `git archive` copies with no `.git`. There, every row, the null included, also failed `the executed harnesses leave their committed output byte-identical` (`git status failed rc=128`). That is the runner, not the mutant (fixer step 2), and the git-initialised re-run above removes it.

`mutant_run.py --diff` is not pin evidence here: it skips `tests/`, and this PR changes only `tests/` and one seat script.

## Null control

- The check pins the defect, not the decoy. With the head tree, P1 to P3 pass from the decoy cwd (the null row above). With the base `tests/harness.py` (M3), the same import from a foreign cwd raises `FileNotFoundError`.
- The finder's harness at both ends. `learner_inputs_swap.py`'s pattern is `sys.path[:0] = [T/tests/hastub, T/custom_components, T/tests]`, then `import harness`, then `profiles`. I ran it with cwd = a `git archive` export of the merge base 40fe1cae2e:
  - T = head copy (8933c424): `profiles <T-head>/tests/profiles.py`.
  - T = M1a copy: `profiles <base-export>/tests/profiles.py`. That is the cwd's tree, the defect of item 6d58568e.
  - `heatpump_optimizer` resolves to T in both runs.
  - The capture is a scratch probe that reuses the finder's sys.path lines. No finder's harness is committed for 6d58568e.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at 8933c424 in the worktree: `ALL 115 HARNESS HEADER CHECKS PASSED` (instrument: that script; scope: its 115 checks, which are the 113 of d710f5dd plus P2 and P3).
- Scoped gate: `python3 tests/closure.py select --diff a7628041dc` printed `MODE: SCOPED -- 21 script(s) run, 12 scoped out` at 8933c424. `GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh` reported `ok` for every script it reached. It stalled in `tests/arch_score.py` and was stopped at the 30-minute background limit before `harness_headers.py` and `stress.py` ran in it. `harness_headers.py` passes separately (above), `tests/arch_score_head.py` alone prints `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`, and `tests/arch_score.py` is the Carry 6 fix below. `tests/stress.py` is left to CI's required run.
- Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no metric moved up.
- Seam enumeration for the cwd-capture class: `git grep -l 'from harness import\|import harness' -- dev/audit/harnesses/ | xargs grep -l sys.path`, less `git grep -l os.chdir -- dev/audit/harnesses/`. Every file it lists imports `tests/harness.py`. P3 now pins that the shared module's inserts are absolute and inside its own tree, so the class is closed at the shared module, not per harness. A harness that inserts its own relative `sys.path` entries for other modules (e.g. `cop_duty_floor.py` inserts `tests`) is its own seam and is not changed here. Carry: dismissed: those inserts resolve a harness the caller already placed in the intended root, and the shared module no longer captures the cwd.

## Red checks

- `policy_lint` budgets (`tests/entities.py` D11-05 arm), from an earlier round: an intermediate commit added a note to `.claude/workflows/web-fragments.md` and then to `tests/README.md`. Both are at zero token headroom. With the note removed, `node tools/policy/policy_lint.mjs` prints TOTAL: 0 error(s). The cheaper detector is that same command, already in `prepr.sh`; its standing cost is nil.
- `tests/arch_score.py` failed in this seat at 8933c424 (`1 of 279 ARCHITECTURE SCORE CHECKS FAILED`, on `arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)`: `fatal: '/opt/hpo/runner-temp/base' already exists`), and `prepr.sh` refused `closures` on it. It is not a required check, and it went red in no CI run of this branch. It is fixed in this PR, not answered as residue: see Carry 6. The cheaper detector is that script itself run twice in a seat, which `prepr.sh`'s closures step already does; its standing cost is nil. Carry: dismissed: fixed here (Carry 6).

## Forward-carry

- Carry 4 (cloud-setup venv-ha lacks scipy and paho): the header of `tools/audit/seat/cloud-setup.sh` now states that venv-ha is typing-only by design, and that the suites run under venv-ci with `PYTHONPATH=tests/hastub`. Measured: under venv-ci with the stub, `import harness` succeeds from a foreign cwd. Adding paho or scipy to venv-ha would need a new hash-pinned lock entry, which the typing lock does not carry; not built. Carry: dismissed: premise stale, venv-ha is not a suite interpreter.
- Carry 2 (no-`pr` dispatch form for a CI-cost hotfix): `.claude/workflows/web-fragments.md` and `tests/README.md` are both at their token caps (`node tools/policy/policy_lint.mjs --budgets`). The one sentence has no home without a cap raise or a payment. Carry: dismissed: needs an owner ruling on a cap raise; the fact is `ci.yml` `workflow_dispatch` with `-f base=<ref>` and no `pr` input.
- Carry 1 (nightly heartbeat respawn): not buildable here. The measurement recipe needs `gh run list --workflow nightly.yml`, which is unavailable in this seat. The brief's own rule closes the group as superseded unless `hb:positive_control` goes red at a main that carries the unwinder fix. Carry: dismissed: no red measured; `tests/nightly_ha.py` already samples with `_remote_debugging` where it exists.
- Carry 5 (stress memory-peak precondition, traced bump on 3.14): addresses a group whose roster stage is done, and it is not this group's seam. Carry: dismissed: no destination is live. The precondition stays in the carry text of the brief: re-measure base beside head on one box before reading a 3.14 stress memory red.
- Carry 6 (cloud prepr.sh environment faults, item ec93383a): one fault reproduced on this seat, and it is fixed here.
  - Cause: the #2068 plant check in `tests/arch_score.py` built its env as `{**env, **throwaway_git_init(repo, "-q")}`. `throwaway_git_env()` copies `os.environ`, so the seat's exported `RUNNER_TEMP=/opt/hpo/runner-temp` (`cloud-setup.sh --variables`) replaced the check's temp `RUNNER_TEMP`. The step's `git worktree add "$RUNNER_TEMP/base"` then wrote outside the temp dir, and every later run failed `already exists`.
  - Measured at 8933c424: with the directory removed, a run passes (`ALL 279 ARCHITECTURE SCORE CHECKS PASSED`) and leaves `/opt/hpo/runner-temp/base` behind. The next run fails as above.
  - Fix: `RUNNER_TEMP` is merged last. A new check, `the #2068 plant's base worktree lands in its own RUNNER_TEMP, not the caller's`, asserts that `<tmp>/t/base` exists after the step.
  - Seams: `git grep -nE '\*\*throwaway_git_(init|env|clone)\(' -- '*.py'` returns five merge sites. Only `tests/arch_score.py` put the throwaway env after a caller override. The other four (`tests/entities.py` three times, `dev/audit/harnesses/r10_tick_owed_level.py`) put their overrides last: already guarded.
  - Null control, at 7215e37c and with the directory absent, run twice: `ALL 280 ARCHITECTURE SCORE CHECKS PASSED` both times, and `/opt/hpo/runner-temp/base` is absent after each run.
  - Mutant: the merge order is reverted (`env = {**{"RUNNER_TEMP": str(runner_temp)}, **throwaway_git_init(repo, "-q")}`) in a worktree of 7215e37c. Result: `1 of 280 ARCHITECTURE SCORE CHECKS FAILED`, on `the #2068 plant's base worktree lands in its own RUNNER_TEMP, not the caller's`, and `/opt/hpo/runner-temp/base` reappears. Killed.
  - The other fault the item quotes, the hooks self-test, does not reproduce: `prepr.sh`'s hooks step prints `HOOKS ok: 4 wired hook(s) exist and pass their own --self-test`.
  - Carry: dismissed: the reproduced fault is fixed in this PR, and the other does not reproduce.
- Carry 7 (the same text as Carry 6, item ec93383a, filed a second time on the roster): answered by Carry 6 above. Carry: dismissed: duplicate of Carry 6, not reproduced.

## Friction

none
