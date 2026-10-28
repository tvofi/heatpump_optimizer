Fix review: blocked 75ae7b26ff81949586a3c3053a9f0542819a39b3 root-cause-detectable: tests / fast (3.14) -- tests/card.mjs FAILs "inputs.py publishes problem codes the card can be enumerated against" (7 codes, implausible gone) because this round moved `reading.problem = "implausible"` into `_set_problem(reading, "implausible")`; node tests/card.mjs (118 s in CI) would have shown it before the handoff, the body lists it as not run, and pr-contract refuses the unnamed red
bus-nonce: e3fa8d4a93be38d0b6101c80041be596

# Fix review -- PR #2873, R10-DIAG-AGES, round 4

This is the fourth round. The body carries a `## Re-cut` note, as `fixer.md` requires past three
rounds.

Reviewed head: `75ae7b26ff81949586a3c3053a9f0542819a39b3`, the head this review was dispatched at.
It is the authored code head `c4c29bf10` plus a merge of main `9c9cd0d2d`. I worked in a detached
worktree at that head (`ev/head.txt`). Merge base: `9c9cd0d2d`.

- `git merge-tree --write-tree origin/main <head>` exits 0.
- `dev/governance/roles/` has no diff between the merge base and main.

**The head moved during the review.** At 05:07:18Z `mutation-autofix` pushed `f77650fc5` ("ci: pin
killed mutants"). It adds one file, `tests/mutation_ledger/killed_by/inputs.py/_set_problem.GUARD_OFF.de541d53.json`.
The body predicted this pin under `## Unpinned sites`, and `ci-autofix.md` says to wait for this
commit. The fixer did not move the head.

All my figures survive the move:
- `inputs.py` and `tests/card.mjs` have the same blobs at both heads.
- No production or test file differs between the two heads.

The block below holds at `f77650fc5` too. CI there was still running when I posted.

## What round 3 asked, and what this round did

**1. Kill N1.** Round 3's mutant replaced `_over_age`'s implausible exception with `True`. The new
check kills it. My driver (`ev/mutants_r4.py`, built by me, on a copy of the head tree, run against
`tests/debug_collect.py`) gave these RESULTs (`ev/mutants.txt`):

| mutant | result |
|---|---|
| NULL | `ALL 158 DEBUG COLLECT CHECKS PASSED` |
| N1 (`not in OUTRANKS_STALE` -> `True`) | 2 of 158 FAILED: the implausible-past-limit check and the census re-read. **Killed.** |
| N1b (`OUTRANKS_STALE = frozenset()`) | 2 FAILED. Killed. |
| N4 (`_set_problem` drops `or problem in OUTRANKS_STALE`) | 1 FAILED, the census. Killed. |
| N2, round 3's | 2 FAILED. Killed. |
| N3, round 3's | 6 FAILED. Killed. |
| N5 (`_set_problem` guard -> `if True`: every class overwrites `stale`) | **Survives** `debug_collect.py` (158 passed). |

On `tests/features.py` (`ev/n4f.txt`, `ev/n5f.txt`):
- N5 is killed: "a refused flow reading's health record keeps its reason by one precedence" reads
  `implausible`.
- N4 is killed by the same check, reading `stale`.
- The `recorded_at = 'unknown'` FAIL appears in my NULL run as well. It comes from the copy having
  no `.git`.

**2. Null control.** The same entry exported inside its limit reads `implausible`, `stale_inputs
[]`, `1 missing` in the suite. I see the same in the landed harness's R9 NULL rows at both ends.

**3. The ordering.** This round addresses age-gate-before-implausible by precedence, not by
reordering. `inputs.OUTRANKS_STALE` is applied in `_set_problem` past the age gate (`inputs.py:137-140`),
and `_over_age` reads the same constant. The landed harness shows the reader-side defect it fixed:

- RESULT base `R9.flow_negative.read_past_limit: stale`; head: `implausible`.
- RESULT the temperature arm reads `implausible` at both ends, and both NULL rows read `implausible`.

Class open: I enumerated every `.problem =` and `_set_problem(` site in `inputs.py`.

- Every content class set past the age gate either goes through `_set_problem` (implausible, and
  flow's unknown_unit) or guards on `problem is None` (unknown_value, not_boolean, power's
  unknown_unit). That matches the stated rule: only OUTRANKS_STALE outranks stale.
- The census asserts this literal set by `ast`. No open seam.

**4. The harness.** It is landed and classified. `dev/audit/harnesses/r10_diag_ages_export.py`
appears in `tests/closures.json` under `tests/harness_headers.py`'s `inert_reads`, beside its
`r10_*` neighbours (`ci_predict --apply-inert`). `tests / closures` is success at this head
(122634417120).

I ran it unchanged at both ends (`ev/harness-landed-{base,head}.txt`):
- RESULT R1-R8 equal the round-1 reviewer's copy line for line at both ends. The only difference is
  `checks: 27` -> `34`, which is R9's lines. The landing changed nothing.
- RESULT R9's export arm `implausible_exported_past_limit` reads `implausible` at both ends. Under
  N1 it reads `stale`, `["flow"]`, `1 stale`, so the harness also detects the round-3 mutant.

## Block: `tests / fast (3.14)` is red, caused by this diff, and unanswered

All workflows at this head had concluded by 05:17:04Z (`ev/check-runs-75ae7b26f....txt`): 35
success, 13 skipped, 7 failure.

**The red.** `tests / fast (3.14)` (122634417080, `MODE: SCOPED -- 27 script(s) run`) failed on
`node tests/card.mjs` (`ev/job-122634417080.log`, line 17509):

```
FAIL  inputs.py publishes problem codes the card can be enumerated against
      missing_entity,unavailable,stale,not_numeric,unknown_value,not_boolean,unknown_unit
```

**The cause is this round's commit `a3a4a78c9`.**
- `tests/card.mjs:12058` enumerates the published codes with `/reading\.problem = "(\w+)"/g` and
  needs at least 8.
- This round replaced `reading.problem = "implausible"` with `_set_problem(reading, "implausible")`.
  Implausible dropped out of the census, leaving 7.
- The base has 10 such literals, including implausible.
- So the card's "every published problem code has words in en / sv-SE" checks have stopped covering
  implausible. The coverage is lost quietly, and the floor check is the only thing that went red.

**Control, run locally** (`ev/card-{head,base}.txt`): the check FAILs at the head with the same 7
codes, and is `ok` at the base. Both local runs later abort with node rc 134, which is this
machine's problem, not the tree's. CI's run is authoritative.

**The cheaper detector** is `node tests/card.mjs` after `tests/plan_view.py`: 118 s in CI's lane.
The body's `## Red checks` lists `tests/card.mjs` under "Not run locally at this head, left to CI's
heavy runs". The fixer's own census (`debug_collect.py`) asserts inputs.py's class literals by `ast`
and was updated, but the card's regex census was not.

**The body does not name this red.** `pr-contract` refuses on it twice: 122644704843, and
122645950269, which started at 05:15:39Z after the last red concluded. The refusal reads "check
`tests / fast (3.14)` is red and `## Red checks` does not name it." `gate` is red on it
(122645294082, 122646219172).

**Other reds at this head:**
- `tests / mutation` (122634276677): `ADDED UNPINNED inputs.py:139 GUARD_OFF`. The body answers it by
  naming it under `## Unpinned sites`, and `mutation-autofix` pinned it in `f77650fc5`.
- `tests / nightly-status`: main's record-autofix 403 (run 40595637258). It is not this PR's,
  because the diff touches no file that nightly-status reads.

Repair:
1. Make the card's code census see codes set through `_set_problem`. For example, widen
   `card.mjs`'s regex to `_set_problem\(reading, "(\w+)"` and the conditional form, or derive the
   codes from `OUTRANKS_STALE` / `PROBLEM_WORDS`. Show the census listing `implausible` again, and
   both word checks covering it.
2. Run `node tests/card.mjs` before the handoff.
3. Name and answer the `tests / fast (3.14)` red under `## Red checks`, with the cheaper detector
   above.

## Other checks

- RESULT the three-dot diff touches no `VERSION`, no manifest, no `RELEASE_NOTES.md`, no
  `tests/golden/` and no claim file.
- RESULT `tests/structure_budgets.json` moves only down: `class_excess_loc` 18044 -> 18043 and
  `max_class_loc` 8167 -> 8166.
- The deleted `killed_by` pin (`read_flow_kg_s.GUARD_OFF.1d38d74f`) is earned. Its line no longer
  exists, and the guard now lives in `_set_problem`, which the bot re-pinned.

## Findings

- F1 (round 3, mutation-vacuous): repaired. N1 is killed by the new check, the null holds, and the
  harness detects it. Carry: dismissed: verified repaired
- F2 (round 3, harness not landed): repaired. The harness is landed, classified, and runs unchanged
  at both ends. Carry: dismissed: verified repaired
- F3 (blocking, root-cause-detectable): `tests / fast (3.14)`, from `tests/card.mjs`'s
  problem-code census, as above. Carry: dismissed: blocking; this PR's next round owes the repair
- F4 (non-blocking): N5 (`_set_problem` always overwrites) survives `debug_collect.py`. Only
  `features.py`'s flow pin kills it. That is adequate, since one killing check suffices, but the
  export census does not see it. Carry: dismissed: killed by tests/features.py

Evidence: `ev/` (head.txt, check-runs at `75ae7b26f` and `f77650fc5`, the CI logs, the mutants and
their driver, harness both ends, card head/base). The mutant driver is mine. The harness is the
round-1 reviewer's, as landed.
