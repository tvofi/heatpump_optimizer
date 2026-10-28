# Reviewer demo: the --group CLI dispatching a reviewer, unmutated vs a mutant.
import importlib.util, json, subprocess, sys, tempfile, contextlib, io
from pathlib import Path
src = Path(sys.argv[1]).resolve(); which = sys.argv[2]
MUT = {"cli-role-fixed": ("print(dispatch_group(args.role,", 'print(dispatch_group("fixer",'),
       "cli-nonce-dropped": ("nonce=args.nonce, overlay=args.overlay))", 'nonce="", overlay=args.overlay))'),
       "cli-pr-dropped": ('head=args.head or "", pr=args.pr,', 'head=args.head or "", pr="",')}
code = src.read_text()
if which in MUT:
    a, b = MUT[which]; assert code.count(a) == 1; code = code.replace(a, b)
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
        g = {"group":"R10-X","brief":"BRIEF\n","resume":{"branch":"handoff/r10-x"}}
        r.write_text(json.dumps({"repo":"o/n","groups":[g]})); git(w,"add","-A"); git(w,"commit","-qm","r")
        git(w,"remote","add","origin",str(o)); git(w,"push","-q","origin","main"); git(w,"fetch","-q","origin")
        head = git(w,"rev-parse","HEAD").strip()
        ov = Path(td)/"ov.json"; ov.write_text(json.dumps({"environment_id":"env_x"}))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.chdir(w), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cd.main(["--role","reviewer","--group","R10-X","--model","m-1","--head",head,"--pr","2577",
                          "--nonce","n0nce","--roster-ref","origin/main","--overlay",str(ov)])
        line = out.getvalue().strip()
        first = ""
        if rc == 0:
            git(w,"fetch","-q","origin","refs/heads/"+line); first = git(w,"show","FETCH_HEAD:PROMPT.md").splitlines()[0]
        print(f"RESULT demo={which} rc={rc} line={line!r} stderr={err.getvalue().strip()[-120:]!r}")
        print(f"    prompt first line: {first[:160]!r}")
finally:
    tmpmod.unlink()
