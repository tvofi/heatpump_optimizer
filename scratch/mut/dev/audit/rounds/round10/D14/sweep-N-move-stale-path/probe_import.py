#!/usr/bin/env python3
"""Probe: run FILE's own prelude (source above LINE) then `import MOD`.
Exit 0 = MOD resolves the way the consumer resolves it; exit 1 = stale path.
Usage: probe_import.py FILE LINE MOD   (run from repo root, python3 -I)"""
import os, sys
f, line, mod = sys.argv[1], int(sys.argv[2]), sys.argv[3]
src = open(f).read().splitlines()[: line - 1]
g = {"__file__": os.path.abspath(f), "__name__": "__probe__"}
try:
    exec(compile("\n".join(src) + "\n", f, "exec"), g)
except ModuleNotFoundError as e:
    print(f"PRELUDE {e}"); sys.exit(1)
except Exception as e:
    print(f"PRELUDE-OTHER {type(e).__name__}: {e}")
import importlib
try:
    importlib.import_module(mod); print("ok"); sys.exit(0)
except ModuleNotFoundError as e:
    print(f"STALE {e}"); sys.exit(1)
except Exception as e:
    print(f"resolves (import-time {type(e).__name__})"); sys.exit(0)
