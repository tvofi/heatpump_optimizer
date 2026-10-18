import sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path.insert(0, str(root / "tools" / "audit"))
from archscore.metrics import shapes, card, literal_clones, hub_solve_writes
from archscore.metrics import common as C
s = shapes.measure(root)
print("RESULT shape_copies=%s" % s.get("value", s.get("shape_copies")), {k: v for k, v in s.items() if k not in ("details",)})
c = card.measure(root); print(f"RESULT card_clone_copies={c['card_clone_copies']} card_dead_definitions={c['card_dead_definitions']}")
print(f"RESULT literal_clone_copies={literal_clones.measure(root)['value']}")
print(f"RESULT hub_solve_writes={hub_solve_writes.measure(C.load(str(root)) if False else root)['value']}")
