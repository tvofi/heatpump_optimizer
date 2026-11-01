import json,sys
f,key,suffix=sys.argv[1:4]
p=f"custom_components/heatpump_optimizer/{f}";d=json.load(open(p,encoding='utf-8'))
n=d
ks=key.split('.')
for k in ks[:-1]: n=n[k]
n[ks[-1]]=n[ks[-1]]+suffix
json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
