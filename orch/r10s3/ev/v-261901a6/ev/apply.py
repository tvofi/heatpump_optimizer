import pathlib, sys, re
src = pathlib.Path(__file__).with_name("mut.py").read_text()
M = eval(src[src.index("M = {")+4: src.index("\n}\n")+2].replace('P+', '"custom_components/heatpump_optimizer/"+'))
root = pathlib.Path(sys.argv[1])
for name,(f,old,new) in M.items():
    if name.split()[0] == sys.argv[2]:
        p = root/f; s = p.read_text(); assert s.count(old)==1; p.write_text(s.replace(old,new)); print("applied", name)
