import subprocess, sys, pathlib, shutil
src = pathlib.Path("/home/user/rev/tools/pr/cancel_superseded.py").read_text()
M = {
 "sweep-main-skip": ('if b == "main" or r.get("event") not in EVENTS or (hr and hr != repo):', 'if r.get("event") not in EVENTS or (hr and hr != repo):'),
 "sweep-event-skip": ('if b == "main" or r.get("event") not in EVENTS or (hr and hr != repo):', 'if b == "main" or (hr and hr != repo):'),
 "fork-run": ('if b == "main" or r.get("event") not in EVENTS or (hr and hr != repo):', 'if b == "main" or r.get("event") not in EVENTS:'),
 "live-bound": ('bound = max([int(r["id"]) for r in rs if r.get("head_sha") == sha] or [sys.maxsize])', 'bound = sys.maxsize'),
 "unreadable-prs": ('    if not isinstance(prs, list):\n        print("CANCEL-SWEEP: unreadable answer; cancelling nothing")\n        return 0\n', '    prs = prs or []\n'),
 "unreadable-runs": ('        if rs is None:\n            prs = None\n            break\n', '        if rs is None:\n            continue\n'),
 "status-active": ('        if r.get("status") not in ACTIVE:\n            continue\n        b = r.get("head_branch")', '        b = r.get("head_branch")'),
 "commit-unreadable": ('                if not isinstance(c, dict):\n                    print("CANCEL-SWEEP: unreadable commit; cancelling nothing")\n                    return 0\n', '                if not isinstance(c, dict):\n                    c = {}\n'),
 "bot-detect": ('                    bot_heads.add(h.get("sha"))', '                    pass'),
 "bot-detect-name": ('                        or ((c.get("commit") or {}).get("author") or {}).get("name") == BOT):', '                        ):'),
 "no-pagination": ('        if len(rs) < PAGE:\n            return out, False', '        return out, False'),
 "no-truncation-line": ('        print(f"CANCEL-SWEEP: truncated: {t} still full', '        pass  # print(f"CANCEL-SWEEP: truncated: {t} still full'),
 "truncated-flag": ('    return out, True\n', '    return out, False\n'),
 "statuses-3": ('    for st in ACTIVE:\n        rs, cut', '    for st in ACTIVE[:3]:\n        rs, cut'),
 "bot-skip-plan": ('        if sha in bot_heads:\n            skipped += len(ids)\n            continue\n', ''),
 "kept-count": ('        kept += sum(1 for r in rs if r.get("head_sha") == sha)\n', ''),
 "ghost-add": ('            ghosts.append(int(r["id"]))\n            continue', '            continue'),
 "pr-open-state": ('if pr.get("state", "open") == "open" and (h.get', 'if (h.get'),
 "commit-only-cancel-prs": ('if any((by_id[i].get("head_branch") == h.get("ref")) for i in first["cancel"]):', 'if True:'),
 "sweep-dryrun": ('        if a.dry_run:\n            print(f"cancel_superseded: would cancel {rid}")\n            continue\n', ''),
}
for name,(a,b) in M.items():
    if src.count(a)!=1: print("MUTANT",name,"NOT-APPLIED count",src.count(a)); continue
    d=pathlib.Path("/home/user/w/m"); shutil.rmtree(d,ignore_errors=True); d.mkdir()
    (d/"cs.py").write_text(src.replace(a,b))
    p=subprocess.run([sys.executable,str(d/"cs.py"),"--self-test"],capture_output=True,text=True)
    fails=[l.strip() for l in p.stdout.splitlines() if "FAIL" in l]
    print("MUTANT",name,"rc",p.returncode,"|",p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-200:])
    for f in fails[:3]: print("   ",f[:220])
