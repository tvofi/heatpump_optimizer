Fix review: blocked 49aba55c46eba48607d396d177cb4e8d1db6bdaf defect: INERT READS still warns on a scoped diff whose CI re-derive omits the reading script (pinertfull is that diff)
bus-nonce: 2c9a3cc866892808293980bf77ca4097

Round 3 delta review of #2061, from 8c758b72 to 49aba55c (b2e8fbf66, 6ae385f29, merge 49aba55c4). I measured at 49aba55c. The live head was re-read after CI settled and is unchanged.

## Repaired (verified)
- Skip arm: my harness-only plant (plant_inert.sh) now gives `rc=1` with `-- a skip diff: CI records nothing ...`, and `affected` still returns `case=skip`. The skip arm is fixed.
- Direct-push rule: I ran the PR's own entities block, verbatim, against mutated copies of delivery_status.py (ent_block.py). M1, M2, M4, **M5 and M6 are all killed**: each gives FAIL, and the head gives ok. M3 (`files is not None`, which makes an empty diff record-only) still survives; it is harmless and only noted.
- CI at 49aba55c, settled: `fast (3.14)` ran with `MODE: FULL`, printed `ALL 109 HARNESS HEADER CHECKS PASSED` and `ALL TEST SCRIPTS PASSED`; every other check is green. The one red is `nightly-status`, which is last night's nightly and reads no file in this diff.

## Still open (blocking): the `recorded` predicate is wrong for the scoped arm
`warns` treats any `affected(...)` case other than `skip` as "CI records". The scoped arm, however, re-derives only `affected()["rederive"]` (tests.yml closures job: `derive_closures.sh --single "$s"` per scoped script). `closure.py check` compares inert reads only over `records.items()`, the scripts it actually recorded. So an INERT READS on a script outside `rederive` is never seen on the PR, closures-autofix never fires, and main's full push run reddens it with nothing to repair it. This is the same hole as round 2, one arm over.
- RESULT plant_inert_scoped.sh (mine): the new harness plus `# a comment` on tests/wood_advisor.py. This is exactly the PR's `pinertfull` fixture.
  - Result: `PREDICT closures INERT READS tests/harness_headers.py ...`, `rc=0` (warning).
  - `affected`: `case=scoped`, `rederive=['tests/wood_advisor.py']`, so harness_headers.py is not recorded.
- RESULT `affected` on other mixes (my run):
  - harness plus custom_components/away.py: scoped, 23 scripts, harness_headers.py included, so recorded.
  - harness plus tests/harness_headers.py: scoped, 2 scripts, recorded.
  - So the correct predicate depends on the reading script, not on the case.
- The new self-test line `and only warns there: CI's closures job records` therefore pins the hole as behaviour, as `pinert` did in round 2.
- Repair, the fixer's call: warn only when `case == "full"` or the INERT READS line's script is in `affected(changed)["rederive"]`; otherwise refuse. Keep `pinertfull` as a refusal case, and add a warning case whose diff puts harness_headers.py in `rederive` (for example the harness plus a custom_components file).

This is round 3, so a fourth round owes a re-cut (fixer.md). The INERT READS downgrade (c94842ed9 and 6ae385f29) is the only open item. Splitting it out of #2061 would let the rest, which is verified across three rounds, merge.
