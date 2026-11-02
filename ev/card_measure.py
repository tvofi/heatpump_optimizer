import sys, json
from pathlib import Path
inst, tree = sys.argv[1], sys.argv[2]
sys.path.insert(0, inst + "/tools/audit")
from archscore.metrics import card as K
r = K.measure(Path(tree))
print(json.dumps({k: r.get(k) for k in ("card_dead_definitions","card_clone_copies","card_rule_copies")}))
