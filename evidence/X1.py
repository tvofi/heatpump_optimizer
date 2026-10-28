import sys
p=sys.argv[1]; s=open(p).read(); old='  [ "$r" -ne 0 ] || r=$cr\n'; new=''
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
