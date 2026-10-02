"""Reviewer variant: walrus junk, uncharged."""
import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0], sys.argv[1], "walrus", "uncharged"]
runpy.run_path(str(Path(__file__).with_name("17_rv_base.py")), run_name="__main__")
