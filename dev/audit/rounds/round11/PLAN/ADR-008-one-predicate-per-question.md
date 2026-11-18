# ADR-008: a question about the plant or an interval is answered by one public predicate

Groups: `R11-SEAM-plant-model` (D12-s2-01, D12-s1-01, D17-s1-03, D17-s3-02,
D8-s1-01), `R11-SEAM-learners` (D7-s2-01, D12-s3-03, D2-s3-08, D2-s3-09),
`R11-SEAM-cycle-reporting` (D10-s1-01). This ADR is the approved design of the
first two groups' predicate work; their law fixes are point fixes.

## Context

`COMPONENTS.md` lists the concerns with two owners. "Is the house two-zone" is
decided in four places, "has hot water" in `thermal_model._dhw_enabled_from_config`
(read across a module boundary by `config_flow.py`) and again, without it, in
the sensor gap advisor. "May a learner ingest this interval" is split between
`coordinator._learning_frozen` and each learner. `away._parse_return_time` is
read by `coordinator.py` and `datetime.py`, and D10-s1-01 needs `services.py`
to parse the same string before the write.

## Decision

1. `thermal_model.py` owns the plant-shape predicates (two-zone, modulating,
   has hot water) as public functions of the entry configuration; the model,
   the plan views, the options page, the action and the gap advisor call them.
2. The learners seam owns one freeze predicate naming every reason an
   interval is not ingested (away, unplanned charge, load-limited probe,
   charge-start dip, and the reasons `_learning_frozen` answers today); each
   learner asks it.
3. `away.py` owns the return-time parser as a public function; the service,
   the coordinator and the datetime entity call it.

## Alternatives

- Renaming a private helper public with no new reader: a rename that moves
  `private_cross_module` and nothing else. Refused for the solver's readers of
  `manual_plan._pin_is_free`, `thermal_model._mean_humidity` and
  `_step_humidity`, and for `price_model._raw_value`: no finding gives them a
  new reader, so they stay as they are.
- A predicate per caller kept equal by a test: the state the findings report.

## Consequences

- Tradeoff T16: one default for two-zone moves the plan of every install that
  never set it; the release notes owe the step first.
- Tradeoff T8: a wider freeze slows learning on installs with few clean
  intervals; `m3_learner_freeze.py` reads the ingest count per signal.

## Scenarios served

Generalization, first scenario (S16, T16); physical sanity, third scenario
(S8, T8); integration quality, second scenario (S19).

## Move and fitness functions

**No dS is predicted.** `private_cross_module` would read three crossings
lower, one in `R11-SEAM-plant-model` and two in `R11-SEAM-cycle-reporting`
(`layering.py`'s crossing list at the fork). Both groups name the metric at
0.0 in `PLAN.json`, and the terms are not in the projected dS: a count that
falls on a rename is not a prediction a plan may rest on (`plan-review.md`
step 3).

**Banked only with the new reader.** The count falls because
`_dhw_enabled_from_config` and `_parse_return_time` lose their underscore; the
readers that cross today still cross. What makes that more than a rename is
the reader each finding adds: the sensor gap advisor calling the hot-water
predicate (D8-s1-01), and `services.py` parsing the return time before the
write (D10-s1-01). The reviewer finds that call in the PR's diff and its
failing test in the PR's suite. Without it the fall is `metric-gamed`
(`fix-review.md` step 14) and is not banked. The predicates are built
whatever the count reads: the decision above is the design, and the findings
it serves are behaviour findings.

Acceptance: C18 (a private read through a module binding still counts); the
d12-cells enumerator reads no single-zone cell with two floors;
`m3_learner_freeze.py` reads zero contaminated ingests.
