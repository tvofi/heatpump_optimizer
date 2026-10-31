# Runs tests/entities.py's bare_array block verbatim, with a stub R and _closure.
import sys, types, re, pathlib, io, contextlib
root = pathlib.Path(sys.argv[1]); src = (root/'tests/entities.py').read_text()
a = src.index('# --- bare array expansion under set -u'); b = src.index('# --- record-autofix')
blk = src[a:b]
fails=[]
class R:
    @staticmethod
    def check(name, ok, detail=""):
        print(("ok  " if ok else "FAIL"), name); (None if ok else fails.append(name))
cl = types.SimpleNamespace(ROOT=root)
with contextlib.redirect_stdout(io.StringIO()) as buf: pass
exec(compile(blk, 'entities-block', 'exec'), {'R': R, '_closure': cl, '__name__':'x'})
print("ROWS-FAILED", len(fails)); sys.exit(1 if fails else 0)
