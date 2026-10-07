R9-EG-A4 (#1774): the architecture score becomes a required check, after the report-only wave was compared with its reviews.

Closes #1774

**Stacked.** This head is cut from `handoff/r9-eg-entry-config` at `d15fc0ae57da63645d6b8d4381ffe83db3a831de` (R9-EG-B11, #2025, approved, not yet merged). Its own diff is `d15fc0ae..HEAD`, and every figure below is measured against that base. After #2025 merges, `origin/main` is merged into this head, and the steps in "After #2025 merges" are re-run. Do not open this pull request until then.

What changed:

1. **The wave comparison.** Every EG pull request of the report-only wave was scored again with one instrument, and each score was set beside its review verdict (table in Figures).
   - Only #1887 and #1958 printed a delta-S in their bodies. Neither the brief's list nor the template required one.
   - Two rows disagree with their reviews, and each one is now a planted case:
     - **#1867 (B3b).** The review said merge; the score says WORSENS, inadmissible: `coord_footprint` +3. The footprint counts an annotated alias and a bare `return <name>` as logic statements. Planted as `a1_N5_annotated_return` (NULL, reads WORSENS), and recorded as a miss.
     - **#1852 (B3a).** The score read +51 IMPROVES. Its round-1 review called that vacuous: the census stopped at `return cast(Payload, data)` and saw 3 produced keys. Planted as red-team attempt `15_payload_cast` (GAME).
2. **Two red-team spellings committed**, swept from every EG fix review. The eight plants against the score on #1874 (R9-EG-A2) were already committed as 04o to 04zz1. Two other reviews found spellings that were not:
   - `14_hub_write_presolve` (#1887 round 1): the solve's grid-cost hub writes move into a pre-solve step the cycle calls.
   - `15_payload_cast` (#1852 round 1): the payload builder's return goes behind a cast.

   Before the fix, both read as gains: on the pin, hub 40 -> 27 and untyped 164 -> 2. Neither is KNOWN-OPEN: the counters below close both.
3. **The counters.**
   - **C13** widens the roots of `hub_solve_writes` to the scheduled cycle. This is the brief's "widen its roots" option. Naming only the pre-solve step would have left a move into any other step open, which is a spelling list.
   - **C12** makes the payload census follow `cast(T, x)` into `x`, and the cast types nothing. The footprint reads a cast as its argument, not as delegation.
   - `tests/arch_score_head.py`'s producer table is now cycle-wide. `CYCLE_HUB_WRITERS` lists 13 writers, each with the fields it writes and its event. A second control plants a write in `_refresh_model_corrections`.
4. **The derived counts.** `tests/arch_score.py` no longer carries the literal 44, nor a known-open count. The red-team set is the scripts in `planted/redteam/` against `expected.json`'s GAME and KNOWN-OPEN rows, and `cases.KNOWN_OPEN` must equal the recorded KNOWN-OPEN set.
5. **The required check.**
   - `.github/workflows/arch-score.yml` runs `tools/audit/archscore/gate.py`. The workflow restores `tools/audit/archscore/` and `tests/structure.py` from the base, so a pull request cannot edit the check that grades it.
   - It passes when delta-S >= 0 and no gate metric rises from the merge base to the head. A rise passes only when the body's `## Architecture score` section has a line naming the metric with a reason. This is "explained in the body like a budget raise", with the reason judged by the fix reviewer. Owner approval of a score rise is not required: neither the brief nor R3-6 asks for it, and that is an open question below.
   - The template states the rule within its policy cap. `pr-contract-rerun.yml` watches the new workflow, and `tests/entities.py` admits it to the files that list `edited`.
   - The weights stay at their frozen hash.

## After #2025 merges

1. `git merge origin/main` into this head (never rebase), resolving against #2025's merged form.
2. Re-run the following, since the merge base moves:
   - `ci_predict.py --base origin/main`;
   - `tests/closure.py select`;
   - `tests/structure.py`;
   - `tests/arch_score_head.py`, because #2025's coordinator changes can add a cycle hub writer, which then needs a `CYCLE_HUB_WRITERS` row;
   - `tests/arch_score.py --stored`;
   - `tests/entities.py`.
3. Re-take this body's merge-base-dependent figures: the head line, scope, and the #2025 row of the wave table, which becomes a merged row.
4. Open the pull request (the orchestrator), with `## Architecture score` as `n/a`. It touches no package file.
5. The ruleset context `arch-score` is tvofi's to add after merge.

## Approval

This changes policy and the enforcement surface, so it merges only on tvofi's approving review at the head, which CODEOWNERS requires. It touches:

- `.github/PULL_REQUEST_TEMPLATE.md`;
- `.github/CODEOWNERS`, which now owns `/tools/audit/archscore/`;
- `.github/workflows/arch-score.yml`, which is new;
- `.github/workflows/pr-contract-rerun.yml`;
- `tests/entities.py`, which admits the new `edited` workflow;
- `tests/run.sh` (a comment);
- `tests/arch_score.py`;
- `tools/audit/archscore/calibration/expected.json`, where two verdicts are re-recorded and three cases added.

The decision it implements is tvofi's R3-6 (2026-09-29). Not yet approved at this head.

Decisions recorded under tvofi's mandate (#201 comment 5951564627), relayed by the orchestrator:

1. A score rise passes on a body `## Architecture score` explanation, judged by the fix reviewer. It does not need the owner's approval at each head; budget-file raises keep their own owner gate.
2. The ratchet's `duplication_copies` keeps the adjacent window. There is no switch to the gapped census.
3. Owning all of `tools/audit/archscore/` in CODEOWNERS is accepted.
4. After merge, tvofi adds the `arch-score` context to `main-protect-checks`. The orchestrator requests it and records it on #201.

## Head

The code head is `handoff/r9-eg-a4` at `545d5bda649518582e72db848130f3e404f6baf2`, on base `d15fc0ae57da63645d6b8d4381ffe83db3a831de` (stacked on R9-EG-B11). `git merge-base origin/main HEAD` is `09ba95d08157e40950104d28a34c94dc899d4be1`, which is #2025's own base. The figures were taken at that head on 2026-10-07.

## Mutation proof

- **C13 (hub roots).** At `4efdd6ce`, the tests are in and the roots are solve-only. `PYTHONPATH=tests/hastub python3 tests/arch_score_head.py` failed 2 of 15:
  - `the hub check refuses a write planted in the pre-solve step, and lists only it` (`planted=True; unlisted []`), so the plant was unseen;
  - `every listed producer is still reached`, the 36 cycle producers.

  At the head, ALL 15 pass.
- **C12 (cast).** With `untyped_payload_keys.py` at `4efdd6ce`, the `15_payload_cast` tree reads untyped 2 against 164 at the pin, a gain. At the head it reads 164.
- **The gate rule.** Replacing `if d["admissible"] and d["dS"] >= 0:` with `if True:` in `gate.py` makes `tests/arch_score.py --stored` fail 6 of 58. The six are all `arch-score gate:` refusal cases: a rise with no section; a section naming another metric; a line naming the metric with no reason; an explanation under another heading; a prefix-named metric; and two rises needing two explanations. Restored, ALL 58 pass.
- **Survivors.** None on touched production sites: the diff touches no `custom_components/` file.

## Null control

- **The rename null.** `rt_00_null_rename` reads NULL at the head (`calibrate.py --only rt_00_null_rename,...`).
- **The footprint re-measure is the null for C12.** It ran on all 87 stored corpus vectors and moved `coord_footprint` on 0 and `params_over_10` on 0 (compared against the pre-run copy). `hub_solve_writes` moved on 87 of 87, as the widened roots must.
- **Unchanged metrics.**
  - The pin's untyped count is unchanged by C12: 164 before and 164 after.
  - Its footprint is unchanged: 2512 before and after.
  - Today's tree reads untyped 0 with 172 produced and 172 typed, before and after.
- **The gate's admissible arm.** It passes a flat change with no section (self-test).
- **The ownership switch.** At `b5f01426` the workflow restored `tools/audit/archscore/` from the base, and `node tools/policy/field_coverage.mjs` refused it: `pinned tools/audit/archscore/gate.py is unregistered`. The repair follows the #1847 precedent: the pull request's own copy runs, and CODEOWNERS owns `/tools/audit/archscore/`. At the head the same command reads `FIELD COVERAGE ok`, and `codeowners_gap.py --check` reads `COVERED tools/audit/archscore/gate.py` with `uncovered_files=0`.

## Figures

The wave comparison comes from `python3 dev/audit/harnesses/eg_a4_wave_deltas.py`, with the instrument at base `d15fc0ae` (pre-A4). The review verdict is each pull request's last `Fix review:` comment.

| PR | group | dS (pre-A4) | verdict | review | agree? |
|---|---|---|---|---|---|
| #1839 | B2 | +0.6670 | IMPROVES | merge | yes |
| #1852 | B3a | +51.1068 | IMPROVES | merge; round 1 called the census vacuous | mechanism no, sign yes. Under C12 it is +51.1062, real: 166 produced, 166 typed against 3 and 3 pre-C12 |
| #1867 | B3b | -0.0017 | WORSENS (`coord_footprint` 2514->2517) | merge | **no**: `a1_N5_annotated_return` |
| #1874 | A2 | +3.3243 | IMPROVES | merge | yes |
| #1887 | B1 | +20.5886 | IMPROVES | merge; round 1 planted the pre-solve write | magnitude no. With C13 it is +4.8690 (hub 71 -> 38) |
| #1958 | A3 | +1.1069 | IMPROVES | merge | yes |
| #1966 | B6 | +4.3119 | IMPROVES | merge | yes |
| #2017 | B7 | +0.0000 | NULL | merge | yes (an instrument PR) |
| #2025 | B11 | +0.6950 | IMPROVES | merge (`0dfb63a8`) | yes |

Re-scored with the A4 instrument (`--only 1852,1867,1887`):

| PR | dS | verdict |
|---|---|---|
| #1852 | +51.1062 | IMPROVES |
| #1867 | -0.0011 | WORSENS (2515->2517) |
| #1887 | +4.8690 | IMPROVES |

Other figures:

- **Red-team sweep.** The instrument was a read of every fix-review comment and every surviving evidence directory on the nine PRs above. It found 11 plants:
  - 8 against the score, all on #1874, all already committed;
  - #1887's pre-solve write, now `14_*`;
  - #1852's cast finding, now `15_*`;
  - and plants against per-PR checks that do not touch the score: #1887's isolation and hand-off plants, #1958's params control, #1966's census mutant, #2017's enumerator plant, and #1852/#1867's payload-key spellings.

  Not verified: #1966 round 5 named a `CoordinatorDiagnostics.of(cls, coord: Any)` reach blind spot as carried forward. No plant script survives, so it is not committed here.
- **The red-team cases at the head**, from `python3 tools/audit/archscore/calibrate.py --only rt_15_payload_cast,rt_14_hub_write_presolve,a1_N5_annotated_return`: `rt_14` reads NULL, admissible; `rt_15` reads NULL, admissible; `a1_N5_annotated_return` reads WORSENS (`coord_footprint` 2512->2514). Each is what `expected.json` records. CI's full `arch_score.py`, over every planted and red-team case, is the verdict of record: CI's dispatched run [37689221025](https://github.com/tvofi/heatpump_optimizer/actions/runs/37689221025), at `6ec6553e` (the head's parent; the head adds only the carry record). There `fast (3.14)` printed `MODE: FULL`, `ALL 169 ARCHITECTURE SCORE CHECKS PASSED` and `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`. So every planted and red-team verdict is as `expected.json` records under the widened census, and none moved past `c2a0448d`.
- **Corpus re-measure**, from `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric hub_solve_writes,footprint --jobs 2`: 87 trees, 0 errors. Then `PYTHONPATH=tests/hastub python3 tests/arch_score.py --stored` moved one corpus verdict, `c2a0448d` (GOOD, #1751), from IMPROVES to WORSENS. The rise is hub 70 -> 71: the forecast-seeded outdoor reading is a cycle write. Re-recorded, with the reason in `ABOUT.md`.
- **Hub sites on today's tree**, from `tests/arch_score_head.py`'s `hub_writers`: 2 solve-only against 38 cycle-wide, in 13 writers. At the pin (`7952d8f9`) it is 40 against 71.
- **The end-to-end gate.** `python3 -I tools/audit/archscore/gate.py --base 12dbd3a5^1 --head 12dbd3a5 --body <empty>` printed `FAIL: dS -0.0011 WORSENS; unexplained: coord_footprint 2515->2517` with rc=1, in 34 s.
- **Local checks**, all from the seat venv (`~/.local/state/hpo/venv-ci`, Python 3.14):
  - `tests/structure.py` passed;
  - `tests/entities.py` passed 2210;
  - `tests/harness_headers.py` passed 109;
  - `tests/arch_score_head.py` passed 15;
  - `tests/arch_score.py --stored` passed 58;
  - `gate.py --self-test` passed;
  - `node .claude/workflows/policy_lint.mjs` returned rc 0;
  - `codeowners_gap.py --check` returned `uncovered_files=0`, with gate.py PINNED.
- **Scope.** `tests/closure.py select --diff d15fc0ae` printed `MODE: FULL`, because `tests/run.sh` changes (a comment). That run is CI's: CI's dispatched run [37689221025](https://github.com/tvofi/heatpump_optimizer/actions/runs/37689221025), at `6ec6553e` (the head's parent; the head adds only the carry record). There `fast (3.14)` printed `MODE: FULL`, `ALL 169 ARCHITECTURE SCORE CHECKS PASSED` and `ALL 15 ARCHITECTURE SCORE HEAD CHECKS PASSED`. So every planted and red-team verdict is as `expected.json` records under the widened census, and none moved past `c2a0448d`.
- **CI prediction.** The predictor from `origin/fix/r9-ro-11-pr` (R9-RO-11, not yet in this tree) was run from a scratch copy with base `origin/handoff/r9-eg-entry-config`. At the head it printed `no closures or fast red predicted`, after the new files were placed beside their siblings in `tests/closures.json`. It is cited here, not re-runnable from this tree.

## Architecture score

`n/a: the diff touches no custom_components/ file, so every score metric is flat at the head.`

## Red checks

Two jobs went red on the dispatched run 37689221025, at `6ec6553e`. Neither is a pull-request run.

- **`briefs` (this diff).** `dev/programme/carries/carry-1774.json` names `SOLVE_PATH_HUB_WRITERS`, which this branch renamed, so brief_lint could not resolve it. The fix is at `b5f01426`: the carry cites `d15fc0ae57da` for the old table and records its discharge. Locally, `node tools/policy/brief_lint.mjs` now returns rc 0.
  - **Cheaper detector:** that same command, about a second, which I had not run before the push. A rename should grep the carry files; `git grep` of the old name finds this one.
- **`mutation` (not this diff).** `MUTATION TABLE REFUSED -- 56 ... added by this diff`, against ratchet base `09ba95d0`. Every site the log names is in `custom_components/` (`coordinator.py`, `__init__.py`, `entry_config.py`, ...), and this diff touches no file there. They are R9-EG-B11's sites on the stacked base, which #2025's own `mutation-autofix` pins. After #2025 merges and main is merged in, the delta is this diff's own, and `ci_predict.py` predicts no unpinned site in it.

- **Ancestry reds (not this diff).** `tools/pr/prepr.sh` reads red check runs on commits this head inherits from the stacked base: `closures`, `closures-autofix`, `delivery-status`, `fast (3.14)`, `mutation-autofix`, `mutation-nightly`, `nightly-status` and `typing`. They sit on R9-EG-B11's commits (`d15fc0ae` and its ancestors since `09ba95d0`). #2025's body answers each one, and its approved head `0dfb63a8` is green. On this branch's own dispatched run, `closures` and `fast (3.14)` were green, and `briefs` and `mutation` are answered above. After #2025 merges they leave this head's ancestry, and step 2 of "After #2025 merges" re-reads them.

## Forward-carry

- **The ratchet's census decision.** Keep the adjacent window in `tests/structure.py`'s `duplication_copies`. The required score check reads the gapped census (C3), so a split that the ratchet credits as a dedupe reads NULL on the gate. Switching the ratchet raises every recorded `duplication_copies` budget, and a raise is the owner's. Decided under the mandate: no switch (see ## Approval).
- **The footprint definition.** A typing-only change reads as a rise, because an annotated alias and a bare `return <name>` count as logic (`a1_N5_annotated_return`). Until the footprint's v2 fix lands (the PRE-STUDY section 10 queue), a UX-5/6/7 or later PR that types a value this way explains the `coord_footprint` rise in its `## Architecture score` section. Placed by the orchestrator as roster carries on R9-UX-5, UX-6 and UX-7, on `handoff/audit-r9-fixplan` at `0180b428`. The roster is not in this tree.
- **The ruleset.** Adding the context `arch-score` to `main-protect-checks` is a repository setting that only tvofi can apply. The orchestrator requests it and records it on #201.

## Friction

- `heavy-scripts-in-ci: cost`: the calibration's planted half can be re-measured only by a full `tests/arch_score.py`. The seat therefore dispatched `tests.yml` on the branch rather than run it locally. The corpus half re-measured locally per metric in 6.5 min (`--only-metric`, added here).
