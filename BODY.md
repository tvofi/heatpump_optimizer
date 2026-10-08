R9-EG-A4 (#1774): the architecture score becomes a required check, after the report-only wave was compared with its reviews.

Closes #1774

**Dependencies merged.** R9-EG-A1 (#1851), B7 (#2017), A2 (#1874), A3 (#1958) and B11 (#2025) are on `main` (4dbe5aac). `origin/main` is merged into this head; its diff against the merge base is this pull request's own.

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
   - `.github/workflows/arch-score.yml` runs `tools/audit/archscore/gate.py` **from a checkout of the base commit**, and `tests/structure.py` with it: `vector.load_structure` loads that file by path into the gate's process, so it is part of the grader. A pull request therefore cannot edit the check that grades it, as `tests.yml` restores its check source. When the base holds no `gate.py` (this pull request, which adds it) the head's copy runs once, and the workflow file saying so is under the owner's review. This is the reviewer's round-1 finding on #2068 (an edit to the unowned `tests/structure.py` waved three rises through), decided on #201 comment 6070657723. CODEOWNERS is unchanged: tvofi's ruling is that audit instruments stay unowned.
   - It passes when delta-S >= 0 and no gate metric rises from the merge base to the head. A rise passes only when the body's `## Architecture score` section has a line naming the metric with a reason. This is "explained in the body like a budget raise", with the reason judged by the fix reviewer. Owner approval of a score rise is not required: neither the brief nor R3-6 asks for it, and that is an open question below.
   - The template states the rule within its policy cap. `pr-contract-rerun.yml` watches the new workflow, and `tests/entities.py` admits it to the files that list `edited`.
   - The weights stay at their frozen hash.

## After merge

The ruleset context `arch-score` is tvofi's to add to `main-protect-checks` (ruleset 23698884). The orchestrator requests it and records it on #201. Until then the check runs but does not gate.

## Approval

This changes policy and the enforcement surface, so it merges only on tvofi's approving review at the head, which CODEOWNERS requires. It touches:

- `.github/PULL_REQUEST_TEMPLATE.md`;
- `tests/arch_score.py`, which gains the plant below;
- `.github/workflows/arch-score.yml`, which is new;
- `.github/workflows/pr-contract-rerun.yml`;
- `tests/entities.py`, which admits the new `edited` workflow;
- `tests/run.sh` (a comment);
- `tools/audit/archscore/calibration/expected.json`, where two verdicts are re-recorded and three cases added.

The decision it implements is tvofi's R3-6 (2026-09-29). Not yet approved at this head.

Decisions recorded under tvofi's mandate (#201 comment 5951564627), relayed by the orchestrator:

1. A score rise passes on a body `## Architecture score` explanation, judged by the fix reviewer. It does not need the owner's approval at each head; budget-file raises keep their own owner gate.
2. The ratchet's `duplication_copies` keeps the adjacent window. There is no switch to the gapped census.
3. The instrument stays unowned (tvofi's ruling that audit instruments are not owned); it is protected by running from the base instead (#201 comment 6070657723).
4. After merge, tvofi adds the `arch-score` context to `main-protect-checks`. The orchestrator requests it and records it on #201.

## Head

The code head is `handoff/r9-eg-a4` at `004807db0c778ef1236b6a580f7a2a9465dbaf2a`, which merges `origin/main` `4dbe5aac` into the authored head `545d5bda`. The merge was clean. One repair followed it: main's twin-route check in `tests/entities.py` (R9-CI-2a, `e960a747d`) required every workflow that lists `edited` to name a route, so `arch-score.yml` takes `budget-raise-gate.yml`'s `per-run` concurrency (never cancels) and `_CC_TWIN_ROUTE` names it. Round 1 of #2068 then blocked e9a7b9b4; `004807db` is its fix (base-copy gate, CODEOWNERS entry dropped, the plant). The figures were taken at this head on 2026-10-09.

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
- **The base-copy switch and the reviewer's plant.** `tests/arch_score.py` drives the workflow's own score step over a throwaway repository whose head carries a different `tests/structure.py` (`PLANT`) than its base (`BASE`), with a stub gate that prints the file it can see. At the head it reads `SAW BASE`. With the `git worktree add` and `cd` lines deleted from the step it fails (`1 of 60 ARCHITECTURE SCORE CHECKS FAILED`, the plant check), and with them restored `ALL 60 ARCHITECTURE SCORE CHECKS PASSED`. The null control, a base with no `gate.py`, reads `SAW PLANT`: the adoption path. This is a drive of the step's shell, not of a real pull request: the end-to-end plant (#2068's P1 patch) cannot run in this pull request's own CI, which takes the adoption path. `node tools/policy/field_coverage.mjs` reads `FIELD COVERAGE ok`, and `codeowners_gap.py --check` reads `uncovered_files=0`, at the head.

## Figures

The wave comparison comes from `python3 dev/audit/harnesses/eg_a4_wave_deltas.py`, with the instrument at `d15fc0ae` (pre-A4; the wave table is a measurement of that period and was not re-taken after the merge). The review verdict is each pull request's last `Fix review:` comment.

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
| #2025 | B11 | +0.6950 | IMPROVES | merge (`0dfb63a8`), merged | yes |

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
- **The red-team cases at the head**, from `python3 tools/audit/archscore/calibrate.py --only rt_15_payload_cast,rt_14_hub_write_presolve,a1_N5_annotated_return`: `rt_14` reads NULL, admissible; `rt_15` reads NULL, admissible; `a1_N5_annotated_return` reads WORSENS (`coord_footprint` 2512->2514). Each is what `expected.json` records. CI's full `arch_score.py`, over every planted and red-team case, is the verdict of record. It runs in `fast (3.14)` on this head; I cite no run here until it has finished at this head, and the next body edit will name it.
- **Corpus re-measure**, from `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric hub_solve_writes,footprint --jobs 2`: 87 trees, 0 errors. Then `PYTHONPATH=tests/hastub python3 tests/arch_score.py --stored` moved one corpus verdict, `c2a0448d` (GOOD, #1751), from IMPROVES to WORSENS. The rise is hub 70 -> 71: the forecast-seeded outdoor reading is a cycle write. Re-recorded, with the reason in `ABOUT.md`.
- **Hub sites on today's tree**, from `tests/arch_score_head.py`'s `hub_writers`: 2 solve-only against 38 cycle-wide, in 13 writers. At the pin (`7952d8f9`) it is 40 against 71.
- **The end-to-end gate.** `python3 -I tools/audit/archscore/gate.py --base 12dbd3a5^1 --head 12dbd3a5 --body <empty>` printed `FAIL: dS -0.0011 WORSENS; unexplained: coord_footprint 2515->2517` with rc=1, in 34 s.
- **Local checks**, all from the seat venv (`~/.local/state/hpo/venv-ci`, Python 3.14):
  - `tests/structure.py` passed;
  - `tests/entities.py` passed 2227 at the merged head (first run: 1 failure, the twin-route check above; repaired. Not re-run after round 1: CI's `fast (3.14)` is the record);
  - `tests/harness_headers.py` passed 109;
  - `tests/arch_score_head.py` passed 15;
  - `tests/arch_score.py --stored` passed 60 (58 plus the plant and its null control);
  - `gate.py --self-test` passed;
  - `node .claude/workflows/policy_lint.mjs` returned rc 0;
  - `codeowners_gap.py --check` returned `uncovered_files=0`, with gate.py PINNED.
- **Scope.** `tests/closure.py select --diff origin/main` prints `MODE: FULL`, because `tests/run.sh` changes (a comment). The scoped run is CI's, on this head; none is cited yet.
- **CI prediction.** The predictor is now in the tree: `python3 tools/pr/ci_predict.py --base origin/main` printed `no closures or fast red predicted against 4dbe5aace744`.

## Architecture score

`n/a: the diff touches no custom_components/ file, so every score metric is flat at the head.`

## Red checks

Two reds on an earlier, stacked dispatched run are answered below, and the ancestry reds the stacked base carried are gone with the merge. `nightly-status` is red on this head and is not this diff's: the diff does not reach what it reads (the round-1 reviewer's reading).

- **`briefs`.** `carry-1774.json` named `SOLVE_PATH_HUB_WRITERS`, which this branch renamed. Fixed at `b5f01426`; `node tools/policy/brief_lint.mjs` returns rc 0 at the head. Cheaper detector: that command, about a second; a rename should `git grep` the carry files.
- **`mutation`.** It was red on #2025's 56 package sites, not this diff. This diff touches no `custom_components/` file, and `ci_predict.py` predicts no unpinned site.
- **`entities` (found after the merge, repaired).** Main's twin-route check refused `arch-score.yml` (see Head). Cheaper detector: `tests/entities.py` run after the merge, which is the step 2 this body's earlier draft listed.

## Forward-carry

- **The ratchet's census decision.** Keep the adjacent window in `tests/structure.py`'s `duplication_copies`. The required score check reads the gapped census (C3), so a split that the ratchet credits as a dedupe reads NULL on the gate. Switching the ratchet raises every recorded `duplication_copies` budget, and a raise is the owner's. Decided under the mandate: no switch (see ## Approval).
- **The footprint definition.** A typing-only change reads as a rise, because an annotated alias and a bare `return <name>` count as logic (`a1_N5_annotated_return`). Until the footprint's v2 fix lands (the PRE-STUDY section 10 queue), a UX-5/6/7 or later PR that types a value this way explains the `coord_footprint` rise in its `## Architecture score` section. Placed by the orchestrator as roster carries on R9-UX-5, UX-6 and UX-7, on `handoff/audit-r9-fixplan` at `0180b428`. The roster is not in this tree.
- **The ruleset.** Adding the context `arch-score` to `main-protect-checks` is a repository setting that only tvofi can apply. The orchestrator requests it and records it on #201.

## Friction

- `heavy-scripts-in-ci: cost`: the calibration's planted half can be re-measured only by a full `tests/arch_score.py`. The seat therefore dispatched `tests.yml` on the branch rather than run it locally. The corpus half re-measured locally per metric in 6.5 min (`--only-metric`, added here).
