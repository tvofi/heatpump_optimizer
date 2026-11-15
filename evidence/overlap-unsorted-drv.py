import sys, importlib.util, pathlib
for name in ("headpr", "mutpr"):
    spec = importlib.util.spec_from_file_location(name, f"{name}.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    base = {"space": "natural", "symbol": "s", "file": "e.py"}
    pl = [{**base, "id": "P06", "old": "def", "new": "DEF"}, {**base, "id": "P05", "old": "abc", "new": "ABC"},
          {**base, "id": "P07", "space": "config", "cell": "layout=x", "old": "return v", "new": "return -v"}]
    doc = {"planter": "p", "plants": pl}
    print(name, "disjoint plants listed out of file order:", m.refusals(doc, pathlib.Path("/nonexistent/P.json"), [pathlib.Path("tree")], {"layout=x"}, ["orch"]))
