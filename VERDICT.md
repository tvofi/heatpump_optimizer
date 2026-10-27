Fix review: merge 3522cd92564309ba64ba08c9bcf5101ccd8f1b8b
bus-nonce: 0f5534bb89c2f503ca5a592771b934a5

Round 2 of #2745. Reviewed only `4522d46b0` and `6d526cfdc` (`ledger.py`
+7/-5); the r1 `merge` at `4bf7c2eaa` does not cover them. Measured head
`3522cd92564309ba64ba08c9bcf5101ccd8f1b8b`.

## The tree is the measured code head
`git diff 6d526cfdc 3522cd925` is empty: the head's tree is the measured code
head's. Branch-side commits in `4bf7c2eaa..3522cd925` that are not reachable
from origin/main are exactly the two fixes; the other 195 changed paths are
main's delta (`git log --name-only 4bf7c2eaa..524c1896b` explains 196 paths;
end-diff paths minus those minus `ledger.py` is empty).

## The check, at every end (`python3 -I tests/finite_boundary.py`)
- `4bf7c2eaa`: `ALL 106 FINITE BOUNDARY CHECKS PASSED`. The census does not
  exist at this head (`_finite_float_census` occurs 0 times), so the old end
  cannot see the defect — which is why the r1 head was green.
- `02a28aed1` (the merge-forward that brought main's census beside the pre-fix
  code): `1 of 108 FINITE BOUNDARY CHECKS FAILED`, and the failing line is
  `FAIL every finite-float coercion is const.finite_float or a dispositioned
  site, and the census reaches the owner and a planted sibling (D7-s2-58)
  [stray=['ledger.py::coverage_factor'] stale=[] owner_found=True
  plant_found=True]`. This is the mutation proof: the pre-fix production line
  against the same census check, failing on the named seam.
- `3522cd925`: `ALL 108 FINITE BOUNDARY CHECKS PASSED`.

## Mechanism, re-derived from the rule (items 1 and 5)
`_finite_float_coercers` matches a module-level function returning `float` or
`float | None` with at most two positional parameters and a builtin `float()`
call under an `isinstance` test or in a `try` catching ValueError/TypeError.
The finder's harness `dev/audit/harnesses/r10_finite_float_census.py` applies
that rule: `RESULT coercers=2` at `02a28aed1` (`const.py::finite_float`,
`ledger.py::coverage_factor`), `RESULT coercers=1` at `3522cd925`
(`const.py::finite_float`). The fixed read is `finite_float(entry.get("sum"),
0.0)`; a `finite_float(...)` Call has `func.id == "finite_float"`, so the
rule's `calls_float` does not match it.
The `int()` blind spot, controlled both ways on the head's `ledger.py` text in
one process: reverting only `int(finite_float(...))` to `int(entry["count"])`
still returns no `coverage_factor`; reverting only `settled` to
`float(entry["sum"])` returns `ledger.py::coverage_factor`. So the two `int()`
counts are guarded by the fix's own decision, invisible to the census — the
claim in `6d526cfdc`'s body, re-derived.

## Bad inputs (item 2), reviewer-built harness `bad_inputs.py`
Old head is the null control: the numbers move, so the harness is not vacuous.
`fallback` = exactly `pro_rata_factor(NOW)` (2.8); `scale` = the covered figure.

| input (settled_hours entry)      | old 4bf7c2eaa | new 3522cd925 |
|---|---|---|
| entry None                       | 2.8 fallback  | 2.8 fallback  |
| entry not a dict (list)          | 2.8 fallback  | 2.8 fallback  |
| entry not a dict (str)           | 2.8 fallback  | 2.8 fallback  |
| missing `sum`                    | KeyError      | 2.8 fallback  |
| `sum` non-numeric "warm"         | ValueError    | 2.8 fallback  |
| `sum` = "nan"                    | 2.8 fallback  | 2.8 fallback  |
| `sum` = "inf"                    | 1.0 OTHER     | 2.8 fallback  |
| `sum` = float("inf")             | 1.0 OTHER     | 2.8 fallback  |
| `sum` = True                     | 672.0 OTHER   | 2.8 fallback  |
| `count` missing (spot absent)    | KeyError      | 28.0 scale    |
| `count` missing (spot count 24)  | KeyError      | 2.8 fallback  |
| `count` "nan" (spot absent)      | ValueError    | 28.0 scale    |
| `count` "nan" (spot count 24)    | ValueError    | 2.8 fallback  |
| spot entry None / not a dict     | 28.0 scale    | 28.0 scale    |
| spot missing `count` / "nan"     | KeyError/ValueError | 28.0 scale |
| whole `meta` is None             | AttributeError | AttributeError |

`whole meta is None` is unchanged at both ends and out of the fix's stated
scope (`meta` is typed `Mapping`; `None` is a caller contract breach).

## The fallback is the right fallback (item 3)
The finder's committed `dev/audit/harnesses/r10_savings_upgrade_month.py`,
run at both ends, is flat at every arm — old then new:
`upgrade 2.800/2.800`, `null 28.000/28.000`, `fresh 2.800/2.800`. The `null`
arm is a genuinely covered month and reads the settled scale 28.0 at both
ends; `upgrade` (coverage lost mid-month) and `fresh` (no coverage) read
`pro_rata_factor` 2.8 at both. In `bad_inputs.py` every fallback row is
asserted equal to `pro_rata_factor(NOW)` exactly, not judged by eye.

## Every admitted value is unchanged (fix1's claim, controlled)
`admitted_grid.py` enumerates 200 cells over exactly what `_clean_month`
admits (`sum` finite, `count` int >= 1, but bools and non-finite dropped
before the function): 10 sums x 4 counts x 5 spot counts. The two ends'
outputs diff to 0 lines. The bad-input table is the perturbation that keeps
the flat grid from being vacuous: the ends differ on unadmitted inputs.

## Nothing else moved in ledger.py (item 4)
The end-to-end diff is three hunks: the `from .const import finite_float`
import (fix1); the docstring clause (fix2, documentation only); and the three
reads, where fix2 rewrote the `settled` line fix1 had written
(`entry["sum"]` -> `entry.get("sum")`). That is why the two commits total
+7/-5 but the end diff is +6/-4. `month_hours`, `pro_rata_factor`,
`savings_pct` and the comparison and return lines are untouched; main did not
touch `ledger.py` in the merged window (`git log 4bf7c2eaa..524c1896b --
ledger.py` is empty).

## Hygiene
- `VERSION` (7.0.4), the manifest and `RELEASE_NOTES.md` are untouched by the
  branch delta; no `tests/golden` path moves between the two ends, so these
  commits owe no claim. The branch's pre-existing `claimed_drift.txt` entry is
  unchanged here.
- `git merge-tree --write-tree origin/main 3522cd925` exits 0 — no conflict;
  `mergeStateStatus: BLOCKED` is not a conflict.
- Forward-carry: `dev/programme/rosters/wave-r10-groups.json`
  `R10-SAV-ACTUATION` carries both controls of carry 5 seam 2 as preconditions
  for its failing test (`dev/programme/rosters/wave-r10-groups.json:9455`).
- Root-cause: the body answers the red `tests / fast (3.14)` at `02a28aed`,
  state (d), cheaper detector `python3 tests/finite_boundary.py` (295 s, the
  fast lane already) — the trigger is answered.
- `fixer.md` step 17 on the added lines: the coercion moves to its one owner
  (`const.finite_float`), no HA import, no side effect, no parallel mechanism.

## Residual (non-blocking)
A settled `count` that is missing or non-finite scales instead of falling back
when the spot `count` is also absent: `folds` and `spot_folds` both read 0,
`0 >= 0` passes, and the function returns the covered figure (28.0 here).
`spot` present (count 24) falls back to 2.8. The docstring's "count ... missing
or not a finite number, reads as no coverage" is therefore over-broad. Not
reachable: the one production call is
`coverage_factor(self.months[key].get("meta") or {}, now)`, and every entry
reaching it comes from `_clean_month` (both keys, count >= 1) or from
`observe_meta_mean`/`book_capacity` (both keys), so `folds == 0` with
`sum > 0` cannot occur. The function is total either way; the sentence is a
precision note, not a wrong published value.
Carry: dismissed: unreachable through the loader and both in-memory writers;
where the inconsistent dict can be built by hand the function still returns a
finite figure; docstring precision only.

## Could not establish
- The fix1 body's phrase "a tenth coercion" is narrative; the measurable form
  is the stray set, which is one entry (`ledger.py::coverage_factor`) at
  `02a28aed1` and empty at the head.
- No `pr-contract` check-run had started at this head (only `budget-raise-gate`
  concluded); the body's own `carry_audit` line is therefore taken from the
  body, not re-read from a run.
