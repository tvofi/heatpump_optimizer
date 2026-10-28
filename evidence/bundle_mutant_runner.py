import sys, subprocess, pathlib, shutil, filecmp
W = pathlib.Path(sys.argv[1]); f = W/"mt/tools/audit/seat/review_strength.py"
exec(open(W/"muts2.py").read()); D = {m[0].split()[0]: m for m in M}
orig = f.read_text(); args = open(W/"bundle_args").read().split()
for k in sys.argv[2:]:
    name, a, b = D[k]; assert orig.count(a) == 1
    f.write_text(orig.replace(a, b))
    out = subprocess.run([sys.executable, str(f), "--repo", "/home/user/heatpump_optimizer", *args], capture_output=True, text=True).stdout
    (W/f"ev/bundle_{k}.txt").write_text(out)
    f.write_text(orig)
    d = subprocess.run(["diff", str(W/"ev/bundle_head.txt"), str(W/f"ev/bundle_{k}.txt")], capture_output=True, text=True).stdout
    (W/f"ev/bundle_diff_{k}.txt").write_text(d)
    print(f"== {name}: {d.count(chr(10)+'<')+d.startswith('<')} lines differ"); print(d[:3000])
print("restored identical:", f.read_text() == orig, subprocess.run(["git","-C",str(W/"mt"),"status","--porcelain"],capture_output=True,text=True).stdout or "clean")
