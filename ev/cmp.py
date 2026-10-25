import json,sys
def load(p):
    d=json.load(open(p)); gs=d['groups'] if isinstance(d,dict) else d
    return d,{g['group']:g for g in gs}, [g['group'] for g in gs]
dm,m,om=load(sys.argv[1]); dh,h,oh=load(sys.argv[2])
print('top keys main',list(dm.keys()) if isinstance(dm,dict) else 'list')
if isinstance(dm,dict):
  for k in dm:
    if k!='groups' and dm[k]!=dh.get(k): print('TOPLEVEL CHANGED',k)
print('order preserved:', [g for g in oh if g in m]==om, 'new:',[g for g in oh if g not in m])
for g in om:
  a,b=m[g],h.get(g)
  if a==b: continue
  for k in sorted(set(a)|set(b)):
    if a.get(k)!=b.get(k):
      va,vb=a.get(k),b.get(k)
      if isinstance(va,list) and isinstance(vb,list):
        pre = vb[:len(va)]==va
        print(f'{g}.{k}: list {len(va)}->{len(vb)} main-is-prefix={pre}', '' if pre else f'\n   removed={[x for x in va if x not in vb]}')
      elif isinstance(va,dict):
        print(f'{g}.{k}:', {kk:(va.get(kk),vb.get(kk)) for kk in set(va)|set(vb) if va.get(kk)!=vb.get(kk)})
      else: print(f'{g}.{k}: changed (str)')
