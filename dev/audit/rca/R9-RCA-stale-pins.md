# RCA-stale-pins: a fix that edits a pinned line reddens `mutation`, and 6d did not say so

The root-cause seat for the red that recurred in three stale-pin PRs on 2026-10-08 and 09.
It follows `dev/governance/roles/root-cause.md` and
`dev/governance/rules/defect-root-cause.md`, and ran at `origin/main` `47b083b0`.
The fix is PR #2073. The seat posted no issue.

The trigger is the second one in `defect-root-cause.md`: a check went red on a
commit in the branch, and a cheaper detector could have run. The three stale-pin
PRs:

- #2066: a new property shifted `thermal_model.py`; two `killed_by` entries
  went stale and the frozen brief_lint fixture at `wood_share:1152` went vacuous.
- #2070: `coordinator._on_off_service` moved to `pump_arbiter.on_off_service`,
  leaving the `coordinator.py:_on_off_service` RETURN_DEL pin stale.
- #2065: round 2 deleted a `from_dict` isinstance line that the bot had just
  pinned.

A fourth observation, that a Red checks answer from an earlier head satisfies
the check because it matches names and not heads, is a separate item (section 6),
not a stale-pin red.

## 1. The cause, reproduced

The ledger is keyed by content anchor, `FILE:SCOPE KIND DIGEST`, and each entry
carries the pinned `old` line text (`tests/mutation_table.py`, `anchor_sites`).
A pure move that keeps the line text stays valid. A pin goes stale when the
line text changes or the site leaves its file. CI's `mutation` job refuses that
through `completeness_problems(budgets, sites)`, run on the whole-tree
`inventory()` before any mutant.

Step 6d of `tools/pr/prepr.sh` runs `tools/pr/ci_predict.py`, which called the
same `inventory()` but only read one direction: unpinned sites the diff adds,
as a warning. Nothing local read the other direction. `mutation-autofix` only
adds pins (`ci-autofix.md`), so a stale pin is the author's to delete, and the
bodies that said the bot would repair it were wrong.

Reproduction at `47b083b0`: edit the pinned line
`return stored_instant(value, dt_util.DEFAULT_TIME_ZONE)` in `away.py`, commit,
run `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`.
The old predictor printed only the ADDED UNPINNED warning, `no closures or fast
red predicted`, rc 0.

## 2. Process state: (c)

The process was followed and did not produce the intended result. Step 6d
existed, was run by the seats, and passed. Its unit covered one of the two
directions the CI check refuses. This is not (b): a firmer instruction to run
6d would not have changed a green 6d. It is not (d): the precondition did not
change, the check was always one-sided.

## 3. How far the class reaches

Searched: every other check `ci_predict.py` models. The closures arms
(UNDER-SCOPED, INERT READS, NO RECORDING, UNCLASSIFIED) already read both what
the diff adds and what it breaks. The ledger was the one pairing of forward and
backward direction with only the forward one ported. Not covered, and left to
CI: a pin whose killing script's closure no longer reaches the module
(`stale_pins`), which `--drain` drops itself.

The brief_lint fixture that #2066 also broke is a separate instance of the same
family, a check pinned to a production line layout, and is section 6.
The #2070 observation that CI never runs a round's `--perturb` arms is a
different class, with no detector at any cost; it is its own carry in
`carry-201.json`, for D11 or D13.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- cost(countermeasure): the comparison `completeness_problems` costs 0.01 s
  after the `inventory()` that step 6d already builds (9.77 s here, one
  measurement under load). The whole predictor takes about 7 s on the unmodified
  tree.
- cost(defect): one CI fast and mutation cycle, about 30 min (the coordinator's
  figure, not measured here), plus the fixer's re-push and re-review.
- P(recurrence): 3 stale-pin PRs in one night, each touching a pinned production line. No release-note frequency was measured.

0.01 s per run against 3 x 30 min leaves the countermeasure well inside the
test.

## 5. The countermeasure

`ci_predict.unpinned` also returns `completeness_problems` as `PREDICT ledger
STALE PIN ...`, a refusing prediction (rc 1) when the stale pin's anchor file or
its own file under `tests/mutation_ledger/` is in the diff, with a remedy line: delete the
stale pin's file under `tests/mutation_ledger/`. A stale pin the base already carries is a warning that names main
(`STALE PIN ON MAIN`), never a refusal: `mutation` is required but not strict, so
PR A's autofix pin and PR B's edit of that line can both merge, and a whole-tree
refusal would then block every unrelated push (review round 1, measured rc 1 on
a README-only diff). Two `--self-test` arms: the plant, and the unrelated
branch on a base that carries a stale pin (rc 0, warning).

Shown failing and passing:

- planted edit of the pinned line: old predictor rc 0; new predictor `PREDICT
  ledger STALE PIN ...away.py:_parse_return_time RETURN_DEL 17d5e3f1`, rc 1.
- the ledger file deleted: no STALE PIN line, rc 0.
- null control, the unmodified tree: rc 0; an unrelated edit on a base that
  carries a stale pin: rc 0 with the STALE PIN ON MAIN warning.
- `prepr.sh --self-test`: "6d predicts STALE PIN for a pinned line the diff
  edits" and "a stale pin refuses, unlike an unpinned site" both ok.

## 6. Refused, with the number

**brief_lint in prepr on every production diff.** `node tools/policy/brief_lint.mjs`
took 1 m 45 s on this machine under load, to guard one fixture, in one of three
cases. Refused. The fixture itself is the defect, and it is carried, not filed:
`dev/programme/carries/carry-201.json`, the entry from this RCA, for the D11
round or the next seat that edits `tools/policy/brief_lint.mjs`.

Measured, with its null control: prepending 14 comment lines to
`thermal_model.py` moves a `return` into the +-1 window around line 1152 and
`brief_lint` goes rc 1, `FIXTURE VACUOUS: 931dffe acceptance pins missing`;
prepending 1 line, and the unmodified tree, stay rc 0.

**A Red checks answer must name the head.** Recorded here as an owner decision,
not filed and not built. The check matches names by design, #1860's ancestry arm
already derives names from earlier heads, the change sits in code-owned
policy_lint and pr-contract machinery, and one observed stale answer is not a
measured class frequency.
