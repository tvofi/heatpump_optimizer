    # REVIEWER PROBE (mixed): A=lo deferring edit gate; E=earlier deferring edit run, gate in_progress;
    # B=hi later edit run in its prelude (waits on A in wait_sources). C=code run completed.
    _lo, _hi, _E = 42192623509, 42193153511, 42192000000
    _coded = run(99, "code", "completed", owed("code")[:-1] + [{"name": "gate", "status": "completed", "conclusion": "success", "id": 9}])
    _ag = deferred + [{"name": "gate", "status": "in_progress", "conclusion": None, "id": 9}]
    get, naps, nap, now = scene([_coded, run(_E, "edit", "in_progress", _ag), run(_hi, "edit", "in_progress", in_prelude)], me=_lo, mine=deferred)
    _v = verdict({**ectx, "run_id": _lo}, get, nap, now, eclaim3)
    print("PROBE-MIXED A beside E(started, earlier) and B(prelude): verdict=%r naps=%d held_s=%d" % (_v, len(naps), sum(naps)))
