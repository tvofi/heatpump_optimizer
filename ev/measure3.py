import sys, json
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools/audit"))
from archscore import vector
v = vector.measure(root, only={"literal_clone_copies", "card"})
print(f"RESULT tree={sys.argv[2]} " + " ".join(f"{k}={v.get(k)}" for k in ("literal_clone_copies","card_dead_definitions","card_clone_copies")))
