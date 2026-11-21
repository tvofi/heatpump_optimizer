# Runs each shape for real under asyncio and reports any log record at WARNING+.
import asyncio, logging, io
buf = io.StringIO(); h = logging.StreamHandler(buf); h.setLevel(logging.WARNING)
logging.getLogger().addHandler(h)
async def main():
    loop = asyncio.get_running_loop()
    loop.call_exception_handler({"message": "x"})            # shape A
    loop.default_exception_handler({"message": "y"})         # shape B
asyncio.run(main())
print("logged:", repr(buf.getvalue().strip()))
