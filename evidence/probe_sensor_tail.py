# head -21300 tests/features.py at 3b5ffde57, then these lines; run as tests/_probe_sensor_tmp.py with PYTHONPATH=tests/hastub

_pc = _le_coord(house=10)
_le_dt.freeze(_LE_NOW)
_pc.data = {**_pc._learning_view(), "insight": _pc._insight_view()}
_le_dt.freeze(None)
_ps = _rs_sensor.ModelStatusSensor(_pc, _FakeEntry(data={}))
_pa = _ps.extra_state_attributes
print("PROBE coordinator.data has learner_progress:", "learner_progress" in _pc.data)
print("PROBE coordinator.data learner_progress.house:", _pc.data["learner_progress"]["house"])
print("PROBE ModelStatusSensor attribute keys:", sorted(_pa))
print("PROBE eta_days or samples_needed in sensor attrs:", "eta_days" in repr(_pa) or "samples_needed" in repr(_pa))
