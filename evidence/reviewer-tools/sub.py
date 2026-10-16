import sys; p,a,b=sys.argv[1:]; s=open(p).read(); assert s.count(a)==1,(p,a); open(p,'w').write(s.replace(a,b))
