"""Read-only: at this tree, which sites of each ratcheted kind are UNPINNED.

Uses main's own `listed_sites` (source-only, no driving, no writes) and filters
to the four files this branch changes, then intersects with the seven sites the
CI pin pass reported as driven-and-survived ("lives").
"""
import sys
from pathlib import Path
sys.path.insert(0, "tests")
import mutation_table as m

FILES = {
    "custom_components/heatpump_optimizer/accuracy.py",
    "custom_components/heatpump_optimizer/coordinator.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
}
SURVIVORS = [  # (file, line, kind) from the CI shard logs' "lives" verdicts
    ("accuracy.py", 678, "CLAMP_DROP"),
    ("accuracy.py", 680, "RETURN_DEL"),
    ("coordinator.py", 4501, "CLAMP_DROP"),
    ("coordinator.py", 4532, "CMP_BOUND"),
    ("draw_range.py", 111, "CMP_BOUND"),
    ("draw_range.py", 216, "CMP_BOUND"),
    ("draw_range.py", 51, "CONST"),
]

budgets = m.load_budgets()
files = [Path(f) for f in FILES]
unpinned = []
for kind in sorted(m.LISTED):
    for site, loose in m.listed_sites(kind, budgets, files):
        if loose:
            unpinned.append((site["file"], site["line"], site["kind"],
                             site["new"].strip()[:60]))
print(f"UNPINNED in the four changed files (whole tree, not scope-limited): {len(unpinned)}")
for u in sorted(unpinned):
    print("   ", " | ".join(str(x) for x in u))

print("\n=== the 7 CI-measured survivors, checked against this tree's ledger ===")
for name, line, kind in SURVIVORS:
    hit = [u for u in unpinned if u[0].endswith(name) and u[1] == line and u[2] == kind]
    print(f"  {name}:{line} {kind} -> "
          + ("UNPINNED at this head (no killed_by, no survivor_triage)" if hit
             else "not in this tree's unpinned set (line/kind not present or disposed)"))
