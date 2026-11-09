Design review: approve a64af2b343b826d253eb86ce2dfe4f12f67da9b9

Design round 3, the last note. Reviewed `design.md` at a64af2b3 from a detached worktree. The base was judged against f365ce75, and the predecessor against #3299 head e066a630 (off_restore.py, `__init__.py` read there). The rulings already made were not re-opened: option (a), C1/C2 landing in this group, the restore-on-stop hook standing, and ghc-d02 as an open owner decision.

## Round 2 (c9069f21, point 1 harness): answered by ruling (a), applied consistently

- `design.md`:48-51: C1 and rule R bind only `neutral=None` consumers. Kind `offset` keeps `armed[key]: float | None` (off_restore.py:88 at e066a630) and the disarm-on-unconfigured rule (async_restore, `value is None` → pop unwritten).
- `design.md`:52-55: `_armed_record` reads a mapping as a baseline entry and every other value as today. #3299 writes only `None`, so no stored record reads differently, and there is no version bump or migration.
- `design.md`:56-62: the entry's shape picks the restore path. A `None` entry follows #3299's path unchanged. A mapping follows rule R, with the per-key writer registered as an optional keyword, so kind `offset`'s registration line stays as it is.
- `design.md`:63-69: the cross-kind arms are both stated. A baseline entry under an `offset` restorer is restored by rule R first. A `None` entry under a `persistent` restorer is disarmed unwritten and never writes 0 onto a persistent target. This matches #3299's `async_restore` arithmetic at e066a630 (neutral None and baseline None mean pop unwritten).
- `design.md`:70-75 and 91-92: the False-return-as-failure rule (ghcp-r5) and C4's WARNING bind baseline entries only. The `restored` signature change leaves kind `offset`'s state and writes unchanged. I4 holds.
- `design.md`:137-142: I4 and I5 are restated to match C1. The contradiction round 2 named is gone.
- `design.md`:245-252: the null control states the kind-`offset` record byte-identical to #3299's with no `state` key. The new record arm is run at both heads, and its perturbation (rule R on neutral entries) turns sub-arm (i) into a mapping, so the control goes red.
- The routed decisions are carried as ruled: `design.md`:284-294 (order; stop, carried to R10-ARBITER-OFF-RESTORE as ghcp-08) and `design.md`:296-300 (ghc-d02 open, with no dependency in C1-C4).
- ghcp-r7 is moot under (a), and correctly so: no legacy entry is resolved against a config.

## Checked and sound

- Seam (step 1): one owner per concern. off_restore owns the record, baseline, MODE_OFF, unload and remove. heat_curve owns the mapping and write policy and persists nothing itself. `__init__.py`:424-438 at e066a630 restores on unload with `effective_config` and calls `async_forget`, both unchanged. No coordinator line is added.
- Shape (step 2): every moved behaviour traces to the owner rulings, PR 3284's P1-P7 and O1-O5, carries a2b5f107, 67895f89 and 73eb63bd, or review rounds 1-2.
- Sibling sites (step 3): the off_restore, MODE_OFF, unload, remove and shutdown sites are tabled (`design.md`:200-208). The arbiter's Store and off rule are R10-ARBITER-OFF-RESTORE's.
- Evidence plan (step 4): the failing test is red at e066a630 for the stated reason (offset fallback, then `range_excludes_zero`). No golden or claim file moves. The null control moves under its perturbation through sub-arm (i), but see the carry on (iii).
- Siblings in flight (step 5): of the open `design/*` refs, only `design/R10-GENERIC-HEAT-CURVE` (the predecessor, #3299) names off_restore or heat_curve. Plain hot-file overlap such as config_flow.py is a matter of serial order, which is the orchestrator's.
- Cost (step 6): the design adds about 40 lines to off_restore, no new production file and no coordinator line. Splitting heat_curve's decision is planned to keep `functions_cc_over_15` flat. This fits L.

## Notes for the fixer (carried)

- `design.md`:249-252, null-control sub-arm (iii), "re-arm, clear the entity in the options, restart": on a loaded entry, an options save reloads the entry (`async_update_options`, `__init__.py`:373-399 at e066a630). The reload's unload restores with the old `effective_config`, so 0 is written to `number.o` and the record is emptied before the restart. As written, (iii) dumps a write of 0, not "no write", in both runs, and the rule-R perturbation cannot flip it. Build (iii) as a crash: drop the entry without unload, change the options in storage, then set up. That exercises the disarm-on-unconfigured branch round 2 named. Keep (i) as the arm that kills the `neutral is None` guard. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r10)
- The same reload applies to the off_restore arms "armed on A, options to B, restart" and "kind `persistent` armed on A, options to kind `offset`" (`design.md`:230-234). To reach rule R rather than the unload restore, each must cross a crash (no unload), as `design.md`:129-130 says. Add one control arm for the loaded-entry path too: A is restored by the reload's unload, then B is armed. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r11)
- C3 adds a `state` section. `_save` (off_restore.py at e066a630 writes `{"armed": ...}`) must omit `state` when no consumer holds one, or the kind-`offset` byte-identity in the null control fails. Carry: R10-GENERIC-HEAT-CURVE-PERSISTENT (item ghcp-r12)

Seat token count: not reported by the harness.
