Fix review: merge 2fbc91c40c17429702fd0c44a3a80080b3157c60
bus-nonce: a6b4c34013436fe446e5e5822641f9e6

# Fix review -- PR #2873, R10-DIAG-AGES, round 5

This is round 5. The body carries a `## Re-cut` note, as `fixer.md` requires past three rounds. The
note states this pass re-cut again, deleted the earlier rounds' figures, and quotes only figures
taken at `060c9bef5`, `d05d521ff` and `d00790305`.

**Reviewed head:** `2fbc91c40c17429702fd0c44a3a80080b3157c60`.
- It is the code head `060c9bef5` plus a merge of main `0b8f8b585`.
- I worked in a detached worktree at that head (`ev/head.txt`).
- Merge base: `0b8f8b585`.
- `git merge-tree --write-tree origin/main <head>` exits 0.
- `dev/governance/roles/` has no diff between the merge base and main.
- The branch still pointed at this SHA at 16:21Z, after the 12:42Z reboot. The worktree is clean: no
  mutant was ever applied in place, because every mutant ran on a `git archive` copy.

## What round 4 asked, and what this round did

Round 4 blocked `root-cause-detectable` on `tests / fast (3.14)`. The card's census regex,
`reading.problem = "(\w+)"`, lost `implausible` when round 4 moved it behind `_set_problem`.

Round 5 makes three changes:
- The card now takes its codes from `PROBLEM_WORDS`' keys, and it refuses any class set by either
  route that is missing from the table.
- The card adds a check per language that reads `STRINGS.en` and `STRINGS.sv` directly.
- `debug_collect.py`'s `ast` census now holds `set(PROBLEM_WORDS) == found - {"not_configured"}`.
  It used to hold `<=`.

`PROBLEM_WORDS` gains `"stale": "stale"`. This moves no output: `describe_problem`'s fallback
already rendered `stale` as itself. The repair is sound and has one owner. The `ast` census is
route-complete, and the card inherits that rather than restating the routes.

## Failing first, and passing at the head

All runs use `PYTHONPATH=tests/hastub`. Card runs use `NODE_OPTIONS=--max-old-space-size=8192`
and run `tests/plan_view.py` first.

| run | at `d05d521ff` (tests only) | at the head |
|---|---|---|
| `tests/debug_collect.py` | `1 of 158 DEBUG COLLECT CHECKS FAILED`: the precedence census, symmetric difference `['stale']` | `ALL 158 DEBUG COLLECT CHECKS PASSED` |
| `tests/card.mjs` | `1 CARD CHECK(S) FAILED`: `FAIL inputs.py publishes problem codes the card can be enumerated against`, detail `implausible,missing_entity,not_boolean,not_numeric,unavailable,unknown_unit,unknown_value \| set but not in PROBLEM_WORDS: stale` | `ALL CARD CHECKS PASSED` |

Evidence files: `ev/debug_collect-{tf,head}.txt` and `ev/card-{tf,head}.txt`. The fixer's
failing-first reading reproduces exactly.

## Mutation proof

The driver is `ev/kmutants_r5.py`, which I built. It runs on a `git archive` copy of the head and
runs both suites. The seven `FAIL a16:*` planted controls are excluded from the counts. Results are
in `ev/kmutants.txt` and `ev/kmut/*.log`.

| mutant | `tests/card.mjs` | `tests/debug_collect.py` |
|---|---|---|
| NULL | `ALL CARD CHECKS PASSED` | `ALL 158` |
| K1: `implausible` deleted from `PROBLEM_WORDS` | 1 FAIL: the census | 3 of 158: the census, the implausible-past-limit check, its null |
| K2: sv `health.p_implausible` deleted | 1 FAIL: "... own words in the card's sv table" | `ALL 158` |
| K3: en `health.p_implausible` deleted | 2 FAIL: the en table check, and "... words in en, none prints as a raw token" | `ALL 158` |
| K4: `stale` deleted from `PROBLEM_WORDS` | 1 FAIL: the census | 1 of 158: the census |
| K5 (mine): sv `health.stale` deleted | 1 FAIL: the sv table check | `ALL 158` |
| K6 (mine): `PROBLEM_WORDS` gains an unpublished `"bogus"` | 4 FAIL: both table checks, both render checks | 1 of 158: the census, equality from the other side |
| K7 (mine): sv `health.p_implausible` set to whitespace | 1 FAIL: the sv table check (`.trim()`) | `ALL 158` |

K1 to K4 agree with the body's table row for row. I wrote K5 to K7 to attack the parts the body's
mutants did not reach:
- the special key for `stale`;
- the reverse direction of the new equality;
- the blank-string guard.

Every one is killed.

**Round-4 mutants.** I re-ran the round-4 reviewer's `mutants_r4.py` unchanged; its sha1
`b301586de6ee1853778ea9be51a4c95d7b82d45d` matches `rev-r4/2873/ev`. It ran on the same archive copy
(`ev/mutants_r4-results.txt`).

| mutant | `tests/debug_collect.py` |
|---|---|
| NULL | `ALL 158` |
| N1 | 2 of 158 |
| N1b | 2 of 158 |
| N2 | 2 of 158 |
| N3 | 6 of 158 |
| N4 | 1 of 158 |
| N5 | `ALL 158` |

On `tests/features.py`:
- N4 is killed: `FAIL a refused flow reading's health record keeps its reason by one precedence ...`, reading `stale`.
- N5 is killed by the same check, reading `implausible`.
- NULL fails only on `recorded_at = 'unknown'`, which is present in all three runs. It comes from the
  copy having no `.git`.

This is identical to round 4.

## The harness: the finder has none, and the reviewer-built one is landed

Issue #2814 ships no committed harness. `dev/audit/harnesses/r10_diag_ages_export.py` is disclosed
in its header as reviewer-built: arms R1 to R8 come from the round-1 reviewer, and R9 from the
round-3 fixer. I ran it unchanged at the merge base `0b8f8b585` and at the head
(`ev/harness-{base,head}.txt`).

- Both ends print `RESULT checks: 34` and 36 `RESULT` lines, with rc 0.
- Leaving out the `RESULT tree:` line, both ends equal the round-4 reviewer's landed-harness output
  line for line (`rev-r4/2873/ev/harness-landed-{base,head}.txt`).
- At the base: `R1.input_ages_minutes.exported_14min_late {'indoor': 2.0, ...}`, `R3 plan_stale False`, `R9.flow_negative.read_past_limit: stale`.
- At the head: `16.0` / `True` / `implausible`.

So round 5 moves no export, as the body claims.

## Class and seams

I re-ran the body's enumeration:

```
git grep -n -E 'reading\.problem = |_set_problem\(reading|PROBLEM_WORDS|p_\$\{' -- tests custom_components/heatpump_optimizer/www
```

It returns 9 lines (`ev/seam-grep.txt`), the same 9 the body dispositions.

I also looked outside `inputs.py` for any other module that sets a class:

```
git grep -E '"problem":\s*"|\.problem = |problem=\s*"' -- custom_components
```

This finds only `diagnostics.py:183`, which promotes to `stale`. `stale` is in the table. No seam is
open.

## Claims, versions and budgets

- `VERSION`, `manifest.json`, the heading of `RELEASE_NOTES.md` and both claim files have no diff
  against the merge base.
- The branch touches no card JS and no golden.
- `tests/structure_budgets.json` moves only down: `class_excess_loc 18038->18037` and
  `max_class_loc 8161->8160`. No budget is raised.
- I did not run `env_drift.py --all`. This round's production change is one dictionary entry that
  changes no output. The CI golden lanes at this head are green.

## Checks at the head

There were 55 check-runs at the head, all concluded (`ev/check-runs-2fbc91c40....txt`). None is red.
- `tests / fast (3.14)` is success (122786477441).
- `gate` is success (122800843341 and 122801953196).
- `pr-contract` is success (122800460358 and 122801625195). Both started after every other run had
  concluded, so `pr-contract` is the evidence that the body was checked.
- `tests / mutation` is success (122786310148). Its log ends `MUTATION TABLE PASSED`, with no
  `INCONCLUSIVE` and no `ADDED UNPINNED` (`ev/mutation.log`).

The body's `## Red checks` section answers each earlier red:
- `tests / fast (3.14)` at `75ae7b26f`: cheaper detector `node tests/card.mjs`. The `debug_collect.py`
  census is now the 2 s detector for the class.
- `pr-contract` and `gate`: the consequence of the unnamed red.
- the mutation `ADDED UNPINNED`: pinned by autofix.
- `nightly-status`: main's.

## Non-blocking notes

- `## Head` and `## Figures` quote the merge base `edd7e0e14`, and `origin/main` as `6349205b6`. The
  orchestrator's merge of main `0b8f8b585` then made `0b8f8b585` the merge base. The figures I
  re-took at the new base agree. The `## Head` paragraph names the current head and that merge.
- `card_mutants.sh` and `census-probe.txt` are out of tree and are the fixer's. I verified the figures
  they produced independently here, as recorded above.
