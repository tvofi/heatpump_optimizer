Fix review: blocked 3785b0d097bc22410f42eae7ba3129c5fece1c61 class-open: the barrier closes the busy argument but not the reader set; a classify call reached through an import alias, a rebinding, getattr or functools.partial, from a function whose name contains self_test, or from any module outside the four hand-listed ones passes the self-test

bus-nonce: 39bd7eee91e51fae2277ec88b02b8cc2

## Round

This is round 6 for the topic. It reviews a re-cut at the handoff tip 3785b0d097bc22410f42eae7ba3129c5fece1c61. ba5d3b2527fb40fe1a15b2fe8dc832f8aeb8406a is not an ancestor of this head, so I reviewed the three-dot diff against origin/main as a whole (12 files, +659/-35). From the fourth round on, `fixer.md` owes a re-cut, and this head is one.

## Block

The dispatch asked for a specific test: every reader of a classify answer is enumerated mechanically, and a new one fails a check. The re-cut meets that test on the argument side only.

- **The argument side is closed.** `busy_reads` is a three-shape allow-list that refuses every other `ast.expr`, and `_busy_candidates` covers every argument shape an `ast.Call` carries. Every spelling that blocked an earlier round is now counted (ev/prior_block_rows.txt): `classify(l, r, None, **kw)`, `busy=(), **kw`, `*rest, busy=None`, a comprehension filter `if 0`, `(not 1) and b`, `b if f'' else ()`, `frozenset(())`, `set([])`, `None or ()` and `() if c else None`. The three reading controls still pass.
- **The reader side is still a list, not a grammar.** `blind_classify_readers` counts only a call whose func is spelled `classify` (as a Name, or as an Attribute's `.attr`). It skips any call inside a function whose qualified-name chain contains the substring `self_test`. `_gate_reader_barrier_self_test` runs it over four hard-coded modules: merge_train.py, orchestrator_tick.py, review_packet.py and proof_watch.py. To test this, I appended each of the following deferral-blind readers to the head tree, one at a time, and ran `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` (ev/plants.txt). The control plant `def _planted(l, r): return classify(l, r)` in review_packet.py gives 680 checks, 1 failed. Each plant below gives **680 checks, 0 failed**:
  1. an import alias in review_packet.py: `from merge_train import classify as gate_read`, then `gate_read(l, r)`
  2. a rebinding: `read = mt.classify; read(l, r)`
  3. `getattr(mt, "classify")(l, r)`
  4. `functools.partial(mt.classify, l)(r)`, where `classify` is passed as a value and never called by name
  5. a production function named `reader_after_self_test` calling `mt.classify(l, r)`, which the substring test `"self_test" in x` skips
  6. a new module, tools/audit/seat/gate_reader_new.py, with `mt.classify(l, r)[2]`
  7. an existing seat module outside the four, tools/audit/seat/record_row.py, with `mt.classify(l, r)`

  None of these needs name or type resolution. Each is decidable from syntax:
  - Seams 1–4: any Load of the name or attribute `classify` other than as the func of a checked call, and any `import ... classify as`, can be counted.
  - Seam 5: the exclusion can key on the exact self-test function-name form, not a substring.
  - Seams 6–7: the module set can be derived (every tracked .py that imports merge_train or names `classify`), not typed.

  So the body's stated known limit, "undecidable for a per-call syntactic predicate", does not cover them. The body's Enumerator line names only the binding, value and steering seams, and none of these seams is in the diff or dispositioned in the body. Under fix-review.md step 6 that is class-open. I list every seam the review found: callee aliasing (import-as, rebinding, getattr, partial or any value use), the self_test substring exclusion, and the hand-typed module list.
- **No current tree reader exploits any of these seams.** The live registry comparison passes, and a grep of tools/ finds no other call of merge_train's `classify` outside the four modules (the other `classify` names, in review_carry.py, record_row.py's `delivery_status.classify` and figure_census.mjs, are different functions). The block is about the barrier's claim that a new reader fails a check. It is not about a live defect.

## Findings

none beyond the block

## Evidence

- Head reviewed: 3785b0d097bc22410f42eae7ba3129c5fece1c61 (ev/HEAD.txt). It equals the body's `## Head`. No pull request exists yet, so there is no review packet and no CI run at this head. I read no check-runs and no red is owed (`## Red checks`: none).
- `git merge-tree --write-tree origin/main <head>` against origin/main 19a8e11a29b58f69bb6856ed376ad90bfcf6f948: rc 0, tree 2d765933b67002032932d2328df5a5b5160c7a0e. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json` and there was no claim-file conflict (ev/merge_and_version.txt).
- VERSION, the manifest and RELEASE_NOTES.md are untouched, and custom_components/ is untouched (ev/merge_and_version.txt). No golden fixture or claim file is in the diff.
- `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` at the head: 680 checks, 0 failed (ev/selftest_head.txt). This matches the body.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 317 checks, 0 failed. `bash tools/audit/seat/merge_pr.sh --self-test`: 26 checks, 0 failed. Both match the body (ev/tick_selftest.txt, ev/merge_pr_selftest.txt).
- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py`: `RESULT mutants=13 survived=0 stale=0 baseline_failed=0`, rc 0 (ev/mutants_head.txt). This matches the body. None of its 13 mutants touches the callee or module-scope seams above, which is why they survive it.
- Finder harness `python3 -I dev/audit/harnesses/r10_gate_defer_barrier.py` at the head: rc 0, with `policy_null_ok=True`, `policy_A_wait=True policy_B_wait=False policy_C_wait=False policy_C_names_fast=True` and `under_queued_null=['TIMEOUT']` (ev/finder_harness_head.txt). This matches the body. I did not re-take its baseline end, because the class-open block stands on the plants.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (ev/entities_head.txt; its in-run `FAIL hb:positive_control` lines are retried tries the check itself absorbs). This matches the body.
- Figures I did not re-derive: the body's a6076a0f corpus arm (`wrong=64`), its null-control plant counts (10/36/5), the prepr.sh diff-mutant draw (17 survivors), the archscore dS and the closure-select scope line. The block does not turn on any of them.
- The CLAUDE.md citation of `tests/entities.py` with `env -u BASH_ENV` alone fails at import (`No module named 'homeassistant'`) under venv-ci. It needs `PYTHONPATH=tests/hastub`, as tests/README.md says.

## Friction

none
