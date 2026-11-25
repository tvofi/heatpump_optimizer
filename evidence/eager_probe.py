import asyncio, sys
async def job(): return 1
async def main(pass_loop):
    kw = {"loop": asyncio.get_running_loop()} if pass_loop else {}
    try:
        r = await asyncio.Task(job(), eager_start=True, **kw)
        return f"ok {r}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"
for pl in (False, True):
    print(sys.version.split()[0], "loop passed" if pl else "no loop", "->", asyncio.run(main(pl)))
