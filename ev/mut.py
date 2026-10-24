import sys
src=open(sys.argv[1]).read(); old=sys.argv[2]; new=sys.argv[3]
assert src.count(old)==1, (old, src.count(old))
open(sys.argv[4],'w').write(src.replace(old,new))
