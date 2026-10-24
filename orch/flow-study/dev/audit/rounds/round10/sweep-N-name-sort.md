# Class sweep N-name-sort (round 10, D14 steps 3-4)

Finding in class: D7-s3-53 (verified, low, hygiene): archscore counter C6
`family_orphan_overrides` accepts an invented two-member family (`zzpair`) that
cures a planted split (family_splits 2 -> 0, orphans 0).

Property: an `ENTITY_FAMILY_OVERRIDES` entry homes an entity only into the
family its own English name leads with; every gate that reads the override table
must refuse an entry that does not.

## Enumerator
`python3 dev/audit/rounds/round10/D14/sweep/namesort_override_seams.py`
(worktree root, baseline = handoff/audit-r10-register @ 9355f107d).
Seams: every override entry in `const.py` (AST), and every non-audit file under
tools/, tests/, custom_components/ that reads the table. A gate is an instance
when its family block carries no name-lead comparison; C6 also gets a
behavioural probe (the D7-s3-53 game tree must read >= 1 orphan).

| control | result |
|---|---|
| baseline | seams=9, instances=4 (0 decl, 4 gate before disposition) |
| positive | re-finds D7-s3-53: C6 INSTANCE, behavioural orphans=0 |
| null (`--null`, clean fixture: lead-token override + gate with the check) | seams=2, instances=0 |
| perturbation (`--perturb`, one-line override `optimization_status -> zzpair`) | decl_instances 0 -> 1, instances 4 -> 5 |

## Dispositions
| seam | disposition |
|---|---|
| decl: cost_total_heating, space_heating_cost, space_heating_energy, total_energy -> lifetime | not applicable: en name leads "Lifetime" (compliant) |
| decl: diagnose_last_interval -> prediction | not applicable: en name leads "Prediction" (compliant) |
| gate: tools/audit/archscore/counters.py C6 | **instance** (the finding's own site) |
| gate: tests/entities.py #1760 family block | **instance, beyond finding**: the only override check is "names a shipped translation key"; the zzpair game passes it, and the contiguity check then reads 0 splits |
| gate: tools/audit/archscore/metrics/family_splits.py | not applicable: it is the measured quantity (the thing gamed), not a validator; C6 is its guard by design |
| gate: tools/audit/archscore/planted/redteam/07_family_declare_away.py | not applicable: a planted red-team fixture, not a gate |

Instances beyond the finding: 1. Barrier: none in tree (bugclasses.json
`detector: null, barrier: null, status: open`).

## Proposed barrier
One shared predicate (override target == casefolded first word of the key's en
name) used by both C6 and the tests/entities.py family block, so the gate and
the score refuse the same game; cost < 0.1 s (one JSON read). Limit: Swedish
names lead with a translated token ("Ackumulerad"), so the predicate is en-only;
an sv-only invented family stays open, and a translation rename that makes two
unrelated names share a lead word stays open (D7-arch3-03 "what stays open").
