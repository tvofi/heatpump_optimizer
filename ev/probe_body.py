# Reviewer probe (PR #3872): behaviour at the call-site arguments my surviving mutants drop.
_pr = {}
# P1: a pass queued before the unload (entry_released) with a 30-minute fault: repair count.
_p1 = _fh_coord(since=-30)
_p1._entry_released = True
_pa_run(_p1, 0)
_pr["P1_released_pass_fault_issues"] = len(_fh_issue(_p1))
# P2: Optimizer Off after a held pass: latch held / fault repair present after one Off pass.
_p2 = _fh_coord(since=-30)
_pa_run(_p2, 0)
_pr["P2_before_off"] = (_fh.held(_p2.entry), len(_fh_issue(_p2)))
_p2._mode = _PA_OFF
_pa_run(_p2, 1)
_pr["P2_after_off"] = (_fh.held(_p2.entry), len(_fh_issue(_p2)))
# P3: heat_curve.publish(mode_off=True) with the alarm on for 30 minutes: calls sent, latch held.
_p3h = FakeHass({_FH_FAULT: FakeState("on", last_updated=_PA_T0 + timedelta(minutes=-30))})
_p3c = EntryConfig.from_mapping({"heat_pump_fault_entity": _FH_FAULT, "ecl110_displace_set_topic": "ecl/displace/set"})
_p3e = _pa_entry(entry_id="probe3")
_sa_dt.freeze(_PA_T0)
_asyncio.run(_fh_hc.publish(_p3h, _p3e, _p3c, -3, {"displace": -3}))
_pr["P3_on_publish"] = ([c[0] for c in _p3h.services.calls], _fh.held(_p3e))
_asyncio.run(_fh_hc.publish(_p3h, _p3e, _p3c, 0, {"displace": 0}, mode_off=True))
_sa_dt.freeze(None)
_pr["P3_off_publish"] = ([c[0] for c in _p3h.services.calls], _fh.held(_p3e), [i[1] for i in getattr(_p3h, "issues", [])])
print("PROBE", _pr)
