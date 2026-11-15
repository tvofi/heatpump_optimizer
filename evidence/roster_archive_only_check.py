import difflib
a=open('/tmp/r.json').read().split('\n'); b=open('/tmp/h.json').read().split('\n')
print(len(a),len(b))
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
n=bad=0
for t,i1,i2,j1,j2 in sm.get_opcodes():
    if t=='equal': continue
    n+=1
    A='\n'.join(a[i1:i2]);B='\n'.join(b[j1:j2])
    # head must equal roster with archive/ inserted only: removing every 'archive/' from both must match
    if t!='replace' or A.replace('archive/','')!=B.replace('archive/',''):
        bad+=1;print(t,i1,repr(A[:120]),'=>',repr(B[:120]))
print('hunks',n,'beyond-archive',bad)
