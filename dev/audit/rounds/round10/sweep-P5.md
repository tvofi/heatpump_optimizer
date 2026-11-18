# Class sweep P5, round 10 (D14 steps 3-4)

Class P5 (`dev/audit/config/bugclasses.json`): a learning or adoption gate keyed
on a quantity that is not the bias it gates. The ledger status is `barriered`,
and that barrier is the R9-P5 block in `tests/features.py`. It covers the sysid
adoption interval only.

Finding in the class: **D2-s3-72** (verified, high). The open-window detector
trips on model bias and freezes every learner. It trips on 17.2-18.7 % of
intervals at delivery 0.4 and on none at 1.0.

## Enumerator

`dev/audit/rounds/round10/D14/sweep-P5/enumerate.py [root]` runs an AST scan over
every `.py` under the package. It lists the following seams:

- every `Cusum(...)` detector, with whether `.update()` is fed a `residual` name
  and whether its `.tripped` is read in `_learning_frozen`. A seam with both is
  an instance candidate.
- every `abs(<residual>) > X` rejection.
- every return of `_learning_frozen`.
- every sysid adoption function.

- **Package:** 14 seams, 1 instance candidate.
- **Positive control:** it re-finds D2-s3-72 as `_vent_cusum@2695 fed_residual=True gates_learning=True`.
- **Null control:** on `D14/sweep-P5/fixture_clean/` it returns 2 seams and 0 candidates. That fixture has a Cusum fed a measured quantity, and its freeze is keyed on a measured state.
- **Perturbation, one line on a copy of the package:** feeding `_vent_cusum` with
  `measured_gap` instead of `residual` moves the count 1 -> 0.
- **Perturbation, on the fixture copy:** changing the feed to `residual` and the
  freeze test to `_watch.tripped` moves the count 0 -> 1.

## Seams and dispositions

| seam | disposition |
|---|---|
| coordinator.py `_vent_cusum` (2695, fed 5063, freeze 6351) | **instance**. This is D2-s3-72 itself. Probe `D14/sweep-P5/probe_vent_bias.py` uses the shipped constants. A sustained 0.10 K/interval colder residual from pure model bias, with no ventilation, trips the detector, and the probe fails. The null control (0.00) passes and so does 0.05, so the result moves with the bias. Any bias above `VENT_CUSUM_DRIFT_C` 0.08 trips it. |
| coordinator.py `_cop_health_cusum` (2912) | not applicable. It is fed a shortfall against an empirical per-bucket, per-curve baseline (lift-normalised), not a model residual. It gates no thermal learner. |
| coordinator.py 5079 `abs(residual) > HOUSE_LOSS_MAX_RESIDUAL` | guarded. The rejection is per interval at 1.0 K, so a bias residual is admitted until it is one degree per interval. The vent feed is clipped at 0.6 K before this point. This disposition rests on magnitude and is not measured at delivery 0.4. |
| coordinator.py 5197 (lower floor, same constant) | guarded. Same reason as 5079. |
| accuracy.py 673 `_refit_pair` | guarded. Same 1.0 K constant (coordinator.py 1059). It mirrors the interval learner. |
| `_learning_frozen`: external_heat_source | not applicable. It is keyed on tank warming against compressor capacity and on a user entity, not on the house residual. |
| `_learning_frozen`: signals.freeze_reason, defrosting | not applicable. These are measured pump signals. |
| `_learning_frozen`: sensor health f-string | not applicable. It is keyed on input health. |
| `_learning_frozen`: ventilation | instance. This is the same seam as `_vent_cusum` above, seen from the read side. |
| `_learning_frozen`: boost.FREEZE_REASON, `_tail_freeze` | not applicable. These are keyed on commanded and actuated state (boost, early cut-off, unmetered power). |
| coordinator.py `_adopt_system_identification` (10971) | guarded. The R9-P5 block in `tests/features.py` and the cases drive every return (#1581). |
| sysid.py `adoption_decision` (1196) | guarded. Same R9-P5 sweep (#1718). |

**Count:** 1 instance seam, and it is the judged site (`beyond_finding: false`).
There are 0 instances beyond the finding.

## Barrier proposal

The existing barrier does not reach the vent detector. Promote the probe property
into the R9-P5 block of `tests/features.py`: model bias with no ventilation must
not trip `_vent_cusum` across the bias range the learners are allowed to correct.
An alternative is to feed the CUSUM a residual de-biased by the learner's own
running mean.
