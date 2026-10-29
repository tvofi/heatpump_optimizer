Fix review: blocked 9b24795b242862ac8ea4f5f9f1c798cf087fbde7 class-rule-missing: the body still names no rule that enumerates the writers of the power band and still does not describe the round-3 repair (5534a0ac9, 9e60fcf77); only its head line changed since 8ecde5f26

bus-nonce: e71a446f1442d9874471924ce41c5c05

Cloud reviewer seat. This is **round 3** of review for R10-COP-PARTLOAD (round 1 blocked `ea4630ace`, round 2 blocked `a7411d7ad`, round 3 blocked `8ecde5f26`); this verdict re-reviews round 3 after the main merge. The next round is the fourth, which owes a re-cut under `fixer.md`, not a repair. Head measured: `9b24795b242862ac8ea4f5f9f1c798cf087fbde7`. At 16:34 UTC it was still the PR head (`ev/pr-head-at-write.txt`), and it is the head the body's `## Head` names. The roles directory has no change between the merge base and main, so this contract is current.

## Block

The round-3 verdict at `8ecde5f26` blocked `class-rule-missing` on the body alone and named a body-only repair. That repair has not been made:

- **There is still no rule that enumerates the band's writers.** The body's only class rule is round 1's reader census, "59 sites in the package where a COP meets a power or a heat" (`## Figures`). That census counts readers of the COP and power. It does not count the saves that move `heat_pump_min_power` or `heat_pump_max_power`, which is the class the round-2 finding opened. The issue now spans more than one seam (the `thermal_model` options page and the Modbus pre-fill save), so fix-review.md step 6 applies.
- **The round-3 repair is still not described.** A grep of the body for `prefill|pre-fill|5534a0|9e60fcf|3dbefe|writer|enumerat|round 3` matches only the `## Head` line (`ev/body-grep.txt`). There is no `## Round 3 delta`, and neither `_prefill_errors` nor its mutation proof appears.
- **The body does not describe the head as it is:**
  - `## Head` names `3dbefe25f` as the authored code head. Its next paragraph says "`e0b5805a0...` is the authored code head ... five commits on the PR head `ea4630ace`", which is round 2's account.
  - "any resolution inside the code head is described below" is not met. `3dbefe25f` is a main merge, and nothing below describes it.
  - The `mutation` line under `## Red checks` still describes round 2's seven unpinned sites. The bot pin `2b215e01e` and the new ledger entries (`_partload_errors` ×3, `_prefill_errors GUARD_OFF`) make it stale.

Repair (body only; no code push is owed by this finding):
- Add `## Round 3 delta` covering `5534a0ac9` (failing first), `9e60fcf77` and its mutation proof, and `2b215e01e`.
- Name the writer-enumeration rule with its command and its output, and disposition each writer it returns.
- Rewrite `## Head` so it describes the `cfe368316` and `9b24795b2` merges.
- Refresh the `mutation` line.

## Findings

- The body names no writer-enumeration rule and does not describe round 3, as above. This is the block itself, and only a body edit settles it. Carry: R10-COP-PARTLOAD

## Evidence

- RESULT the reviewer's own writer enumeration (my definition, because the body states none): `git grep` at the head for `CONF_HEAT_PUMP_{MIN,MAX}_POWER`, the `"heat_pump_{min,max}_power"` literals, `CONF_HEAT_PUMP_COP_PARTLOAD_DERATE`, `_power_errors(` and `_partload_errors(` (`ev/band-writers-grep.txt`). It returns these band writers:
  - the options `thermal_model` page (`config_flow.py:3235`, `_power_errors or _partload_errors`)
  - the pre-fill save (`_prefill_errors`, `config_flow.py:2175-2178`, reached from the setup flow at `:2591` and the options flow at `:3852`)
  - the setup wizard's `building_extras` and `thermal` steps (`:2800`, `:2817`). These run only `_power_errors`. On first setup no derate is stored yet, so the derate is 0, which is always below the limit; I read these as covered by construction.
- Other paths I checked:
  - Reconfigure (`async_step_reconfigure` → `_async_save_reconfigure`) writes only first-screen keys into `entry.data`, and options win in every runtime merge (`__init__.py:297`).
  - `services.py`'s three options writers (an entity slot, the topology, the schedule updates) do not write the band keys by name. I did not trace the schedule service's whole key domain.
  - On this reading the code closes every writer I found. The block is the body's missing rule, not an open seam.
- RESULT `git merge-tree --write-tree origin/main 9b24795b2`: rc 0, no conflict (`ev/merge-tree.txt`).
- RESULT `review_carry.py 8ecde5f26 9b24795b2`: `FRESH-REVIEW`, because `cfe368316` resolves `tests/golden/claimed_drift.txt` to something other than the union of its parents (`ev/review_carry.txt`). I read the three versions. The resolved file has the same entry set as the union; only `config_flow`'s line position differs, and its text is identical. Against the merge base `279578074`, the branch's three-dot claim diff adds one line, `config_flow`, and touches no `claims-for:` line.
- RESULT the branch-only non-merge commits since `8ecde5f26` number 0. The three branch-only commits (`3dbefe25f`, `cfe368316`, `9b24795b2`) are all merges.
- RESULT `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched three-dot (`ev/version-diff.txt` is empty).
- CI at this head (`ev/check-runs.tsv`, all pages, read at 16:34 UTC, 39 runs):
  - `tests / nightly-status` reads failure. It grades main's Nightly, the body answers it under `## Red checks`, and the diff does not reach what it reads, so it is not this PR's.
  - Still in progress: `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / mutation`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and `prelude`.
  - Every other run succeeded or was skipped; `CodeQL` reads neutral.
  - This verdict does not turn on those runs; the block stands whatever they return.
- Not re-run this round:
  - the mutation proof and the finder's harness `r10_cop_partload.py`, because no production line changed since `8ecde5f26` (branch-only commits are merges only). The round-3 review's mutation proof of `9e60fcf77` and the bot's ledger pins (`_prefill_errors GUARD_OFF 9fbfea67` killed by `tests/config_flow_steps.py`) stand as read in the review packet's ledger diff (`ev/review-packet.md`).
  - the body's figures. I did not re-derive them at this head. They are quoted at earlier heads (`ad2bf7fd6`, `e0b5805a0`, `635e991a4`), so they are unverified at this head.
