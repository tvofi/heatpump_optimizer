Fix review: blocked 72b696d96700e0509d03e06479464b5f71c95241 root-cause-unanswered: arch-score and mutation went red, neither named in `## Red checks`

bus-nonce: 8a01ac3f4efc3d17169d09014dc96362

Round: first review of this head. Measured at 72b696d96700e0509d03e06479464b5f71c95241, detached worktree /Users/timmalmstrom/hpo-seats/r9rev-2119/wt; merge base `git merge-base origin/main HEAD` = 7cd5a588cbbbef354c00148040da2d720b8a888c (origin/main is d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e). The body's `## Head` names this head. `git merge-tree --write-tree origin/main <head>` exits 0 — no conflict.

**The fix itself measures sound. The body does not answer two red gate checks, and
the repo's own `pr-contract` gate says so in two ERROR lines (#2119, job 114245619291):**

```
red checks the body must answer: arch-score,mutation
ERROR [pr-body]: check `arch-score` is red and `## Red checks` does not name it.
ERROR [pr-body]: check `mutation` is red and `## Red checks` does not name it.
PR-BODY: 2 error(s)
```

This is exactly what the blocked class means: the fix is sound, the branch turned a check
red, and the body neither names the cheaper detector nor records that none exists. The
`## Unpinned sites` section discusses the mutation triage, but `## Red checks` (the section
the gate reads) names neither check; `arch-score` is absent from the body entirely, and no
`## Architecture score` section exists. Evidence: `pr-contract-red.txt`, `arch-score-red.txt`,
`mutation-red.txt`.

RESULT the two reds are this diff's:
- `arch-score`: `dS -0.9549 WORSENS (inadmissible: shared_inplace_writes 22->25)`.
  My own measurement of the metric (`arch-score-sites.txt`): `shared_inplace_writes`
  22->25 is `collaborator_sites 4->7`, `coord_async_sites 18->18`. The 3 new sites are
  `ledger.py:421,429,433` — `reports[month] = freeze(month)`, `reports[month] = {...}`,
  `del reports[old]` in `roll_receipts`. The base held the identical three writes in
  `_roll_month`, a **sync** coordinator method (rule (a) needs `async`, so it did not count);
  moving them into a collaborator module makes rule (b) count them. So the movement is a
  relocation artifact of the seam move, not three new hazards — but `fixer.md` step 17's
  "`archscore/score.py --diff` not regressed" is still breached and the body neither avoids
  nor names it.
- `mutation`: `MUTATION TABLE REFUSED -- 4641 unpinned site(s) against 4608 at the ratchet
  base, 41 of them added by this diff`. The body's `## Unpinned sites` says the diff adds
  `39` (from `ci_predict.py`); CI measured 41.

RESULT arithmetic reproduced at both ends (probe `probe_ux6.py`, mine, both ends; base 709.5, head 194.5):
- base `coord._freeze_month_report` on the finder's fixture: `total_sek=709.5` (`= sum of
  every non-reason line`), matching the body's figure.
- base null control (no splits/comparisons): `194.5` either way.
- head same call: `total_sek=194.5`, `basis=['spot','grid_fee','immersion','wear']`.
- head `ledger.freeze_month_report`: `194.5`, same basis. `BILLED_LINES = ('spot','grid_fee',
  'capacity','immersion','wear')`.

RESULT failing-first arm moves. The finder's harness is the UX-6 block of `tests/features.py`,
run with the in-tree `tools/audit/seat/features_block.py` (as the body names):
- M0, head unmodified: `ALL 19 FEATURES BLOCK PASSED` (`M0.txt`).
- M1, `billed_total` sums every line (defect restored): `5 of 19 FAILED`, and the null control
  stays `ok` under M1 — it moves only on the double count, so it is a real null control
  (`M1.txt`). The check compares `total_sek` against the literal `194.5`, not against a
  re-implementation of the formula.
- M2, `book_capacity` disabled in `_roll_month`: `3 of 19 FAILED`. M4, `restate_total`
  dropped from `_async_load_ledger`: `1 of 19 FAILED`. Both match the body's counts.

RESULT `restate_total` on load (Q2): `restate_total(fresh)` = `194.5` = the fresh total (the
already-correct receipt is returned content-identical); `restate_total(old 709.5)` = `194.5`;
`restate_total({"lines": {}})` = `0.0`; the load path calls it (M4 arm). Pinned by the block's
"a receipt stored with the old total loads with the billed total".

RESULT `BILLED_LINES` is complete — no mirror bug. The ledger can book exactly `spot`,
`grid_fee`, `capacity`, `immersion`, `wear`, `space`, `dhw`, `savings_baseline`,
`savings_actual`, `reason:*`. In `observe_spot_and_settle_savings`, `space`+`dhw` = the
partition of the metered energy (`= spot + immersion` in money) and `reason:*` = the
partition of `spot`; `savings_baseline`/`savings_actual` are the thermostat comparison
(`ledger.py:197,201,265-268`). So every excluded line is derived from a billed one.

RESULT Q3, the 24-receipt attribute: all 24 reach the sensor, nothing is silently dropped —
`extra_state_attributes['receipts']` carries every frozen receipt (`head-receipts.txt`), and
`_unrecorded_attributes = {receipts, plan_replay}` is the repo's established pattern (11 other
sensors use it). The size reason is directionally right but the body's figure is not
re-derivable: my constructions give 15553 bytes (minimal month) and 21817 bytes (8 reasons,
capacity) for 24 receipts — the second exceeds 16384, but I could not reproduce "about 30 KB"
from a real capture, and the committed `coord_*` captures carry `"receipts": []`.

RESULT Q4, seam_map: `tests/seam_map.json` is byte-unchanged, and the tree's own check passes —
`python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` with `seam_cut_total 762 <= 762`
(`structure.txt`). `max_class_loc` is re-recorded 8818 -> 8745 (a payment, not a raise).

RESULT claims and version clean: `env_drift.py --all origin/main` → `NO UNCLAIMED DRIFT: 56`,
`NO STALE FIXTURE: 56`; `--claims-only` → `claims hygiene: origin/main ok`; the five `coord_*`
claim lines agree with the diff. VERSION, the manifest version and the notes heading are
untouched (`git diff --name-only` empty).

RESULT forward-carry (step 10): the body says `none`, and I confirmed the named siblings
(U1/U5, `carry-1795.json`) are not findings of this PR, so there is no destination to open.

RESULT `## Figures`: 19 resolved, 0 not verified, 0 refused (pr-contract log).
