import importlib.util, sys
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.PLANTS.clear()
m.PLANTS.update({
 "O1": ('"merge-base", "--is-ancestor",\n                                sha, cand', '"merge-base", "--is-ancestor",\n                                cand, sha'),
 "O2": ('"merge-base", "--is-ancestor",\n                                sha, cand', '"cat-file", "-e",\n                                sha'),
})
sys.exit(m.main(sys.argv[2:]))
