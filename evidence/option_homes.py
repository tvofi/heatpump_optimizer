import sys, re, json, pathlib, importlib.util
root = pathlib.Path(sys.argv[1]); sys.path[:0] = [str(root/'tests')]
spec = importlib.util.spec_from_file_location("dc", root/'tests'/'doc_claims.py')
dc = importlib.util.module_from_spec(spec); spec.loader.exec_module(dc)
import heatpump_optimizer.config_flow as cf
en = dc._EN_STRINGS['options']['step']
print(type(cf._OPTION_FIELDS), list(cf._OPTION_FIELDS)[:2] if not isinstance(cf._OPTION_FIELDS, dict) else list(cf._OPTION_FIELDS.items())[:2])
firsts=set()
for name,t in dc.CORPUS.items():
    for l in t.splitlines():
        m=re.match(r'\s*\|\s*([^|]+?)\s*\|', l)
        if m: firsts.add(dc._label(m.group(1).replace('**','').replace('`','')))
labels={}
def walk(n):
    if isinstance(n,dict):
        for k,v in n.items():
            if k=='data' and isinstance(v,dict):
                for kk,vv in v.items():
                    if isinstance(vv,str): labels.setdefault(kk,vv)
            else: walk(v)
walk(en)
miss=[]
for f in cf._OPTION_FIELDS:
    key = f.key
    lab = labels.get(str(key))
    if lab is None or dc._label(lab) not in firsts: miss.append((key,lab))
print(len(miss), miss)
corpus=' '.join(dc._label(t) for t in dc.CORPUS.values())
print("labels not mentioned:", [k for k,l in labels.items() if dc._label(l) not in corpus][:10])
s=json.loads((root/'custom_components/heatpump_optimizer/strings.json').read_text())['issues']
rd=dc.README
print("issues named by key/title in README:", [k for k,v in s.items() if k in rd or v.get('title','@@') in rd])
