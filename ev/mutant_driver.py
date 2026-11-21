import subprocess, shutil, sys, os, re, pathlib, concurrent.futures as cf
SRC=pathlib.Path(os.environ["HOME"])/"wt"; OUT=pathlib.Path(os.environ["HOME"])/"w"/"mut"
F="custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
M=[
 ("hitmax","Math.max(3.5, _targetMinPx() * unitsPerPx)","Math.min(3.5, _targetMinPx() * unitsPerPx)"),
 ("foldmax","min-height: ${Math.max(32, targetFloorPx)}px","min-height: 32px"),
 ("prunecut","if (chunk < cut) this.covered.delete(chunk);","if (chunk <= cut) this.covered.delete(chunk);"),
 ("trkey","if (err && err.translation_domain && err.translation_key &&","if (false && err.translation_domain && err.translation_key &&"),
 ("critfill",'"--hpo-crit-fill": { light: "#b3261e", dark: "#b3261e" }','"--hpo-crit-fill": { light: "#b3261e", dark: "#f28b82" }'),
 ("keeplast","return rows[at] && rows[at].t < cutMs ? rows.slice(at) : rows;","return rows[at] && rows[at].t < cutMs ? rows.slice(at + 1) : rows;"),
 ("emptyloc","    if (text) return text;\n  }\n  return (err && err.message)","    return text;\n  }\n  return (err && err.message)"),
 ("fitold",'for (const sel of [".tt-reason", ".tt-shared"])','for (const sel of [])'),
 ("hitedge","const edge = data.edge || data.hitEdge;","const edge = data.edge;"),
 ("noprune","    this.prune(liveEdge);\n",""),
 ("chunkskeep","if (chunk < cut) this.chunks.delete(chunk);",""),
 ("noph","err.translation_placeholders || {}","{}"),
 ("noscale",'dlg.style.setProperty("--hpo-type-scale", (px / DIALOG_FONT_PX_MIN).toFixed(4));',''),
 ("nosubgrid","display: grid; grid-template-rows: subgrid; row-gap: 0;","display: block; row-gap: 0;"),
]
def run(m):
    name,a,b=m; d=OUT/name
    if d.exists(): shutil.rmtree(d)
    shutil.copytree(SRC,d,ignore=shutil.ignore_patterns(".git","node_modules"),symlinks=True)
    p=d/F; s=p.read_text(); n=s.count(a)
    if n!=1: return f"{name}: APPLY-FAIL count={n}"
    p.write_text(s.replace(a,b))
    r=subprocess.run(["timeout","900","node","--max-old-space-size=6144","tests/card.mjs","/tmp/plandata-822e9fee8627.json"],cwd=d,capture_output=True,text=True)
    o=r.stdout+r.stderr; (OUT/f"{name}.log").write_text(o)
    fails=[l for l in o.splitlines() if "FAIL" in l]
    shutil.rmtree(d)
    return f"{name}: rc={r.returncode} fails={len(fails)}\n" + "\n".join("   "+l[:220] for l in fails[:8])
with cf.ThreadPoolExecutor(3) as ex:
    for res in ex.map(run,M): print(res,flush=True)
print("MUTDONE",flush=True)
