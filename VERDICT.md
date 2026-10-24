Fix review: merge abeeb5dac1b711638cbbc21601a207fa33de0ff1

bus-nonce: fcdbf35a9257e5e2e61e822af4bc8309

Round: first review of #2771 (round-10 roster batch 6). Head measured: `abeeb5dac1b711638cbbc21601a207fa33de0ff1`, still the head of `fix/audit-r10-roster-pr6` when this verdict was written (`ev/head_at_post.txt`). Merge base `c176ee55d` = origin/main. The roles diff against origin/main is empty, so the contract read is current.

## Findings

- #2753's body still reads `## Forward-carry: none` at its head `ba02b95fc`. The two carries this PR lands (R10-HEAT-METER and R10-COP-GATE, from `handoff/audit-r10-roster` at `6a57b0a79` and `78f195461`) answer the `carry-missing` block in #2753's first review (hpo-approver comment 6389452050). So the text I checked them against is that review's `## Block` and its replay_freeze finding, not the #2753 body. The repair of #2753 has to name both roster SHAs in its own `## Forward-carry` for its step-10 check to pass. That is #2753's work, not this PR's. Carry: R10-THERMAL-POWER-OPTION

## Evidence

- RESULT roster equality: `git rev-parse` gives blob `a1673a3a2` at both the head and `78f195461` for `dev/programme/rosters/wave-r10-groups.json`, and `git diff` of the two blobs is empty (0 bytes; `ev/blob_compare.txt`). The parent of the batch's first op (`1558cf55f`) holds main's blob `03802c797`, so the five ops apply to main's exact roster.
- RESULT scope (three-dot `c176ee55d...abeeb5dac`): 2 files. The roster has +46/-5. `dev/programme/delivery/2771.md` is the PR's own row (+1). The five handoff commits (`d4d3f5a19` set-stage, `c60d917ca` append-group, `ce0520798` set-after, `6a57b0a79` and `78f195461` append-carry) are each titled `roster_edit <op> ... (tools/audit/seat/roster_edit.py)`, and each touches only the roster file (`ev/handoff_ops.txt`).
- RESULT semantic diff against main (`ev/roster_checks.txt`). The group-by-group compare shows exactly these changes and nothing at top level:
  - NEW R10-FLY-LEDGER-SAMPLE. Its after-edge R10-MUTATION-ANCHOR resolves.
  - R10-ARCH-DOCS `after` gains R10-FLY-LEDGER-SAMPLE.
  - R10-FLY-CIPREDICT-LAYOUT resume goes from in-progress to done, at commit `0c7d6ca4f`. That commit is on origin/main, the merge of #2707.
  - R10-HEAT-METER carries go 8 to 9 and R10-COP-GATE carries go 4 to 5. In both, the earlier entries are byte-equal and only one entry is appended. Both groups are `not-started`.
  - Re-dumping with `json.dumps(indent=1)` (roster_edit.py's canonical bytes) reproduces the file byte for byte, so this is a load/dump edit and not a string splice.
- RESULT JSON valid (`ev/json_valid.txt`). `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` reports `0 error(s), 0 warning(s)`, `TOTAL: 0 error(s) across 1 file(s)`, rc=0 (`ev/brief_lint.txt`). CI `tests / briefs` is also green.
- Carry content, checked against #2753's review block. The HEAT-METER carry states each precondition the block names:
  - `CONF_THERMAL_POWER_ENTITY` / `probe_install(...).measured_heat` is a second heat source.
  - It says which source wins, and keeps the no-fallback rule.
  - Its reading routes through `read_heat_output_kw`.
  - The COP sample site is already replaced, so the exact-fold and null tests go through `cop_evidence`.
  - The replay_freeze / `_commanded_split` mode-split requirement is extended to the thermal reading.
  - Its control is #2753's check "a configured heat meter answers in kW, and outranks the flow meter's estimate", killed by mutant M1.

  The COP-GATE carry says that a thermal-power entity counts as "a heat meter" for the not-measurable scoping, citing the `metered` arm's spread 0.0000. Its control is that a thermal-power-metered install never gets the not-measurable state and its fold still moves `cop_scale`. Both carries state their control as a precondition. Ordering: `cop_evidence`, `space_reference_cop`, `replay_freeze`, `CONF_THERMAL_POWER_ENTITY` and `dev/audit/harnesses/r10_thermal_power_option.py` exist on #2753's head and are absent at this head. R10-HEAT-METER's `after` lists R10-THERMAL-POWER-OPTION, and R10-COP-GATE's `after` lists R10-HEAT-METER, so neither fixer starts before #2753 merges.
- Mutation proof (step 1) and harness (step 2) do not apply. The diff is roster data only and writes no production line, so `changed_lines` draws no mutant. CI `tests / mutation` is green on that basis.
- `VERSION`, the manifest version, `RELEASE_NOTES.md` and both claim files are untouched: the three-dot diff stat is empty.
- Merge: `git merge-tree --write-tree origin/main abeeb5dac` with origin/main `c176ee55d` gives rc=0, tree `62f2233ae`, no conflict (`ev/merge_tree.txt`).
- CI on this head, from the check-runs API with every run listed (`ev/check_runs.txt`): every workflow concluded success, skipped or neutral. One `gate` run (job 121003242751, 22:17:37Z) concluded failure with `FAIL run(s) [40137747826] at this head are still being judged; their gate decides`. That run started while the tests workflow was still running, and the diff did not cause the red. The later `gate` runs (121005413298 and 121005541808, 22:27-22:28Z) passed after every workflow had concluded, and `pr-contract` passed on runs both before and after (121005303465 at 22:26:50Z). The check-runs listing no longer carries the failed run. No red check is owed an answer by step 11.
- The body's `## Head` names `abeeb5dac1b711638cbbc21601a207fa33de0ff1`, which is the head measured (step 7). The body quotes no figures (`## Figures: none`), so there is nothing to re-derive. No instrument number moves (step 14), and no structure or budget file is in the diff.
