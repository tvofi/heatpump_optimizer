import importlib.util, sys
W=sys.argv[1]; repo=sys.argv[2]
for n in ("bot_base","bot_head"):
    s=importlib.util.spec_from_file_location(n,f"{W}/{n}.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
    st,_=m.plan_one(repo,"fe964895e628e0fc54762f9e80dc6098ff606e0b","34cd75bf1",mergeable=False,same_repo=True,pins=lambda:[])
    print(f"RESULT replay-2872 exact at={n} lines={len(st.splitlines())}"); print("  "+st.replace("\n","\n  "))
