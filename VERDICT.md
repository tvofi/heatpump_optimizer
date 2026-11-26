Fix review: blocked 454abc83f05e3e9d290ad4e68c4e6b36eca69897 head-moved: measured 454abc83f05e3e9d290ad4e68c4e6b36eca69897, head is ea316e99f52dfccc38c08b09a7abddf49a5297a3

bus-nonce: 6cac33f2a90b611b5d38e7e0b35f2938

## Block

The pull request's head moved off the dispatched head: `ea316e99f52dfccc38c08b09a7abddf49a5297a3` ("ci: pin killed mutants") adds four mutation-ledger pins to the PR's own diff. The dispatched head `454abc83f05e3e9d290ad4e68c4e6b36eca69897` is RED (`merge_train.py classify`: `RED 454abc83f05e3e9d290ad4e68c4e6b36eca69897 pending: none red: gate`), and a red verdict does not carry. `review_carry.py 454abc83f05e3e9d290ad4e68c4e6b36eca69897 ea316e99f52dfccc38c08b09a7abddf49a5297a3` prints `CARRY`. The delta is the four `killed_by` files below and nothing else. A re-dispatch at `ea316e99f52dfccc38c08b09a7abddf49a5297a3` is a delta round over those pins, and the code review below already holds for it. At render time, `classify ea316e99f52dfccc38c08b09a7abddf49a5297a3` read `WAIT ... pending: gate`.

## Evidence

- Round: first review of this PR (packet `## Review scope: full`). The role-contract drift check (`git diff merge-base...origin/main -- dev/governance/roles/`) is empty.
- Mutation proof, re-run in a worktree at `454abc83f05e3e9d290ad4e68c4e6b36eca69897` with `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`. The head passes: `ALL 167 DEBUG COLLECT CHECKS PASSED`. All five targeted mutants are killed (rc=1; diffs and logs are in `ev/m_M*.diff`/`.log`):
  - M1: `_number` predicate set back to the base's `not isinstance(value, bool)` fails the `_number keeps a value exactly when...` check (nan, inf kept).
  - M2: coordinate guard changed to `not isinstance(value, str) or numeric(value)` fails the `clean_value nulls a coordinate...` check.
  - M3: text-record guard changed to `if True` fails the same check (inf/-inf recorded).
  - M4: `_number` changed to `numeric(value)` alone (admits text) fails `_number` and the attribute-shape check.
  - M5: text-record guard changed to `if False` fails two clean_value checks.
- Null control: with the merge base's `replay_doc.py` (1d3077736d) at the head's tests, both new checks fail (`ev/null_base.log`): `_number` keeps nan/inf, and the coordinate drop list is `['north']` only.
- Enumeration rule (the body's grep) at the base and at the head (`ev/enum_base.txt`, `ev/enum_head.txt`). It returns lines 191, 198, 202, 205, 222, 242/245, 269 and 709 at the base. Each one is dispositioned in the body (numeric, json_decimal_places, text_ok, coordinate cut, _number, _scan_leaf). I confirmed `_scan_leaf` (line 711 at the head) writes no number.
- Side effect, verified: at the base, a coordinate given as an int past a double raised `OverflowError` out of `clean_value`. At the head it is nulled (`ev/probe_passthrough.txt`).
- Merge: `git merge-tree --write-tree origin/main ea316e99f52dfccc38c08b09a7abddf49a5297a3` exits 0, and so does the same command at `454abc83f05e3e9d290ad4e68c4e6b36eca69897`.
- `tests/structure.py`: STRUCTURE RATCHET PASSED. `closure.py select --diff <merge-base>`: `MODE: SCOPED -- 15 script(s) run, 19 scoped out`, matching the body's figure.
- VERSION, the manifest and RELEASE_NOTES are untouched. No golden or claim file is touched.
- The four pins in `ea316e99f52dfccc38c08b09a7abddf49a5297a3` (anchors `_number BOOLOP fe369c32`, `_number GUARD_OFF fe369c32`, `clean_value GUARD_OFF 07dca257`, `clean_value GUARD_OFF e56b82c3`) match the body's four `## Unpinned sites`.
- The finder's harness (`probes_p2.py` at 872510cd3e) was not re-run by this seat. The body's base/head/perturb figures for it are not verified here.
- CI, classify, carry and merge-tree output: `ev/ci_carry_merge.txt`.

Note: root-cause-unanswered: the owed red `gate` at `454abc83f05e3e9d290ad4e68c4e6b36eca69897` is not named under the body's `## Red checks`. Its failing lane is `tests / mutation`, which the body does answer, so the note is paperwork.

## Findings

- Residual: `_entry_shape` passes a number unchanged, so `_keep_keys({'min_temp': nan, 'max_temp': inf}, ..., _entry_shape)` keeps `nan`/`inf` in the sanitised entry data and options (`ev/probe_passthrough.txt`). This is outside the claim's stated set ("every number coercion", the grep), because it is a pass-through, not a coercion. Reachability is unmeasured: entry data and options come back from HA's JSON store. Carry: dismissed: outside this PR's stated set and not shown reachable from a persisted config entry; a later replay_doc sweep may measure it
