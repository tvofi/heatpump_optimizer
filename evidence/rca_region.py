_mut_seed = getattr(_mut, "seed_pool_seconds", None)
_mut_pool_read = getattr(_mut, "pool_seconds", None)
_mut_pool_write = getattr(_mut, "write_pool_seconds", None)
_mut_tmo = getattr(_mut, "driver_timeout", None)
_RCA_FLOOR = 1200
# boost_drift_replay.py at the 10-08 head 816547efe: solo recording 800.2 (rc 0),
# pool cost reached the 2401 s bound and timed out (rc 124). A completed run the
# night before measured the same script's pool cost at 1573 s against a 1576 s
# bound -- three seconds of margin.
_RCA_SOLO = 800.2
_RCA_POOL = 2401.0
_rca_old_bound = _mut_tmo(_RCA_FLOOR, _RCA_SOLO) if _mut_tmo else None
_rca_basis = (_mut_seed({"b": _RCA_SOLO}, {"b": _RCA_POOL})["b"]
              if _mut_seed else None)
_rca_new_bound = (_mut_tmo(_RCA_FLOOR, _rca_basis)
                  if (_mut_tmo and _rca_basis is not None) else None)
R.check(
    "RCA-1565: the baseline bound covers the MEASURED pool cost with the scale's "
    "margin, not TIMEOUT_SCALE x a band-stale solo recording",
    # The defect, reproduced from the committed table with the tree's own
    # function: 3x the solo recording IS the bound the lane timed out at, so it
    # carried zero margin over the pool cost.
    _rca_old_bound == 2401 and _rca_old_bound <= _RCA_POOL
    # The fix: bounding by max(solo, pool) gives the pool cost the full
    # TIMEOUT_SCALE headroom the scale exists to provide.
    and _rca_new_bound is not None
    and _rca_new_bound >= _mut.TIMEOUT_SCALE * _RCA_POOL,
    f"old bound driver_timeout({_RCA_FLOOR}, {_RCA_SOLO}) = {_rca_old_bound} "
    f"(the bound the 10-08 pool cost reached and exceeded, rc 124); new bound "
    f"driver_timeout({_RCA_FLOOR}, max({_RCA_SOLO}, {_RCA_POOL})) = "
    f"{_rca_new_bound}, need >= {_mut.TIMEOUT_SCALE} x {_RCA_POOL} = "
    f"{_mut.TIMEOUT_SCALE * _RCA_POOL}",
)
# Null control, re-taken at THIS merge base: a driver whose solo recording already
# covers its pool cost is untouched -- the seed only ever raises a bound
# (max(solo, pool) >= solo, and driver_timeout is monotonic), and a
# floor-protected driver stays floor-protected. Committed solo seconds via the
# tree's own recorded_seconds(); pool costs are the CI-measured values from job
# 113233890923 (2026-10-08). env_drift's solo recording is the declared 0.9 s
# stub (closure.py #934), so the FLOOR covers its 524 s pool cost, not the scale
# -- the fix reads flat on it, which is the point.
_RCA_POOL_MEASURED = {
    "tests/features.py": 772.0,
    "tests/stress.py": 434.0,
    "tests/entities.py": 142.0,
    "tests/env_drift.py": 524.0,
    "tests/harness_headers.py": 211.0,
}
_rca_rec = getattr(_mut, "recorded_seconds", lambda: {})()
_rca_null = {}
for _s, _pool in _RCA_POOL_MEASURED.items():
    _solo = _rca_rec.get(_s, 0.0)
    _oldb = _mut_tmo(_RCA_FLOOR, _solo) if _mut_tmo else None
    _basis = _mut_seed({_s: _solo}, {_s: _pool})[_s] if _mut_seed else _solo
    _newb = _mut_tmo(_RCA_FLOOR, _basis) if _mut_tmo else None
    _rca_null[_s] = (_solo, _pool, _oldb, _newb)
R.check(
    "RCA-1565 null control: a healthy driver's bound still covers its pool cost, "
    "the seed never lowers a bound, and env_drift stays floor-bound (not scaled)",
    all(oldb is not None and newb is not None and newb >= _pool and newb >= oldb
        for (_solo, _pool, oldb, newb) in _rca_null.values())
    and _rca_null["tests/env_drift.py"][2] == _RCA_FLOOR,
    f"rows (solo, pool, old bound, new bound) = {_rca_null}",
)
# Item 3: the pool measurement persists and reads back, fail-soft -- an absent or
# malformed file seeds NOTHING, so the bound falls back to the solo recording
# (today's behaviour) and is never smaller for a missing measurement.
_rca_roundtrip = False
if _mut_pool_read is not None and _mut_pool_write is not None:
    _rca_dir = Path(_tempfile.mkdtemp(prefix="rca1565-pool-"))
    _rca_path = _rca_dir / "pool_seconds.json"
    _mut_pool_write({"tests/boost_drift_replay.py": 1573.0}, _rca_path, "abc123")
    _rca_back = _mut_pool_read(str(_rca_path))
    _rca_roundtrip = (
        _rca_back == {"tests/boost_drift_replay.py": 1573.0}
        and _mut_pool_read(None) == {}
        and _mut_pool_read(str(_rca_dir / "absent.json")) == {}
    )
    _rca_bad = _rca_dir / "bad.json"
    _rca_bad.write_text("{not json")
    _rca_roundtrip = _rca_roundtrip and _mut_pool_read(str(_rca_bad)) == {}
    _mut_shutil.rmtree(_rca_dir, ignore_errors=True)
R.check(
    "RCA-1565: the pool measurement round-trips through pool_seconds.json, and an "
    "absent/unreadable/malformed file seeds nothing (fail-soft, never a smaller bound)",
    _rca_roundtrip,
    f"round-trip and fail-soft ok = {_rca_roundtrip}",
)
# Item 1: a baseline TIMEOUT against a green committed recording must NOT read as
# "fix the suite first" -- the suite was green (`fast` ran it rc 0); the lane was
# judging its own bound. `baseline_refusal` gained an optional `recorded` param,
# so on the unfixed 2-arg tree this falls back and the timeout reads as a generic
# red, which is exactly the defect the check refuses.
_mut_br2 = getattr(_mut, "baseline_refusal", None)
_rca_arity = getattr(getattr(_mut_br2, "__code__", None), "co_argcount", 0)
_RCA_TO_RUN = _mut.ScriptRun(
    _mut.TIMEOUT_RC, 0, 2401.0, "",
    "tests/boost_drift_replay.py: timed out after 2401s", True)
_RCA_TO_REC = {"tests/boost_drift_replay.py": {"seconds": 800.2, "rc": 0}}


def _rca_br(baseline, scope, recorded):
    _buf = _mutb_io.StringIO()
    with _mutb_contextlib.redirect_stdout(_buf):
        if _mut_br2 is None:
            _rc = None
        elif _rca_arity >= 3:
            _rc = _mut_br2(baseline, scope, recorded)
        else:
            _rc = _mut_br2(baseline, scope)
    return _rc, _buf.getvalue()


_RCA_TO_RC, _RCA_TO_OUT = _rca_br(
    {"tests/boost_drift_replay.py": _RCA_TO_RUN}, "full", _RCA_TO_REC)
R.check(
    "RCA-1565: a baseline that TIMED OUT against a green committed recording "
    "names the stale recording and the bound, not 'fix the suite first'",
    _RCA_TO_RC == 1 and "MUTATION TABLE INCONCLUSIVE" in _RCA_TO_OUT
    and "Fix the suite first" not in _RCA_TO_OUT
    and "STALE" in _RCA_TO_OUT
    and "2401" in _RCA_TO_OUT and "800.2" in _RCA_TO_OUT,
    f"rc={_RCA_TO_RC!r} out={_RCA_TO_OUT.strip()!r} -- a timeout is the lane's "
    "own bound, which no cheaper check measures, so it must not be reported as "
    "the suite's red",
)
# Null control on the wording: a REAL red baseline (a failing check, not a
# timeout) still reads as "fix the suite first" -- the timeout arm did not
# weaken the case the refusal exists for.
_RCA_RED_RUN = _mut.ScriptRun(1, 2, 41.0,
                              "  FAIL payroll rounding\n"
                              "  2 of 3 ENTITY CHECKS FAILED\n")
_RCA_RED_RC, _RCA_RED_OUT = _rca_br(
    {"tests/entities.py": _RCA_RED_RUN}, "changed",
    {"tests/entities.py": {"seconds": 259.6, "rc": 0}})
R.check(
    "RCA-1565 null control: a real red baseline (a failing check, not a timeout) "
    "still says 'fix the suite first' and names the check",
    _RCA_RED_RC == 0 and "Fix the suite first" in _RCA_RED_OUT
    and "payroll rounding" in _RCA_RED_OUT
    and "TIMED OUT" not in _RCA_RED_OUT,
    f"rc={_RCA_RED_RC!r} out={_RCA_RED_OUT.strip()!r}",
)
# Wired in the driver. The five checks above drive the functions; none of them
# would notice a `main()` that never called one -- "defined-but-never-called is
# the silent-green shape this repository keeps finding" (this file's own words at
# the `_MUT_BODY` definition), and the class this PR countermeasures IS a lane that
# did not consult its own measurement. So each new function is pinned at its CALL
# SITE: reverting the seed to `own_s = recorded_seconds()`, dropping the
# `--pool-seconds` flag, or moving the persist out of the `finally` each reddens
# this check while leaving all five above green.
_RCA_WIRE_MISSING = [w for w in (
    'ap.add_argument("--pool-seconds"',
    'prior_pool = pool_seconds(getattr(args, "pool_seconds", None))',
    "own_s = seed_pool_seconds(recorded_seconds(), prior_pool)",
    "measured_pool[s] = run.seconds",
    "write_pool_seconds({**prior_pool, **measured_pool},",
) if w not in _MUT_BODY]
# The persist rides the `finally` on purpose: a run that refuses on its own bound
# returns before `write_drain`, so a persist placed beside the drain write would
# leave nothing behind on exactly the night the next run needs it.
_RCA_FIN = _MUT_BODY.find("    finally:\n        # Persist the pool cost")
_RCA_CLEANUP = _MUT_BODY.find("        for tree in made:\n            drop_tree(tree)")
R.check(
    "RCA-1565 wired in the driver: main() takes --pool-seconds, seeds the bound "
    "with it, records each pool baseline, and persists from the finally",
    not _RCA_WIRE_MISSING and 0 < _RCA_FIN < _RCA_CLEANUP,
    f"missing={_RCA_WIRE_MISSING!r}; finally-persist at {_RCA_FIN}, tree cleanup "
    f"at {_RCA_CLEANUP} -- the persist must be inside the finally and first in it",
)
# Wired, against the YAML, in the `_MUT_BW_MISSING` idiom: the carrier is what
# makes the seed anything but a local variable. Deleting `--pool-seconds` from a
# nightly lane, or the cache pair that carries the measurement between runs,
# leaves every check above green and the nightly back on TIMEOUT_SCALE x a solo
# recording -- this PR's defect, restorable without tripping a check. The save is
# pinned to `if: always()` IN THE MEASURING JOB and pinned ABSENT from
# `mutation-ledger-push`, which is the trap the RCA names: that job is gated on
# `needs.mutation-ledger.result == 'success'`, so it does not run on the night the
# bound trips. Both jobs stay grant-free (decision 0011's measuring-job invariant).
_RCA_YAML_MISSING = [(j, w) for j, w in (
    ("mutation-nightly", '--pool-seconds "$RUNNER_TEMP/pool-seed/pool_seconds.json"'),
    ("mutation-nightly", "actions/cache/restore@"),
    ("mutation-nightly", "restore-keys: pool-seconds-"),
    ("mutation-ledger", '--pool-seconds "$RUNNER_TEMP/pool-seed/pool_seconds.json"'),
    ("mutation-ledger", "actions/cache/restore@"),
    ("mutation-ledger", "actions/cache/save@"),
    ("mutation-ledger", "Save the pool measurement for the next nightly"),
) if w not in _workflow_job(_TESTS_YML, j)]
_rca_ledger_job = _workflow_job(_TESTS_YML, "mutation-ledger")
_rca_push_job = _workflow_job(_TESTS_YML, "mutation-ledger-push")
R.check(
    "RCA-1565 wired in the workflow: both nightly lanes pass --pool-seconds, and "
    "mutation-ledger persists on an if: always() cache save in the measuring job, "
    "never in the success-gated push job",
    not _RCA_YAML_MISSING
    # The save step carries `if: always()` -- pinned as the adjacency, so a SHA
    # bump does not break it and moving the condition off the save does.
    and bool(_re.search(r"actions/cache/save@[0-9a-f]{40}[^\n]*\n\s+if: always\(\)",
                        _rca_ledger_job))
    and "actions/cache/save@" not in _rca_push_job
    and "needs.mutation-ledger.result == 'success'" in _rca_push_job
    # The carrier costs the measuring job no grant and no secret.
    and "secrets." not in _rca_ledger_job
    and "contents: write" not in _rca_ledger_job,
    f"missing={_RCA_YAML_MISSING!r}; save-if-always="
    f"{bool(_re.search(r'actions/cache/save@[0-9a-f]{40}[^\\n]*\\n\\s+if: always\\(\\)', _rca_ledger_job))}",
)
