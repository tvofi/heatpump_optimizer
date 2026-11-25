import ast,sys,os,subprocess,tempfile,re
from pathlib import Path
rev=sys.argv[1]; wt=sys.argv[2]
src=subprocess.run(["git","show",f"{rev}:tests/entities.py"],capture_output=True,text=True,check=True).stdout
tree=ast.parse(src)
want={"_pg_run","_pg_plan_defects"}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in want]
consts=[n for n in tree.body if isinstance(n,ast.Assign) and ast.unparse(n.targets[0]) in ("_PG_PLAN","(_PG_STAGE, _PG_GUARD)")]
sys.path.insert(0,str(Path(wt)/"tests"))
from throwaway_git import throwaway_git_init
import yaml as _yaml
g=dict(os=os,subprocess=subprocess,tempfile=tempfile,Path=Path,re=re,_yaml=_yaml,yaml=_yaml,throwaway_git_init=throwaway_git_init)
exec(compile(ast.Module(body=consts+nodes,type_ignores=[]),"x","exec"),g)
wf=subprocess.run(["git","show",f"{rev}:.github/workflows/pages.yml"],capture_output=True,text=True,check=True).stdout
print(rev[:8], "_pg_plan_defects:", g["_pg_plan_defects"](wf))
