import ast,sys
p,cls,n=sys.argv[1],sys.argv[2],int(sys.argv[3])
src=open(p).read();t=ast.parse(src);L=src.splitlines()
c=next(x for x in ast.walk(t) if isinstance(x,ast.ClassDef) and x.name==cls)
i=next(m for m in c.body if isinstance(m,ast.FunctionDef) and m.name=="__init__")
ind=" "*i.body[-1].col_offset; mi=" "*i.col_offset
blk=[]
for m in range(n):
    blk.append(f"{mi}def _v2x{m}(self, v):"); 
    for k in range(80): blk.append(f"{ind}v = (v ^ {m*7919+k*104729}) % {m*31+k+97}")
    blk.append(f"{ind}return self._v2x{m+1}(v) if {m+1}<{n} else v")
out=L[:i.end_lineno]+[f"{ind}self._v2x0(1)"]+L[i.end_lineno:c.end_lineno]+blk+L[c.end_lineno:]
open(p,"w").write("\n".join(out)+"\n");print(n*82+1)
