import sys, importlib.util, pathlib
src = pathlib.Path("ci_critpath.py").read_text()
g = {"a": {"needs": ["b"]}, "b": {"needs": ["a"]}}
for label, text in (("head", src), ("c7-mutant", src.replace("        if n in path:\n", "        if False:\n"))):
    ns = {"__name__": "x", "__file__": str(pathlib.Path("ci_critpath.py").resolve())}; exec(compile(text, "ci_critpath.py", "exec"), ns)
    try: ns["topo"](g); print(label, "-> no error (silent)")
    except SystemExit as e: print(label, "-> SystemExit:", e)
    except RecursionError as e: print(label, "-> RecursionError (uncaught crash, non-zero exit)")
