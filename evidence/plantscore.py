import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit")
from pathlib import Path
from archscore import vector, score
b = vector.measure(Path(sys.argv[2])); 
for p in sys.argv[3:]:
    c = vector.measure(Path(p)); d = score.delta(b, c)
    moved = {k: f"{b[k]}->{c[k]}" for k in c if k in b and b[k] != c[k] and not k.startswith("_")}
    print(f"RESULT plant={Path(p).name} dS={d['dS']:+.4f} verdict={d['verdict']} moved={moved}")
