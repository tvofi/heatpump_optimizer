# Class sweep I4 (round 11, PLAN phase D)

Mechanism: two independent parsers or definitions of one concept disagree.
Ledger status (`bugclasses.json`): detector/barrier `tools/policy/agreement.mjs`
covers registered governance concepts only; product-side placeholder sets,
weekday numberings, replay judges and bundle rows are not registered there.

Worktree: detached at `handoff/audit-r11-register` (28b864af6d).

## Enumerator
`bash dev/audit/rounds/round11/D14/sweep/i4_enum.sh` (39 s) runs every finding's
seam rule over the whole package (all flow cells, all 4569 leaf strings, all 37
exception sites, every card STRINGS key, all options fields, every weekday
reader) and prints one RESULT per reader pair.

- Positive control: re-finds every finding still present at this head
  (D4-s2-01 8, D6-s3-01 3, D17-s1-01 156, D15-s1-02 72, D15-s3-02 48,
  D15-s2-05 tuple, D4-s2-51 dead placeholder). D10-s2-03, D4-s2-02, D6-s4-01 and
  D2-s3-04 read 0: fixed at this head (each finding's own --perturb re-raises them).
- Null control: those four fixed seams are the clean fixture, 0 each.
- Perturbation: `--perturb` plants one `isoweekday()` in grid_fee.FeeRule.applies;
  `isoweekday_readers` moves 0 -> 1.

## Dispositions
| seam | disposition |
|---|---|
| config_flow device_prefill error re-render | instance (D4-s2-01), probe flow_errors.py |
| config_flow device_prefill refusal description | instance (D6-s3-01), probe prefill_placeholders.py |
| config_flow tibber_info | instance (D4-s2-51) |
| enumerate.py d17 options | instance (D17-s1-01), probe h_enum.py |
| D15 privacy gate scope | instance (D15-s1-02) |
| dbg_bundle_gen rows | instance (D15-s3-02) |
| debug_replay judge tuple | instance (D15-s2-05) |
| debug_replay seeded ids / store age | instance on record (D15-s2-01, D15-s2-02); owner bundle needed, local re-run owed |
| exception translation placeholders (37 sites) | guarded: exc_translations.py bad=0 |
| leaf-string placeholder parity (4569) | guarded: services_icons.py 0 |
| card STRINGS en/sv/de | guarded: card_placeholders.mjs 0 |
| weekday readers (grid_fee, tariff, quiet_windows, silent_mode, dhw_schedule, optimizer, price_model, coordinator, dhw_learning) | guarded: all Monday=0 weekday(), 0 isoweekday |

No seam beyond the judged sites: instances (beyond_finding) = 0.

## Proposed barrier
Register placeholder-set parity (flow form placeholders vs string tokens, raise
placeholders vs translation tokens, card L() vars vs STRINGS) as agreement.mjs
concepts, plus a one-line lint refusing `isoweekday()` in custom_components.
Not barriered today.
