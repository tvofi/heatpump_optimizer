# R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT: main's self-test read-set table, repaired by hand nine times

Round-end family analysis under loop card L8 (machinery friction is counted by family in the
round and analysed once per family at round end). It runs beside no fix and lands no code.
Measured at `origin/main` `a39627da59` on 2026-11-15. It does not repeat the per-defect
analysis the round-10 root-cause seat wrote on 2026-11-13
(`$HPO_STATE_DIR/s14/seat/rca-selftest-scope/R10-RCA-SELFTEST-SCOPE-DRIFT.md`, out of tree, 467
lines, state (c)); it re-checks that analysis against the tree and closes the family.

## 1. Instances

- Main's non-required `governance / instrument-self-tests` step "Refuse a self-test read set
  the committed table misses" went red in six episodes in the round-10 orchestrator's sweep
  log: lines 1004 (2026-11-12T12:27Z), 1727 (11-13T15:59Z), 2156 (11-14T10:07Z), 2330
  (11-14T16:10Z, four pushes red), 2552 (11-15T04:06Z) and 2600 (11-15T07:38Z). The log's own
  family count after the 2026-11-14 L8 ruling reads 4 (lines 2552, 2600); both counts are stated.
- Hotfix merges re-recording or repairing the table in round 10: #3375, #3409, #3419, #3482,
  #3487, #3535, #3557, #3589, #3595, #3606 (`git log --first-parent --oneline origin/main
  --since=2026-10-14 | grep -i -E "selftest-scope|main-selftest|ist-prepr|prepr-readset"`, less
  the RCA record #3410): ten, nine of them after #3315 introduced the table.
- 27 of the 255 first-parent merges since #3315 touched `tools/ci/selftest_closures.json`
  (`git log --first-parent --format=%h ba6fd7e8b0..origin/main --
  tools/ci/selftest_closures.json | wc -l`; `git rev-list --first-parent --count
  ba6fd7e8b0..origin/main`).

No required check turned red: `classify --main` read GREEN through each episode (lines 1004,
2156). The family qualifies on count.

## 2. Named cause

The table is a measurement taken on main's push runs only (the drift step runs on push,
`governance.yml` near line 1553, `if: ... env.SELFTEST_TRACE != ''`), so a pull request that
adds a read to a gated self-test cannot see the drift its merge will cause; and the repair, a
hand re-record, replaces entries rather than unioning them: `tools/ci/selftest_scope.py:750-751`
at `a39627da59` still reads `entries = dict(old["steps"]) if old and only else {}` then
`entries.update(measured)`, so a whole-table re-record taken at a stale base drops reads main
measures (#3409 dropped 660 entries, #3419 8, #3506 10; the 2026-11-13 analysis, re-run then by
the triage seat: 3 of 15 table-touching merges fire its shrink probe).

## 3. Process state: (c)

The process (measure on push, repair by a re-record hotfix) existed and was followed every time:
nine hotfixes, each reviewed and merged. It did not produce the intended result, because the
unit is wrong: a generated artifact is edited by hand in pull requests, and its measurement is
taken where no pull request can read it. Not (b): no step was skipped. Not (d): the table's
preconditions did not change under it; it was born with them.

## 4. Class reach

The same shape (a generated or measured file edited by hand inside pull requests) is
`tests/closures.json` (closures-autofix already regenerates it after push), the structure
budgets, figure blocks in bodies (`R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`) and the claim files'
stamp line (PC-1113-18). Loop card L9, ruled yes by tvofi on 2026-11-14, names all four.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- cost(defect): median 5 h 52 min from a drift group's roster append to its merge (the
  2026-11-13 triage seat, five hotfixes: 2 h 18 m, 18 h 38 m, 16 h 49 m, 5 h 52 m, 5 h 41 m),
  plus one fixer, one reviewer and one FULL CI run each (the table is a gate file).
- P(recurrence): ten repairs in the round, about one per 25 merges (the 2026-11-13 figure: 6
  drift groups in 149 merges; this window: 9 in 255).
- cost(countermeasure, recurring): countermeasure A (a bot re-records the refused steps by
  union from the failing push run's own trace artifact and lands them through the record
  autofix route) adds one bot commit per drifting push and no seat; its standing cost on a
  green push is zero (it writes nothing).

At one repair per 25 merges and about 6 h of wall clock plus two seats each, the countermeasure
pays at the first instance. The cost test passes.

## 6. Countermeasure

A, as the 2026-11-13 analysis specified, built as the first part of R11-PRE-SHARED-FILES
(triage `dev/programme/triage/r10-round-end.md#P748`, with P762 and P763): `record` unions, then
the main-side bot. The pull-request shrink guard (countermeasure C, PR #3551) is dropped: once
no pull request edits the table, a guard over pull-request edits of it has no input (L9's own
text). Demonstration owed by the building group, as the analysis states it: the job red on a
planted unrecorded read and green after the bot commit; null control, a green push writes
nothing. The 2026-11-13 analysis lands in the tree with that part, as its own record.
