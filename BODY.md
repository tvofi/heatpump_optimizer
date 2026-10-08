Encodes the owner's ruling that every fix is architecturally sound, binding on the fixer, the fix reviewer and the orchestrator.

- `dev/governance/roles/fixer.md` step 17: a fix is sound, and a list of architectural rules for new code, each checked against the tree (below). Where minimal and sound conflict, the fixer asks the orchestrator.
- `dev/governance/roles/fix-review.md` step 15: a breach the body does not name as a kept exception is `blocked <sha> architecture-unsound: <how>`.
- `.claude/workflows/web-fix-wave.js`: `architecture-unsound` joins `VERDICT_CLASSES`, so the wave routes it as itself, not to `other`. `bus.sh`'s blocked grammar (`[a-z-]+`) already accepts the word. `merge_train.py` reads only `merge` verdicts.
- `dev/governance/roles/orchestrator.md` section 5: concurrent fixes sharing a concern push only after a binding architect design note.
- `CLAUDE.md`: the fixer row in the role table says "architecturally sound".

## Approval

tvofi, in chat on 2026-10-08, verbatim: "That fixes should be done in an architecturally sound way should always be true, binding and persistent".

tvofi's follow-up request, relayed by the orchestrator the same day, extended `fixer.md` with generic architectural rules fitted to this codebase. Each rule was checked against `custom_components/heatpump_optimizer/` at the merge base. Where the tree already breaks a rule, the rule applies to new code and the known exceptions are listed here:

- **No `homeassistant` import in model, optimizer or learner modules.** `thermal_model.py`, `optimizer.py`, `sysid.py`, `curve_learning.py` and `comfort_learning.py` import none. Exceptions: `dhw_learning.py` imports `HomeAssistant` and `dt_util`, and `legionella.py` imports `issue_registry`. `accuracy.py`, `defrost.py`, `away.py`, `boost.py` and `inputs.py` import only `homeassistant.util.dt`.
- **Entity reads go through `InputReader`.** `hass.states.get(` also appears in `away.py`, `pump_signals.py`, `setpoint_check.py`, `pump_arbiter.py`, `coordinator.py`, `services.py` and `config_flow.py`.
- **Actuator writes come from the coordinator or `pump_arbiter.py`.** `services.async_call` also appears in `repairs.py` (a repair flow) and `disinfection.py`. In `disinfection.py` the call is an injected callable.
- **No module-level state.** `boost.py` has `global _cold_lease` (the arbiter registers it to avoid a reverse import), and `coordinator.py` has `_PROCESS_WORKER`.
- **Fail closed.** This matches `inputs.py`'s contract: an over-age value is reported as missing, and the caller freezes rather than guesses.

tvofi's second clarification, relayed the same day: a budget may rise as a last resort when the raise is what lands a truly better architecture. The list therefore does not include "structure ratchet held". It sends a budget that blocks the better architecture to `fixer.md`'s existing raise path (`CLAUDE.md` rule 2, owner confirmation before the push) and does not restate that path. "No new import cycles" (the ratchet's `import_cycle_modules`) is left to the ratchet for the same reason.

The `fixer.md` budget raise in `dev/governance/config/policy_budgets.json` (`files` and `files_tokens`) is the orchestrator's decision under mandate 6067089637. It raises to the measured values only. The payments taken were the step 6 "Coordinator" gloss, which nothing in that step uses, and #714's line-number sentence in step 14, which step 9's rule against bare line numbers already covers. They did not cover the owner's list. `orchestrator.md` and `fix-review.md` were paid in full within their caps: the role list in the preamble that duplicates `CLAUDE.md`'s index, the step 12 restatement of "check it is still the head", and two clauses restating `fixer.md` step 9 and `root-cause.md`.

## Head

`38c8170147a6cd3d87e75ef7d39752bbcf4de79a`

## Mutation proof

The diff writes no production code line. The one script change is the `VERDICT_CLASSES` entry. Deleting `'architecture-unsound',` from `.claude/workflows/web-fix-wave.js` and running `node tools/policy/check-wave-script.mjs` exits 1 with `FAIL fix-review.md teaches block class "architecture-unsound", and VERDICT_CLASSES carries it`. With the entry restored it exits 0.

## Null control

The same check at the head with the entry present prints `ok` for both the example's parse and the taught class. The deletion above is the arm that would have shown the vocabulary not carrying the word.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: every per-file cap is met at the head. `fixer.md` is at its raised cap, and the aggregates are within cap plus band.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`. No rule source changed.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/check-wave-script.mjs`: 0 failed at the head.
- `git grep -lE "^\s*(from|import) homeassistant" -- custom_components/heatpump_optimizer/`: enumerates the HA-importing modules behind the exceptions in `## Approval`.

## Red checks

- `budget-raise-gate`: red by design until tvofi approves at the head (0013); the raise is the two `fixer.md` caps above, decided under mandate 6067089637. No cheaper detector is owed: the gate is the detector, and it fired.

## Forward-carry

none: the rule binds through the contracts it edits.

## Friction

none
