"""Reviewer's step-14 null (round 5): put the fuse formula back inline in the
coordinator (both sites), exactly as bfaf5486 had it, and let structure.py measure."""
import pathlib
p = pathlib.Path("/Users/timmalmstrom/hpo-seats/r9c-rev-2025-r5/custom_components/heatpump_optimizer/coordinator.py")
s = p.read_text()
R = [("        return self.effective_config.fuse_kw()\n",
      "        config = self.effective_config\n        amps = config.main_fuse_amperes\n        if amps <= 0:\n            return None\n        phases = int(config.main_fuse_phases)\n        return amps * max(1, phases) * 230.0 / 1000.0\n"),
     ("        candidate_kw = self.effective_config.fuse_kw_at(smaller)\n",
      "        phases = int(self.effective_config.main_fuse_phases)\n        candidate_kw = smaller * max(1, phases) * 230.0 / 1000.0\n")]
for a, b in R:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
p.write_text(s)
