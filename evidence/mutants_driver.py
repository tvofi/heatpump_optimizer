import subprocess, sys, shutil, pathlib
WT = pathlib.Path(sys.argv[1])
OT = "tools/audit/seat/orchestrator_tick.py"; LG = "tools/audit/seat/ledger.py"; CP = "tools/pr/ci_predict.py"
M = [
 ("M01 ledger record skip", LG, "or (skip_branch and pr.get(\"headRefName\") == skip_branch)", "or False"),
 ("M02 gate-race arm", OT, "elif req_red and run and set(req_red) <= GATE_CONTEXTS:", "elif False:"),
 ("M03 self-test exclusion", OT, ' or "--self-test" in cmd:', ':'),
 ("M04 null started_at", OT, "        except ValueError:\n            return True\n        return (self.now - st)", "        except ValueError:\n            return False\n        return (self.now - st)"),
 ("M05 PARK arm", OT, "        if n in parked:\n", "        if False:\n"),
 ("M06 train bucket", OT, 'return "train", "", ""', 'pass'),
 ("M07 recut threshold 4", OT, "RECUT_BLOCKED = 3 ", "RECUT_BLOCKED = 4 "),
 ("M08 recut re-cut body", OT, 'and "## Re-cut" not in (pr.get("body") or "")', ''),
 ("M09 blocked age threshold", OT, "if age_h >= self.stall_hours:", "if False:"),
 ("M10 blocked newer handoff", OT, "            if newer:\n                return \"fixer-round\"", "            if False:\n                return \"fixer-round\""),
 ("M11 verdicted bucket", OT, 'return "verdicted", "", ""', 'pass'),
 ("M12 verdict-pending bucket", OT, 'return "verdict-pending", "", ""', 'pass'),
 ("M13 waiting-on files", OT, 'if m < n and mine & {f', 'if False and mine & {f'),
 ("M14 waiting-on after-edge", OT, '                    if rl.group_for_branch(roster, other.get("headRefName") or "") == a:', '                    if False:'),
 ("M15 DIRTY arm", OT, 'if ms == "DIRTY":', 'if False:'),
 ("M16 red-unowned seat test", OT, 'if getattr(self, "_red", {}).get(n) and not self._seat_on(n, topics, heads):', 'if getattr(self, "_red", {}).get(n):'),
 ("M17 red-unowned arm", OT, 'if getattr(self, "_red", {}).get(n) and not self._seat_on(n, topics, heads):', 'if False:'),
 ("M18 seat window cutoff", OT, "if (when is None or when >= cutoff)", "if (True)"),
 ("M19 fire payload key", OT, 'r"#{n}(?!\\d)|payload-(?:fix-)?{n}-r\\d+\\.json"', 'r"#{n}(?!\\d)"'),
 ("M20 handoff-wip seat", OT, "if age is not None and age <= SEAT_WINDOW_MIN:", "if False:"),
 ("M21 body-ahead in_head", OT, "and body_age < head_age and in_head", "and body_age < head_age"),
 ("M22 body-ahead age compare", OT, "and body_age < head_age and in_head", "and in_head"),
 ("M23 body-ahead seat", OT, "                    and not self._seat_on(n, topics, heads, kinds=(\"handoff-wip\", \"handoff\"))):", "                    ):"),
 ("M24 fire-owed grace", OT, "if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in fired):", "if not any(f.name in l for _, l in fired):"),
 ("M25 fire-owed fired check", OT, "if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in fired):", "if age > FIRE_GRACE_MIN:"),
 ("M26 PARK after last STARTED", OT, "for l in lines[start + 1:]:", "for l in lines:"),
 ("M27 owed_levels call", OT, "        self.owed_levels(S, prs)\n", ""),
 ("M28 tick passes record branch", OT, '                                       getattr(rr, "RECORD_BRANCH", None)):', '                                       None):'),
 ("M29 owed_levels record skip", OT, " or branch == record or", " or"),
 ("M30 crit ordering", OT, "owed.append((0 if group in crit else 1,", "owed.append((1 if group in crit else 0,"),
 ("M31 STUCK_FACTOR 3", OT, "STUCK_FACTOR = 2 ", "STUCK_FACTOR = 3 "),
 ("M32 ci_predict regex", CP, 're.search(r"--self[-_]test", ln)', 're.search(r"self[-_]test", ln)'),
]
only = sys.argv[2:] 
for name, f, a, b in M:
    if only and name.split()[0] not in only: continue
    p = WT / f; src = p.read_text()
    if src.count(a) != 1:
        print(f"{name}: PATTERN COUNT {src.count(a)}", flush=True); continue
    p.write_text(src.replace(a, b))
    try:
        cmd = ["python3", CP, "--self-test"] if f == CP else ["python3", OT, "--self-test"]
        r = subprocess.run(cmd, cwd=WT, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith(("FAIL", "FAILED")) or " FAIL " in l][:4]
        summ = [l for l in out.splitlines() if "self-test:" in l][-1:] 
        print(f"{name}: rc={r.returncode} {summ} {fails}", flush=True)
    finally:
        p.write_text(src)
