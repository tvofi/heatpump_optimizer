"""Reviewer's own mutant runner (fix-review step 1): edit one file, run one script, restore."""
import os, subprocess, sys

WT = "/tmp/claude-0/wtm"
J2 = "/tmp/claude-0/-home-user-heatpump-optimizer/7331d838-5084-598b-bd81-b25fab97f4c4/scratchpad/j2"
WF = "custom_components/heatpump_optimizer/wood_fuel.py"
CO = "custom_components/heatpump_optimizer/coordinator.py"
BP = "blueprints/automation/notify_wood_cheaper_window.yaml"
WA = ["python3", "tests/wood_advisor.py"]
FE = ["python3", "tests/features.py"]

MUTANTS = [
    ("coord: local_tz arg deleted", CO, "            local_tz=dt_util.DEFAULT_TIME_ZONE,\n", "", FE),
    ("coord: local_tz=None", CO, "local_tz=dt_util.DEFAULT_TIME_ZONE,", "local_tz=None,", FE),
    ("bp: notify_on_replan cond deleted", BP, '          - "{{ notify_on_replan }}"\n', "", WA),
    ("bp: not-yet-open clause deleted", BP, " and ws\n            > as_timestamp(now())", "", WA),
    ("bp: overlap seen.hit deleted", BP, "{% set\n            seen.hit = true %}", "", WA),
    ("bp: followup_until cond deleted", BP, '          - "{{ now() < today_at(followup_until) }}"\n', "", WA),
    ("bp: send_time cond deleted", BP, '          - "{{ now() >= today_at(send_time) }}"\n', "", WA),
    ("bp: overlap test inverted to equality (round-1 rule)", BP,
     "ws <\n            as_timestamp(o.end) and as_timestamp(o.start) < we",
     "ws ==\n            as_timestamp(o.start) and as_timestamp(o.end) == we", WA),
    ("bp: overlap test start-only", BP,
     "ws <\n            as_timestamp(o.end) and as_timestamp(o.start) < we",
     "ws ==\n            as_timestamp(o.start)", WA),
    ("bp: overlap strict -> non-strict (adjacent counts as overlap)", BP,
     "ws <\n            as_timestamp(o.end) and as_timestamp(o.start) < we",
     "ws <=\n            as_timestamp(o.end) and as_timestamp(o.start) <= we", WA),
    ("bp: daily trigger branch deleted", BP, "      - \"{{ trigger.id == 'daily' }}\"\n", "", WA),
    ("wf: one-step guard off", WF, "    if len(timestamps) < 2:\n", "    if False:\n", WA),
    ("wf: pump-off drop bool(on)", WF, "            bool(on)\n            and cop_f", "            cop_f", WA),
    ("wf: merge off", WF, "        if out and out[-1][1] == ts:", "        if False:", WA),
    ("wf: today break deleted", WF, "        if day(ts) != today:\n            break\n", "", WA),
    ("wf: UTC day", WF, "        return (ts.astimezone(local_tz) if local_tz is not None else ts).date()", "        return ts.date()", WA),
    ("wf: lead dropped", WF, "max(first_start - timedelta(minutes=lead_minutes), now)", "max(first_start, now)", WA),
    ("wf: now clip dropped", WF, "max(first_start - timedelta(minutes=lead_minutes), now)", "first_start - timedelta(minutes=lead_minutes)", WA),
    ("wf: lead option ignored", WF, "config.get(CONF_WOOD_LIGHTING_LEAD_MINUTES)", "None", WA),
    ("wf: iso local conversion dropped", WF, "        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()", "        return ts.isoformat()", WA),
    ("wf: iso local conversion dropped (features)", WF, "        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()", "        return ts.isoformat()", FE),
    ("wf: 493 if count -> if True (wood_advisor)", WF, "        if count:\n            cheap =", "        if True:\n            cheap =", WA),
    ("wf: 493 if count -> if True (features)", WF, "        if count:\n            cheap =", "        if True:\n            cheap =", FE),
    ("wf: 604 suppress guard off (features)", WF, "    if result is not None and det.suppressing:", "    if result is not None:", FE),
    ("wf: 604 suppress guard off (wood_advisor)", WF, "    if result is not None and det.suppressing:", "    if result is not None:", WA),
    ("null: comment added to wood_fuel (wood_advisor)", WF, "def lighting_window(", "# reviewer null control\ndef lighting_window(", WA),
]

only = sys.argv[1:]
env = dict(os.environ, PYTHONPATH=f"tests/hastub:{J2}")
for name, path, old, new, cmd in MUTANTS:
    if only and not any(o in name for o in only):
        continue
    p = os.path.join(WT, path)
    src = open(p).read()
    if src.count(old) != 1:
        print(f"RESULT {name}: NOT-APPLIED (anchor count {src.count(old)})", flush=True)
        continue
    open(p, "w").write(src.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True, timeout=1800)
        out = (r.stdout + r.stderr).strip().splitlines()
        fails = [l for l in out if "FAIL" in l or "Error" in l][:3]
        print(f"RESULT {name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} tail={out[-1] if out else ''!r} fails={fails}", flush=True)
    finally:
        open(p, "w").write(src)
r = subprocess.run(["git", "diff", "--exit-code", "--stat"], cwd=WT, capture_output=True, text=True)
print("RESTORED clean" if r.returncode == 0 else "NOT CLEAN " + r.stdout)
