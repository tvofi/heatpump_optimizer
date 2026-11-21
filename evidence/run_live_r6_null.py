# null control for run_live_r6.py: the same loop and handler, no exception-handler call
import asyncio, logging, io
buf = io.StringIO(); h = logging.StreamHandler(buf); h.setLevel(logging.WARNING)
logging.getLogger().addHandler(h)
async def main():
    asyncio.get_running_loop()
asyncio.run(main())
print("logged:", repr(buf.getvalue().strip()))
