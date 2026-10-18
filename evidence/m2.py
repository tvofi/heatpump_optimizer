import subprocess, sys, pathlib
F = pathlib.Path("/home/user/heatpump_optimizer/tools/audit/carry_audit.py")
orig = F.read_bytes()
s0 = orig.decode()
LINE = 'segs.append(text[at:starts[i + 1] if i + 1 < len(starts) else len(text)].split("\\n", 1)[0])'
M = [("M15b-line-cut", LINE, 'segs.append(text[at:starts[i + 1] if i + 1 < len(starts) else len(text)])'),
     ("M16-next-cut", LINE, 'segs.append(text[at:len(text)].split("\\n", 1)[0])'),
     ("SPAN-skip", "        if any(a <= at < b for a, b in spans):\n            continue\n", ""),
     ("ITEMREF-bare", r'ITEM_REF = re.compile(r"\(item\s+([0-9a-f]{8})\)")', r'ITEM_REF = re.compile(r"\bitem\s+([0-9a-f]{8})\b")'),
     ("SEG-scope", "        for ref in ITEM_REF.findall(seg):", "        for ref in ITEM_REF.findall(text):")]
try:
  for name,a,b in M:
    assert s0.count(a)==1, (name, s0.count(a))
    F.write_text(s0.replace(a,b))
    r = subprocess.run([sys.executable,"-I",str(F),"--self-test"],capture_output=True,text=True,cwd=F.parents[2])
    print(f"RESULT mutant={name} rc={r.returncode}", r.stdout.strip().splitlines()[-1])
    for l in [l for l in r.stdout.splitlines() if "FAIL" in l][:3]: print("   ",l)
finally:
  F.write_bytes(orig)
