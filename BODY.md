#3885 L4 (design/r11-ci-3885-queue §3 L4): a record branch's changed list, which holds only `dev/programme/delivery/` rows, now idles every lane that `lane_reads_delivery.recording.json` reads as row-blind. That set is `tests / arch-instrument` alone. `prelude.machinery(rowblind=True)` drops every path under `DELIVERY_DIR`. Before, it dropped only the pull request's own row. The lanes the recording reads as row readers keep `machinery`.

Leaves #3885 open: L3 (W1 + W2) and carry 2 are still owed. Carry: #3885

## Head

77f41cbb0dbd6e46ce4f015c43f1ce3d81e7b599, cut from origin/main 8890fc2bada17f6c7d8a6bbf03e6625a16a0967c.

## Mutation proof

Each mutant was applied to `tools/ci/prelude.py` at the head. Then `python3 tools/ci/prelude.py --self-test` was run, and the file was restored. The restored file reads `prelude self-test: 159 checks, 0 failed`.

- M1 deletes the row clause (`or (rowblind and f.startswith(DELIVERY_DIR))`). Result `159 checks, 6 failed`:
  - FAIL C7a-row: a package file plus its own delivery row idles the row-blind lanes
  - FAIL C7a-row: ... and ANOTHER pull request's row idles them too
  - FAIL L4: a record branch's list (rows only) idles the row-blind lanes
  - FAIL C7a-row: package + row 7 on pull request 7 idles the row-blind lanes
  - FAIL C7a-row: ... and row 8 on pull request 7 idles them too
  - FAIL L4: a record pull request (other PRs' rows only) is light, idles the row-blind lanes, runs the row readers
- M2 makes `outputs` call `machinery(changed)` with no `rowblind`. Result `159 checks, 3 failed`: the three `outputs` rows above.
- M3 changes the prefix to `"dev/programme/delivery"`, without its slash. Result `159 checks, 1 failed`: FAIL L4: ... and so does a path beside delivery/ that only shares its stem (null control).

prepr ran with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, as the dispatch brief directs, so prepr drew no `diff mutants`. The three hand mutants above are the proof for the one added predicate.

## Null control

The unmodified tree's rule, applied to a record pull request's list. The list is #3891's two rows, `dev/programme/delivery/3891.md` and `3892.md`, on pull request 3903. The probe imports each tree's own `tools/ci/prelude.py`:
- Base 8890fc2bad: `light True machinery True machinery_rowblind True`, so arch-instrument runs.
- Head: `light True machinery True machinery_rowblind False`, so arch-instrument stands down.

At both ends `stand_down` is `['browser', 'coverage', 'hassfest', 'typing', 'validate']`, and the row readers run (`machinery True`).

In the self-test, the null rows sit beside each positive row:
- rows + `dev/programme/HANDOVER.md` runs the lanes;
- rows + `tools/ci/gate.py` runs them;
- `dev/programme/delivery.md` runs them;
- an empty list, an unread list or an unreadable script table runs them.

## Figures

- Per-lane answer to "which lanes can a record PR skip". The rule enumerating the set is every job of the record PR's CI run 45907701622, attempt 1, from its job listing (`gh api repos/tvofi/heatpump_optimizer/actions/runs/45907701622/jobs`), 30 jobs. Each job's disposition:
  - Already stood down at base, `prelude.stand_down` (LIGHT_LANES): `tests / browser`, `tests / typing`, `hassfest / hassfest`, `validate / validate-hacs`, `tests / coverage`. The `codeql` python leg is also already stood down (LIGHT_SKIP_LEGS).
  - Idled by this diff: `tests / arch-instrument`. `lane_reads_delivery.recording.json` records `"arch-instrument": "reads no row"`. Re-run at this head: see the lane_reads_delivery line below.
  - Kept, because the recording reads a row: `tests / closures` (its re-record), `governance / env-matrix`, `governance / instrument-self-tests` (policy_lint's tree-wide `git grep`). Command: `jq -r .verdict dev/audit/harnesses/lane_reads_delivery.recording.json`.
  - Kept, because a measured closure reads a row: `tests / fast (3.14, 1/2)` and `(3.14, 2/2)`. Their scope runs `tests/doc_claims.py` and `tests/entities.py`, the two scripts whose closure lists a `dev/programme/delivery/` path. Command: `jq -r '.closures|to_entries[]|select(any(.value[]; startswith("dev/programme/delivery/")))|.key' tests/closures.json`.
  - Residue, by category: every other job in the listing is one whose reads no recording and no closure measures, so nothing proves it row-blind and it runs (fail closed). That is prelude, cancel-superseded, refresh, arch-score, budget-raise-gate, `governance / policy-docs`, `governance / wave-script`, `tests / briefs`, `tests / closure-scope`, `tests / mutation`, `tests / graders-head-copy`, `tests / nightly-status`, codeql actions and javascript-typescript, and the skipped kernel-points, `governance / record`, `tests / nightly-ha` and `tests / replay`.
- Saving per record run: `tests / arch-instrument` ran 22:57:32Z to 22:59:28Z in run 45907701622 (same listing), 1.9 runner-min. A stood-down job still takes a runner for its echo step. So the saving is at most 1.9 runner-min per record run, not the design's ≤456 runner-min/day. The design figure counted every record-branch job.
- Finder's harness: `dev/audit/harnesses/ci3885_queue.py report DAY` counts record-branch runner-min on a past day. It cannot read this head before the merge, and it reads the same at both ends on 11-25. Its after-merge reading is owed on the first busy day after the merge. The companion that applies the tree's own rule to the same inputs is the base-vs-head probe under `## Null control`.
- lane_reads_delivery re-run at this head (`python3 dev/audit/harnesses/lane_reads_delivery.py --lanes arch-instrument --out <scratch>/rec/arch-instrument`, then `--summarize`): at head 77f41cbb0d, `arch-instrument` is `complete: true`, `steps_traced: 3`, `reads_a_row: false` (`lane arch-instrument: 3 run step(s), 2 uses: step(s) listed, 0 exited non-zero, 546585 trace lines, 0 step(s) read a row`), beside the planted `control` lane at `reads_a_row: true` (the tracer's own null control); summary sha1 ba9e319d3d3873ce87f3ef5de0935a0748657155, kept in scratch, the in-tree recording left as recorded at f020f31c. The harness gains the one expression the arch-instrument job now carries, `inputs.range_base || format('origin/{0}', inputs.base || 'main')`, which is `origin/main` on a pull_request run. Before that, the trace refused with `no value for expression`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2791 ENTITY CHECKS PASSED`.
- Gate scope (`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate. Only the arch-instrument echo line changed: the old text, "Every changed file but its own delivery row is product", is false under this rule.

## Red checks

none

## Forward-carry

- Carry 2 of `dev/programme/carries/carry-3885.json` (env_drift cache after a light push) is not measured in this pull request. Its remeasure clause needs main push-run `fast` logs. Per `tests.yml`, a push never restores the drift cache: `Restore the drift baseline` runs on pull_request, merge_group and dispatch only. A push saves only a warmed entry keyed by its own SHA. So a push log always reads MISS, and the cost lands on a pull request whose merge base is a light push that never ran env_drift. The next seat measures it against that reading. Carry: #3885
- The row-blind classification rests on a trace taken at one head. A step added to `tests / arch-instrument` that reads a row would not be noticed by `lane_gates`, which pins the job's `inputs.machinery*` names and not its reads. Carry: #3885

## Friction

none
