import importlib.util, json, subprocess, sys, tempfile, contextlib, io
from pathlib import Path
src = Path(sys.argv[1]).resolve(); mutate = sys.argv[2] == "mutant"
code = src.read_text()
if mutate:
    code = code.replace("roster_ref = roster_lib.reader_ref(repo_dir, roster_ref)", "roster_ref = roster_lib.reader_ref(repo_dir, None)")
tmpmod = src.parent / "_demo_cd.py"; tmpmod.write_text(code)
try:
    spec = importlib.util.spec_from_file_location("_demo_cd", tmpmod); cd = importlib.util.module_from_spec(spec); sys.modules["_demo_cd"]=cd; spec.loader.exec_module(cd)
    sys.path.insert(0, str(src.parents[3] / "tests"))
    from throwaway_git import throwaway_git_environ, throwaway_git_init
    def git(c,*a): return subprocess.run(["git","-C",str(c),*a],capture_output=True,text=True,check=True).stdout
    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
        o, w = Path(td)/"o.git", Path(td)/"w"
        throwaway_git_init(o,"-q","--bare"); throwaway_git_init(w,"-q","-b","main")
        r = w/cd.roster_lib.ROSTERS_DIR/"wave-r10-groups.json"; r.parent.mkdir(parents=True)
        g = {"group":"R10-X","brief":"MAIN BRIEF\n","resume":{"branch":"handoff/r10-x"}}
        r.write_text(json.dumps({"repo":"o/n","groups":[g]})); git(w,"add","-A"); git(w,"commit","-qm","r")
        git(w,"remote","add","origin",str(o)); git(w,"push","-q","origin","main"); git(w,"fetch","-q","origin")
        r.write_text(json.dumps({"repo":"o/n","groups":[{**g,"brief":"BRANCH BRIEF\n"}]})); git(w,"commit","-qam","b")
        git(w,"push","-q","origin","HEAD:refs/heads/handoff/audit-r10-roster"); git(w,"fetch","-q","origin")
        with contextlib.redirect_stderr(io.StringIO()):
            ref = cd.dispatch_group("fixer","R10-X","m-1",repo_dir=str(w),roster_ref="origin/main",environ={"HPO_CLOUD_ENV_ID":"env_x"})
        git(w,"fetch","-q","origin","refs/heads/"+ref); p = git(w,"show","FETCH_HEAD:PROMPT.md")
        print(f"RESULT demo={sys.argv[2]} roster_ref=origin/main brief_in_prompt={'MAIN' if 'MAIN BRIEF' in p else 'BRANCH' if 'BRANCH BRIEF' in p else '?'}")
finally:
    tmpmod.unlink()
