import sys, re
p = sys.argv[1] + "/custom_components/heatpump_optimizer/coordinator.py"
s = open(p).read()
s = s.replace('_LOGGER = logging.getLogger(__name__)\n',
 '_LOGGER = logging.getLogger(__name__)\n_ZK: Final = "zzz4_const"\n', 1)
# handover store
s = s.replace('    handover["plan_stale"] = coord._plan_is_stale()\n    return handover\n',
 '    handover["plan_stale"] = coord._plan_is_stale()\n    handover["zzz5_handover"] = 1  # P5\n    return handover\n', 1)
# extra helper method returning dict[str, Any] (P9) and Any (P10)
s = s.replace('    def _build_data_dict(self) -> Payload:\n',
 '    def _zzz_any_view(self) -> dict[str, Any]:  # P9\n        return {"zzz9_anyview": 1}\n\n'
 '    def _build_data_dict(self) -> Payload:\n', 1)
old = '        return data\n\n    # ==================================================================\n    # Persistence for the new learners'
assert old in s
new = ('        data.setdefault("zzz1_setdefault", 1)  # P1\n'
       '        data |= {"zzz2_ior": 1}  # P2\n'
       '        data.update(zzz3_kw=1)  # P3\n'
       '        data[_ZK] = 1  # P4\n'
       '        for _k in ("zzz6_loopvar",):\n            data[_k] = 1  # P6\n'
       '        dict.__setitem__(data, "zzz7_dunder", 1)  # P7\n'
       '        _esc: Any = data\n        _esc["zzz8_anyalias"] = 1  # P8\n'
       '        data = {**data, **self._zzz_any_view()}  # P9\n'
       '        data = {**data, **getattr(self, "_zzz_any_view")()}  # P10\n'
       '        data["insight"]["zzz11_nested"] = 1  # P11\n'
       '        data.update({"zzz12_updlit": 1})  # P12\n'
       '        data.update(self._zzz_any_view())  # P13\n'
       + old)
s = s.replace(old, new, 1)
open(p, "w").write(s)
