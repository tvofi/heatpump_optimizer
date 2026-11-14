import subprocess, sys, pathlib
wt=pathlib.Path(sys.argv[1])
M=[("null",None,None,None),
 ("readme_cost_row_loses","README.md","| Estimated cost of the planned hot water | On a combi tank, the `dhw_split` attribute says this is what the heat pump spends in hot-water mode, which includes space heat drawn from the tank |","| Estimated cost of the planned hot water | |"),
 ("readme_space_row_gains","README.md","| Lifetime Space Heating Energy | kWh | Accumulating, for the Energy dashboard | |","| Lifetime Space Heating Energy | kWh | Accumulating, for the Energy dashboard | `dhw_split` |"),
 ("config_combi_loses","docs/configuration.md"," Each says so in its `dhw_split` attribute."," "),
 ("code_sentence","custom_components/heatpump_optimizer/entity.py",'"what the heat pump spends in hot-water mode; with a combi store this "','"what the pump spends in DHW mode; with a combi store this "'),
]
for n,f,a,b in M:
    p=wt/f if f else None; o=p.read_text() if p else None
    try:
        if p: assert o.count(a)==1,(n,o.count(a)); p.write_text(o.replace(a,b))
        out=subprocess.run(['python3','tests/doc_claims.py'],cwd=wt,capture_output=True,text=True).stdout
        fails=[l.strip()[:90] for l in out.splitlines() if l.strip().startswith('FAIL')]
        print('SURVIVED' if not fails else 'KILLED', n, '|', len(fails), 'fails |', '; '.join(fails))
    finally:
        if p: p.write_text(o)
