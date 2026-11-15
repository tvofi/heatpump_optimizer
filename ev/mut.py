import subprocess, sys, tempfile, pathlib
src = pathlib.Path(sys.argv[1]); tests = sys.argv[2]
code = src.read_text(); mark = "# ------ self-test: mutants edit only"
head, tail = code.split(mark, 1)
M = {
 "overlap strict->le": ("if start < end:", "if start <= end:"),
 "ancestors drop self": ("(t.resolve(), *t.resolve().parents)", "(*t.resolve().parents,)"),
 "overlap unsorted": ("at = sorted(spans(t / f, here))", "at = spans(t / f, here)"),
 "splice wrong new": ('text = text[:start] + here[k]["new"] + text[end:]', 'text = text[:start] + here[0]["new"] + text[end:]'),
 "spans once->any": ('and text.count(p["old"]) == 1]', ']'),
 "plant skip write": ("f.write_text(text)", "pass"),
 "PLANTED only first tree": ('out += [f"PLANTED', 'out = [f"PLANTED'),
}
for n,(o,nw) in M.items():
    assert head.count(o)>=1, n
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td)/src.name; p.write_text(head.replace(o,nw,1)+mark+tail)
        r = subprocess.run([sys.executable,"-I",str(p),"--self-test","--no-mutants","--tests",tests],capture_output=True,text=True,timeout=120)
        fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        print(("KILLED  " if r.returncode and fails else "SURVIVED") , n, "|", fails[:2])
