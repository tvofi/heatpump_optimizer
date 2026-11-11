Anchor `tests/harness.py` to its own tree so a harness run from another root no longer measures the cwd's tree (carry 3, R10-RCA-COP-UNMEASURED item 6d58568e), and settle the cloud-seat environment carries. Topic r10-suite-env-residue.

## Head

6ce0b46dda03523c269cbc169bc2c80ea54bc5ee (code head of this branch).

## Mutation proof

Production change: `tests/harness.py` anchors its two `sys.path` inserts and the translations listing to `_ROOT`. The check `tests/harness.py from a foreign cwd finds its catalogues and its own tree's package` in `tests/harness_headers.py` runs `import harness, heatpump_optimizer` from a cwd holding a decoy `custom_components/heatpump_optimizer/` and asserts `heatpump_optimizer.__file__` lies under this tree's `custom_components`. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`:

- head: ALL 113 HARNESS HEADER CHECKS PASSED.
- M1 (reviewer's mutant: both `sys.path.insert` calls reverted to `"tests"` / `"custom_components"`, translations anchor kept): 1 of 113 HARNESS HEADER CHECKS FAILED. It survived the previous head; the decoy cwd now kills it.
- M3 (whole `tests/harness.py` at the base): fails through the same check.

`mutant_run.py --diff 40fe1cae2ed3...HEAD` lists no mutant: diff mode reads added lines outside `tests/` and `dev/`, and this PR changes only `tests/` and one seat script, so the proof above is the manual M1 run.

## Null control

The same check at the base raises FileNotFoundError reading `custom_components/heatpump_optimizer/translations` from cwd `/`; the base tree's other checks are unchanged (113 pass at the head, so the other 112 are untouched).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at the head: the pass above (instrument: that script; scope: its 113 checks).
- Seam enumeration for the cwd-capture class: `git grep -l 'from harness import\|import harness' -- dev/audit/harnesses/ | xargs grep -l sys.path`, less `git grep -l os.chdir -- dev/audit/harnesses/`. Every file it lists imports `tests/harness.py`, whose inserts are now absolute, so the class is closed at the shared module, not per harness. A harness that inserts its own relative `sys.path` entries for other modules (e.g. `cop_duty_floor.py` inserts `tests`) is its own seam and is not changed here: Carry: dismissed: those inserts resolve a harness the caller already placed in the intended root, and the shared module no longer captures the cwd.
- `tests/entities.py` and `tests/arch_score.py` run on the base checkout and on the head: entities passes at the base (rc=0) and failed at an intermediate head only on the policy-lint token cap (see Red checks); at the head only the unrelated arch-score check below fails, identically at the base.

## Red checks

- `policy_lint` budgets (`tests/entities.py` D11-05 arm): an intermediate commit added a note to `.claude/workflows/web-fragments.md` and then `tests/README.md`, both at zero token headroom; removed, `node tools/policy/policy_lint.mjs` prints TOTAL: 0 error(s). The cheaper detector is that same command, already in `prepr.sh`; standing cost nil.
- `tests/arch_score.py` check `arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)`: fails identically on the base checkout (`fatal: '/opt/hpo/runner-temp/base' already exists`), a stale directory in this seat, not a repository defect. `prepr.sh` therefore printed one REFUSE `closures ... tests/arch_score.py (exit 1)`; CI runs a clean runner. Carry: dismissed: seat residue, not reproducible on a fresh runner.

## Forward-carry

- Carry 4 (cloud-setup venv-ha lacks scipy and paho): `tools/audit/seat/cloud-setup.sh` header now states venv-ha is typing-only by design and the suites run under venv-ci with `PYTHONPATH=tests/hastub`; measured: under venv-ci with the stub, `import harness` succeeds from a foreign cwd. Adding paho or scipy to venv-ha would need a new hash-pinned lock entry, which the typing lock does not carry; not built. Carry: dismissed: premise stale, venv-ha is not a suite interpreter.
- Carry 2 (no-`pr` dispatch form for a CI-cost hotfix): `.claude/workflows/web-fragments.md` and `tests/README.md` are both at their token caps (`node tools/policy/policy_lint.mjs --budgets`), so the one sentence has no home without a cap raise or a payment. Carry: dismissed: needs an owner ruling on a cap raise; the fact is `ci.yml` `workflow_dispatch` with `-f base=<ref>` and no `pr` input.
- Carry 1 (nightly heartbeat respawn): not buildable here. The measurement recipe needs `gh run list --workflow nightly.yml`, unavailable in this seat; the brief's own rule closes the group as superseded absent a red `hb:positive_control` at a main carrying the unwinder fix. Carry: dismissed: no red measured; `tests/nightly_ha.py` already samples with `_remote_debugging` where it exists.
- Carry 5 (stress memory-peak precondition, traced bump on 3.14): addresses a group whose roster stage is done and is not this group's seam. Carry: dismissed: no destination is live; the precondition (re-measure base beside head on one box before reading a 3.14 stress memory red) stays in the carry text of the brief.
- Carry 6 (cloud prepr.sh environment faults, item ec93383a): not reproduced on this cloud seat at 45adb0c3b4: `prepr.sh`'s hooks step printed `HOOKS ok: 4 wired hook(s) exist and pass their own --self-test`, and `tests/entities.py` at the base checkout exits rc=0 (`python3 tests/entities.py`, run on the unmodified base). Carry: dismissed: neither fault reproduces here; the one environment fault seen was a stale `/opt/hpo/runner-temp/base` (Red checks).

## Friction

none
