import sys, pathlib
p = pathlib.Path("/Users/timmalmstrom/hpo-seats/r9c-rev-2025-r5/custom_components/heatpump_optimizer/entry_config.py")
s = p.read_text()
M = {
 "R0": ("    def fuse_kw_at(self, amps: float) -> float:\n", "    def fuse_kw_at(self, amps: float) -> float:  # null\n"),
 "R1": ("    def __reduce__(self) -> tuple[Any, ...]:", "    def _no_reduce(self) -> tuple[Any, ...]:"),
 "R2": ("        return self.fuse_kw_at(amps) if amps > 0 else None\n", "        return self.fuse_kw_at(amps)\n"),
 "R3": ("        return amps * max(1, int(self.main_fuse_phases)) * 230.0 / 1000.0\n", "        return amps * int(self.main_fuse_phases) * 230.0 / 1000.0\n"),
}
a, b = M[sys.argv[1]]; assert s.count(a) == 1, sys.argv[1]; p.write_text(s.replace(a, b))
