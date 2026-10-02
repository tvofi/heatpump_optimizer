import subprocess, sys, json
from pathlib import Path
P = Path("tests/mutation_table.py"); orig = P.read_text()
code = ("import sys,json;sys.path.insert(0,'tests');import mutation_table as mt;"
        "s=[m for m in mt.inventory() if m['kind']=='CMP_BOUND'];"
        "import ast;bad=0\n"
        "for m in s:\n"
        "  t=m['new'].strip(); t=t+' pass' if t.endswith(':') else t\n"
        "  try: ast.parse(t)\n"
        "  except SyntaxError: bad+=1\n"
        "print(len(s), bad, json.dumps(sorted(m['file']+':'+str(m['line'])+' '+m['new'].strip() for m in s))[:0])")
M = {"base": ("",""),
     "R5": ("if bounds and isinstance(node, ast.Compare) and _one_line(node, lines):", "if bounds and isinstance(node, ast.Compare):"),
     "R6": ("if flip and gap.strip(\" \\t()\") == flip[0]:", "if flip:")}
for k,(a,b) in M.items():
    if a: P.write_text(orig.replace(a,b))
    try:
        r = subprocess.run(["python3","-c",code],capture_output=True,text=True)
        print(f"RESULT inv_under [{k}] cmp_sites unparsable =", r.stdout.strip(), r.stderr.strip()[-200:])
    finally: P.write_text(orig)
