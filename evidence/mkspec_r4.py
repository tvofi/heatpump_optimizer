# reviewer-built (round 4): v3 = probe/rev-3423-33f72110 ev/mkspec.py unchanged; v2 = probe/rev-3423-23bb0265 ev/mutants.py M table; v1 = rebuilt from probe/rev-3423-468a0851 prose; r4 = this round's own
import json,subprocess,sys
F="tools/audit/worktree_gc.sh"; src=open(sys.argv[1]).read(); ev=sys.argv[2]
subprocess.run([sys.executable,ev+"/mkspec.py",sys.argv[1],ev+"/spec-v3.json"],check=True)
spec=[dict(m,name="v3-"+m["name"]) for m in json.load(open(ev+"/spec-v3.json"))]
LG='for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do'
T='if (t=="" || t=="/" || t=="\\"" || t=="\\x27" || t==":" || t==",") f=1'
M={'lockglob':(LG,'for f in "$p/train.pid"; do'),
 'lockglob-star':(LG,'for f in "$p/train.pid" "$p"/.*.lock; do'),
 'lockglob-dot':(LG,'for f in "$p/train.pid" "$p"/*.lock; do'),
 'argvterm-slash':('t=="" || t=="/" ||','t=="" ||'),
 'argvterm-empty':('if (t=="" || t=="/" ||','if (t=="/" ||'),
 'argvterm-any':(T,'f=1'),
 'argvterm-quote':(' || t=="\\"" || t=="\\x27"',''),
 'argvterm-colon':(' || t==":" || t==","',''),
 'lsofall':('out=$(lsof -Fn 2>/dev/null) || return 2','out=$(lsof -Fn 2>/dev/null)'),
 'nopsbin':('out=$(ps -eo args= 2>/dev/null) || return 2','out=$(ps -eo args= 2>/dev/null)'),
 'lsofcwd-empty':('[ -n "$out" ] || return 2\n','\n')}
spec+=[dict(name="v2-"+k,file=F,old=a,new=b) for k,(a,b) in M.items()]
ARGV='    HELD_WAY=argv-inside; return 1\n'; OPEN='    HELD_WAY=open-file; return 1\n'
V1={'argv':(ARGV,'    :\n'),'open':(OPEN,'    :\n'),
 'pid':('kill -0 "$pid" 2>/dev/null && { HELD_WAY=pidfile-live; return 1; }','true'),
 'psunread':('out=$(ps -eo args= 2>/dev/null) || return 2','out=$(ps -eo args= 2>/dev/null) || true'),
 'killcheck':('kill -0 "$pid" 2>/dev/null && {','true && {'),
 'heldway':('1) printf \'keep  %s  %s\\n\' "$1" "$HELD_WAY"','1) printf \'keep  %s  %s\\n\' "$1" cwd-inside'),
 'lockglob':(LG,'for f in "$p/train.pid"; do'),
 'argvterm':(T,'if (t=="") f=1'),
 'lsofall':('out=$(lsof -Fn 2>/dev/null) || return 2','out=$(lsof -Fn 2>/dev/null) || out=""')}
spec+=[dict(name="v1-"+k,file=F,old=a,new=b) for k,(a,b) in V1.items()]
OF='if (d==p || index(d, p "/")==1) f=1 } END { exit f ? 0 : 1 }\'; then\n    HELD_WAY=open-file'
R4={'trainpid':(LG,'for f in "$p"/*.lock "$p"/.*.lock; do'),
 'openfile-slash':(OF,OF.replace(' || index(d, p "/")==1','')),
 'cwd-slash':('if (d==p || index(d, p "/")==1) f=1 } END { exit f ? 0 : 1 }\'; then\n    HELD_WAY=cwd-inside','if (d==p) f=1 } END { exit f ? 0 : 1 }\'; then\n    HELD_WAY=cwd-inside'),
 'pidfile-head':('head -c 32 "$f"','head -c 0 "$f"')}
spec+=[dict(name="r4-"+k,file=F,old=a,new=b) for k,(a,b) in R4.items()]
for m in spec: assert src.count(m["old"])==1,(m["name"],src.count(m["old"]))
json.dump(spec,open(ev+"/spec.json","w"),indent=1); print(len(spec))
