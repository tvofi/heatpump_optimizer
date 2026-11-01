"""Scratch runner: exec tests/entities.py's claim-merge-driver section (22716..ledger section) with a minimal prelude."""
import sys, os, re, subprocess, tempfile, json, pathlib
from pathlib import Path
wt = sys.argv[1]
os.chdir(wt); sys.path[:0] = ["tests", "tests/hastub"]
from throwaway_git import throwaway_git_env, throwaway_git_init
from harness import Results
import env_drift as _env_drift
import tempfile as _tempfile, subprocess as _subprocess, shutil as _shutil, os as _os, json as _json
R = Results("CM")
src = open("tests/entities.py").read().splitlines(keepends=True)
start = next(i for i, l in enumerate(src) if l.startswith("# --- the claim-file merge driver"))
end = next(i for i in range(start, len(src)) if src[i].startswith("# The ledger merge driver"))
__file__ = os.path.abspath("tests/entities.py")
exec(compile("".join(src[start:end]), "entities-cm", "exec"), globals())
sys.exit(R.close("CM"))
