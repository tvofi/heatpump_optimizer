import sys; sys.path.insert(0,'tests'); import replay
res=replay.controls(); bad=[(n,d[:200]) for n,ok,d in res if not ok]
print("CONTROLS", len(res)-len(bad), "of", len(res), "ok"); [print("FAIL",n,d) for n,d in bad]
