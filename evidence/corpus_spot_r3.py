"""Reviewer spot-check (review-2373 r3): literal_clones/card at the newest corpus trees vs stored vectors."""
import json, subprocess, sys, tempfile, tarfile, io
from pathlib import Path
head = Path(sys.argv[1])
sys.path.insert(0, str(head / "tools" / "audit"))
from archscore.metrics import card, literal_clones
v = json.load(open(head / "tools/audit/archscore/calibration/corpus_vectors.json"))
def ctime(s): return int(subprocess.check_output(["git", "-C", str(head), "log", "-1", "--format=%ct", s]).strip())
shas = sorted(v, key=ctime)[-int(sys.argv[2]):]
bad = 0
for s in shas:
    with tempfile.TemporaryDirectory() as d:
        data = subprocess.check_output(["git", "-C", str(head), "archive", s, "custom_components"])
        tarfile.open(fileobj=io.BytesIO(data)).extractall(d)
        lc = literal_clones.measure(Path(d))["value"]; c = card.measure(Path(d))
        got = (lc, c["card_dead_definitions"], c["card_clone_copies"])
        want = tuple(v[s].get(k) for k in ("literal_clone_copies", "card_dead_definitions", "card_clone_copies"))
        bad += got != want
        print(f"RESULT corpus {s[:10]} live={got} stored={want} {'SAME' if got == want else 'DIFF'}")
print(f"RESULT corpus_spot trees={len(shas)} diff={bad}")
