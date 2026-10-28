import sys
p=sys.argv[1]; s=open(p).read(); old='  git fetch -q --no-tags "${1%%/*}" "+refs/heads/${1#*/}:refs/remotes/$1" >/dev/null 2>&1 || return 3\n'; new=''
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
