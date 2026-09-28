import json,os,collections
D=os.path.dirname(os.path.abspath(__file__))+'/r9/tools/audit/round9/D14/sweep'
def classes():
    out=[]
    for s in ['S1','S2','S3','S4','S5','S6','S7']:
        d=json.load(open(f'{D}/{s}.json'))
        if isinstance(d,list): cl=d
        elif 'classes' in d: cl=d['classes']
        else: cl=[d]
        for c in cl: out.append((s,c))
    return out
if __name__=='__main__':
    for s,c in classes():
        seams=c.get('seams',[])
        disp=collections.Counter(x.get('disposition') for x in seams)
        print(s, repr(c['class']), 'N=',c.get('N'), 'seams',len(seams), dict(disp))
        print('   keys', sorted(set(k for x in seams for k in x)))
