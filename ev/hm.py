import subprocess, sys
M = [  # (name, file, old, new, cmd)
 ("c25 base predicate inverted (849)", "tools/audit/seat/review_packet.py", 'part line" if part_carries(prompt) else ""', 'part line" if not part_carries(prompt) else ""', "rp"),
 ("c25 base always empty (849)", "tools/audit/seat/review_packet.py", 'part line" if part_carries(prompt) else ""', 'part line" if False else ""', "rp"),
 ("c25 handoff ignores prompt (848)", "tools/audit/seat/review_packet.py", "carries = handoff_carries(prompt, live)", "carries = handoff_carries(None, live)", "rp"),
 ("c25 assigned ignored (619)", "tools/audit/seat/review_packet.py", "return assigned or found or None", "return found or None", "rp"),
 ("c25 hand branch disabled", "tools/audit/seat/review_packet.py", "    if hand:\n", "    if False:\n", "rp"),
 ("c25 gen branch disabled", "tools/audit/seat/review_packet.py", "    if not gen:\n        return None", "    if True:\n        return None", "rp"),
 ("c24 range predicate always true", "tools/audit/seat/cloud_dispatch.py", "if prev and prev[0] != design else", "if prev else", "cd"),
 ("c24 range predicate always false", "tools/audit/seat/cloud_dispatch.py", "if prev and prev[0] != design else", "if False else", "cd"),
 ("c24 render guard always off", "tools/audit/seat/cloud_dispatch.py", '+ (round_context(topic, design, verdict) if verdict else ""))', '+ (""))', "cd"),
 ("c24 role tuple narrowed", "tools/audit/seat/cloud_dispatch.py", 'if role in ("designer", "design-reviewer"):', 'if role in ("designer",):', "cd"),
 ("c24 fetch deleted (681)", "tools/audit/seat/cloud_dispatch.py", '            _git(repo_dir, "fetch", "-q", "origin", vref)\n', '            pass\n', "cd"),
 ("c10 isinstance guard inverted", "tools/audit/seat/review_strength.py", "if isinstance(model, str) else", "if not isinstance(model, str) else", "rs"),
 ("c10 string branch returns none", "tools/audit/seat/review_strength.py", "(model if isinstance(model, str) else", "(None if isinstance(model, str) else", "rs"),
 ("NULL (identical replacement)", "tools/audit/seat/review_strength.py", "if isinstance(model, str) else", "if isinstance(model, str) else", "rs"),
]
CMD = {"rp": ["python3", "tools/audit/seat/review_packet.py", "--self-test"],
       "cd": ["python3", "-I", "tools/audit/seat/cloud_dispatch.py", "--self-test"],
       "rs": ["python3", "tools/audit/seat/review_strength.py", "--self-test"]}
for name, f, old, new, c in M:
    src = open(f).read()
    if src.count(old) != 1:
        print(f"RESULT {name}: NOT-APPLIED (anchor count {src.count(old)})"); continue
    open(f, "w").write(src.replace(old, new))
    try:
        r = subprocess.run(CMD[c], capture_output=True, text=True, timeout=300)
        tail = [l for l in (r.stdout + r.stderr).splitlines() if "checks," in l or "Error" in l][-1:] 
        print(f"RESULT {name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {tail}", flush=True)
    finally:
        open(f, "w").write(src)
subprocess.run(["git", "diff", "--stat"])
