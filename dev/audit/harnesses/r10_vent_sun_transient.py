"""Does a sun-scaled bias still trip the open-window detector on the first
sunny days? #2391's scratch probe, landed so a later seat reruns it.

A bare production ``Cusum`` built with the coordinator's own construction
constants, fed four days, counting intervals with ``tripped`` set. Two
schedules: the ``tests/features.py`` check's (30-minute, 10 h of 600 W/m2) and
the ``R10-P5`` census's (15-minute on/off heat, 0.15 sun).

Why it is here: #2391 carried the transient to R10-NIGHT-FOLDS on the
condition that its aperture fix might remove it. The learners' night gate does
not touch the detector's feed, and the probe reads the same at both ends --
so the features check stays at 0.4 K and the census keeps its end-state read.

Metric (one line per arm): ``per_day`` is the tripped 15/30-minute intervals
per day for four days; ``end_tripped`` is the state after them.
Command (tree root):
    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_vent_sun_transient.py
Expected (same at the baseline and at R10-NIGHT-FOLDS' head): check schedule
bias 0.4 K ``[0, 0, 0, 0]``, bias 1.0 K ``[0, 20, 0, 0]``; census schedule
bias 0.4 K ``[0, 27, 0, 0]``, bias 1.0 K ``[0, 39, 38, 30]``; every arm
``end_tripped=False``. Null control: bias 0.1 K never trips on either schedule.
"""
from datetime import datetime, timedelta, timezone

from heatpump_optimizer.const import (
    VENT_CUSUM_CLIP_C,
    VENT_CUSUM_DRIFT_C,
    VENT_CUSUM_REFERENCE_HOURS,
    VENT_CUSUM_THRESHOLD_C,
)
from heatpump_optimizer.drift import Cusum

T = datetime(2026, 1, 15, 7, tzinfo=timezone.utc)


def run(residuals, regressors, step_min):
    detector = Cusum(
        threshold=VENT_CUSUM_THRESHOLD_C, drift=VENT_CUSUM_DRIFT_C, side=-1,
        clip=VENT_CUSUM_CLIP_C, reference_hours=VENT_CUSUM_REFERENCE_HOURS,
    )
    tripped = []
    for i, (residual, regressor) in enumerate(zip(residuals, regressors)):
        detector.update(T + timedelta(minutes=step_min * i), residual, regressor)
        tripped.append(detector.tripped)
    return tripped, detector.tripped


def per_day(tripped, step_min):
    per = int(round(24 * 60 / step_min))
    return [sum(tripped[d * per:(d + 1) * per]) for d in range(len(tripped) // per)]


def check_schedule(bias):
    n = 48 * 4
    sun = [600.0 if i % 48 < 20 else 0.0 for i in range(n)]
    residuals = [-bias * q / 600.0 for q in sun]
    regressors = [(1.0, q * 0.5 / 1000.0) for q in sun]
    tripped, ended = run(residuals, regressors, 30)
    return per_day(tripped, 30), ended


def census_schedule(bias):
    n = 96 * 4
    heat = [1.5 if (i // 16) % 2 == 0 else 0.0 for i in range(n)]
    sun = [0.15 if i % 96 < 40 else 0.0 for i in range(n)]
    residuals = [-bias * q / 0.15 for q in sun]
    regressors = list(zip(heat, sun))
    tripped, ended = run(residuals, regressors, 15)
    return per_day(tripped, 15), ended


for bias in (0.1, 0.4, 1.0):
    days, ended = check_schedule(bias)
    print(f"RESULT check.bias{bias:.1f}.per_day={days} end_tripped={ended}")
for bias in (0.1, 0.4, 1.0):
    days, ended = census_schedule(bias)
    print(f"RESULT census.bias{bias:.1f}.per_day={days} end_tripped={ended}")
