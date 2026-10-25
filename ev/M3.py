import sys
p=sys.argv[1]; s=open(p).read(); old='--roster-ref "$ref" check --body "$1"'; new='check --body "$1"'
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
