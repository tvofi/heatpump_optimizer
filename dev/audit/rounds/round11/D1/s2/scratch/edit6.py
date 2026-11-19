p = "dev/audit/rounds/round11/D1/s2/clock_save.py"
s = open(p).read()
s = s.replace('''async def arm_clock(out):
    now = L.T0
    res = {}
    for tag, writer in (("control", now), ("ahead", now + AHEAD)):
        disk, vers = healthy_at(writer)
''', '''async def arm_clock(out, disks):
    now = L.T0
    res = {}
    for tag in ("control", "ahead"):
        disk, vers = disks[tag]
''')
s = s.replace('''async def arm_save(out, no_wait):
    disk, vers = healthy_at(L.T0)
''', '''async def arm_save(out, no_wait, disks):
    disk, vers = disks["control"]
''')
s = s.replace('''    out = {}
    for p in ps:
        p.start()
    try:
        if not a.no_wait:
            asyncio.run(arm_clock(out))
        asyncio.run(arm_save(out, a.no_wait))''', '''    out = {}
    disks = {"control": healthy_at(L.T0), "ahead": healthy_at(L.T0 + AHEAD)}
    for p in ps:
        p.start()
    try:
        if not a.no_wait:
            asyncio.run(arm_clock(out, disks))
        asyncio.run(arm_save(out, a.no_wait, disks))''')
open(p, "w").write(s)
