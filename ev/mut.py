import subprocess, sys, os, re, shutil, tempfile
sha = sys.argv[1]; only = sys.argv[2:] 
P = "custom_components/heatpump_optimizer/"
M = {
 "M1": (P+"debugger.py", "        if entry is not None:\n", "        if False:\n"),
 "M2": (P+"debugger.py", "        return None if PRIVATE_ENTITY_ID.search(node) else node\n", "        return node\n"),
 "M3": (P+"debugger.py", "        if download_bytes(whole) + DOWNLOAD_HEADROOM_BYTES <= INLINE_CAP_BYTES:\n", "        if True:\n"),
 "M4": (P+"debugger.py", '        "version": coordinator.integration_version,\n', ""),
 "M5": (P+"replay_doc.py", '        raise Refused("refusing to write: " + "; ".join(left[:5]))\n    return clean\n', '        raise Refused("refusing to write: " + "; ".join(left[:5]))\n    return raw\n'),
 "M6": (P+"store.py", '        "rows/#/version": _TEXT,\n', ""),
 "M7": (P+"debugger.py", '    before = [s for s in states if s.last_updated < start]\n', '    return states\n'),
 "M8": (P+"debugger.py", '    if wants["candidates"] is not None:\n', '    if False:\n'),
 "MA": (P+"replay_doc.py", "_collect_strings(value, dropped, bool(SECRET_KEY.search(str(key))))", "_collect_strings(value, dropped, False)"),
 "MB": (P+"replay_doc.py", "    if isinstance(node, bool) or node is None:\n        return\n", "    if False:\n        return\n"),
 "MC": (P+"replay_doc.py", "if SECRET_KEY.search(str(key)) or not KEY.match(str(key)):", "if not KEY.match(str(key)):"),
 "MD": (P+"replay_doc.py", "    if leaked:\n        raise Refused(", "    if False:\n        raise Refused("),
 "R1": (P+"replay_doc.py", "len(s) >= 6 and s in blob", "len(s) >= 7 and s in blob"),
 "R2": (P+"replay_doc.py", "    if left:\n        raise Refused(\"refusing to write: \" + ", "    if False:\n        raise Refused(\"refusing to write: \" + "),
}
LIT = ("s3cret-value", "bob123456", "abc123456", "secretvalue123")
for name in (["M0"] + only if only else ["M0"] + list(M)):
    d = tempfile.mkdtemp()
    subprocess.run(f"git -C /home/user/heatpump_optimizer archive {sha} | tar -x -C {d}", shell=True, check=True)
    if name != "M0":
        f, a, b = M[name]; p = os.path.join(d, f); s = open(p).read()
        n = s.count(a)
        if n != 1: print(f"RESULT mutant={name} sha={sha[:8]} APPLY-FAILED matches={n}"); continue
        open(p, "w").write(s.replace(a, b))
    r = subprocess.run([sys.executable, "tests/debug_collect.py"], cwd=d, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True, timeout=1200)
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if "FAIL" in l and not l.lstrip().startswith("a16:")]
    lit = [l for l in fails if any(x in l for x in LIT)]
    last = [l for l in out.splitlines() if l.strip()][-1:] 
    print(f"RESULT mutant={name} sha={sha[:8]} rc={r.returncode} fail_lines={len(fails)} fail_lines_with_credential={len(lit)} last={last[0][:110] if last else ''!r}", flush=True)
    shutil.rmtree(d)
