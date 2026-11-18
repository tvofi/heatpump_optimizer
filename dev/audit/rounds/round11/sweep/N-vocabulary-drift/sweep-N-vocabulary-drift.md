# Class sweep: N-vocabulary-drift (round 11, phase D)

Class mechanism: a record's writer holds one vocabulary and its reader holds
another, so the writer accepts a word that no read can close.
Judged findings: D13-s2-01 (block-class words) and D13-s2-02 (friction rule
ids). In the ledger the class is barriered for the R10 roster stage and size
pair (`roster_lib.py`); that barrier covers only `roster_edit` and `roster_sync`.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep/vocabulary_drift.py` scans `tools/`,
`.claude/workflows` and `.claude/hooks`. It applies two rules:

- **R1**: every pair of named word-set literals in different definitions (Python
  AST; JS const arrays, Sets and regex alternations; shell variables) that
  share at least 2 words and at least 0.2 of the smaller set, and differ.
- **R2**: every vocabulary-named constant (`*CLASS*`, `*STAGE*`, `*VERDICT*`,
  `*KIND*`, `*ID*`, `*STATUS*`) whose regex accepts an open word.

At the register head it lists 23 seams. Controls (`vocabulary_drift_controls.sh`):

| control | result |
|---|---|
| positive | all three judged sites: bus.sh `MECHANICAL_CLASSES` vs `VERDICT_CLASSES`, `VERDICT_RE`, `FRICTION_ID`; at pre-fix `21b1ed140` it also re-finds the R10 drift (replan `LIVE_STAGES` 'in-review' vs roster_sync `DERIVABLE_STAGES`) |
| null: a clean fixture of unrelated closed lists | 0 |
| perturbation: one drifting `ROSTER_STAGES` line appended to a copy of `replan.py` | 23 -> 24 |

## Dispositions

**Judged sites (3, beyond_finding false).** `bus.sh:672` vs `web-fix-wave.js:175`,
`web-fix-wave.js:272 VERDICT_RE`, `policy_lint.mjs:6658 FRICTION_ID`. Their
probes are the findings' own harnesses.

**Instances beyond the findings (5).** Each one fails `vocabulary_drift_probe.py <seam>`:

| seam | probe | what fails |
|---|---|---|
| `replan.py:116 LIVE_STAGES` / `roster_lib.STAGE_KIND` vs `web-fix-wave.js:164 KNOWN_STAGES` | stage_vocab | 15 stage words the roster writer accepts, among them the live `fixing` and `in-progress`, make the wave throw (`web-fix-wave.js:329-334`); neither `KNOWN_STAGES` nor `LIVE_STAGES` derives from `roster_lib`, so the R10 barrier does not reach them |
| `proof_watch.py:108 VERDICT_BLOCKED` vs the wave's `VERDICT_RE` | blocked_grammar | `blocked <sha>`, `blocked <sha>: why` and a digit-bearing class parse as blocked in the wave and as `None` in `parse_verdict`, which `merge_train`, `orchestrator_tick` and `review_packet` read |
| `owed_watch.py:66 DESIGN_VERDICT` | design_verdict | a word other than approve or revise (for example `aprove`) matches and raises neither FIXER-OWED nor DESIGN-REVIEW-OWED |
| `review_strength.py:118 REAL_CATCH` vs `policy_lint.mjs:2827 FRICTION_FAMILIES` | friction_family | `defect`, `figures-false`, `mutation-untriaged` and `policy-regression` are real catches to one reader and in no family of the other |
| `ci_priority.py:42/48` | ci_priority_guard | `check_setting` admits `train-head` in `never_cancel`, a word that `tier()` never yields, so the entry is inert |

**Guarded (3).** `GOV` vs `BODY_UNITS`: `GOV` is pinned to the workflow files
by `tests/entities.py:31837` and `agreement.mjs:481`. `REAL_CATCH` vs
`VERDICT_CLASSES`: the untaught-real split is asserted at
`review_strength.py:912-914`. `fold_ledger.py CLASS_ID`: an unknown id is minted
or refused, never dropped.

**Not applicable (12 seams).** These are in-file derived subsets (owed_watch ×3,
ref_privacy, review_strength strata, `ROOT_CAUSE_CLASSES`), a self-test fixture
(`ABSENT5` ×2), and lists that name different concepts (round_metrics vs
replan work classes, `CODE_EXTS` vs `NOT_A_DOCUMENT`, figure programs vs
classes ×2). The JSON gives the reason for each.

## Count and barrier

There are 5 instances beyond the findings. The class is not barriered beyond
the R10 roster pair. Proposed barrier: one vocabulary module per record
(verdict, stage, design verdict, friction family) that every writer, reader and
the wave script import or extract. A `tests/` check built on
`vocabulary_drift.py` would refuse any R1 pair that is not on an allow-list of
deliberate subsets, at about 2 s of gate time.
