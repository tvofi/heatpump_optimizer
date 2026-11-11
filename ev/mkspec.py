import json,sys
F="tools/audit/worktree_gc.sh"
src=open(sys.argv[1]).read()
T='if (t=="" || t=="/" || t=="\\"" || t=="\\x27" || t==":" || t==",") f=1'
assert src.count(T)==1, T
def term(new): return T.replace(' || '.join(MEM), new)
OF_OLD='if (d==p || index(d, p "/")==1) f=1 } END { exit f ? 0 : 1 }\'; then\n    HELD_WAY=open-file'
assert src.count(OF_OLD)==1
CW_OLD='[ -n "$out" ] || return 2\n'
EM='t==""'; SL='t=="/"'; DQ='t=="\\""'; SQ='t=="\\x27"'; CO='t==":"'; CM='t==","'
MEM=[EM,SL,DQ,SQ,CO,CM]
assert ' || '.join(MEM) in T
m=[
] + [(n, T, term(" || ".join(x for x in MEM if x not in drop) or "1")) for n,drop in [
 ("argvterm-quote",{DQ,SQ}),("argvterm-colon",{CO,CM}),("argvterm-dq",{DQ}),("argvterm-sq",{SQ}),
 ("argvterm-col",{CO}),("argvterm-com",{CM}),("argvterm-slash",{SL}),("argvterm-empty",{EM}),("argvterm-any",set(MEM))]] + [
 ("openfile-eq", OF_OLD, OF_OLD.replace('d==p || ','')),
 ("openfile-sib", OF_OLD, OF_OLD.replace('index(d, p "/")==1','index(d, p)==1')),
 ("pidzero-tr", "tr -dc '0-9')\n    kill", "tr -dc '1-9')\n    kill"),
 ("pidguard-restored", 'kill -0 "$pid" 2>/dev/null && { HELD_WAY=pidfile-live', '[ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && { HELD_WAY=pidfile-live'),
 ("pidempty-unquoted", 'kill -0 "$pid" 2>/dev/null && { HELD_WAY=pidfile-live', 'kill -0 $pid 2>/dev/null && { HELD_WAY=pidfile-live'),
 ("lockglob-star", '"$p"/*.lock "$p"/.*.lock', '"$p"/.*.lock'),
 ("lockglob-dot", '"$p"/*.lock "$p"/.*.lock', '"$p"/*.lock'),
 ("lsofall", 'out=$(lsof -Fn 2>/dev/null) || return 2', 'out=$(lsof -Fn 2>/dev/null)'),
 ("psunread", 'out=$(ps -eo args= 2>/dev/null) || return 2', 'out=$(ps -eo args= 2>/dev/null)'),
 ("lsofcwd-empty", CW_OLD, '\n'),
 ("trap-zpid-unguarded", 'trap \'[ -n "${ZPID:-}" ] && kill "$ZPID" 2>/dev/null; rm -rf "$W"\' EXIT', 'trap \'rm -rf "$W"\' EXIT'),
]
for n,o,_ in m: assert src.count(o)==1,(n,src.count(o))
json.dump([dict(name=n,file=F,old=o,new=w) for n,o,w in m],open(sys.argv[2],'w'),indent=1)
print(len(m))
