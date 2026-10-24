import pathlib,subprocess,sys
root=pathlib.Path('.').resolve()
for pats in (['.claude/workflows/*.js'], ['.claude/workflows/*.js','tools/policy/*.mjs'], ['.claude/workflows/*.js','nosuch/*.js']):
    ign={p:sorted(str(f.relative_to(root)) for f in root.glob(p) if f.is_file()) for p in pats}
    parse=[f for fs in ign.values() for f in fs if any(subprocess.run(["node",f"--input-type={g}","--check"],input=(root/f).read_bytes(),capture_output=True).returncode==0 for g in("module","commonjs"))]
    print(pats, "ok" if all(ign.values()) and not parse else f"REFUSED parseable={len(parse)} empty={[p for p,v in ign.items() if not v]}")
