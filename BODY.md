R10-DIAG-REDACT: Download diagnostics now redacts each value its keyed passes remove wherever else that value reaches. It also states when it was exported, measures the plan's age at that instant, and labels the frozen debug collection's window. Part of #2271 and part of #2814; whether either can close is the orchestrator's call (see Forward-carry).

This is round 2. Round 1 was blocked because carries 1 and 2 were missing (issue comment 6401817546). The round-1 prompt was rendered without them. This round satisfies all three carries, item by item, under `## Carries`. The carry-0 code is unchanged from round 1.

**Carry 0, the redaction.** The download's redaction (`diagnostics.async_get_config_entry_diagnostics`) is keyed. `async_redact_data(..., TO_REDACT)` blanks `tibber_token` and `name`, and `_coarsen` cuts `latitude`/`longitude`, but only under those keys. A copy of the token, the entry name or the exact coordinate under any other key, inside a message, as a key, or as a number under `lat`/`lon` went out unredacted. The fix is one value pass, owned by `diagnostics.py`:
- `_private_values` collects the text of every value the keyed passes remove from the entry's own `data` and `options`.
- `_without_values` then redacts each of those values anywhere in the payload: inside a string, as a dict key, and as a number whose text matches.
- A value shorter than `replay_doc.LEAK_MIN_CHARS` (the replay seal's existing bound of 6) is not searched for. Both leak checks now read that one named bound.

Alternatives for carry 0, and why each lost:
- (a) Widen `TO_REDACT`. This is still keyed, so it would close no path where a value sits under an innocent key or inside text.
- (b) Redact at each producer. One rule would be spread over every writer, and the next writer would be unguarded.
- (c) Refuse the whole download. A diagnostics file must still download, and over-redaction there fails safe.

**Carries 1 and 2, the ages.**
- The download reads the clock once (`now = dt_util.utcnow()` in `async_get_config_entry_diagnostics`) and states it as a top-level `exported_at`.
- `_plan_summary(data, now)` no longer copies `plan_age_minutes` from the payload. It measures the age from `last_optimization` at `now`.
- The debug manifest gains `first_row_at`, `last_row_at`, `span_hours` and `age_hours`, from the new pure function `debugger.collection_window(rows, now)`.
- Both ages go through one new helper, `drift.stored_age_seconds(raw, now)`, next to `stored_instant`. It returns `None` for an instant that does not parse, and also for one ahead of `now`, because such an age is unknowable, never 0 (#775; fixer.md step 16). The coordinator's publish-time `_plan_age_minutes` clamps an instant ahead of the clock to 0. That clamp is the coordinator's and is left alone here.

Alternatives for carries 1 and 2, and why each lost:
- (d) Have the coordinator publish a fresher age. Rejected: any age copied from the payload is stale by however long the payload sat before the download. Only the export clock removes that.
- (e) Drop `plan_age_minutes` from the download. Rejected: `last_optimization` alone makes every reader subtract by hand, and #2814's reproduction shows readers trust the stated age.
- (f) Replace the manifest's `days` with the measured span. Rejected: it is an `hpo-debug/1` key, so changing what it means breaks the schema's readers. `days` stays the configured length, and the measured window sits beside it.
- (g) Compute the age in `diagnostics.py` and `debugger.py` separately. Rejected: that writes the ahead-of-clock rule twice. Its owner is `drift.py`, the module of the stored-instant rule.

## Carries

- **Carry 0** (D15 production triage: redaction incomplete). Satisfied as in round 1, with code unchanged; the round-1 reviewer found it satisfied. Evidence: `diagnostics._private_values` and `_without_values`, applied at the return of `async_get_config_entry_diagnostics`. The test is `tests/debug_collect.py` check `Download diagnostics carries none of the values its redaction removes ...`, with its section census and two null controls. Mutation proof: the 9 mutants under `## Mutation proof`.
- **Carry 1** (#2814: no label for the frozen collection, no export time, wrong plan age).
  - Export time: `diagnostics.py` adds `"exported_at": now.isoformat()` to the download dict in `async_get_config_entry_diagnostics`. Test: `the download carries its own export time, outside the debug half ...`. Mutant `no-exported-at` is killed.
  - The collection's end and age: `debugger.collection_window`, spread into the manifest in `DebugCollector.async_bundle` under the existing `days`. Tests: `the manifest labels the finished collection: its first and last row, the 3 h the rows span, and the last row's age at the export, not the configured 7 days` and `a collection with no row has no window, and a row stamped ahead of the export clock has an unknowable age, never 0`. Mutants `no-window`, `first-last-not-min-max` and `window-age-ahead-0` are killed.
  - `days` stays the configured `COLLECT_SPAN.days` (alternative (f)). The measured span beside it answers "days is a constant 7".
  - The plan's stated age: carry 2.
- **Carry 2** (P119, lead L7: `plan_age_minutes` may be the age at publish).
  - VERIFY result: it is the publish-time age. `coordinator.py` `_plan_age_minutes` measures against `dt_util.now()` when `_build_data_dict` builds the payload (the `"plan_age_minutes"` entry). At `e3c97ba6`, `diagnostics._plan_summary` copied it.
  - Remedy: `diagnostics._plan_summary(data, now)` sets `"plan_age_minutes"` to `round(stored_age_seconds(last_optimization, now) / 60, 1)`.
  - Controls, in `tests/debug_collect.py` `_aged_download`. The payload says `plan_age_minutes: 0.8` and the clock is frozen relative to `last_optimization`.
    - At +14 min the export reads 14.0 (check `the download's plan age is measured at the export: 14 minutes after the solve it reads 14 ...`).
    - The null control: at +1 min it reads 1.0 (check `the null control: a plan solved a minute before the export reads 1`).
    - At -5 min it reads `None`, and a payload with no solve also reads `None`.
  - The carry's mutant keeps the published value (`round(age / 60.0, 1)` → `data.get("plan_age_minutes")`). Killed: both the 14 and the 1 checks fail, reading `[0.8]`.

## Head

The code head is `70b57a370322` (`handoff/r10-diag-redact`), a fast-forward of round 1's `c11ecdff359b`. It merges the PR head `e3c97ba6a694` (the delivery row and a main merge). On top it adds one commit of code and tests (`69a02ccd5`) and two test-only commits: one rewords a check's name (`d5bad3ea5cda`) and one renames a test-local `_window` that `closure.py no-copies` refused (`70b57a370322`). The merge base with `origin/main` is `dfcd8d9be1da`. At 2026-10-25T19:42Z `origin/main` was at `c9cbe6b458a7`, 10 commits ahead in 8 files, all roster, triage and audit-tooling merges. `git merge-tree --write-tree origin/main HEAD` exited 0 with no conflict, so main was not merged in (fixer.md step 6). The gate, the census and the base run were measured at `69a02ccd5`. The head differs from it only in `tests/debug_collect.py`: one check's name and one local name. At the head:
- `tests/debug_collect.py` passes 135 of 135.
- The 8 round-2 mutants were re-run and all 8 were killed.
- `tests/structure.py` passes.
- `python3 tests/closure.py no-copies` printed `closure: no test file defines a symbol production also defines`.

`tools/pr/prepr.sh` at `d5bad3ea5cda` refused twice. The first was that `no-copies` collision, fixed in `70b57a370322`. The second is `closures failed while being recorded: tests/entities.py (exit 1)`, caused by the same two main-side entity checks named under `## Figures`. They fail at the merge base with this diff absent. This seat writes only its return refs and does not touch workflow tests, so that refusal is left to the orchestrator.

## Mutation proof

Command: `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`, run with each mutant applied to the production file and then restored. The driver was a scratch loop.

Round 2 (8 mutants, run at `69a02ccd5` and again at the head `70b57a370322`). Each one exited 1 both times:
- `keep-published` (the age walrus → `None`). FAIL: `the download's plan age is measured at the export ...` `[None]`, and `the null control: a plan solved a minute before the export reads 1` `[None]`.
- `keep-published-value` (`round(age / 60.0, 1)` → `data.get("plan_age_minutes")`; the carry's mutant). FAIL: the same two checks, `[0.8]`.
- `ahead-reads-0` (`stored_age_seconds`: `return age if age >= 0.0 else None` → `return max(age, 0.0)`). FAIL: `a plan stamped ahead of the export clock has an unknowable age, never 0 ...` `[0.0]`; `a collection with no row has no window, and a row stamped ahead ...`; `a stored instant's age is the seconds to now ...`.
- `ge-to-gt` (`>=` → `>` in the same line). FAIL: `a stored instant's age is the seconds to now ...`.
- `no-exported-at` (the `"exported_at"` line deleted). FAIL: the section census (`exempt-gone=['.exported_at']`), then `KeyError: 'exported_at'`.
- `no-window` (the `**collection_window(self.rows, now)` line deleted). FAIL: `the manifest labels the finished collection ...`, then `KeyError: 'first_row_at'`.
- `first-last-not-min-max` (`min(stamps), max(stamps)` → `stamps[0], stamps[-1]`). FAIL: `the manifest labels the finished collection ...`. The fixture's rows are out of order (0 h, 3 h, 1 h), as rows look after the clock is set back.
- `window-age-ahead-0` (`age_hours` from `max(elapsed, 0)` rather than `stored_age_seconds`). FAIL: `a collection with no row has no window, and a row stamped ahead ...`.

Round 1 (carry 0; 9 mutants, killed then, production lines unchanged since): value pass deleted; `>= LEAK_MIN_CHARS` → `>`; coordinate cut predicate removed; `(list, tuple)` → `list`; keys not passed; number arm returns `value`; options not read; `LEAK_MIN_CHARS = 7` with `>` in `seal`. Their failing checks are listed in the round-1 body, and the round-1 reviewer re-ran the value-pass mutant: 1 of 128 failed.

## Null control

- Failing test first. These are the production files `diagnostics.py`, `debugger.py` and `drift.py` at `e3c97ba6`, the base this round was given, run against this branch's `tests/debug_collect.py`. That run printed these FAIL lines:
  - `the download's plan age ... reads 14` `[0.8]`
  - `the null control: a plan solved a minute before the export reads 1` `[0.8]`
  - `a plan stamped ahead of the export clock ...` `[0.8]`
  - the section census, `exempt-gone=['.exported_at']`
  - then `KeyError: 'exported_at'`

  So at the base the export carried the published 0.8 whatever the clock said, and it had no export time. At the head all 135 checks pass.
- The 1-minute control is the carry's null. It separates "measured at the export" from a constant: the keep-published mutant fails it too, reading 0.8 where 1 is expected.
- Carry 0's null controls are unchanged. A clean install's download is byte-identical with the value pass on and off. Every field of the planted download that holds no private value matches the pass-off download.
- Seven `FAIL a16:...` lines print at both ends. They are the sub-results inside the A16 writer check's own detail, not checks: the totals read `ALL 135 ... PASSED` at the head.

## Figures

- Plan age at a frozen clock 14 min after `last_optimization`, against a payload stating 0.8: 0.8 at `e3c97ba6`, 14.0 at the head. At 1 min: 0.8 at the base, 1.0 at the head. Command: `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`; at the base, the three production files are checked out from `e3c97ba6`. Rule: the value of `download["plan"]["plan_age_minutes"]`.
- Debug collect checks at the head: 135 of 135 pass (`ALL 135 DEBUG COLLECT CHECKS PASSED`), up from 128 in round 1, with 7 new checks. Same command.
- Mutants killed: 8 of 8 in round 2, plus round 1's 9 of 9. Same command, with each mutant applied.
- Class census, fixer.md step 8. The class is a relative age the download copies from the published payload, so it states the age at publish. Rule: over the keys the download copies from `coordinator.data` (`_plan_summary`'s copied tuple, `INPUT_KEYS`, `LearningView.__annotations__`), select the keys matching `(_minutes|_hours|_h|_days|_age|_ago|_since|stale)$|age_|_stale_`.
  - At `e3c97ba6` it returns `plan_age_minutes`, `plan_stale` and `input_ages_minutes`. At the head it returns `plan_stale` and `input_ages_minutes`, because `plan_age_minutes` is no longer copied.
  - Dispositions:
    - `plan_age_minutes`: closed in this diff.
    - `input_ages_minutes`: open, #2814. The payload carries no publish instant to re-base the per-entity ages from.
    - `plan_stale`: open, #2814. It is a flag judged against the interval at publish, and recomputing it here would duplicate `_plan_is_stale`.
  - `learning`: 38 keys, none selected.
  - The instrument was an inline script; it is not in the tree.
- Architecture score: `python3 tools/audit/archscore/score.py --diff dfcd8d9be1da HEAD` printed `Architecture score: dS +0.0000 NULL`.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scoped gate at `69a02ccd5`: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=dfcd8d9be1da bash tests/run.sh` printed `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`. 26 of 27 scripts ran ok. `tests/entities.py` reported `2 of 2445 ENTITY CHECKS FAILED`: `gate-sweep.yml: on CI's completion, ...` and `graders-head-copy's delivery_status step is red only when ...`. These are the same two that round 1 found red at its merge base with this diff absent. Neither reads `diagnostics.py`, `debugger.py` or `drift.py`; both read workflow files. Re-run at the merge base `dfcd8d9be1da` with this diff absent (`PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree there): `2 of 2445 ENTITY CHECKS FAILED`, the same two names, so neither failure is this branch's. `tests/typing_ruler.py` and `tests/debug_collect.py` passed in that run.
- The finder's harness: the triage record (`dev/programme/triage/s6-batch24.md#P119`) and #2814's reproduction read the owner's bundle, and the bundle is not in the tree. The companion applies #2814's own rule to a synthetic download: `last_optimization` + `plan_age_minutes` compared against the export time. That companion is the `_aged_download` checks above. They read the defect at the base (0.8 against 14) and not at the head.

## Unpinned sites

`tools/pr/ci_predict.py --base origin/main` lists 21 sites the diff adds against `dfcd8d9be1da`. Every one is in `custom_components/`, which is `mutation-autofix`'s lane:
- `custom_components/heatpump_optimizer/debugger.py:308 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:122 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:124 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:126 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:128 BOOLOP`
- `custom_components/heatpump_optimizer/diagnostics.py:130 BOOLOP`
- `custom_components/heatpump_optimizer/diagnostics.py:130 CMP_BOUND`
- `custom_components/heatpump_optimizer/diagnostics.py:130 RETURN_DEL`
- `custom_components/heatpump_optimizer/diagnostics.py:135 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:138 RETURN_DEL`
- `custom_components/heatpump_optimizer/diagnostics.py:139 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:142 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:144 GUARD_OFF`
- `custom_components/heatpump_optimizer/diagnostics.py:147 RETURN_DEL`
- `custom_components/heatpump_optimizer/diagnostics.py:337 RETURN_DEL`
- `custom_components/heatpump_optimizer/drift.py:123 GUARD_OFF`
- `custom_components/heatpump_optimizer/drift.py:126 CMP_BOUND`
- `custom_components/heatpump_optimizer/drift.py:126 RETURN_DEL`
- `custom_components/heatpump_optimizer/replay_doc.py:101 CONST`
- `custom_components/heatpump_optimizer/replay_doc.py:507 BOOLOP`
- `custom_components/heatpump_optimizer/replay_doc.py:507 CMP_BOUND`

Each one: pinned by mutation-autofix. The round-2 sites (`debugger.py:308`, `drift.py:123`, `drift.py:126`) are killed by the mutants above (`no-window`, `ahead-reads-0`, `ge-to-gt`). The `debugger.py:308` guard `if not stamps:` is driven by the `fresh` download, which has no row.

## Red checks

- `tests / mutation`: predicted red. The cause is the 21 sites under `## Unpinned sites`, which no ledger pin covers until `mutation-autofix` pins them after the push (`ci-autofix.md`). The cheaper detector exists and ran here: `tools/pr/ci_predict.py`, which `body_push.sh` runs too. Its standing cost is seconds per handoff. No further detector is owed.
- `governance / delivery-status`: red at round 1 on main's own overdue rows, not this diff's. It is not a required context. The only row in the diff is #2824's own, written by the orchestrator. That check is its own detector, at one CI step, and no cheaper one is owed.

## Forward-carry

- The round-1 carry stands. The owner bundle and the triage record are not in the tree, so the two values the triage named were not reproduced. R10-REPLAY-REAL-DAY's precondition ("R10-DIAG-REDACT's redaction holds on the exported document") is met only by running `export.check_file` and `seal` on the owner's own exported day. The destination is that group's brief in `dev/programme/rosters/wave-r10-groups.json`, and the orchestrator owes the roster edit. Carry: R10-REPLAY-REAL-DAY
- Three parts of #2814 are outside carries 0-2 and stay open on that issue, so this PR does not close it:
  - re-basing `input_ages_minutes` to the export clock: the payload carries no publish instant to re-base from;
  - `plan_stale`, judged at publish;
  - a run time on the stored self-test results, which needs a field in the collection's store document.

  Carry: #2814

## Friction

- carries-omitted: unenforced: the round-1 prompt was rendered without the group's carries, so round 1 shipped carry 0 only and was blocked. The cause the orchestrator names is `cloud_dispatch --group` (proposal V61), and the orchestrator holds that fix. Carry: dismissed: already owned by the orchestrator as V61
