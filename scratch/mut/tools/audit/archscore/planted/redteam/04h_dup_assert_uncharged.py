"""Variant of 04: ``assert`` junk, skipping the coordinator and footprint-charged functions."""
import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0], sys.argv[1], "assert", "uncharged"]
runpy.run_path(str(Path(__file__).with_name("04_dup_noop_interleave.py")), run_name="__main__")
