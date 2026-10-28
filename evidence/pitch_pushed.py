# Reviewer's own probe: --pitch-check over a tree where the beat's rows commit
# already rows the owed merge (the automerge step's HEAD on a `pushed` beat).
import contextlib, io, json, subprocess, sys, tempfile
from pathlib import Path
R = Path(sys.argv[1]); sys.path[:0] = [str(R / "tools/audit/seat"), str(R / "tests")]
import record_row as rr
from throwaway_git import throwaway_git_init
with tempfile.TemporaryDirectory() as td:
    g = Path(td); env = throwaway_git_init(g, "-q")
    def tip(m):
        subprocess.run(["git","commit","-q","--allow-empty","-m",m],cwd=g,env=env,check=True)
        return rr._git_out(g,"rev-parse","HEAD")
    import delivery_status
    owed, rec = tip("a rowless merge"), tip("a record merge"); tip("the tip")
    merges = [{"number":7,"merge_sha":owed,"title":"fix: x","head_ref":"fix/x","state":"closed"},
              {"number":8,"merge_sha":rec,"title":"record: rows","head_ref":rr.RECORD_BRANCH,"state":"closed"}]
    (g/"merges.json").write_text(json.dumps(merges))
    delivery_status.self_disposing = lambda s: s == rec  # the record merge is record-class, as on main
    def cli(*f):
        a, sys.argv = sys.argv, ["record_row.py","--root",str(g),*f]
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out): rc = rr.main()
        finally: sys.argv = a
        return rc, out.getvalue().strip()
    print("held-shape tree (row not yet written):", cli("--pitch-check","--merges-file",str(g/"merges.json"),"--event","push"))
    plan = rr.plan_merges(merges, g, self_disposing=lambda s: s == rec)
    print("plan before apply:", [r["number"] for r in plan])
    rr.write_rows(plan, g)
    subprocess.run(["git","add","-A"],cwd=g,env=env,check=True)
    subprocess.run(["git","commit","-q","-m","ci: record delivery rows"],cwd=g,env=env,check=True)
    print("row:", (g/rr.row_path(7)).read_text().strip(), "plan after:", [r["number"] for r in rr.plan_merges(merges, g, self_disposing=lambda s: s == rec)])
    print("pushed-shape tree (rows commit, the automerge step's HEAD):", cli("--pitch-check","--merges-file",str(g/"merges.json"),"--event","push"))
