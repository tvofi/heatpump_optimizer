import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit")
from pathlib import Path
from archscore.metrics import layering
r = layering.measure(Path(sys.argv[2]))
d = r["details"]
print(f"RESULT {sys.argv[3]} layer_violations={r['layer_violations']} private_cross_module={r['private_cross_module']} unused_boundary_imports={r['unused_boundary_imports']}")
