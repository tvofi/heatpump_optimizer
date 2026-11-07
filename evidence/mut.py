import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); f = root/"tools/audit/seat/outside_intake.py"
orig = f.read_text()
M = [
 # round-3 delta (Thread.mark)
 ("thirdbot_moves_out", '        if c["login"] not in OURS:\n            return\n', '        if c["login"] not in OURS:\n            self.last_out = max(self.last_out, c["at"])\n            return\n'),
 ("mark_guard_false", '        if c["login"] not in OURS:\n            return\n', '        if False:\n            return\n'),
 ("mark_guard_outside", '        if c["login"] not in OURS:\n            return\n', '        if outside(c["login"], c["type"]):\n            return\n'),
 ("mark_old_restored_EQUIV", '        if c["login"] not in OURS:\n            return\n', '        if c["login"] not in OURS:\n            if outside(c["login"], c["type"]):\n                self.last_out = max(self.last_out, c["at"])\n            return\n'),
 # saw() now sole owner of last_out
 ("saw_no_last_out", '        self.last_out = max(self.last_out, at)\n', ''),
 ("saw_first_max", '        self.first = min(self.first or at, at)', '        self.first = max(self.first or at, at)'),
 ("one_thread_bot_saw", '    for c in cs:\n        if outside(c["login"], c["type"]):\n            t.saw', '    for c in cs:\n        if True:\n            t.saw'),
 ("one_thread_no_comment_saw", '    for c in cs:\n        if outside(c["login"], c["type"]):\n            t.saw(c["login"], c["at"])\n', '    for c in cs:\n'),
 ("one_thread_no_mark", '            t.saw(c["login"], c["at"])\n        t.mark(c)\n', '            t.saw(c["login"], c["at"])\n'),
 ("one_thread_opener_bot", '        if outside(r["login"], r["type"]):\n            t.saw(r["login"], r["at"])', '        if True:\n            t.saw(r["login"], r["at"])'),
 ("one_thread_pr_reviews_drop", '        if r["kind"] == "pr":\n            cs +=', '        if False:\n            cs +='),
 ("one_thread_disc_opener", '        if outside(d["login"], d["type"]):\n            t.saw(d["login"], d["at"])', '        if False:\n            t.saw(d["login"], d["at"])'),
 ("one_thread_return_all", '    return t if t.by else None', '    return t'),
 ("scan_no_mark", '        for c in cs:\n            t.mark(c)\n', '        for c in cs:\n            pass\n'),
 ("scan_since_ignored", '        if at >= since and outside(login, typ):', '        if outside(login, typ):'),
 ("scan_bot_saw", '        if at >= since and outside(login, typ):', '        if at >= since:'),
 ("scan_disc_kind", '        if t.n in disc:\n            t.kind = "discussion"', '        if False:\n            t.kind = "discussion"'),
 ("scan_review_comments_drop", '("pulls/comments", "pull_request_url")', ''),
 # owed
 ("owed_reply_ge", '"reply" if t.last_out > max(disposed, t.last_ours) else None', '"reply" if t.last_out >= max(disposed, t.last_ours) else None'),
 ("owed_ignore_last_ours", '"reply" if t.last_out > max(disposed, t.last_ours) else None', '"reply" if t.last_out > disposed else None'),
 ("owed_refused_ignored", '    disposed = max(t.answered, t.refused)', '    disposed = t.answered'),
 ("owed_live_ignored", '"answer" if live else "wait"', '"answer"'),
 ("owed_triage_none", '    return "triage"', '    return None'),
 # mark ours
 ("mark_answered_drop", '        if c.get("answered"):\n            self.answered', '        if False:\n            self.answered'),
 ("mark_refused_drop", '        if c.get("refused"):\n            self.refused', '        if False:\n            self.refused'),
 ("last_ours_drop", '        self.last_ours = max(self.last_ours, c["at"])\n', ''),
 # identity
 ("bots_outside", 'return login not in OURS and typ != "Bot"', 'return login not in OURS'),
 ("ours_ignored", 'return login not in OURS and typ != "Bot"', 'return typ != "Bot"'),
 # dispose
 ("dispose_twice", '    if t.refused or t.answered:\n        return 1', '    if False:\n        return 1'),
 ("dispose_disc", '    if t.kind == "discussion":\n        return 1', '    if False:\n        return 1'),
 ("dispose_no_group", '        if group is None:\n            return 1', '        if False:\n            return 1'),
 ("dispose_not_live", '        if not ok:\n            return 1', '        if False:\n            return 1'),
 ("dispose_none_thread", '    if t is None:\n        return 1', '    if False:\n        return 1'),
 ("refused_mark_drop", '        body = f"{REFUSED_MARK}\\n{body}"', '        body = f"{body}"'),
 ("answer_mark_drop", '    return (f"{ANSWER_MARK}\\nThank', '    return (f"\\nThank'),
 # post
 ("post_rc", '    return runner(argv).returncode', '    runner(argv); return 0'),
 ("dry_drop", ' + (["--dry-run"] if dry else [])', ''),
 ("dry_always", '(["--dry-run"] if dry else [])', '(["--dry-run"])'),
 ("post_issue_arg", '"--issue", str(n)', '"--issue", str(n+1)'),
 ("script_path", '"tools/pr/gh_comment.py"', '"tools/pr/gh_commentX.py"'),
 # listing
 ("keep_now", '        keep = min(keep, t.first)\n', ''),
 ("wait_counted_as_line", '        if word == "wait":\n            waiting += 1\n            continue\n', ''),
 ("unavailable_line_drop", '    if waiting:\n        lines.append', '    if False:\n        lines.append'),
 ("rows_rc_ignored", '    if rc != 0:\n        raise Unreadable(f"gh {', '    if False:\n        raise Unreadable(f"gh {'),
 ("has_disc_ignored", '    if out.strip() != "true":\n        return []', '    if False:\n        return []'),
 ("who_no_suffix", '            login = f"{login}[bot]"', '            pass'),
 ("plan_live_200", 'return r.status == 200,', 'return True,'),
]
CMD=[sys.executable,"-I","-c","import sys; sys.path.insert(0,'tools/audit/seat'); import outside_intake_selftest as s; sys.exit(s.run(False))"]
null = subprocess.run(CMD,capture_output=True,text=True,cwd=root)
print(f"NULL(cases-only) rc={null.returncode} {null.stdout.strip().splitlines()[-1]}", flush=True)
try:
  for name,a,b in M:
    if orig.count(a)!=1: print(f"{name} NOAPPLY count={orig.count(a)}"); continue
    f.write_text(orig.replace(a,b))
    r = subprocess.run(CMD,capture_output=True,text=True,cwd=root,timeout=300)
    fails=[l for l in (r.stdout+r.stderr).splitlines() if "FAIL" in l[:8] or l.startswith(("not ok","Traceback"))]
    print(f"{name} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {fails[0][:160] if fails else ''}", flush=True)
finally:
  f.write_text(orig)
