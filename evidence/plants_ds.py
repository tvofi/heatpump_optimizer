import sys
from pathlib import Path
S = Path("/Users/timmalmstrom/hpo-seats/r10s3/review-2373")
sys.path.insert(0, str(S / "head" / "tools" / "audit"))
from archscore import score, vector
b = vector.measure(S / "plants" / "base")
for name in ("P1_module_alias", "P2_keyword_mix", "P3_card_noop_split"):
    v = vector.measure(S / "plants" / name)
    d = score.delta(b, v)
    moved = {m: (b.get(m), v.get(m)) for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY) if b.get(m) != v.get(m)}
    print(f"RESULT {name} delta_S={d['dS']:+.4f} admissible={int(d['admissible'])} verdict={d.get('verdict')} moved={moved}")
