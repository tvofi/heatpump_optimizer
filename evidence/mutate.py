import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
MT, OT, TP = "tools/audit/seat/merge_train.py", "tools/audit/seat/orchestrator_tick.py", "tools/audit/merge_throughput.py"
muts = [
 ("counted_poll readable guard dropped", MT, "        if not readable:\n            return False\n        now = self.actions_mark()", "        now = self.actions_mark()"),
 ("counted_poll moved=True", MT, "moved = not mark or mark[0] != now  # mut:stalled", "moved = True  # mut:stalled"),
 ("counted_poll None mark counted", MT, "        if now is None:\n            return False\n        moved", "        moved"),
 ("review_settle unread ends wait", MT, "            if runs is not None and not open_:\n                return", "            if not open_:\n                return"),
 ("rejoin idle never accrues", MT, "                    if runs is None or not counted:", "                    if False:"),
 ("_gate_busy mints Busy()", MT, "            return None  # no reading: never an empty Busy", "            return Busy()  # no reading: never an empty Busy"),
 ("wait_ci classify on None busy", MT, "                    if busy:  # a deferral reading", "                    if True:  # a deferral reading"),
 ("blind_sites FINAL arm off", MT, '                if name == "classify" and final and', '                if False and name == "classify" and final and'),
 ("blind_sites Busy arm off", MT, '                if name == "Busy" and not ch.args', '                if False and name == "Busy" and not ch.args'),
 ("pre_approve dropped", MT, "        for a in serial if lead else serial[1:]:", "        for a in []:"),
 ("pre_approve includes first serial", MT, "        for a in serial if lead else serial[1:]:", "        for a in serial:"),
 ("pre_approval head-moved check off", MT, "        if self.head(pr) != h:\n            return \"the head moved\"", "        if False:\n            return \"the head moved\""),
 ("pre_approval main-inside off", MT, "        if not a.get(\"rc_head\") and not self.contains_main(h) and self.strict_update() is not False:", "        if False:"),
 ("pre_approval GREEN off", MT, "        if state != \"green\":\n            return f\"not GREEN", "        if False:\n            return f\"not GREEN"),
 ("pre_approval CARRY off", MT, "        if \"CARRY: yes\" not in self.run", "        if False and \"CARRY: yes\" not in self.run"),
 ("pre_approval policy off", MT, "        if self.policy_paths(a[\"files\"]):", "        if False:"),
 ("pre_approval raise off", MT, "        if self.raise_hold(pr, h, a[\"files\"])[0]:", "        if False:"),
 ("pre_approval bot route off", MT, "        if BOT_ROUTE in a[\"route\"]:", "        if False:"),
 ("pre_approval unverdicted off", MT, "        if not is_sha(a.get(\"verdict\") or \"\"):", "        if False:"),
 ("_batch skipped not filtered", MT, "                self.pre_approve([a for a in serial if a[\"pr\"] not in skipped],", "                self.pre_approve([a for a in serial],"),
 ("_batch lead always False", MT, "                                 len(entries) > len(serial), head_req)", "                                 False, head_req)"),
 ("one_pr GREEN always", OT, "\"GREEN\" if reading is not None and reading[0] == \"green\" else", "\"GREEN\" if True else"),
 ("one_pr unjudged->GREEN", OT, "f\"WAIT:{','.join(reading[1])}\" if reading is not None else \"UNJUDGED\")", "f\"WAIT:{','.join(reading[1])}\" if reading is not None else \"GREEN\")"),
 ("replan stall ignores classify", OT, "if not runs or req is None or self._classify_reading(h, runs, req)[0] != \"green\":", "if not runs:"),
 ("flow wrong False", TP, "\"wrong\": seen[-1][2] != \"merge\"}", "\"wrong\": False}"),
 ("bench margin <=", TP, "and med[\"chain\"] < (1 - BENCH_MARGIN)", "and med[\"chain\"] <= (1 - BENCH_MARGIN)"),
 ("bench min prs dropped", TP, "beats = (all(len(v) >= BENCH_MIN_PRS for v in waits.values()) and", "beats = (True and"),
 ("bench green start dropped", TP, "max(r[\"verdict_at\"], g)", "r[\"verdict_at\"]"),
 ("bench wrong ignored", TP, "and not any(wrong.values())", "and True"),
 ("bench train path by any key", TP, "path = \"train\" if by_train.get(r[\"pr\"]) else \"chain\"", "path = \"chain\""),
 ("bench self-test call dropped", TP, "    _bench_self_test(check)\n", "    pass\n"),
]
shard, nsh = int(sys.argv[2]), int(sys.argv[3])
for i, (name, f, old, new) in enumerate(muts):
    if i % nsh != shard: continue
    tests = [f]
    p = root / f; src = p.read_text()
    c = src.count(old)
    if c != 1:
        print(f"SKIP {name}: anchor count {c}"); continue
    p.write_text(src.replace(old, new))
    try:
        res = []
        for t in tests:
            r = subprocess.run([sys.executable, t, "--self-test"], cwd=root, capture_output=True, text=True, timeout=900)
            fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if "FAIL" in l and "FAILED:" not in l or "Traceback" in l]
            if r.returncode != 0: res.append(f"{pathlib.Path(t).stem} rc={r.returncode} first: {(fails or ['?'])[0][:150]}")
        print(("KILLED " if res else "SURVIVED ") + name + (" :: " + " | ".join(res) if res else ""), flush=True)
    finally:
        p.write_text(src)
