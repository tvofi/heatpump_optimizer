import sys, subprocess, os
S, wt = sys.argv[1], sys.argv[2]
src = open(os.path.join(wt, ".claude/hooks/pre-edit.sh")).read()
L_PARTS = '#         parts += [str(e.get("new_string", "")) for e in edits if isinstance(e, dict)]\n'
M = {
 "M1 drop edits read":       (L_PARTS, ""),
 "M2 join space":            ('#     text = "\\n".join(parts)', '#     text = " ".join(parts)'),
 "M3 list->tuple guard":     ('#     if isinstance(edits, list):', '#     if isinstance(edits, tuple):'),
 "M4 drop dict guard":       (' for e in edits if isinstance(e, dict)]', ' for e in edits]'),
 "M5 old_string read":       ('e.get("new_string", "")', 'e.get("old_string", "")'),
 "M6 guard -> truthy":       ('#     if isinstance(edits, list):', '#     if edits:'),
 "M7 read only edits[0]":    (' for e in edits if isinstance(e, dict)]', ' for e in edits[:1] if isinstance(e, dict)]'),
 "M8 drop top-level fields": ('if k in ("new_string", "content", "new_source")]', 'if k in ()]'),
}
for name, (a, b) in M.items():
    assert src.count(a) == 1, name
    p = os.path.join(S, "mut", name.split()[0] + ".sh")
    open(p, "w").write(src.replace(a, b))
    r = subprocess.run(["bash", p, "--self-test"], cwd=wt, capture_output=True, text=True)
    fails = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
    tail = r.stdout.strip().splitlines()[-1]
    print(f"{name}: rc={r.returncode} {tail} -> {'KILLED' if r.returncode else 'SURVIVED'}")
    for f in fails: print("     ", f)
