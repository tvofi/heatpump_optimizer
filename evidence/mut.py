import subprocess, sys, pathlib
W = sys.argv[1]
F = pathlib.Path("custom_components/heatpump_optimizer/draw_range.py")
src = F.read_text()
RET = "    return ASK_FOLLOWS if slope >= FOLLOW_SLOPE_MIN and level_moves <= DISAGREE_FACTOR else ASK_IGNORED"
LVL = "    level_moves = float(high / low) ** abs(1.0 - slope)"
assert src.count(RET) == 1 and src.count(LVL) == 1
M = {
 "NULL": (RET, RET),
 "level_conjunct_dropped": (RET, RET.replace(" and level_moves <= DISAGREE_FACTOR", "")),
 "slope_conjunct_dropped": (RET, RET.replace("slope >= FOLLOW_SLOPE_MIN and ", "")),
 "and_to_or": (RET, RET.replace(" and ", " or ")),
 "level_lt": (RET, RET.replace("level_moves <=", "level_moves <")),
 "slope_gt": (RET, RET.replace("slope >=", "slope >")),
 "abs_dropped": (LVL, LVL.replace("abs(1.0 - slope)", "(1.0 - slope)")),
 "factor_to_1.5": (RET, RET.replace("<= DISAGREE_FACTOR", "<= 1.5")),
 "factor_to_1.2": (RET, RET.replace("<= DISAGREE_FACTOR", "<= 1.2")),
 "exponent_slope": (LVL, LVL.replace("abs(1.0 - slope)", "abs(slope)")),
 "level_moves_1": (LVL, "    level_moves = 1.0"),
}
S = "# `follows_ask`'s own thresholds"
E = "# MeasuredCop.judge_ratio holds a departure only while"
for name, (old, new) in M.items():
    F.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{W}/prelude.py').read())", S, E], capture_output=True, text=True, timeout=200)
        tail = [l for l in r.stdout.splitlines() if "BLOCK" in l]
        verdict = "SURVIVED" if r.returncode == 0 else "KILLED"
        if name == "NULL":
            verdict = "NULL-PASS" if r.returncode == 0 else "NULL-FAIL"
        print(f"{verdict} {name} rc={r.returncode} {tail[-1] if tail else r.stderr.strip().splitlines()[-1:]}", flush=True)
    finally:
        F.write_text(src)
