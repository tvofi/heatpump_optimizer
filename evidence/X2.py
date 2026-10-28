import sys
p=sys.argv[1]; s=open(p).read(); old='  CARRY_LINE=$(carry_line "$BODY")\n'; new='  CARRY_LINE=$(carry_line "$BODY")\n  :\n'
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
