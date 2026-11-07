import subprocess,sys,shutil,pathlib
wt=pathlib.Path('wt'); f=wt/'tools/plan/replan.py'; orig=f.read_text()
M=[
("free-slot-overflow-filter","        used = {s for s in used if s < overflow_base}\n        if len(used) >= slots:","        if len(used) >= slots:"),
("check-counted-exempt",'if not g.get("exempt") and not g.get("post_closure")}','if not g.get("post_closure")}'),
("post-propagate","    grew = True\n    while grew:","    grew = False\n    while grew:"),
("post-owner-step",'(G[n].get("kind") == "owner-step"','(False'),
("post-after-mark","or any(CLOSE_STAMP_MARK in a for a in G[n].get(\"after\") or [])}","}"),
("credit-lane","if n in G and lane[n] in PRODUCTION]","if n in G]"),
("check-post-before-stamp",'        if closes and mins(groups[n]["start"]) < mins(closes[0]["at"]):','        if False:'),
("chain-walk-max","node = (max(deps[node], key=lambda a: (merged_t[a], a))","node = (min(deps[node], key=lambda a: (merged_t[a], a))"),
("arrivals-median",'"work_hours": round(n_exp * sz[len(sz) // 2], 2)}','"work_hours": round(n_exp * sz[0], 2)}'),
("work-ref",'    if any(p + t in refs for p in WORK_REF_PREFIXES for t in topics):\n        return "work"','    if False:\n        return "work"'),
("live-refs-prefix",'            out.add(ref[len("refs/heads/"):])','            out.add(ref)'),
("check-produced-credit","    produced = credit + produced\n","\n"),
("design-start-t0","started = live | settled | design_only","started = live | settled"),
("post-dur-in-closure","        if g.get(\"done\") or g.get(\"post_closure\"):\n            continue","        if g.get(\"done\"):\n            continue"),
("post-check-carries",'            bad.append(f"post-closure: {n} is in a stamp\'s carries")','            pass'),
("stamp-while-cut","cut, carry = carry[:every], carry[every:]","cut, carry = list(carry), []"),
]
for name,a,b in M:
  if orig.count(a)!=1: print(name,'ANCHOR',orig.count(a)); continue
  f.write_text(orig.replace(a,b))
  try:
    r=subprocess.run([sys.executable,'tools/plan/replan.py','--self-test'],cwd=wt,capture_output=True,text=True,timeout=900)
    fails=[l for l in r.stdout.splitlines() if l.startswith('FAIL')]
    print(name,'rc=',r.returncode,'KILLED' if r.returncode else 'SURVIVED',fails[:2])
  finally: f.write_text(orig)
