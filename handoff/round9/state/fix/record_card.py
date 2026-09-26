import json,sys
p='/mnt/project-files/audit-r9/fix/CARDS.json'
d=json.load(open(p)); cid,ans=sys.argv[1],sys.argv[2]
d['cards'][cid][1]=ans; json.dump(d,open(p,'w'),indent=0)
open_=[v[0] for v in d['cards'].values() if v[1] is None]
print(d['cards'][cid][0],'=',ans,'| open:',len(open_),open_)
