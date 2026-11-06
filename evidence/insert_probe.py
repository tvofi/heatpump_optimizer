import sys,re
src,snip,mut=sys.argv[1],sys.argv[2],sys.argv[3]
t=open(src).read(); s=open(snip).read()
anchor='    done_edit = run(101, "edit", "completed"'
assert t.count(anchor)==1
t=t.replace(anchor, s+anchor)
if mut=='M24':
    o='deferring(kind, pr, claim) and not all('
    assert t.count(o)==1; t=t.replace(o,'deferring(kind, pr, claim) and not any(')
open(src,'w').write(t)
