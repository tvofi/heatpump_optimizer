Fix review: blocked 6ccf3e03e277611926c711da54d738b9608a821f head-moved: measured 6ccf3e03e277611926c711da54d738b9608a821f, head is 4863ec0529f6eb7802288add93a5612557d5c2b8

bus-nonce: fd6488fabbf87528104cc36f235eefec

Round 2. This is a delta review of `411932cae1..6ccf3e03e2` against the round-1 verdict `blocked 411932cae1 class-open` (probe/rev-3914-580cd535).

## Block

- The PR head moved while this review ran. The measured head is `6ccf3e03e2`. The live head `4863ec0529` adds `c5bb97a7db` and two merges over `tests/open_meteo.py` only (`ev/moved_delta_6ccf3e03_4863ec05.diff`). `review_carry.py 6ccf3e03e2 4863ec0529` prints `FRESH-REVIEW`, so this verdict does not carry.
- The measured head is also red on a required check. `merge_train.py classify 6ccf3e03e2 --pr 3914` exits 1 with `RED ... pending: none red: gate`. The red under `gate` is `tests / mutation`. So the measured head could take no merge verdict either way (C8).
- No defect in code, tests or harness was found at the measured head. The next round is a delta: `git diff 6ccf3e03e2 <new head>` (the `tests/open_meteo.py` check, plus the mutation pins once `mutation-autofix` lands them) and the live required checks. Every figure under `## Evidence` survives, because the move touches no file those figures read.

## Findings

- Note: stale-body: the PR body is malformed. After a stray `## Red checks\`.` line, `## Mutation proof`, `## Null control`, `## Figures` and `## Unpinned sites` appear a second time. The two `## Unpinned sites` copies differ: the first lists per-line sites with ledger dispositions, and the second gives a prose summary by function. This is paperwork and does not block (C5). Carry: dismissed: body paperwork, the fixer rewrites it in the next round
- Note: surviving mutants, by this seat's targeted run (`ev/mutants.txt`). Neither breaks a check, and neither is a gap:
  - M4, `t > utc_instant(now)` to `>=`. This is the triaged-equivalent CMP_BOUND `e2e8012d`. Equality cannot pass the filter, because a start or jump at `now` is already inside the window and returns 0.0 first.
  - M6, `_wall_inside` without `wall.date() == on`. Alone it reads 0 off in the census, the wrap oracle and the checks. It matters only together with M8 or M11 (the `_offset_change` early return, triaged equivalent `171717b6`). Without that guard, the bisection returns the next midnight, and only the date test refuses it. Mutation-table's BOOLOP and RETURN_DEL at line 609 are killed (M9, M10).

  Carry: dismissed: equivalent alone, both guards together are pinned by M9/M10 kills and the 171717b6 triage

## Red checks

- `tests / mutation` (required, in `merge_train.py owed-reds`) is red at `6ccf3e03e2`. The job log shows `MUTATION TABLE REFUSED -- 1825 unpinned site(s) against 1818 ... 9 of them added by this diff`. The 9 `ADDED UNPINNED` lines are exactly the sites the body's first `## Unpinned sites` copy lists as "pinned by mutation-autofix": 571 BOOLOP and GUARD_OFF, 581, 597, 604, 609 BOOLOP and RETURN_DEL, 618 and 621. The two triaged sites (579, 616) are absent from the list, as they should be.
- The body's `## Red checks` predicts this red and answers it. The cheaper detector named there is the local per-line mutants, which this seat re-ran. That answers the trigger.
- `mutation-autofix` had not pushed when the head moved. `tests / mutation-pins (1)` and `(2)` were `in_progress` at `6ccf3e03e2`, and the commits after it are the fixer's open_meteo test, not a pin commit. Whether the autofix pins or goes red is unsettled, and the next round must read it at the new head.

## Evidence

- RESULT: head measured `6ccf3e03e277611926c711da54d738b9608a821f` (`ev/HEAD.txt`).
  - The dispatch PROMPT.md's header line names `190ffb10c2`, but the job log reports that sha as the ratchet base (origin/main), not the PR head. The brief section and the scheduled prompt name `6ccf3e03e2`, the PR head at dispatch.
  - The live head at return is `4863ec0529`, which is the block above.
- RESULT: `git merge-tree --write-tree origin/main 6ccf3e03e2` exits 0 (`LEDGER-MERGE: resolved tests/closures.json`; `ev/merge_tree.txt`). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- RESULT: the round-1 block is resolved. Its own probe re-run at the head (`ev/fold_probe_head.txt`, Europe/Stockholm 2026-10-25, window 02:45-03:30):
  - fold 0 `now` 02:30+02:00 returns 0.25.
  - fold 1 `now` 02:30+01:00 returns 0.25 (round 1: -0.75).
  - `vvc_should_run` pre-heats in both passes. Sydney and Lord_Howe repeated hours agree too.
- RESULT: the axis rule (`next_window_census`, the fixer's instrument added in this round, not the finder's) gives, re-derived by this seat (`ev/census_*.txt`):

  | ref | spring | autumn | plain |
  |---|---|---|---|
  | merge base `46d0a521be` | 4293 of 71040 | 14300 of 76416 | 0 of 73728 |
  | reviewed head `411932cae1` | 136 of 71040 | 76 of 76416 | 0 of 73728 |
  | this head | 0 of 71040 | 0 of 76416 | 0 of 73728 |

  Each cell equals the body's `## Figures` table. The harness moves under its own perturbation (the prior code), and the plain day is the null.
- RESULT: the census caps every window at 24:00, so it never drives a wrap-past-midnight schedule. The parser stores such a schedule as a split pair `(s, 24.0), (0.0, e)`, because `hour_in_windows` has no wrap branch.
  - This seat built its own oracle for that (`ev/wrap_oracle.py`, the reviewer's instrument). It walks the zone's clock minute by minute, and an entry is an outside-to-inside step under `hour_in_windows`. It covers four zones, every 2026 spring and autumn day, and split windows of 60, 90 and 150 min at 30-min starts.
  - Head: 0 of 5376 cells off (`ev/wrap_oracle_head.txt`).
  - Null control at the prior head `411932cae1`: 6 off, e.g. Santiago 2026-04-04 23:00-04:00 fold 1 gives -0.5 against 0.5 (`ev/wrap_oracle_controls.txt`).
  - So the wrap sub-domain is closed at this head too. No class-open seam was found on the axis.
- RESULT: targeted mutants on `dhw_schedule.py` (`ev/mutants.txt`). Each was applied alone to a copy, run against `ev/replica_check.py`, and then restored, and a `cmp` against the head file read identical. `replica_check.py` copies the two new `features.py` checks verbatim; the census arms ran too.
  - M1 (fold loop `(0,)`): FAIL, and the census reads autumn 47.
  - M2 (jump append deleted): FAIL, spring 80 and autumn 19.
  - M3 (round-trip guard `if True:`): FAIL, spring 156.
  - M5 (jump predicate negation flipped): FAIL.
  - M7 (zone forced to UTC): FAIL, census about 96% off.
  - M9 and M10 (609 BOOLOP and RETURN_DEL): FAIL.
  - M12 (621 RETURN_DEL): FAIL.
  - M13 (604 RETURN_DEL): TypeError.
  - M4, M6, M8 and M11 survive, as stated under `## Findings`. M8 and M11 are the triaged `171717b6`.
  - The body's M1 to M3 census figures are equal to this seat's.
- RESULT: the real `tests/features.py` at the head, under `PYTHONPATH=tests/hastub`, reads `ALL 6276 FEATURE CHECKS PASSED`, and both new P7 checks print `ok` (`ev/features_head_full.txt`).
- RESULT: the delta touches no `VERSION`, manifest, release-notes heading or `*_budgets.json`.
  - The mutation-ledger delta deletes 5 entries for removed `hours_until_next_window` lines. It moves the CMP_BOUND triage `efe0497c` to `e2e8012d` and adds the `_offset_change` GUARD_OFF triage `171717b6`. M4 and M8/M11 confirm both triages by run.
  - Nothing else in the delta moves an instrument (step 14).
- Not re-derived: `Architecture score: dS +0.0000 NULL` for `411932c..HEAD`, and `MODE: SCOPED -- 29 script(s) run, 5 scoped out`. Neither is decisive here, and no heavy gate was re-run (cite-CI rule).
- CI: `ev/classify.log` holds every classify poll. All read WAIT from 03:11Z, then RED at 03:24:58Z (`red: gate`).
