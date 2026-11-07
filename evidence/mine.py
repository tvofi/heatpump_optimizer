import subprocess,sys,pathlib
f=pathlib.Path(sys.argv[1])/'tools/plan/replan.py'; orig=f.read_text()
M=[
("part-hit-or-swap",'hit = [t for t in by_topic if topic == t or topic.startswith(t + "-")]','hit = [t for t in by_topic if topic.startswith(t + "-")]'),
("part-endswith",'topic.startswith(t + "-")]','topic.endswith("-" + t)]'),
("part-hit-ignored",'n = by_topic[max(hit, key=len)] if hit else None','n = by_topic.get(topic)'),
("part-no-squash-after-topic",'        if n is None:\n            named','        if n is None and not topic:\n            named'),
("part-sep-underscore",'topic.startswith(t + "-")]','topic.startswith(t + "_")]'),
]
for name,a,b in M:
    c=orig.count(a)
    if c<1: print(name,"ANCHOR",c); continue
    f.write_text(orig.replace(a,b,1))
    try:
        r=subprocess.run([sys.executable,"tools/plan/replan.py","--self-test"],cwd=sys.argv[1],capture_output=True,text=True,timeout=900)
        fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        print(name,"rc=",r.returncode,"KILLED" if r.returncode else "SURVIVED",fails[:2])
    finally: f.write_text(orig)
