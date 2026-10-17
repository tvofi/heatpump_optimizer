# does naming a NON-read file in _CITATION_POLICY fail anything?
import sys, subprocess, json; sys.path.insert(0,"tests")
import closure as C
ent = set(json.loads(C.CLOSURES.read_text())["closures"]["tests/entities.py"])
cand = [f for f in subprocess.run(["git","ls-files"],capture_output=True,text=True).stdout.split()
        if f not in ent and C.is_inert(f) and f.endswith(".md")]
print("candidate (inert, not in entities.py closure):", cand[:4])
X = "docs/architecture.md" if "docs/architecture.md" in cand else cand[0]
print("planting:", X, "| in entities.py closure:", X in ent, "| currently inert:", C.is_inert(X))
_old = C._CITATION_POLICY
C._CITATION_POLICY = tuple(_old) + ("^" + X.replace(".", r"\.") + "$",)
print("  after planting: is_inert =", C.is_inert(X))
print("  orphan_files():", len(C.orphan_files()), "->", sorted(C.orphan_files())[:4])
sel = C.select([X]); print("  select mode=%s run=%s" % (sel["mode"], sel["run"]))
print("  the arm's own source-select set unchanged:", sorted(C._is_citation_source(f) for f in [X])[0])
C._CITATION_POLICY = _old
