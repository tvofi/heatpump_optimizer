    # REVIEWER PROBE: A=lo deferring edit run at its gate; B=hi later edit run still in its prelude
    # (wait_sources, which waits on A because judging(A) is False); C=code run completed.
    from prelude import judging as _jd
    _lo, _hi = 42192623509, 42193153511
    _coded = run(99, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])
    _A_jobs = {j["name"]: (j["status"], j["conclusion"]) for j in deferred + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]}
    print("PROBE judging(A) as B's prelude reads it:", _jd({"id": _lo, "title": title("edit", "7", "main", "M"), "jobs": _A_jobs}))
    get, naps, nap, now = scene([_coded, run(_hi, "edit", "in_progress", deferred + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}])], me=_lo, mine=deferred)
    _v = verdict({**ectx, "run_id": _lo}, get, nap, now, eclaim3)
    print("PERTURB(B gate in_progress) A's gate beside B-in-prelude: verdict=%r naps=%d held_s=%d" % (_v, len(naps), sum(naps)))
