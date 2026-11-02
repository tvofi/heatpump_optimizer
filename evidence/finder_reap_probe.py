import os, sys, time, tempfile, importlib.util
from pathlib import Path
seat = Path(sys.argv[1]); sys.path.insert(0, str(seat))
spec = importlib.util.spec_from_file_location("od", seat / "open_driver.py")
od = importlib.util.module_from_spec(spec); spec.loader.exec_module(od)
SHA = "4"*40
class W(od.World):
    def __init__(s, repo, sd, topic): super().__init__(repo, sd); s.topic = topic
    def tips(s): return {f"refs/heads/handoff/{s.topic}": SHA, f"refs/heads/handoff-body/{s.topic}": "5"*40, "refs/heads/main": "6"*40}
    def roster(s): return {}
    def landed(s, m, x): return False
    def body_head(s, t): return ""
od.roster_lib.groups_of = lambda r: ["A/B", "R10-X", "OPEN-DRIVER"]
od.roster_lib.critical_path = lambda r: []
bad = 0
for topic in ["a/b", "r10-x"]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); sd = tmp / "s d"; sd.mkdir()
        op = tmp / "open_pr.sh"; op.write_text("echo opened\n")
        w = W(str(tmp), sd, topic); w.opener = op
        board = f"OWED 2026-11-02T00:00:00Z handoff-no-pr refs/heads/handoff/{topic} {SHA}\n"
        out = []
        od.run_pass(board, w, sd, 1000.0, out.append)
        time.sleep(1.5)
        od.run_pass(board, w, sd, 1010.0, out.append)
        od.run_pass(board, w, sd, 1020.0, out.append)
        ok = any(l.startswith(f"RESULT {topic} 44444444 rc=0") for l in out) and any(l == f"SKIP {topic} 44444444 seen" for l in out)
        bad += not ok
        print(("ok  " if ok else "FAIL"), topic, " | ".join(l for l in out if not l.startswith("START")))
print(f"RESULT reap_probe failed={bad}")
