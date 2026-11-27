Part 2 of 2 of R11-SEAM-store (the persisted store seam), roster group R11-SEAM-store-p2. Refs #3744, #3757, #3758 (left open). Part 1 merged as #3875.

Carry 0 (P1 sweep, six store loaders admitting a stored boolean as a number) is built once, at the store's load boundary. `QuarantiningStore.async_load` walks each document against its `DOMAINS` trie (`store._unflag_numbers`) and reads a `bool` as `None` wherever the declaration declares a number. `None` is the absent value every loader already defaults. No loader is patched.

**Review answer (review/3932 at 959ce0d0, blocked aa1bb8d34c class-open on `accuracy/lead_pending/#/1`).** The axis is "declarations that declare a number". At aa1bb8d34c the rule for it was the kind alone (`real`/`int`), so a `choice` among numbers (`LEAD_BUCKETS`) fell outside it. `in_domain` admitted `true` there (`True in (1.0, ...)`), and `AccuracyTracker.from_dict` read it as a 1-hour lead. This head names the set by one rule and closes both halves:
- `store._declares_number(domain)` returns true for a `real`, an `int`, or a `choice` whose members are all numbers that are not flags (each member passes `_number` against an unbounded real). `_unflag_numbers` reads that predicate, not the kind.
- `_KINDS["choice"]` compares a flag only with a flag member (`v == m and isinstance(v, bool) == isinstance(m, bool)`). `in_domain` therefore refuses `true` at a numeric choice, which makes the docstring's claim true. No choice in `DOMAINS` has a flag member, so no declared value changes domain.
- The census in `tests/features.py` places every `DOMAINS` declaration by that rule, from the declaration's own content: numeric (real, int, choice of numbers), flag, or other (text, instant, day, month, a choice of no numbers). It refuses a declaration it cannot place, such as an unknown kind or a choice mixing numbers with other members, so a new kind is classified before it can be skipped. It drives a stored `true` through a `QuarantiningStore` load at every placed declaration, requires `in_domain` to refuse it at each numeric one, loads a numeric choice's member as stored, and asserts that it drove each numeric kind (real, int, choice).
- The six-loader check also reads the accuracy tracker's `lead_pending` through `_async_load_accuracy`, with a stored `true` lead beside a stored 3.0.
- The optional note is taken: `_tries()` is `functools.cache`d. `DOMAINS` is fixed at import, and no reader writes the trie: its only writer is `_tries` itself, and no test rebinds or mutates `DOMAINS` (a tree-wide search for an assignment to it found none).

The quantified sets and their rules:
- Declarations that declare a number: the census's placement rule above, whose output is the numeric row set. Residue, by category: a map key (`~`) is JSON text and never a flag; an alias pattern mirrors a store whose own patterns are driven.
- Stores: every `DOMAINS` table, through `QuarantiningStore`. The review verified that no plain `Store(` is constructed outside `store.py`.
- Values read as absent: `bool` only, Python's one type that is also an `int`.

Alternatives for the choice half:
- **Only refuse a flag in `_KINDS["choice"]`, and leave `_unflag_numbers` on the kind.** This makes `in_domain` right, but the load still passes the `true` to `from_dict`, because the load reads off-domain values only to log them. It does not close the defect.
- **Special-case `lead_pending` in `AccuracyTracker.from_dict`.** This is a per-loader patch, which the carry refuses, and it leaves the next numeric choice open.
- **The predicate plus the choice check (taken).** One rule names the set, both the load and `in_domain` read it, and the census enumerates it.

Carry 1 (P2 sweep, three DHW weekday/weekend window readers) is already on main, by R11-SEAM-entity-service (865dff33d6, dbaf42a411). All three readers resolve the day through `dhw_schedule.windows_in_force`, the registered owner of `tests/entities.py`'s P2 fact `dhw_window_in_force`, and `tests/features.py`'s D17-s3-51 block pins them. This PR adds no P2 code.

Carries 2-4 (D3 wave fold, class I1, #3755) were re-derived with `d3_fnstate.py` on `D3-FOLD.json` (both at e8aefbb452). D3-g03 and D3-g12 are pinned here. D3-g11 is already killed at the merge base (see `## Forward-carry`).

## Head

`acc7e11a0c365b805096e2ac5c04eea6ed3e754b`, merge base `190ffb10c230b6beaf77593b2926d55682e37f47`, origin/main `b4ebe3dcf3c9ca70854267f23c1e4c1c81c4b2e6` at 2026-11-27T06:41Z. `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict). The three commits since aa1bb8d34c are the repair. The figures from earlier rounds that this head did not re-take name the SHA they were taken at.

## Mutation proof

Each mutant was run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# R11-SEAM-store-p2 (round-11 sweep P1"`, and the line was restored afterwards. Taken at this head:
- `_unflag_numbers`: `numeric = ... and _declares_number(domain)` reverted to `domain.kind in ("real", "int")`, the pre-repair rule. 2 of 4 fail: "a stored true where a number is declared loads as absent at each of the six loaders ... and at the accuracy tracker's pending leads" (it reads `'lead_pending': [1.0, 3.0]`), and the census ("numeric kept [('accuracy', 'accuracy/lead_pending/#/1', 'choice', True)]").
- `_declares_number` GUARD_OFF (`if domain.kind in ("real", "int")` to `if False`): 2 of 4 fail, the same two checks.
- `_declares_number` choice arm deleted (RETURN_DEL), and replaced by `return False`: 2 of 4 fail each time, the same two checks.
- `bool(domain.choices) and` deleted, so an empty choice counts as numeric: 1 of 4 fails, the census ("flag or other lost"). The `choice` declarations with no members are containers, and a stored `true` there must stay.
- `_KINDS["choice"]` reverted to `v in d.choices`, and its BOOLOP (`and` to `or`): 1 of 4 fails each time, the census ("in_domain admits [('accuracy', 'accuracy/lead_pending/#/1')]").
- `_unflag_numbers` BOOLOP (`and` to `or` at `numeric`): 1 of 4 fails, the census.
- `data = _unflag_numbers(data, node)` deleted: 2 of 4 fail.

Ledger rows, hand-recorded with the earlier rounds' rule (each mutant driven against the block above and red under it): added under `tests/mutation_ledger/killed_by/store.py/`: `_declares_number.GUARD_OFF.f0bfbb47`, `_declares_number.RETURN_DEL.f3b39f1d`, `@module.BOOLOP.55969c59` (the choice check) and `_unflag_numbers.BOOLOP.f4ed69ea`. The last replaces `_unflag_numbers.BOOLOP.adb1a211`, deleted because its `old` line is gone. The other four `_unflag_numbers` rows keep their anchors. `_number` keeps its text, so its pins keep their anchors. `mutation_table.completeness_problems(load_budgets(), inventory())` returns 0 problems, and `unpinned_sites` names none of the four new anchors (the store.py sites it does name, at `_poisoned`, `_bound_instants`, `_parses`, `_number` CMP_BOUND and `_fields`, are unchanged lines that this diff does not add).

From earlier rounds, at e8aaf72e00, not re-taken (the lines are unchanged): D3-g03 BOOLOP and both D3-g12 CMP_BOUND mutants each fail their own check, and the D3-g11 patch reads `1 of 122 FINITE BOUNDARY CHECKS FAILED` in `tests/finite_boundary.py` at the merge base.

## Null control

- The census drives every `flag` declaration and every other non-numeric declaration with `true`, and requires `true` to load (122 other, 23 flag, at this head). Each numeric choice's first member (1.0) loads as stored.
- The six-loader check loads the numbers stored beside each `true` as stored: `dhw_energy_kwh` 4.0, off_restore `c` 20.5, reservoir 2.0, peak 3.0, pending lead 3.0.
- Before the fix (aa1bb8d34c plus this head's test only), the block read 2 of 4 failed. The census listed exactly one numeric declaration kept as `true`, `accuracy/lead_pending/#/1`, and the same one admitted by `in_domain`. The tracker read `[1.0, 3.0]`.
- The `_tries` cache: `_tries() is _tries()` is True with the cache and False with `_tries.__wrapped__`.

## Figures

- The reviewer's probe, `git show 959ce0d0:evidence/probe_choice.py > probe_choice.py && PYTHONPATH=tests/hastub python3 probe_choice.py` (sha1 4427ab452a3c8d89da96205da8240d78d26308f0). At aa1bb8d34c (the review's `evidence/probe_choice_head.txt`) it reads `loaded leaf: True`, `in_domain(choice, True): True`, and a lead of 1.0 in `lead_pending`. At acc7e11a0c it reads `loaded leaf: None`, `in_domain(choice, True): False`, `tracker lead_pending: []`.
- The features block, `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# R11-SEAM-store-p2 (round-11 sweep P1"`: `ALL 4 FEATURES BLOCK PASSED` at acc7e11a0c. The census's row counts are printed in the check's detail field on a failure, by the rule above.
- `_tries` cost, `timeit` over 200 calls of `store._tries.__wrapped__` against the cached `store._tries`: 0.325 ms per uncached build, against 6e-05 ms per cached call, on this seat at acc7e11a0c (one build per store load before the change).
- Scoped gate: `python3 tests/closure.py select --diff 190ffb10c2` reads `MODE: SCOPED -- 23 script(s) run, 11 scoped out`. Each named script was run with `PYTHONPATH=tests/hastub`, golden under `GOLDEN_MODE=drift` against the merge base, plus `tests/env_drift.py --claims-only`: all 23 rc=0 at acc7e11a0c, claims hygiene ok. A first run at 11255468a9 read `tests/doc_claims.py` 1 of 445 failed (the comment ratchet refused one docstring sentence over 40 words in `store.py`); acc7e11a0c splits it, and that run was stopped before it finished.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at acc7e11a0c.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 190ffb10c230b6beaf77593b2926d55682e37f47` reads `Architecture score: dS +0.0000 NULL` at acc7e11a0c.
- P1 end-to-end companion at a0b598938d (earlier round, not re-taken): `PYTHONPATH=tests/hastub python3 $EXPORT/p1_e2e.py` (sha1 d909bdfa07d900189a5e4bbf00226602a64a5eaf) reads `RESULT stored_true_read_as_one=6 of 6` at 7194ff84c0 and `0 of 6` at a0b598938d. Its six loaders do not include `lead_pending`, which the in-tree block now drives.
- In-tree finder harness: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_probes.py` reads `store_bool_admitted_as_number=6 of 7` at both ends (earlier round). Its store arm calls each loader with a hand-built payload, past the store load where the fix sits, so it measures what the fix rightly leaves alone. The features block applies the tree's own load to the same inputs.
- P2 companion at a0b598938d (earlier round): `PYTHONPATH=tests/hastub python3 $EXPORT/p2_companion.py [--perturb]` (sha1 9f4877fd4f444bb182e71fd729209fc054f84a62) reads `RESULT companion_failed=0 of 3` at 7194ff84c0 and at the head, and `3 of 3 (--perturb)`.
- D3 re-derivation (earlier round): `python3 -I d3_fnstate.py D3-FOLD.json HEAD --group R11-SEAM-store-p2 --ids` (files at e8aefbb452) reads `same 2 changed 1 gone 0 module 0`.

## Red checks

none

## Unpinned sites

none: the four sites this repair adds are pinned by the rows under `## Mutation proof`, each driven before recording.

## Forward-carry

- D3-g11 (`_learned_pair` CMP_BOUND, `value > 0` to `>= 0`) is already killed at the merge base, so it returns to the judge as a non-finding (ADR-011 decision 4). Carry: dismissed: killed at the merge base by tests/finite_boundary.py, ledger row _learned_pair.CMP_BOUND.26881a60
- The in-tree P1 harness's store arm (`p1_probes.py` `arm_store_bool`) calls loaders past the store load, so a re-run reads 6 of 7 at this head too. The features block is the rerunnable measurement. Carry: dismissed: a round's harness records its round; the features block re-measures the class

## Friction

none
