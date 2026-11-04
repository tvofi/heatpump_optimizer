"""Reviewer-built mutant driver for #3200 at c46a9c6a (the reviewer's own instrument).
Each mutant: anchor must occur exactly once; apply; run the owning self-test(s); restore."""
import subprocess, sys, pathlib
R = pathlib.Path(sys.argv[1])
T = "tools/audit/seat/orchestrator_tick.py"; C = "tools/pr/ci_predict.py"; L = "tools/audit/seat/ledger.py"
TT = ["python3", T, "--self-test"]
M = {
 "A01_train_arm": (T, '            return "train", "", ""', '            pass'),
 "A02_blocked_newer_exempt": (T, '            if newer:\n                return "fixer-round", "", ""', '            if False:\n                return "fixer-round", "", ""'),
 "A03_verdicted": (T, '            return "verdicted", "", ""', '            pass'),
 "A04_verdict_pending": (T, '            return "verdict-pending", "", ""', '            pass'),
 "A05_waiting_file_overlap": (T, 'if not f.startswith(ROW_DIR)}:\n                return "waiting-on"', 'if not f.startswith(ROW_DIR)}:\n                pass; "waiting-on"'),
 "A06_waiting_after_edge": (T, '== a:\n                        return "waiting-on", f"#{m}", ""', '== a:\n                        pass'),
 "A07_dirty_arm": (T, '        if ms == "DIRTY":\n            return "owed"', '        if False:\n            return "owed"'),
 "A08_body_ahead_in_head": (T, 'body_age < head_age and in_head', 'body_age < head_age'),
 "A09_fire_grace": (T, 'if age > FIRE_GRACE_MIN and not', 'if age >= 0 and not'),
 "A10_owed_levels_unwired": (T, '        self.owed_levels(S, prs)\n', ''),
 "A11_record_skip_owed": (T, '"record branch"\n                   if branch == record else', '"record branch"\n                   if False else'),
 "A12_crit_order": (T, '(0 if group in crit else 1, n,', '(1, n,'),
 "A13_O3_none_unreadable": (T, '            if newer is None:\n                return "unreadable"', '            if False:\n                return "unreadable"'),
 "A14_not_bucketed_tail": (T, '                     if skipped else ""))', '                     if False else ""))'),
 "A15_unreadable_printed": (T, '            if bucket == "unreadable":\n', '            if False:\n'),
 "A16_stuck_null": (T, '        except ValueError:\n            return True\n        return (self.now - st)', '        except ValueError:\n            return False\n        return (self.now - st)'),
 "A17_selftest_not_train": (T, ' or "--self-test" in cmd:', ':'),
 "A18_recut_threshold": (T, 'if blocked >= RECUT_BLOCKED and', 'if blocked > RECUT_BLOCKED and'),
 "A19_recut_split_exempt": (T, ' and "## Re-cut" not in (pr.get("body") or ""):', ':'),
 "A20_blocked_stall": (T, '            if age_h >= self.stall_hours:', '            if False:'),
 "A21_red_unowned": (T, "        if getattr(self, \"_red\", {}).get(n) and not", "        if False and not"),
 "A22_parked": (T, '        if n in parked:\n', '        if False:\n'),
 "A23_body_ahead_seat": (T, ' and in_head\n                    and not self._seat_on(n, topics, heads, kinds=("handoff-wip", "handoff"))):', ' and in_head):'),
 "A24_seat_window": (T, '                if age is not None and age <= SEAT_WINDOW_MIN:', '                if age is not None:'),
 "A25_claim_files_excluded": (T, ' and f not in CLAIM_FILES}', '}'),
 "A26_verdict_kind_head": (T, 'return m.group(1) if m and m.group(2) == head else None', 'return m.group(1) if m else None'),
 "A27_queue_ancestor": (T, 'if v and (v == head or self.git(["merge-base", "--is-ancestor", v, head])[0] == 0):', 'if v and (v == head):'),
 "A28_heads_none": (T, '        if heads is None:\n            self.unreadable(S, "owed buckets"', '        if False:\n            self.unreadable(S, "owed buckets"'),
 "A29_fired_window": (T, 'if (when is None or when >= cutoff) and', 'if True and'),
 "A30_review_owed_record_arg": (T, '                                       getattr(rr, "RECORD_BRANCH", None)):\n                self.line', '                                       None):\n                self.line'),
 "A31_ledger_skip_branch": (L, '\\\n                or (skip_branch and pr.get("headRefName") == skip_branch):', ':'),
 "A32_ci_quoted_subcmd": (C, r'''_RUNS_SELF_TEST = re.compile(r"--self[-_]test|[\"']self-test[\"']")''', r'''_RUNS_SELF_TEST = re.compile(r"--self[-_]test")'''),
 "A33_ci_old_word": (C, r'''_RUNS_SELF_TEST = re.compile(r"--self[-_]test|[\"']self-test[\"']")''', r'''_RUNS_SELF_TEST = re.compile(r"self[-_]test")'''),
 "A34_ci_quoted_any_quote_ok_underscore": (C, r'''[\"']self-test[\"']")''', r'''[\"']self[-_]test[\"']")'''),
 "A35_gate_contexts": (T, 'GATE_CONTEXTS = {"gate", "pr-contract"}', 'GATE_CONTEXTS = set()'),
 "A36_stuck_factor": (T, 'STUCK_FACTOR = 2 ', 'STUCK_FACTOR = 3 '),
}
OWN = {T: [TT, ["python3", "tools/audit/seat/r10_ledger_mutants.py", "--self-test"]],
       C: [["python3", C, "--self-test"]],
       L: [TT, ["python3", L, "--self-test"], ["python3", "tools/audit/seat/r10_ledger_mutants.py", "--self-test"]]}
only = sys.argv[2:]
for k, (f, a, b) in M.items():
    if only and k not in only: continue
    p = R / f; src = p.read_text()
    n = src.count(a)
    if n != 1:
        print(f"ANCHOR {k}: occurs {n}x", flush=True); continue
    p.write_text(src.replace(a, b))
    try:
        res = []
        for cmd in OWN[f]:
            r = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=600)
            out = r.stdout + r.stderr
            fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
            res.append((r.returncode, cmd[1].split("/")[-1], fails, out.strip().splitlines()[-1:] ))
        killed = any(rc != 0 for rc, *_ in res)
        print(f"{'KILLED ' if killed else 'SURVIVED'} {k}: " + " | ".join(f"{s} rc={rc} {tail} {fails[:2]}" for rc, s, fails, tail in res), flush=True)
    finally:
        p.write_text(src)
