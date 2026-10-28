import sys
p=sys.argv[1]; s=open(p).read(); old='  CARRY_LINE=$(carry_line "$BODY")\n  step "carry" $? "$CARRY_LINE"\n'; new=''
if s.count(old)!=1: sys.exit(1)
open(p,'w').write(s.replace(old,new))
