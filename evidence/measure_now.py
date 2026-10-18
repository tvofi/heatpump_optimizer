import sys, json
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "tools" / "audit"))
from archscore.metrics import card, literal_clones
c = card.measure(root); l = literal_clones.measure(root)
print(f"RESULT card_dead_definitions={c['card_dead_definitions']} dead={c['details']['dead']}")
print(f"RESULT card_clone_copies={c['card_clone_copies']}")
print(f"RESULT literal_clone_copies={l['value']} classes={l['details']['classes']}")
