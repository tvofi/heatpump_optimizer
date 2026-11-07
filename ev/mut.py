import subprocess, sys, pathlib
root = pathlib.Path("/home/user/rv"); f = root/"tools/audit/seat/outside_intake.py"
orig = f.read_text()
M = [
 ("r1_cursor_read", '                since = json.loads(a.cursor.read_text()).get("since") or since', '                pass'),
 ("r1_cursor_write", '{"since": keep}', '{"since": utc()}'),
 ("r1_post_rc", '    return runner(argv).returncode', '    runner(argv); return 0'),
 ("r1_dry_drop", ' + (["--dry-run"] if dry else [])', ''),
 ("r1_script_path", '"tools/pr/gh_comment.py"', '"tools/pr/gh_commentX.py"'),
 ("r1_list_rc", '    return 1 if lines else 0', '    return 0'),
 ("mark_revert_old", '        if c["login"] not in OURS:\n            if outside(c["login"], c["type"]):\n                self.last_out = max(self.last_out, c["at"])\n            return\n',
                     '        if outside(c["login"], c["type"]):\n            self.last_out = max(self.last_out, c["at"])\n            return\n'),
 ("mark_thirdbot_moves_out", '            if outside(c["login"], c["type"]):\n                self.last_out', '            if True:\n                self.last_out'),
 ("mark_no_last_out", '            if outside(c["login"], c["type"]):\n                self.last_out = max(self.last_out, c["at"])\n', '            pass\n'),
 ("who_no_suffix", '            login = f"{login}[bot]"', '            pass'),
 ("who_never_bot", '        if typ == "Bot":\n            login', '        if False:\n            login'),
 ("who_typ_user", '"Bot" if (a or {}).get("__typename") == "Bot" else "User"', '"User"'),
 ("cursor_exists_guard", '            if a.cursor and a.cursor.exists():', '            if False:'),
 ("cursor_write_skip", '    if a.cursor:\n        a.cursor.parent', '    if False:\n        a.cursor.parent'),
 ("dry_always", '(["--dry-run"] if dry else [])', '(["--dry-run"])'),
 ("post_issue_arg", '"--issue", str(n)', '"--issue", str(n+1)'),
 ("last_ours_drop", '        self.last_ours = max(self.last_ours, c["at"])\n', ''),
 ("keep_now", '        keep = min(keep, t.first)\n', ''),
]
null = subprocess.run([sys.executable,"-I",str(f),"--self-test"],capture_output=True,text=True,cwd=root)
print(f"NULL rc={null.returncode} {null.stdout.strip().splitlines()[-1]}")
try:
  for name,a,b in M:
    if orig.count(a)!=1: print(f"{name} NOAPPLY count={orig.count(a)}"); continue
    f.write_text(orig.replace(a,b))
    r = subprocess.run([sys.executable,"-I",str(f),"--self-test"],capture_output=True,text=True,cwd=root,timeout=300)
    fails=[l for l in (r.stdout+r.stderr).splitlines() if l.startswith(("FAIL","not ok","Traceback")) or "FAIL" in l[:6]]
    print(f"{name} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {fails[0][:150] if fails else ''}")
finally:
  f.write_text(orig)
