Fix review: blocked 8d1774b5b0d903a4d335ff49b0fd44857d8cbb32 tests-red: tests / fast (3.14) fails stress.py memory budgets on 10 rows; the CI-platform re-record and its owner-confirmed raise are owed in this PR before merge

bus-nonce: e196494272c5a019cd53b69840b986ce

## Block

Round 1 (first review). The code change is sound. The head is not mergeable: the required `tests / fast (3.14)` is red at this head, on the check this PR newly exposes.

- CI run, job 139068952639 (`ev/fast_job.log`): `FAILED python3 tests/stress.py`, `1 of 122 STRESS CHECKS FAILED`, `FAIL the probed scenarios' memory peaks stay within their recorded budgets`. It names traced rows over 1.5x their record: flat/1z/space 1.7 vs 0.9 MiB, flat/2z/space 2.2, shoulder/1z/space 1.5, shoulder/2z/space 2.2, summer/2z/space/wood-two-tank 1.4, winter/2z/space 2.0, winter_extreme/2z/space 2.2, winter_mild/1z/space 1.8, winter_mild/2z/dhw 3.3, and more. `ok   the memory pass probes every recorded row` passes on the same run.
- The body predicts this red (`## Red checks`). Design §7 names what clears it: the memory-half re-record from this CI platform's clean all-row run. Every row that rises is a raise under `budget-raise-gate` (0013) and needs the owner's confirmation before the push (CLAUDE.md rule 2). `tests/stress_budgets.json` is untouched at this head, so that step has not been done.
- Repair: re-record the memory half from the CI platform's run (`stress.py --record-memory`, five passes per row), and list every raised row under `## Raise justification`. The repair needs the owner's or the mandate's raise approval. A delta review then judges the new head. The CI log above is the clean all-row reading the design asks for. It reads 10+ rows, where the body's local null read 11: that is the set to decide.

## Findings

- Body paperwork: `## Null control` says the flagged rows "are the rows the re-record must decide (Forward-carry)", but `## Forward-carry` reads `none`. The owed re-record is this PR's own step, design §7, so no carry is needed. The cross-reference points at nothing. Carry: dismissed: the re-record is owed in this PR (the block), not carried

## Evidence

- Head reviewed: 8d1774b5b0d903a4d335ff49b0fd44857d8cbb32 (`ev/HEAD.txt`). Merge base f52e700d. `git merge-tree --write-tree origin/main <head>` at origin/main dc5face1: rc 0, clean (`ev/merge_tree.txt`).
- RESULT finder's harness (step 2). Harness: `dev/audit/rounds/round11/D9/s3/mem_confined.py` at the merge base, sha1 39310648bc51427e915a78c121722066ecefa8c5, the unported copy the body names. I ran its own selector read (`gate_probe_labels`, exec'd from each tree's stress.py, `--top-n 6`) at both ends (`ev/finder_selector_{base,head}.txt`):
  - base: `universe=54`, `probed_by_gate=6`, `never_probed=48`;
  - head: `probed_by_gate=54`, `never_probed=0`.

  This matches the body's inject-arm `probed_by_gate` 6 -> 54. I stopped the full probing arms (54 subprocess probes per arm) on this loaded host before they reported: no `detected_confined`, `flagged_if_probed` or null figure of mine exists. The body's inject and null tables are therefore unverified by me, except as CI's all-row run corroborates them.
- Step 1, mutation: b8a5aaee is the design's named mutant (the top-N selection restored) under the new check. The body's figure for it is `48 recorded row(s) not probed`, `2 of 122` failed. I did not re-run it: stress.py needs the exclusive lease, and CI's head run already shows the check passing with every row probed. CI's `tests / mutation` is green at this head.
- Step 6: no timing measurement runs after the memory pass. After `R.section("Memory (D9-04)")` (stress.py:5399), `grep` finds no `perf_counter`, `process_time` or `reference_solve(` call. The two later `timing_check`s grade the sweep's earlier measurements (`_sweep_ratio`, `pathological`). The body's claim that room-history moves ahead of the pool holds.
- The pool: probes are subprocesses whose verdicts are traced bytes and per-child `ru_maxrss` over the empty probe. The parent's RSS-growth check is unchanged. CI reads `attributable RSS: 54 of 54 ... at this platform's import floor`, so the RSS arm is blind there as before, not because of the pool.
- Design deviation (`MEMORY_TOP_N` deleted, five passes for every row in record mode): consistent with `record_memory_table`'s own rule, now that check mode compares every row. The harness ports (h7_memory_gate.py execs the nested selector; mem_confined.py falls back to `getattr(..., None)`) are fixer step 3 ports and are disclosed.
- Step 5: `VERSION`, the manifest and the notes heading are untouched. No claim file is touched.
- Step 11, owed red: `tests / fast (3.14)` is in the owed-reds set, and the body's `## Red checks` answers it (predicted, no cheaper detector). `tests / nightly-status` is red and not owed. The `gate` failures aggregate fast's red. `merge_train.py classify` read `RED ... red: gate` at 09:15Z (`ev/classify_poll.log`).
