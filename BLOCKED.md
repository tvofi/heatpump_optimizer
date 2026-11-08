# BLOCKED: r10-min-power-floor handoff body refused on unlanded carries

Code head f60b4d8c0f5c219e6b8c6d506f4874ce4c8f2a0a is pushed to `handoff/r10-min-power-floor`, after a clean `tools/pr/prepr.sh <body>` run (`PRE-PR: f60b4d8c0 ... rc=0`).

`tools/audit/seat/body_push.sh r10-min-power-floor <body>` refused with `CARRY-LANDED: 5 missing`. Each `## Forward-carry` item must already be in its group's brief or carries on the round's roster branch (`carry_audit.py land-ops`). The brief lets this seat write only its return refs and `handoff-wip/r10-min-power-floor[-body]`, so it cannot push `handoff/audit-r10-roster`. body_push kept the refused body at `handoff-wip/r10-min-power-floor-body` (903bff2c8).

Question for the orchestrator: land the five ops below on `handoff/audit-r10-roster` with `roster_edit.py`, then push the kept body with `body_push.sh r10-min-power-floor`. Or tell this seat it may do so.

Output of `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster land-ops --body <body> --topic r10-min-power-floor` at head f60b4d8c0:

```
append-carry R10-I18N-DE 'From r10-min-power-floor, body item c7e2fe29: The new option'\''s German label: no German translation file exists at base. Owed to R10-I18N-DE'\''s roster brief (item 9980b124), which the orchestrator writes, since a fixer seat writes no roster. Carry: R10-I18N-DE (items c7e2fe29)'
append-carry R10-USER-DOCS-VERIFY 'From r10-min-power-floor, body item cc1cca91: The docs row "Compressor runs below min power" in `docs/configuration.md` is a claim that `tests/doc_claims.py` may pin. Owed to R10-USER-DOCS-VERIFY'\''s roster brief (item df23e57c). Carry: R10-USER-DOCS-VERIFY (items cc1cca91)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item a4565419: The reply on 3289 names the option: the reporter picks `on_off` unless their surface is switch plus setpoint, where the probe already clamps and only the DHW projection moves (item 052fa8fb). The orchestrator answers the issue. Carry: R10-MIN-POWER-FLOOR (items a4565419)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item de37a181: Re-read #3297'\''s `probe_install` and `InstallCapability` at its merge. If it changes `can_duty_cycle` or `fully_metered`, revalidate the `on_off` early return and the block'\''s checks before this merges (item df5196cc). Carry: R10-MIN-POWER-FLOOR (items de37a181)'
append-carry R10-MIN-POWER-FLOOR 'From r10-min-power-floor, body item b8c2d996: After R10-GENERIC-HEAT-CURVE merges, re-measure the `option_doc_coverage.py` EXPECTED counts at the merge (+1 field from each side). `option_fields_undocumented` must stay 0 (item 3c867235). Carry: R10-MIN-POWER-FLOOR (items b8c2d996)'
```

---

# BLOCKED: body_push.sh refused

`bash tools/audit/seat/body_push.sh r10-min-power-floor body.md` at PR head fb5658f13a16 printed:

    body_push: handoff/r10-min-power-floor is at f60b4d8c0f5c, this checkout at fb5658f13a16; push the code, then the body

The code ref handoff/r10-min-power-floor is behind the PR head: the head adds the main merge 33c51f71b, the delivery row feb778843 and the bot's pin commit fb5658f13. The brief forbids overriding a refusal and this seat changes no code, so nothing was pushed to handoff/ or handoff-body/.

Findings (no code defect; the diff caused none of the reds beyond the stale mutation red the bot already repaired):
- tests / mutation: red once at feb778843 (six unpinned sites this diff added, all killed locally); mutation-autofix pinned them in fb5658f13; green at the head.
- codeql / Analyze (python): cancelled at 05:06Z, no steps recorded, run attempt 4: infrastructure. No alert.
- gate: fails only on `FAIL codeql / Analyze (python): cancelled`.
- pr-contract: one error, `tests / mutation` not named in `## Red checks`.

BODY.md in this commit is the re-taken body. `prepr.sh --body-check BODY.md --pr-branch fix/r10-min-power-floor` at fb5658f13 prints `pr-body ok: PR-BODY: 0 error(s)`, carry, preflight, figures and privacy ok.

Ask for the orchestrator: either fast-forward handoff/r10-min-power-floor to fb5658f13 and run body_push.sh with this BODY.md, or post BODY.md as the PR body directly. The codeql job also needs a re-run.

Note: `git merge-tree --write-tree origin/main fb5658f13` at main 2a3c056 reports a content conflict in tests/golden/claimed_drift.txt, the file the claimnotes merge driver resolves; merge-tree does not run that driver.
