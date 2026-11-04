import os,subprocess,sys,tempfile
sys.path.insert(0,os.path.abspath("tools/audit/seat")); import prune_refs as p
d=tempfile.mkdtemp(); g=lambda *a,cwd=None: subprocess.run(["git",*a],cwd=cwd,capture_output=True,text=True,check=True).stdout.strip()
bare=d+"/r.git"; g("init","-q","--bare",bare); w=d+"/w"; g("init","-q",w)
for k,v in (("user.name","t"),("user.email","t@t")): g("config",k,v,cwd=w)
g("commit","-q","--allow-empty","-m","a",cwd=w); s=g("rev-parse","HEAD",cwd=w)
g("push","-q",bare,"HEAD:refs/heads/fix/x",cwd=w)
g("commit","-q","--allow-empty","-m","b-after-plan",cwd=w); s2=g("rev-parse","HEAD",cwd=w)
g("push","-q",bare,"HEAD:refs/heads/fix/x",cwd=w)  # ref moves after the plan read s
os.chdir(w); tag=p.archive_tag("fix/x")
out=p.apply_plan_push(bare,[("tag",tag,s),("delete","fix/x",s)],dry_run=False)
print("planned",s[:8],"moved-to",s2[:8]); print("done",out)
print("heads:",g("ls-remote","--heads",bare) or "(none)"); print("tags:",g("ls-remote","--tags",bare))
print("RESULT moved-tip-deleted-untagged=%d" % (s2 not in g("ls-remote",bare)))
