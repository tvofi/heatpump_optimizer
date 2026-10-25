import sys,re
src=open(sys.argv[1]).read()
a=src.index('_RCH_DRIVER = """')
b=src.index('R.check(\n    "the coverage ratchet is wired')
body=src[a:b]
pre='''import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mutation_table as _mut
class _R:
    fails=0
    def check(self,name,ok,detail=""):
        print(("ok   " if ok else "FAIL ")+name[:90]+("" if ok else "  :: "+detail[:400]))
        if not ok: self.fails+=1
R=_R()
'''
open(sys.argv[2],'w').write(pre+body+"\nprint('FAILS',R.fails)\n")
