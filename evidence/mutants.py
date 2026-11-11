import sys,re
src=open(sys.argv[1]).read()
name=sys.argv[2]
M={
 'lockglob': ('for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do','for f in "$p/train.pid"; do'),
 'lockglob-star': ('for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do','for f in "$p/train.pid" "$p"/.*.lock; do'),
 'lockglob-dot': ('for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do','for f in "$p/train.pid" "$p"/*.lock; do'),
 'argvterm-slash': ('t=="" || t=="/" ||','t=="" ||'),
 'argvterm-empty': ('if (t=="" || t=="/" ||','if (t=="/" ||'),
 'argvterm-any': ('if (t=="" || t=="/" || t=="\\"" || t=="\\x27" || t==":" || t==",") f=1','f=1'),
 'argvterm-quote': (' || t=="\\"" || t=="\\x27"',''),
 'argvterm-colon': (' || t==":" || t==","',''),
 'lsofall': ('out=$(lsof -Fn 2>/dev/null) || return 2','out=$(lsof -Fn 2>/dev/null)'),
 'nopsbin': ('out=$(ps -eo args= 2>/dev/null) || return 2','out=$(ps -eo args= 2>/dev/null)'),
 'lsofcwd-empty': ('[ -n "$out" ] || return 2\n','\n'),
}
a,b=M[name]
assert src.count(a)==1,(name,src.count(a))
open(sys.argv[1],'w').write(src.replace(a,b))
