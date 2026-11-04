import sys, importlib.util
p=sys.argv[1]; sys.path.insert(0,'tests'); sys.path.insert(0,'tools/audit/seat')
spec=importlib.util.spec_from_file_location("rr",p); rr=importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
SHA="616868bdc5ca54d9555cfc89715f05a33527661e"
def api(repo,path,token):
    if path==f"/commits/{SHA}/pulls": return []
    if path.startswith("/commits/"): 
        return [{"number":0,"title":"x","state":"closed","head":{"ref":"x"},"merge_commit_sha":path.split("/")[2]}]
    if path=="/pulls/3179": return {"number":3179,"title":"R10-ARCHSCORE-SPELLINGS-P2","state":"closed","head":{"ref":"fix/r10-archscore-spellings-p2"},"merge_commit_sha":SHA}
    raise SystemExit("unexpected "+path)
rr._api=api
try:
    got=rr.enumerate_merges("tvofi/heatpump_optimizer","fad43b0471b9cef3c563d2c2ae1eab3d87a34190","t")
    print("RESULT e2e:", [m["number"] for m in got if m["number"]])
except rr.Refuse as e: print("RESULT e2e: REFUSE", e)
