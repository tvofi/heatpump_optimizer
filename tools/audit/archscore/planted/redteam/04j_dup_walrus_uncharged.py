"""KNOWN-OPEN variant of 04: ``walrus`` junk, skipping the coordinator and footprint-charged functions. Reads IMPROVES: see ABOUT.md "Known limit"."""
import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0], sys.argv[1], "walrus", "uncharged"]
runpy.run_path(str(Path(__file__).with_name("04_dup_noop_interleave.py")), run_name="__main__")
