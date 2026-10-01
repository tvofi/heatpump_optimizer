"""Wall seconds of tests/closure.py record() per script, with and without strace (shutil.which patched to hide it)."""
import shutil, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "tests")
import closure
real = shutil.which
for script in sys.argv[1:]:
    for arm in ("hook", "strace", "hook", "strace"):
        shutil.which = (lambda n, *a, **k: None if n == "strace" else real(n, *a, **k)) if arm == "hook" else real
        with tempfile.TemporaryDirectory() as d:
            t = time.monotonic(); rc = closure.record(script, Path(d)); w = time.monotonic() - t
        print(f"RESULT {script} {arm} rc={rc} wall={w:.1f}s", flush=True)
