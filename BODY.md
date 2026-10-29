Root-cause record for the recurring-friction key `.claude/rules/gate-scoping.md`, with the one countermeasure its cost test passes landed: the stand-in environments in `tests/entities.py` no longer carry `BASH_ENV` into `bash -c`.

The key counts 10 PRs / 11 entries in `v7.0.4..origin/main` at the merge base. `dev/audit/rca/R10-FRICTION-GATE-SCOPING.md` groups them by the rule step each one names. Four PRs (#2698, #2707, #2834, #2837) have one cause. A cloud container's `BASH_ENV` re-prepends `/opt/hpo/venv-ci/bin` before every `bash -c`, so the real `python3`/`python` shadows the stand-in that U0c and the delivery_status check put first on `PATH`. Both checks then read red at every tree, and CI, which sets no `BASH_ENV`, stays green. The tree's earlier answer (`8f2abbedf`, the profile written by `cloud-setup.sh`) never reached a running environment: this seat's profile is still the older form. All four entries merged after it, and that is the reopening condition `s6-batch22.md` recorded. The other groups are refused or already owned, each for a stated reason: interpreter, lease, closures, and two entries that name no step of the rule. No policy file changes.

Disposes #2835. No closing keyword: the roster lists 2835 in `R10-FRICTION-GATE-SCOPING`'s `issues` with `fixes: []`, so `pr-contract`'s intended list (`prepr.sh` step 7, `INTENDED_JQ`) refuses a closing keyword on it. The brief says the delivery closes it; adding 2835 to the group's `fixes` or closing it at merge is the orchestrator's.

## Head

`6670a91b74530df212ea50bd72143c77bcd790a1` on origin/main `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c` (2026-10-29). The `tests/entities.py` runs were taken at `c24f1dbd46b64389ccec84bc31d95cff09beef03`. The one commit after it edits only the record's prose (`git diff --stat c24f1dbd4 6670a91b7` names `dev/audit/rca/R10-FRICTION-GATE-SCOPING.md` alone), so `tests/entities.py` is byte-identical at both (sha1 prefix `956fd3b65415`).

## Mutation proof

Mutant: in `_stub_path_env`, `env = {k: v for k, v in os.environ.items() if k != "BASH_ENV"}` becomes `env = dict(os.environ)`, which keeps `BASH_ENV` (sha1 prefix `dc50ae797d78`). The run's command is the same as for every run below: `PATH=/opt/hpo/venv-ci/bin:$PATH PYTHONPATH=$PWD/tests/hastub python tests/entities.py`, with `BASH_ENV=/etc/profile.d/hpo-toolchain.sh` or under `env -u BASH_ENV`.

- In CI's environment (`env -u BASH_ENV`): `1 of 2471 ENTITY CHECKS FAILED`, rc=1. The failing check is `a stand-in on PATH wins in a bash -c under a BASH_ENV that re-prepends a toolchain (#2835)`, with `control='toolchain' … read='toolchain' (want the stand-in's 'stub')`.
- With the container profile as `BASH_ENV`: `3 of 2471 ENTITY CHECKS FAILED`, rc=1. The new check fails, and so do `gate-sweep.yml: on CI's completion, no concurrency, …` (U0c) and `graders-head-copy's delivery_status step is red only when …`.
- Restored: `ALL 2471 ENTITY CHECKS PASSED` under both.

The mutant changes the predicate: it is the line that decides whether `BASH_ENV` reaches the child.

## Null control

- The unmodified tree (the merge base `88c6ad5`) in CI's environment: `ALL 2470 ENTITY CHECKS PASSED`. The defect is invisible there, which is why CI never caught it.
- The new check's own null control is its `control` arm. The planted profile, run through a plain `bash -c` that keeps `BASH_ENV`, must read `toolchain`. A profile that fails to load would make the arm red, so the check cannot pass vacuously.
- The enumerator's null control: the same 285 bodies with `gate-scoping` rewritten to `gate-scopinX` print `TOTAL 0 PR(s) / 0 entr(ies) over 285 bodies`.

## Figures

- The key's count: `node tools/policy/policy_lint.mjs --stats --since v7.0.4` at `88c6ad5`, rc=0, prints `10 / 11 .claude/rules/gate-scoping.md` over `285 merged pull request(s)` (`dev/audit/rca/gate-scoping/stats_v7.0.4_88c6ad5.txt`). The control is #2896's run at `6eb552157`: `8 / 8` over 218 (`dev/audit/rca/harness-friction/stats_v7.0.4.txt`).
- The independent enumeration: `python3 -I dev/audit/rca/gate-scoping/friction_lines.py <bodies>` over one `gh api repos/tvofi/heatpump_optimizer/pulls/<N> --jq .body` per `Merge pull request #N` subject in `git log --format=%s v7.0.4..origin/main` prints `TOTAL 10 PR(s) / 11 entr(ies) over 285 bodies` (`dev/audit/rca/gate-scoping/friction_lines_88c6ad5.txt`). This matches the histogram on both numbers.
- Base reproduction at `88c6ad5`: with `BASH_ENV=/etc/profile.d/hpo-toolchain.sh` the run prints `2 of 2470 ENTITY CHECKS FAILED`, rc=1. Under `env -u BASH_ENV` it prints `ALL 2470 ENTITY CHECKS PASSED`, rc=0. A sorted diff of the two runs' `FAIL` lines (`diff <(grep '^  FAIL' a | cut -c1-110 | sort) <(grep '^  FAIL' b | cut -c1-110 | sort)`) leaves exactly U0c and delivery_status. Every other line in either list is a planted control (`a8:register_once`, `hb:positive_control`) whose measured figures differ between runs.
- Head at `c24f1dbd4`: `ALL 2471 ENTITY CHECKS PASSED`, rc=0, both with that `BASH_ENV` and without it.
- The container's profile: `cat /etc/profile.d/hpo-toolchain.sh` prints `export PATH="/opt/hpo/venv-ci/bin:$PATH"` with no guard. That is the form from before `8f2abbedf`.
- This seat's interpreter: `python3 --version` prints `Python 3.11.17` and `/opt/hpo/venv-ci/bin/python --version` prints `Python 3.14.7`. `bash tools/audit/seat/cloud-setup.sh --check` prints `REFUSE python3 is /usr/local/bin/python3, HPO_TYPING_PYTHON is unset, OPENBLAS_CORETYPE is unset`.
- Merge times: `git log -1 --format=%cI --grep="Merge pull request #<N> " origin/main` for each PR, against `git log -1 --format=%cI 8f2abbedf` (2026-10-24T10:31:51Z) and `aa44f4bcc` (2026-10-24T08:09:13Z).
- Class seams. At the merge base, `git grep -n '"PATH":' -- 'tests/*.py'` returns 9 sites. Each one's disposition:
  - `_gs_step_verdict` (U0c): closed in this diff.
  - `_train_hold_status`: closed in this diff.
  - `_pt_trigger`: closed in this diff.
  - `_pt_ds_rc` (delivery_status): closed in this diff.
  - `_raf_job_ok`: already guarded. It builds a bare environment under `bash --noprofile --norc`.
  - `_fetch_ledger` and the `liveRequiredContexts` probe: not in the class. They run `node -e`, whose `execFile` resolves the stub with no `BASH_ENV` read first. Both are green in the base `BASH_ENV` run.
  - The `("path", {"PATH": "1"})` row: not in the class. It is a data literal.
  - `tests/throwaway_git.py` `hostile`: already guarded. It builds a bare environment.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` and names `tests/entities.py` and `tests/harness_headers.py`. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=88c6ad5 ./tests/run.sh` at the head prints `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, rc=0, at `6670a91b7` (553 s); `tests/harness_headers.py` passed in its "alone on the box" stage (133 s).
- Ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Unpinned sites

none

## Red checks

none

## Forward-carry

- `_train_hold_status`, `_pt_trigger`, `_pt_ds_rc` and `_gs_step_verdict` now build their environment with `_stub_path_env` (`tests/entities.py`). Countermeasure B switches these same helpers to `bash -e -c`, and its "under `BASH_ENV` unset" precondition no longer needs a seat to unset anything. Its fixer edits the `subprocess.run` argv and keeps the `env=_stub_path_env(...)` argument. Carry: R10-ERREXIT-COUNTERMEASURES

## Friction

- defect-root-cause: cost: `policy_lint.mjs --stats` prints a key's counts but no PR numbers, so this seat, P81 (`s6-batch12.md`) and `s6-batch22.md` each re-enumerated the window's bodies by hand to learn which PRs a friction key counted. `dev/audit/rca/gate-scoping/friction_lines.py` lands here and reproduces both numbers. Carry: dismissed: the enumerator lands in this pull request
