import yaml, sys
src = open(".github/workflows/ci.yml").read()
def pin(text):
    doc = yaml.safe_load(text)
    r = next((str(st.get("run","")) for st in ((doc.get("jobs") or {}).get("prelude") or {}).get("steps") or [] if st.get("name")=="Restore the programs from the base"),"")
    rs = next((ln.split("--",1)[1].split() for ln in r.splitlines() if 'git checkout "$PINNED" --' in ln), [])
    return "refs/heads/batch/*" in r and "git merge-base FETCH_HEAD HEAD" in r and {"tools/pr/codeql_scope.py","tests/closure.py"} <= set(rs)
muts = {"head": src,
 "batch arm deleted": src.replace('elif [ -z "$PINNED" ] && [[ "$GITHUB_REF" == refs/heads/batch/* ]]; then','elif false; then'),
 "closure.py dropped": src.replace(" tools/pr/codeql_scope.py tests/closure.py"," tools/pr/codeql_scope.py"),
 "own tip restored": src.replace("PINNED=$(git merge-base FETCH_HEAD HEAD)","PINNED=$(git rev-parse HEAD)"),
 "main tip restored (not merge base)": src.replace("PINNED=$(git merge-base FETCH_HEAD HEAD)","PINNED=$(git rev-parse FETCH_HEAD)"),
 "merge base kept as comment, arm sets tip": src.replace("PINNED=$(git merge-base FETCH_HEAD HEAD)","PINNED=$(git rev-parse HEAD)  # git merge-base FETCH_HEAD HEAD"),
}
for k,v in muts.items():
    assert k=="head" or v!=src, k
    print(f"RESULT entities-pin {k}: {'ok' if pin(v) else 'FAIL'}")
