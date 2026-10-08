Fix review: blocked 8e0dcb72c8f8379926e075f83823a0e0549e3b2d class-open: fixer.md 17 states three rules the tree breaks routinely (constants in const.py: 531 module constants outside it; no module-level state: 9 sites, body names 2; "the rest is pure": store/network/notify/issue-registry edges) and names no exception, so step 15 blocks ordinary fixes

bus-nonce: c020eae857b6904b428a7f2666216b33

Round 1. Measured head 8e0dcb72c8f8379926e075f83823a0e0549e3b2d (merge base 4dbe5aace), from a detached worktree. Live head re-read at 2026-10-08T21:58:36Z: unchanged. Evidence: /Users/timmalmstrom/hpo-seats/review-2064/evidence.

## RESULT lines

- RESULT policy_lint (CI venv) rc=0; `--budgets` rc=0: fixer.md 310/310 lines and 5109/5109 tokens (at its raised cap); role fixer ~6219 against cap 5852 plus a 500 band (6352).
- RESULT rules_sync --check: RULES-SYNC ok. RESULT brief_lint rc=0. RESULT structure.py: STRUCTURE RATCHET PASSED.
- RESULT check-wave-script.mjs: 172 passed, 0 failed. `VERDICT_RE` accepts `architecture-unsound` (`[a-z][a-z0-9-]*`), and `VERDICT_CLASSES` routes it as itself. policy_lint and friction_issues read `VERDICT_CLASSES` from the wave file. bus.sh `--self-test`: 45 checks, 0 failed (grammar `[a-z-]+`).
- RESULT merge_train.py `--self-test`: NOT RUN. It died with ENOSPC because the host disk was full (119 MiB free). The diff does not touch it, and it reads only `Fix review: merge` lines, so the new class gives it nothing new to parse.
- RESULT entities.py locally with tests/hastub: rc=1, failing only `a3:roster` and `a3:orjson`. Both need real HA, and the diff contains no Python. I rely on CI's `fast (3.14)` result instead, which passed at this head.
- RESULT the mutation proof is not re-run as a separate step. check-wave-script's taught-class check is the arm that fires, and it is ok with the entry present.
- RESULT VERSION, the manifest and the notes heading are untouched (6 files: 3 role/CLAUDE docs, budgets, the wave file).
- RESULT check-runs at the head (40 runs, all concluded by 21:53Z; `coverage` passed; `pr-contract` started at 21:00:13Z, after the last red concluded at 20:59:35Z): `budget-raise-gate` is red, and the body answers it (a raise held for tvofi's review, 0013). `nightly-status` is red. It is not this PR's, because the diff does not reach what it reads. No other red.

## Why blocked: rules false to the tree, with no named exception

Step 17 says "Sound, for new code (the body names each exception it keeps)", and the new step 15 blocks "a breach the body does not name". The body's `## Approval` enumerates exceptions for HA imports, entity reads and actuator writes. For three other rules the tree's established pattern is the breach, and neither the policy nor the body names it (`evidence/tree_checks.txt`):

1. **"constants in `const.py`"**: there are 531 module-level UPPER_CASE assignments outside const.py. The rule was `^_?[A-Z][A-Z0-9_]+\s*(:[^=]+)?=`, with const.py excluded. Examples: optimizer.py 24, sysid.py 23, defrost.py 15 (its `STORE_VERSION` included). The codebase keeps a concept's constants beside their owner. Read literally, the rule makes a new `_MAX_ITER` in optimizer.py `architecture-unsound`. It also contradicts the same list's "one owner per concern" and "the existing mechanism, never a parallel one". The rule tvofi gave was "units in names and constants in const.py". A wording true to the tree would scope it to shared and configuration constants, or to constants used by more than one module, with module-private tuning constants staying beside their owner.
2. **"no module-level state"**: there are 9 sites. The body names 2 (`boost._cold_lease`, `coordinator._PROCESS_WORKER`). It omits `boost._STATES`, `boost._PLAN_BASES`, `pump_arbiter._STATES`, `debugger._COLLECTORS` (the per-coordinator `WeakKeyDictionary` side-table pattern), `coordinator._FENCED_CAUSES`, `coordinator._WORKER_FALLBACK_CAUSES` and `store._NEWER_ON_DISK`. The side-table pattern is how state stays off the coordinator class, which `attrbag_classes_over_30` measures. So this rule pulls against the ratchet and against "reuse existing patterns", and the text does not resolve the conflict.
3. **"entity reads through InputReader, actuator writes from the coordinator or pump_arbiter.py; the rest is pure"**: the allowed side effects are entity reads and actuator writes only. Store I/O (store.py), network (open_meteo.py), notifications (notifier.py) and the issue registry (legionella.py, repairs.py) are edges the list does not cover. Read literally, a new store write or notification is a breach. tvofi asked for "side effects at the edges", which names the shape, not two permitted kinds.

Step 6's rule for class openness applies: the body states one enumeration rule (the HA-import grep), but its issue states eight rules. The seams that rule does not reach are the three above.

## Further points the repair owes (not separately blocking)

- **Exceptions live only in the PR body.** Step 15 reviewers read `fixer.md`, not #2064's body. Either put the known-exception list (or "existing code is not a breach; only lines the diff adds are judged") in step 17, or say in step 15 that the reviewer judges added lines only. As written, "a breach the body does not name as a kept exception" invites a block on any fix that touches dhw_learning.py or coordinator.py.
- **"Where minimal and sound conflict, ask the orchestrator"**: no "minimal" rule exists anywhere in the policy corpus (0 hits). The clause it replaces, "scope and the ratchet still bind (below)", was cut without being listed among the payments. Name the scope rule it means (the preamble's ~400-production-line group cap), or keep the cut clause.
- **The binding architect design note has no consumer.** orchestrator.md section 5 says concurrent fixes "push only after a binding architect design note". No role contract defines the architect, the note has no location, and neither fixer.md 17 nor fix-review.md 15 tells the fixer to follow it or the reviewer to block on a departure from it. tvofi's ruling is that the orchestrator dispatches the note, and the text should say so. "Binding" needs one clause in step 15, for example: "a departure from the group's architect note is `architecture-unsound`".
- **"the store's versioned migration (at most one per release)"**: tvofi's list does not contain this, and nothing in the tree backs it. Either cite its source or drop the parenthesis.
- **"D7 and archscore held"**: "held" is unmeasured next to a raise path that permits a move. Say "not regressed, or the raise path".

## Payments and the budget

The raise is minimal: both new caps equal the measured values (310 lines, 5109 tokens). These payments are sound:
- the step 6 "Coordinator" gloss, because step 17 now names `coordinator.py` in code font;
- #714's line-number sentence, which fixer.md step 9 covers ("never a bare line number");
- the orchestrator role list, which duplicates CLAUDE.md;
- the clause restating root-cause.md in fix-review step 11.

The fix-review step 12 cut ("Step 7 checks the body's SHA ... live head at posting time") removes the only text that distinguishes step 12 from step 7. It is defensible but not a pure restatement. One payment is not listed in the body: "scope and the ratchet still bind (below)" (see above).

## #2063 overlap: not a block, but the PR that merges second owes this

`git merge-tree` of #2064 onto main plus #2063 (f118161) conflicts only in `dev/governance/config/policy_budgets.json`, on the adjacent fix-review.md and fixer.md cap lines. fix-review.md, orchestrator.md and web-fix-wave.js merge textually, and the merged step 11 reads coherently. After the obvious resolution (fix-review 141/2449 from #2063, fixer 310/5109 from #2064), `policy_lint` fails with one error: fix-review.md is at about 2454 tokens against #2063's cap of 2449. So whichever PR merges second must recarry the budgets file, and must either pay 5 more tokens in fix-review.md or raise its `files_tokens` cap to 2454. A raise sends that PR back through budget-raise-gate.
