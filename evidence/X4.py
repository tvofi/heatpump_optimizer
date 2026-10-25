import sys
p=sys.argv[1]; s=open(p).read(); old='kill -TERM -- -"$hpid" 2>/dev/null ) & wpid'; new='kill -TERM "$hpid" 2>/dev/null ) & wpid'
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
