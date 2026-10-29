Fix review: blocked 8ecde5f26aaf89d95da32c64e6ca736846479ab8 class-rule-missing: the body names no rule that enumerates the writers of the power band, which the round-2 verdict required, and it does not describe the round-3 repair (5534a0ac9, 9e60fcf77) at all

bus-nonce: 7c653758a17c8b0e6e1afbe838652ddd

Cloud reviewer seat, **round 3** of review for R10-COP-PARTLOAD. Round 1 blocked `ea4630ace`. Round 2 blocked `a7411d7ad` on the pre-fill path. This review is of head `8ecde5f26aaf89d95da32c64e6ca736846479ab8`, the head the PR's `## Head` names and still the PR head when this verdict was written (02:14 UTC). The code repair is sound and mutation-proven. The block is on the body only, and fixing it is a PR-body edit that does not move the head.

## Block

The round-2 verdict named three things the repair had to close:

1. Judge the derate on every save that can move the band. **Closed**: `9e60fcf77` makes `_prefill_errors` run `_power_errors(...) or _partload_errors(...)` on any save that carries either band key, and puts the error on `base`.
2. Add a `tests/features.py` cell for the pre-fill path, written to fail before the fix. **Closed**: `5534a0ac9`, killed by both mutants below.
3. "Say in the body which rule enumerates 'writers of the band' so the class is closed." **Not closed.** The PR body's only class rule is still round 1's reader census, "59 sites in the package where a COP meets a power or a heat" (`## Figures`). That census counts readers of the derate. It does not count the writers that move the band. No line of the body mentions the pre-fill path, `_prefill_errors`, `5534a0ac9` or `9e60fcf77` (`ev/body.md`; grep for `prefill|pre-fill|9e60fcf|5534a0a|round 3` returns only the head SHA line).

So under fix-review.md step 6, the body names no rule for a class whose issue now spans more than one seam. That is the round-2 verdict's own seam: the band has more than one writer.

The body is stale against the head in other places too:
- `## Head` says the code head is `2b215e01e`, and two lines later says "`e0b5805a0` is the authored code head".
- It promises "any resolution inside the code head is described below", but nothing below describes round 3.
- `## Round 2 delta` is the last delta section.
- `## Red checks` still quotes `ALL 4550 FEATURE CHECKS PASSED` at `ad2bf7fd6`. That is a historical figure, and the round-2 review showed it did not hold at `a7411d7ad`.
- The `mutation` line still describes round 2's 7 unpinned sites. The bot pin `2b215e01e` has made that line stale (ci-autofix.md).

Repair, for the fixer. Edit the body only; no code push is owed:
- Add a `## Round 3 delta`. It covers `5534a0ac9` (written to fail first), `9e60fcf77` (the pre-fill guard and the reachability probe's 0.25 fallback sentinel), its mutation proof, and the bot pin `2b215e01e`.
- Name the writer-enumeration rule and its output. For example: grep the `CONF_HEAT_PUMP_{MIN,MAX}_POWER` and `CONF_HEAT_PUMP_COP_PARTLOAD_DERATE` names and string values, plus `async_update_entry` / `async_create_entry` / `async_migrate_entry`, under `custom_components/heatpump_optimizer/`.
- Give a disposition for each writer. The reviewer's own enumeration (`ev/writers-enumeration.txt`) gives the expected result: two options writers, both guarded; setup and reconfigure writers that cannot reach a stored derate; no service or migration writer.
- Refresh `## Head` and the stale `## Red checks` lines.

## Findings

- The body does not state the round-3 class rule or delta (the `## Block` above). It must be fixed in this PR's body before merge; the code head need not move. Carry: R10-COP-PARTLOAD
- `review_packet.py render` again refused this head with `host-path` and wrote no packet. This is the same instrument false positive the round-2 verdict carried. `HOME=/root` here, and the substring `/root` matches `dev/governance/roles/root-cause.md` on line 3 of `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` (`ev/review-packet-refusal.txt`). The fixer should not rewrite the path to satisfy it. Carry: dismissed: instrument false positive outside this PR's diff, already carried by the round-2 verdict to the orchestrator, who owns tools/audit/seat/

## Evidence

- Reviewed head: `ev/HEAD.txt` holds `8ecde5f26aaf89d95da32c64e6ca736846479ab8`. The REST pulls API returned the same head at 01:01, 01:35 and 02:14 UTC.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. Merge base `6493ea362`.
- Merge: `git merge-tree --write-tree origin/main 8ecde5f26aaf89d95da32c64e6ca736846479ab8` with the repo's drivers installed exits 0 with tree `99cae1615` (`ev/merge-tree.txt`). Its stderr shows `LEDGER-MERGE: resolved tests/structure_budgets.json` and `resolved tests/closures.json`, and no `MERGE-CLAIM: refused` (`ev/merge-tree-stderr.txt`). GitHub's `mergeable_state: dirty` comes from those driver-resolved files.
- `tests/features.py` at this head, run on this host in a worktree: `ALL 4553 FEATURE CHECKS PASSED`, rc 0 (`ev/features-head.txt`). The reachability check that failed at `a7411d7ad` now passes.
- Mutation proof of the round-3 site, each mutant applied in its own worktree with the full `tests/features.py` run (`ev/m1.diff`, `ev/m2.diff`):
  - M1, `_partload_errors` dropped from the pre-fill save: `1 of 4553 FEATURE CHECKS FAILED`, the new pre-fill check `[max 5->2: {}]` (`ev/features-m1.txt`).
  - M2, the gate narrowed back to `CONF_HEAT_PUMP_MAX_POWER in saved`: `1 of 4553 FEATURE CHECKS FAILED`, the same check, through its min-only save (`ev/features-m2.txt`).
  - Null control: the unmutated head passes all 4553 checks.
  - M1 is the pre-fix behaviour, so it also shows the check would have failed before `9e60fcf77`.
- Class, re-derived by the reviewer with an instrument of their own building (`ev/writers-enumeration.txt`): the two writers that can move the band under a stored derate both run `_partload_errors` at this head. The class is closed in code. The body does not say so, hence the block.
- Error strings: `partload_derate_above_limit` exists under `options.error` in `strings.json`, `translations/en.json` and `translations/sv.json`. It is absent under `config.error`, but the setup path cannot produce it, because a new entry stores no derate and the limit is judged against the default 0.
- Claims: `tests/env_drift.py --all` reads `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, rc 0 (`ev/env_drift.txt`).
- Structure: `tests/structure.py` reads `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure-head.txt`). `budget-raise-gate` is green on this head.
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched three-dot (`ev/version-untouched.txt`).
- CI on this head, from the check-runs API with `filter=all` (`ev/checks.tsv`): every concluded run is success, skipped or neutral, except `governance / delivery-status`. That run is red on OVERDUE rows #2921, #2910, #2873 and #2909, all other PRs' rows. Its log states it is NOT a required context and blocks no merge. This diff adds only its own row `dev/programme/delivery/2872.md` and touches nothing else that check reads, so per defect-root-cause.md the body owes it no answer. `pr-contract / pr-contract` started at 02:13:24, after that red concluded (00:43:04), and passed. `tests / fast (3.14)` is green.
- `tests / mutation` is green, and its log shows a real evaluation, not INCONCLUSIVE: 8 mutants over 4 files, baselines green, the null control survived every driver, `PIN RE-VERIFICATION: 6 reproduced`, `1 survivor(s) of 8 evaluated = 0.0% (1 triaged equivalent)`, `MUTATION TABLE PASSED` (`ev/head-mutation.log`). The `_prefill_errors` site is pinned by `2b215e01e` (`_prefill_errors.GUARD_OFF.9fbfea67.json`).
- `gate` was still in progress when this verdict was written.
- The reviewer did not re-take the body's round-1 and round-2 figures (the partload harness grid, the 32-hash null control, the stress call counts). Round 2's review checked them, and round 3 changes no priced code.
