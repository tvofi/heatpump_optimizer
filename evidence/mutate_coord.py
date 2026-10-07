import pathlib
p = pathlib.Path("/Users/timmalmstrom/hpo-seats/r9c-rev-2025/custom_components/heatpump_optimizer/coordinator.py")
s = p.read_text()
old = "        self._ctx = replace(_ctx_of(self), _config=_with_quiet_keys(ctx._config, params))  # #1910\n"
assert s.count(old) == 1
p.write_text(s.replace(old, ""))
