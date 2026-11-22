exec(open('/tmp/claude-0/sp/explore5.py').read().split('# d742: power constant')[0])
import math
outs=[0.0,4.0,-2.0,8.0,2.0,-4.0,6.0,0.0,10.0]
for key, which in (('87c3_2126','k'),('3e78_2126','p')):
    found=0
    v=1e-6
    for j in range(-300,301):
        x=1e-6
        step=j
        x=v
        for _ in range(abs(step)): x=math.nextafter(x, math.inf if step>0 else -math.inf)
        smp=exact_series(x,0.25,[4.0]*9,outs) if which=='k' else exact_series(0.5,x,[4.0]*9,outs)
        b=L.call(L.SI.identify,smp); m=L.call(M[key],smp)
        if repr(b)!=repr(m):
            found+=1
            if found<=2: print(key,'hit ulp',j,repr(x),L.short(b),'|',L.short(m))
    print(key,'hits',found)
