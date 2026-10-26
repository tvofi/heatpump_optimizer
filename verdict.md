Fix review: merge 3c32a0a0e4df0e8f59ee0de17448b294e74ce528

bus-nonce: f93d552e46446473d01c34af299bc3f4

## Scope

Delta review of #2824 (R10-DIAG-REDACT), round 3, against the prior merge verdict at fa23170a1. Measured at head 3c32a0a0e4df0e8f59ee0de17448b294e74ce528 from a detached worktree; the head is unchanged at verdict time (refs/pull/2824/head = 3c32a0a0e4df). fix-review.md at the merge base equals origin/main's (three-dot diff over dev/governance/roles/ is empty).

## Findings

None. Every item in the scope is settled at this head.

## Evidence

### 1. The three sites (diagnostics.py:126, :138, :144 at 0fee7df71)

No mutant survives at any of them at the head: the fixer removed the two type guards and rewrote the text branch, then pinned the change with a check that kills each removed site when it is restored. RESULT lines from `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` with each mutant applied in a scratch worktree at the head, then restored (ev/debug_collect_mutant_*.txt):

- RESULT head: ALL 136 DEBUG COLLECT CHECKS PASSED, rc=0.
- RESULT :126 GUARD_OFF (`if not isinstance(node, (str, int, float)): return set()` restored in `_private_values`): rc=1, 1 of 136 failed, the new check "a removed leaf of any other type is searched for and redacted by its text ...", detail `[set()]`.
- RESULT :144 GUARD_OFF (`if not isinstance(value, (int, float)): return value` restored in `_without_values`): rc=1, 1 of 136 failed, the same check, detail `[{'2026-01-12 00:07:00+00:00'}]`.
- RESULT :138 RETURN_DEL, the replacement line `return reduce(...)`: as a bare expression statement, rc=1, 2 of 136 failed; replaced by `pass`, rc=1, 2 of 136 failed. Both runs fail "Download diagnostics carries none of the values its redaction removes ..." and "the value pass redacts a private value inside text, as a key, and as a number, in a tuple too ...".
- RESULT null control (a comment-only edit to diagnostics.py): rc=0, ALL 136 PASSED.
- The seven `FAIL a16:...` lines print at the head and under every mutant alike; they are sub-detail of the A16 writer check, which passes, and not checks.

The figures in the body's `## Head` section (1 of 136 `[set()]`, 1 of 136 with the datetime set, 2 of 136 for the `pass` mutant) re-derive exactly.

Static ratchet at the head, computed in-process with tests/mutation_table.py's own functions (load_budgets, inventory, unpinned_sites, base_unpinned_sites, added_unpinned, diff_sides) against ratchet base 63a1c5fe8 (ev/ratchet_at_head.txt): completeness problems 0; 3943 unpinned at head, 3943 at base; 0 added unpinned. Every inventory site in `_private_values` and `_without_values` (lines 127-147) carries a `killed_by: tests/debug_collect.py` disposition. The new `return reduce(...)` line has no inventory site, as the body says: it is the sole statement of its `if`.

Equivalence check on the old :138: confirmed by reading. At fa23170a1, deleting `return value` fell through to the :144 guard, which returned the already-replaced string unchanged, so that mutant was equivalent. The rewrite removes it rather than triaging it.

### 2. Code delta since fa23170a1

The branch's own delta over fa23170a1 is exactly two commits. `git merge-tree --write-tree fa23170a1 63a1c5fe8` diffed against the head shows only these 6 files (ev/delta_since_fa23170a.txt):
- 0fee7df71 (bot: `ci: pin killed mutants`): four killed_by ledger files for debugger.py collection_window and drift.py stored_age_seconds. Ledger completeness is 0 problems at the head.
- db5f00828: diagnostics.py (+import reduce, the two guards deleted, the text branch as one reduce) and one new check in tests/debug_collect.py.
- The four merges (059f0f788, ce2520a67, bab45b1f5, 3c32a0a0e) each have an empty `--remerge-diff`, so each one is a clean automatic merge with no hand resolution (ev/merges_remerge_diff.txt).

Correctness and behaviour change, read against the code:
- `_without_values`: any leaf that is not a str, Mapping, list or tuple is now replaced by REDACTED when its whole `str()` is a private value, and is otherwise returned unchanged. Before, only int/float leaves were matched. The change can only redact more, never less. `True`/`False` (4 or 5 characters) and `None` (4) are shorter than LEAK_MIN_CHARS = 6 (replay_doc.py:101), so they can never be in `private`. For a JSON-shaped payload the output is therefore unchanged, matching the fixer's claim.
- `_private_values`: a non-scalar leaf under a TO_REDACT key, or under a coordinate key whose `_coordinate` changes it, now adds its `str()`. `_coordinate` catches TypeError/ValueError and returns REDACTED, so a non-numeric leaf cannot raise. A `None` token gives "None", which is under 6 characters and is excluded, as the new check asserts.
- The reduce over a frozenset applies the same sequential replaces as the old loop, so the string behaviour is unchanged.
- This diff makes no behaviour change outside the redaction value pass and the ledger pins.

### 3. Gate and CI at this head (check-runs API, ev/check_runs_at_head.tsv)

- `tests / mutation` (job 121351527886): success. Its log (ev/ci_mutation_job_121351527886.log) shows the run evaluated mutants, so the green is not an INCONCLUSIVE pass. It reads "3943 unpinned site(s) of 6376 candidate sites, 3943 at the ratchet base 7d2056970e08", then "0 survivor(s) of 10 evaluated = 0.0%, cap 20.0%" and "MUTATION TABLE PASSED". Killed sites include diagnostics.py:133 RETURN_DEL, :140 GUARD_OFF and :147 RETURN_DEL. The lane is no longer refused.
- `gate`: success (two runs, 121361557231 and 121362064175). `pr-contract / pr-contract`: success (121361411998 and 121361911259), both started after every other workflow concluded. Every `tests / *` lane is success or skipped.
- `governance / delivery-status`: failure. Its log lists main's overdue rows (#2821, #2823, ...), not #2824. Its own log says it is not a required context and blocks no merge. The body answers it under `## Red checks`.
- The body answers the round-2 red `tests / mutation` under `## Red checks`: it names the cause and the cheaper detector (ci_predict.py), and says why that detector cannot tell a survivor apart (step 11).

### 4. Delivery row, merge, and versions

- `git diff $(git merge-base origin/main HEAD)...HEAD -- dev/programme/delivery/` shows dev/programme/delivery/2824.md, +1 line: "#2824 — open, R10-DIAG-REDACT: redact owner data in the diagnostics bundle" (ev/delivery_row_3dot.txt).
- `git merge-tree --write-tree origin/main <head>`, with origin/main at 7d2056970e08: rc=0 and no conflict (ev/merge_tree.txt).
- VERSION, manifest.json, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff.
- The body names the head 3c32a0a0e4df as the head measured (step 7).

### Notes

- The body's `## Figures` section still quotes round-2 totals (135 checks) beside `## Head`'s 136. Both are labelled by round, and neither is contradicted.
- The dispatch's snapshotted brief asks for the verdict to be posted as a PR comment. The rendered prompt says "Do not post comments", so no comment was posted. The verdict returns only on the probe ref.
