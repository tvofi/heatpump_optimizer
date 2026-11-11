import re,json,pathlib,sys,yaml as _yaml
L=open("tests/entities.py").read().split("\n")
def seg(a,b): return "\n".join(L[a-1:b])
res=[]
class R:
    @staticmethod
    def check(n,c,d=""): res.append(bool(c))
g={"re":re,"json":json,"pathlib":pathlib,"_yaml":_yaml,"R":R,"__file__":str(pathlib.Path("tests/entities.py").resolve())}
code=seg(21918,21919)+"\n"+seg(21973,21973)+"\n"+seg(21999,21999)+"\n"+seg(22020,22028)+"\n"+seg(22046,22066)
exec(code,g)
print("PASS" if res and all(res) else "FAIL", res)
