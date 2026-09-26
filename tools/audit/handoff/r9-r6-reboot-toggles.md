_Requested by **tvofi**_

The owed work in #1621's delivery row (`docs/delivery/1621.md`), from bug 5
of tvofi's v6.6.12 report: "After reboot. Away, boost DHW, optimizer active
and boost space heating are all on and can not be switched back off". #1621
fixed the "can not be switched back off" half. Two items remained. Closes
nothing: no issue exists.

**(b) The mode-persistence gap: fixed.** `async_set_mode` changed `_mode` in
memory and nothing wrote it until `_async_save_accuracy` at the end of a
completed `_async_update_data` cycle. A restart before that point, or a cycle
that raised first (a failed price fetch raises `UpdateFailed` before the
save), restored the previously stored mode. With `off` set and `auto` stored,
"Optimizer active" came back on after the restart. `async_set_mode` now calls
`_async_save_accuracy`, the store's existing and only save path, after it
changes the mode and before the refresh it may request. There is no second
writer path. The refresh can still fail after the save, and the mode is kept.

The added coordinator line and call edge are paid in the same method family:
in `_async_update_data`, the comfort, boost and off branches each built their
action with `"price": self._get_current_price()`. They now set it once after
the branch, for those three modes only. That is one line and two
`self._get_current_price()` calls fewer. The price is the same value, and a new
features check pins it for all three modes through the real update cycle.
`internal_call_edges` (318 to 317), `cross_seam_edges` (138 to 136) and
`cut_fetch` (131 to 129) are recorded down. The reasons are in the commit
message. No budget is raised.

**(a) "All on after reboot": the cause is still not identified.** What I ran
and what it showed:

- `reboot_probe_realha.py` runs on real Home Assistant (a real
  `HomeAssistant` core and the real `storage.Store` on a temporary config
  dir). It builds the tree's real `HeatPumpOptimizerCoordinator`, whose
  constructor spawns the store loads and `boost.restore_session`, and the
  real switch platform's four entities. It toggles each switch through the
  entity's own `async_turn_on` and `async_turn_off`, then runs
  `coordinator.async_shutdown()` and the real `hass.async_stop()`. A fresh
  `HomeAssistant` on the same config dir is the restart. After the spawned
  loads land, it reads each switch's `is_on` and what the coordinator holds.
  - All four turned on, then all four off, then a completed cycle's save,
    then the restart: every switch reads off. The disk holds away
    `active: false`, boost `{}` and accuracy `mode: off`. Same result at the
    merge base, at the head, and on the v6.6.12 tree (`git archive v6.6.12`,
    with `coordinator.data` published first, because v6.6.12's optimizer and
    away switches read the payload).
  - The same without the completed cycle: at the merge base and at v6.6.12,
    Optimizer active reads **on** (`_mode=auto`) and the other three read
    off. There is no accuracy store on disk at all. At the head all four
    read off. This is (b), and it is the only part of the symptom this
    reproduction produces.
  - Control, all four turned on, then the restart: all four read on. The
    store round trip is live, so an off result is not an empty read.
- `reboot_probe.py` runs the same off-then-restart drive on `tests/hastub`,
  whose `Store` shares a disk across instances. It gives the same results:
  Optimizer active on without a completed cycle at the base, and off at the
  head.
- A stored off never came back on in any run. Away and both boosts only read
  on after a restart when their own store said on: an away override with
  `active: true`, or a boost `until` less than `BOOST_HOURS` (2 h) in the
  future. At startup the only writers are `boost.restore`,
  `away.restore_override` and `_async_load_accuracy`, which copy the store,
  and `expire_override`, which only turns things off. The one exception is
  `away._migrate_helpers`. It can turn Away on only when the away store lacks
  `migrated_helpers` and the configured presence entity is an
  `input_boolean` that reads on. It has been one-shot since v6.3.16
  (`e4bc3756`), so it cannot have fired on a v6.6.12 upgrade to an install
  that already had an away store. `tuya_heat_pump` (cloned at `5c97dac`)
  references none of this integration's entities or services. This
  integration's `pump_arbiter` calls none of the four setters at the head,
  and at v6.6.12 it called only `async_set_mode(MODE_OFF)`, which turns the
  optimizer off.
- One ordering does bring a toggle back: a turn-off issued before the spawned
  restores land. The probe's `off_before_restore` scenario stores all four
  on, restarts, and turns all four off at once, before the loads settle. At
  the base and at the head, Away and Optimizer active read on afterwards,
  because the restore (or the stale accuracy load) applied what it read
  before the toggle. On v6.6.12, one run left only Optimizer active on, so
  the outcome depends on timing. I do not think the entities can reach that
  ordering. `async_setup_entry` forwards the platforms only after
  `async_config_entry_first_refresh()` returns, and that refresh awaits the
  sensor reads and the price and weather fetches, which were issued after the
  loads. This is an argument, not a measurement on a live instance.

What would explain "all on": the away and boost stores held on, for example
toggles made within the two hours before the restart, and the optimizer's
mode was set to off with no completed cycle after it, which is (b). The
evidence I have does not show who set Away and the boosts on. Queued turn-offs
cancelled by the restart are one untested possibility: at v6.6.12
`PARALLEL_UPDATES = 1` held each switch action behind a 33 to 73 s solve, so a
restart could cancel them before they ran. The probe does not drive Home
Assistant's service queue, so this is not established. The root-cause seat
owns the RCA. The cause recorded here is (b) for Optimizer active only.

**Residual, stated rather than fixed.** Before `_async_load_accuracy` lands,
the new save would write the in-memory default accuracy history over the
stored one. `async_reset_comfort_weight` has the same exposure today. It can
only happen if `async_set_mode` runs before the spawned load finishes, and
the entities and the `set_mode` service, which acts on loaded entries only,
exist only after the first refresh described above.

The delivery row `docs/delivery/<N>.md` is written by the Mac seat once this
pull request has a number.

## Root cause

For (b), as `defect-root-cause.md` requires of a defect that reached a
release. The RCA itself belongs to the parallel root-cause seat.

- **Cause.** `async_set_mode` wrote `_mode` only in memory. The one writer of
  the stored mode was the cycle-end `_async_save_accuracy` in
  `_async_update_data`, which runs only when every await before it succeeds.
  The comment beside that write ("Mode resets to auto on every reload;
  persist it.") shows the intent was persistence across a restart. The
  write's placement made that true only after a completed cycle.
- **Reproduced.** `reboot_probe_realha.py` and `reboot_probe.py` at the merge
  base, and the features check below (red at `c1450733`, which has the test
  and not the fix).

## Head

df50ab42e1fb2c9e02ba8c10c1ab9fc52bbd43b6 (merge base cb78e997; the code head
before merging main was a296478426c76953f15a528b24d0dd572a5b7b98 on merge base
81f2c18c). Main's merge brought only `.claude/skills/steward/SKILL.md`,
`docs/delivery/1632.md`, `tools/audit/README.md`,
`tools/audit/briefs/D4.md` and `tools/audit/prepare_baseline.sh`.

## Mutation proof

Each mutant is a detached worktree at a2964784 with one production edit.
Each ran `PYTHONPATH=tests/hastub python3 tests/features.py`, rc 1, `1 of 3367
FEATURE CHECKS FAILED`:

- m1, `await self._async_save_accuracy()` deleted from `async_set_mode`:
  FAIL "a mode change survives a restart with no completed cycle, and one
  whose refresh fails", `[('off', 'auto'), ('economy', 'auto')]`.
- m2, the save moved after the refresh (the predicate: before any await that
  can fail): the same check, `[('off', 'off'), ('economy', 'auto')]`. The
  `refresh=False` case passes and the failing-refresh case does not.
- m3, the hoisted `self._current_action["price"] = ...` replaced by `pass`:
  FAIL "each fixed-rule mode's action carries its own mode and the current
  price", `{'comfort': ('comfort', False), 'boost': ('boost', False), 'off':
  ('off', False)}`.

## Null control

- The unmutated head (a2964784): `ALL 3367 FEATURE CHECKS PASSED`, rc 0.
- The test commit without the fix (c1450733): `1 of 3366 FEATURE CHECKS
  FAILED`, only the mode-restart check, `[('off', 'auto'), ('economy',
  'auto')]`.
- The probes' own control is the `on_control` scenario (all on, then the
  restart): all four read on at every tree. A store read that came back empty
  would read off there.

## Figures

- `PYTHONPATH=<tree> <venv>/bin/python reboot_probe_realha.py`
  (`$SCRATCH/probe/reboot_probe_realha.py`, sha1
  4c573d45e6c43647dd3f469999bd9014d1be620b; the venv is CPython 3.14.0rc2
  with homeassistant 2026.2.3, mashumaro 3.22, numpy, scipy and
  threadpoolctl; the probe sets `typing.ByteString = bytes` because 3.14.0rc2
  dropped it and mashumaro still names it at import). `RESULT` lines, one per
  scenario, as `switch=is_on`:
  - base 81f2c18c, `on_then_off_no_cycle`: `OptimizerEnableSwitch=True
    AwaySwitch=False BoostDhwSwitch=False BoostSpaceSwitch=False _mode=auto`;
  - head a2964784, same scenario: all four `False`, `_mode=off`;
  - v6.6.12 (`PROBE_PUBLISH=1`), same scenario: as at the base;
  - `on_then_off_cycle` at every tree: all four `False`, `_mode=off`;
  - `on_control` at every tree: all four `True`, `_held=['dhw', 'space']`;
  - `off_before_restore`, base and head: `OptimizerEnableSwitch=True
    AwaySwitch=True`, both boosts `False`; v6.6.12: only
    `OptimizerEnableSwitch=True`.
- `PYTHONPATH=tests/hastub python3 reboot_probe.py`
  (`$SCRATCH/probe/reboot_probe.py`, sha1
  b947360f79b679067e6b7c8b11b7b08f253174af), run from the tree root:
  `RESULT optimizer_on_after_reboot_without_cycle= True` at the base and
  `False` at the head. `RESULT any_on_after_reboot_with_cycle= False` at both.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
  at df50ab42: `MODE: SCOPED -- 16 script(s) run, 10 scoped out.`
- `PYTHON=<venv314> GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=<merge base>
  bash tests/run.sh` at df50ab42: each of the 16 selected scripts and the always-run lines `ok`, `rc=0`; `golden.py` skipped in drift mode as `run.sh` skips it.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET
  PASSED`. The recorded rows (`internal_call_edges` 318 to 317,
  `cross_seam_edges` 138 to 136, `cut_fetch` 131 to 129) are `git show
  9183aef3 -- tests/structure_budgets.json`, as `structure.py --record`
  wrote them.
- No golden fixture moved, and neither claim file is touched: `git diff
  $(git merge-base origin/main HEAD)...HEAD --stat` lists only
  `coordinator.py`, `tests/features.py` and `tests/structure_budgets.json`.
  `env_drift.py --all` passed in the run above.

## Red checks

none: no check on this branch has run red in CI yet. Locally, the one red
check was the deliberate failing-test-first commit (c1450733).

## Forward-carry

none

## Friction

- `fixer-step-13: cost: no pinned real-HA environment in the cloud container; tests/requirements-typing.txt pins homeassistant 2026.9.3, which needs Python >= 3.14.2, and the container has 3.14.0rc2, so the real-HA probe ran on 2026.2.3 with a typing shim for mashumaro.`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
