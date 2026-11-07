import json, re, subprocess, sys, ast, pathlib, shutil, os
wt = pathlib.Path(sys.argv[1]); pins = sys.argv[2:]
def func_range(src, qual):
    tree = ast.parse(src); parts = qual.split(".")
    def walk(nodes, parts):
        for n in nodes:
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.name==parts[0]:
                if len(parts)==1: return n
                return walk(n.body, parts[1:])
    n = walk(tree.body, parts); return (n.lineno, n.end_lineno)
for p in pins:
    d = json.load(open(wt/p))
    path, qual, kind, h = re.match(r"(\S+):(\S+) (\S+) (\S+)", d["anchor"]).groups()
    mut = re.search(r"\(`(.*?)`\)", d["reason"]).group(1)
    f = wt/path; orig = f.read_text(); lines = orig.split("\n")
    a,b = func_range(orig, qual)
    hits = [i for i in range(a-1,b) if lines[i]==d["old"]]
    if len(hits)!=1: print("AMBIG", p, hits); continue
    i=hits[0]; ind = re.match(r"\s*", lines[i]).group(0)
    lines[i] = mut if mut.startswith(" ") else ind+mut.lstrip()
    f.write_text("\n".join(lines))
    try:
        r = subprocess.run(["python3", d["killed_by"]], cwd=wt, capture_output=True, text=True, timeout=1800)
    finally:
        f.write_text(orig)
    print(("KILLED" if r.returncode!=0 else "SURVIVED"), "rc=%d"%r.returncode, kind, qual, "->", d["killed_by"], "|", r.stdout.strip().splitlines()[-1][:150] if r.stdout.strip() else r.stderr.strip()[-150:], flush=True)
