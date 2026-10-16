import sys, io, contextlib
sys.argv=['arch_score.py']; sys.path.insert(0,'tests'); sys.path.insert(0,'tools/audit')
import arch_score as A
buf=io.StringIO()
with contextlib.redirect_stdout(buf): A.hub_spellings()
lines=buf.getvalue().splitlines()
fails=[l for l in lines if 'FAIL' in l]; oks=[l for l in lines if l.strip().startswith('ok')]
print("RESULT hub_spellings ok=%d fail=%d" % (len(oks), len(fails))); [print("  ",l.strip()[:170]) for l in fails]
