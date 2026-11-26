Fix review: merge ea316e99f52dfccc38c08b09a7abddf49a5297a3

bus-nonce: dee2af28420906d6f825c2ce7ef2d195

Round: first verdict at this head; the packet's `## Review scope` reads `full` (no verdict names ea316e99), so the whole three-dot diff was reviewed, the bot delta 454abc83..ea316e99 included.

## Evidence

- RESULT: the previous verdict on this PR (comment 7192174772, `blocked 454abc83 head-moved`) is resolved: this review is at ea316e99, the head it named, and that head is GREEN. Its code findings (five killed mutants, null control at the base) agree with this seat's independent re-run; its residual is the same seam as the follow-up below, reached independently.
- RESULT: `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` at ea316e99 in a detached worktree: `ALL 167 DEBUG COLLECT CHECKS PASSED` (ev/debug_collect_head.txt).
- RESULT: mutation proof re-run (step 1), each against tests/debug_collect.py at the head, restored after: `_number` predicate back to the base's `not isinstance(value, bool)`: `1 of 167 DEBUG COLLECT CHECKS FAILED`, the new `replay_doc._number keeps a value exactly when ...` check, nan/inf kept (ev/mut_number_base.txt). Coordinate `if numeric(value):` to `if not isinstance(value, str) or numeric(value):`: 1 of 167 failed, the new `replay_doc.clean_value nulls a coordinate ...` check (ev/mut_coord_off.txt). `if isinstance(value, str):` to `if False:`: 2 of 167 failed (ev/mut_coord_str_off.txt). `if numeric(value):` to `if True:`: the script dies on `ValueError: could not convert string to float: 'north'` (ev/mut_coord_try.txt). No survivor among the four.
- RESULT: the body's mutation-proof figures (1 of 166, 1 of 167) are re-derived as 1 of 167 at this head for both; the 166 was the count before the second check landed, consistent with the commit order.
- RESULT: enumeration rule re-run at base dbdc71faea and head (ev/enumeration.txt): the same nine lines at both; the body's dispositions match each hit (`numeric` the owner, `json_decimal_places`/`text_ok` write no number, coordinate cut and `_number` closed, `_scan_leaf` writes none). No seam of the rule's output is undispositioned.
- RESULT: the delta 454abc83..ea316e99 is four added ledger pins under tests/mutation_ledger/killed_by/replay_doc.py/ (ev/delta_stat.txt); their `old` lines match the head's lines 244, 247, 271 verbatim, and the two deleted 59b66cd2 pins named the rewritten base line.
- RESULT: `git merge-tree --write-tree origin/main ea316e99` exits 0: merges cleanly.
- RESULT: VERSION, manifest and RELEASE_NOTES.md are not in the branch's diff; no golden or claim file moves.
- RESULT: CI: `merge_train.py classify ea316e99f52dfccc38c08b09a7abddf49a5297a3 --pr 3910` printed `GREEN ea316e99f52dfccc38c08b09a7abddf49a5297a3 pending: none red: none` (ev/classify.txt). No owed red to answer.
- RESULT: finder's harness (probes_p2.py from 872510cd3e) not re-run by this seat; its base/head figures in the body are the fixer's, not verified here. The committed check in tests/debug_collect.py drives the same seam and fails at the base's predicate (mutant above), which stands as the both-ends check.
- RESULT: the scoped-gate count, structure ratchet and archscore figures are cited from CI's green `gate`, `arch-score` and structure lanes, not re-run (step 11: cite heavy runs).

## Findings

- Follow-up: `_keep_keys` with `_entry_shape` passes a non-string entry data/options value through unchanged, and `clean_value` returns a non-coordinate float as is, so a float NaN under an allowlisted entry key would survive `sanitise`. It is no number coercion, so it is outside the set the body's rule defines and outside finding F16; no path writing a non-finite float into entry data or options was shown. Carry: dismissed: outside the claim's rule-defined set and no reachable writer shown; a later D14 sweep may take it as its own seam.
