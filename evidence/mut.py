import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
M = [
 ("A beatd floor check disabled", "tools/audit/seat/beatd.py", "    if sys.version_info < FLOOR:", "    if False:"),
 ("B beatd launch.json never written", "tools/audit/seat/beatd.py", '(d / "launch.json").write_text(', '(d / "launch.jsonX").write_text('),
 ("C overlay checkouts ignored", "tools/audit/seat/hooks/liveness.py", '        names.update({k: v for k, v in ov.items() if "checkout" in k and isinstance(v, str)})', "        pass"),
 ("D restart drops HPO env", "tools/audit/seat/hooks/liveness.py", '            cmd += ["--env", f"{k}={v}"]', "            pass"),
 ("E restart ignores recorded cwd", "tools/audit/seat/hooks/liveness.py", '"--cwd", cwd]', '"--cwd", "/"]'),
 ("F corpus never written on compaction", "tools/audit/seat/hooks/liveness.py", '    owed = event == "PostCompact" or', '    owed = False and'),
 ("G HELD answers never match", "tools/audit/seat/pulse.py", 'HELD = ("spooled for the live train\'s next batch", "still to run in this train")', 'HELD = ("x",)'),
 ("H dead train still holds", "tools/audit/seat/pulse.py", '    if not isinstance(train, dict) or not train.get("alive"):', '    if not isinstance(train, dict):'),
 ("I live snapshot never reads the train", "tools/audit/seat/pulse.py", '        snap["train"] = read_train(train_state)', '        pass'),
 ("J relay stale bound 15 -> 100", "tools/audit/seat/hooks/liveness.py", '_env_min("HPO_RELAY_STALE_MIN", 15)', '_env_min("HPO_RELAY_STALE_MIN", 100)'),
 ("K proof never clears marker", "tools/audit/seat/hooks/liveness.py", '    (state / "compact-owed").unlink()', '    pass'),
 ("L --train-state not passed to snapshot", "tools/audit/seat/pulse.py", 'repo_of(a.checkout, a.remote), a.train_state)', 'repo_of(a.checkout, a.remote), None)'),
]
TESTS = [["tools/audit/seat/hooks_setup.py","--self-test"],["tools/audit/seat/pulse.py","--self-test"]]
for label, f, old, new in M:
    p = root / f; t = p.read_text()
    n = t.count(old)
    if n != 1:
        print(f"{label}: anchor count {n}, SKIP"); continue
    p.write_text(t.replace(old, new))
    try:
        res = []
        for tc in TESTS:
            r = subprocess.run([sys.executable, "-I", *tc], cwd=root, capture_output=True, text=True, timeout=200)
            last = (r.stdout.strip().splitlines() or [""])[-1]
            res.append(f"{tc[0].split('/')[-1]} rc={r.returncode} [{last}]")
        killed = any("rc=0" not in x for x in res)
        print(f"{'KILLED ' if killed else 'SURVIVED'} {label}: " + " ; ".join(res))
    finally:
        p.write_text(t)
