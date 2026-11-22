Design review: approve 3850f3368e69f2b442bcf07cf84464fcd056a235

This is a delta review of design/R11-OWNER-FAULT-TEXT from cd54988f8f to 3850f3368e (`git diff cd54988f 3850f336`). Code was read at origin/main eaaaf24e5b. R1 was routed as `decision: owner`. The orchestrator relays the owner's ruling of 2026-11-22, "I think it should suggest it", which restores the fault-alarm discovery rows. This is a product decision the contract routes to the owner. It is not a contract change, so this review applies it as relayed. Nothing else in the note moved: the diff touches only Discovery, test 9, the sibling-site line, the release note and one carry.

## Delta
- The restored rows fit the existing shape.
  - `("binary_sensor","fault")` in `_TUYA_HEAT_PUMP` maps to the Tuya "Fault Alarm" (`value != 0` on dp 20; tuya_heat_pump models/000004k4z6.py:348-354).
  - `binary_sensor.{p}_alarm` in `_NAMED` is the GCHV "HP Alarm", which is an OR over the four alarm registers (rotenso_windmi_gchv.yaml:1127-1132).
  - `CONF_HEAT_PUMP_FAULT_ENTITY` becomes a scalar `_NAMED` key. So `infer`'s existing loop (modbus_prefill.py:266-268) suggests it on the device path and the Modbus path alike, behind the existing `not current.get(slot)` guard. No list-role shape is needed, so R2's cut stands.
- The effects are disclosed instead of hidden. The note lists the three readers an accepting install comes under: FAULT-HOLD after 10 min (57d5d278), `FREEZE_FAULT` (pump_signals.py:514-528) and the duty-switch void (`pump_arbiter._switch_context`). It also names the GCHV warning-bit case and its way out (the `fault_hold` opt-out, which ends the hold but not the freeze or the void). The prefill page text, the docs row and the leading release-note line all say so, and that order meets the release-extra-steps rule.
- The flag read stays domain-strict (R3 holds), so a binary sensor suggested here reads through the flag path unchanged.
- Test 9 now covers Tuya (text list plus flag), GCHV (flag only, no text) and two nulls: no signature gives no suggestion, and a configured flag slot is not suggested. `qualifies` is unchanged, as in rev 2.
- Carry flag-prefill-reach covers the case where FAULT-TEXT lands before FAULT-HOLD: the text then names only the freeze and the void. That is consistent with the serial order FLOWCAP > FROST-HOLD > FAULT-HOLD > FAULT-TEXT.

## Notes for the fixer
- The rev 2 carries list-loop-empty and item-split still stand.
- Carry: R11-OWNER-FAULT-TEXT (gchv-warning-test): pin the GCHV warning case the note names. With the suggested `binary_sensor.<p>_alarm` on and only a bitmap-1 sensor-fail bit set, the docs row's claim (hold after 10 min, released by the opt-out, freeze kept) is checked by one features case against FAULT-HOLD once it has merged.
