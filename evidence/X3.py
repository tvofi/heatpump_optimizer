import sys
p=sys.argv[1]; s=open(p).read()
old="""reads like a current one)' "${ref#origin/}"\n    return 1"""
new="""reads like a current one)' "${ref#origin/}"\n    return 0"""
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
