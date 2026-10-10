import subprocess, sys, re
sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/r9rev-2111/wt/tools/audit/seat")
sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/r9rev-2111/wt/tests")
import record_row as R
import delivery_status as DS

WT = "/Users/timmalmstrom/hpo-seats/r9rev-2111/wt"
def ls(ref):
    out = subprocess.run(["git","-C",WT,"ls-tree","--name-only","-r",ref,"dev/programme/delivery/"],
                         capture_output=True,text=True,check=True).stdout
    return [p for p in out.split() if re.match(r"dev/programme/delivery/\d+\.md$", p)]
def show(ref,path):
    return subprocess.run(["git","-C",WT,"show",f"{ref}:{path}"],capture_output=True,text=True,check=True).stdout
def sha(ref): return subprocess.run(["git","-C",WT,"rev-parse",ref],capture_output=True,text=True,check=True).stdout.strip()

for ref in sys.argv[1:]:
    files = ls(ref)
    ing_merged=ing_open=0
    out_multiline=out_prose=out_other=0
    opens=[]
    for p in files:
        txt = show(ref,p)
        lines = txt.splitlines()
        n = int(re.search(r"/(\d+)\.md$",p).group(1))
        anchored = DS.anchored(n, lines[0]) if lines else False
        st = R.line_status(lines[0]) if lines else None
        if len(lines)==1 and anchored and st is not None:
            if st[0]=="merged": ing_merged+=1
            else:
                ing_open+=1; opens.append(n)
        else:
            if len(lines)!=1: out_multiline+=1
            elif st is None: out_prose+=1
            else: out_other+=1
    print(f"ref {ref} = {sha(ref)}")
    print(f"  numeric row files: {len(files)}")
    print(f"  in-grant merged: {ing_merged}")
    print(f"  in-grant open:   {ing_open}  -> {sorted(opens)}")
    print(f"  outside grant:   {out_multiline+out_prose+out_other}  (multi-line {out_multiline}, prose-status {out_prose}, other {out_other})")
