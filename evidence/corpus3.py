import sys, subprocess, importlib.util
s=importlib.util.spec_from_file_location('h',sys.argv[1]+'/tools/audit/carry_audit.py'); h=importlib.util.module_from_spec(s); s.loader.exec_module(h)
for name in sys.argv[2:]:
    b=subprocess.run(['git','show','origin/handoff-body/'+name+':BODY.md'],capture_output=True,text=True).stdout
    S=[x for x in h.items(b,False) if x['why']=='owed carry' and not h.CARRY.search(x['text'])]
    orig=h.owed_carry; h.owed_carry=lambda t: bool(h.OWED_CARRY.search(t))
    U={x['id'] for x in h.items(b,False) if x['why']=='owed carry' and not h.CARRY.search(x['text'])}
    h.owed_carry=orig
    print('=====',name)
    for x in S:
        bare=h.QUOTED.sub(' ',h.CODE_SPAN.sub(' ',x['text']))
        m=h.OWED_CARRY.search(bare)
        print(('WIDENED ' if x['id'] not in U else '')+x['id'],'sec=',x['section'][:40],'| match:',repr(m.group(0)[:140]))
