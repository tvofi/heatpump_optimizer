#!/usr/bin/env python3
"""Reviewer's block mutants of price_tiles.take / the tile caller, one edit each on a
scratch worktree of the head, the round's block of tests/features.py as the command."""
import subprocess, sys, os, pathlib
WT = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
PT = WT / "custom_components/heatpump_optimizer/price_tiles.py"
CO = WT / "custom_components/heatpump_optimizer/coordinator.py"
START = "async def _st_tiles():"
END = 'R.check(\n    "#1753: the background callers\' steady pairs leave the user\'s slot and "'
CLOCK = "        if 0.0 <= (now - taken).total_seconds() < STEADY_REFRESH_HOURS * 3600.0:\n"
MUTS = [
 ("control", None, None, None),
 ("null_comment", PT, "STEADY_REFRESH_HOURS = 6.0\n", "STEADY_REFRESH_HOURS = 6.0  # null\n"),
 ("p1_clock_if_false", PT, CLOCK, "        if False:\n"),
 ("p2_first_turn_taken", PT, "        taken = _STEADY_TAKEN.setdefault(owner, now)\n" + CLOCK,
    "        taken = _STEADY_TAKEN.get(owner)\n        if taken is not None and 0.0 <= (now - taken).total_seconds() < STEADY_REFRESH_HOURS * 3600.0:\n"),
 ("p3_stamp_not_moved", PT, "        _STEADY_TAKEN[owner] = now\n", "        pass\n"),
 ("p4_lower_bound_dropped", PT, CLOCK, "        if (now - taken).total_seconds() < STEADY_REFRESH_HOURS * 3600.0:\n"),
 ("p5_one_clock_for_all_owners", PT, "        taken = _STEADY_TAKEN.setdefault(owner, now)\n" + CLOCK + "            return None\n        _STEADY_TAKEN[owner] = now\n",
    "        taken = _STEADY_TAKEN.setdefault(take, now)\n" + CLOCK + "            return None\n        _STEADY_TAKEN[take] = now\n"),
 ("p8_clock_in_minutes", PT, "STEADY_REFRESH_HOURS * 3600.0:", "STEADY_REFRESH_HOURS * 60.0:"),
 ("p9_stamp_moved_on_every_turn", PT, "        taken = _STEADY_TAKEN.setdefault(owner, now)\n" + CLOCK + "            return None\n",
    "        taken = _STEADY_TAKEN.setdefault(owner, now)\n" + CLOCK + "            _STEADY_TAKEN[owner] = now\n            return None\n"),
 ("p10_tile_asks_no_steady", CO, 'limited=False, base=record, steady="power_cap_kw" in overrides', "limited=False, base=record, steady=False"),
 ("p11_cap_tile_reads_settled", PT, 'key = "monthly_steady_cost_delta" if "power_cap_kw" in overrides', 'key = "monthly_settled_cost_delta" if "power_cap_kw" in overrides'),
 ("p12_cursor_not_moved_on_held_turn", PT, CLOCK + "            return None\n", CLOCK + "            _CURSORS[owner] = cursor\n            return None\n"),
]
env = dict(os.environ, PYTHONPATH="tests/hastub")
pre = OUT / "prelude.py"
r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", str(pre), START, END], cwd=WT, env=env, capture_output=True, text=True)
print("emit-prelude rc", r.returncode, flush=True)
for name, path, old, new in MUTS:
    if path is not None:
        src = path.read_text()
        assert src.count(old) == 1, (name, src.count(old))
        path.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f'exec(open("{pre}").read())', START, END],
                           cwd=WT, env=env, capture_output=True, text=True, timeout=900)
        log = r.stdout + "\n--stderr--\n" + r.stderr
        (OUT / f"{name}.log").write_text(log[-6000:])
        fails = [l.strip()[:150] for l in r.stdout.splitlines() if l.strip().startswith(("FAIL", "✗", "not ok")) or " FAIL" in l[:8]]
        last = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()][-1][:200]
        print(f"RESULT {name}: rc={r.returncode} | {last} | fails={fails}", flush=True)
    finally:
        if path is not None:
            path.write_text(src)
print(subprocess.run(["git", "status", "--short"], cwd=WT, capture_output=True, text=True).stdout or "git status --short: empty")
