import re,subprocess,sys
def blocks(ref,f):
    t=subprocess.check_output(['git','show',f'{ref}:{f}'],text=True)
    return {m.group(1):m.group(0) for m in re.finditer(r'(?ms)^([A-Za-z0-9][A-Za-z0-9._-]*)==.*?(?=^[A-Za-z0-9][A-Za-z0-9._-]*==|\Z)',t)}
for f in ['tests/requirements-ci.txt','tests/requirements-typing.txt']:
    a=blocks('origin/main',f); b=blocks('FETCH_HEAD',f)
    print("RESULT",f,len(a),len(b),'added',set(b)-set(a),'removed',set(a)-set(b),'changed',sorted(k for k in a if k in b and a[k]!=b[k]))
