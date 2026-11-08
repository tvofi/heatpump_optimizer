import sys,re,pathlib
name,root=sys.argv[1],pathlib.Path(sys.argv[2])
def sub(rel,old,new,count=1):
    p=root/rel; t=p.read_text(); assert old in t,(name,rel,old[:60]); p.write_text(t.replace(old,new,count))
T='custom_components/heatpump_optimizer/'
if name=='P1': sub(T+'topology.py','_TRANSLATIONS: dict[str, dict[str, str]] = {"sv": _SV, "de": _DE}','_TRANSLATIONS: dict[str, dict[str, str]] = {"sv": _SV}')
elif name=='P2': sub(T+'topology.py','    "Defrosting":\n        "Abtauen",\n','')
elif name=='P3':
    t=(root/T/'narrative.py').read_text(); i=t.index('    },    "de": {'); j=t.index('    },\n\n}',i); (root/T/'narrative.py').write_text(t[:i]+'    },\n}'+t[j+len('    },\n\n}'):])
elif name=='P4': sub(T+'config_flow.py','    "de": "Die Ableitung','    "xx": "Die Ableitung')
elif name=='P5':
    C=T+'www/heatpump-optimizer-card.js'; t=(root/C).read_text(); i=t.index('\n  de: {'); (root/C).write_text(t[:i]+'\n  xx_de: {'+t[i+len('\n  de: {'):])
elif name=='P6':
    import json; p=root/T/'translations/de.json'; d=json.loads(p.read_text()); del d['config']['abort']['reauth_successful']; p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
elif name=='M1': sub('tests/entities.py','red = ((script == _MUT_AN_KILL and text not in (base, _mut_an_nulled(base)))','red = ((script == _MUT_AN_KILL and text != base and "(null control)" not in text)')
elif name=='M2': sub('tests/entities.py','red = ((script == _MUT_AN_KILL and text not in (base, _mut_an_nulled(base)))','red = ((script == _MUT_AN_KILL and text != base)')
elif name=='NULL': sub(T+'topology.py','    code = (language or "en").lower().replace("_", "-").split("-")[0]\n','    code = (language or "en").lower().replace("_", "-").split("-")[0]  # (null control)\n')
else: raise SystemExit('unknown')
print('planted',name)
