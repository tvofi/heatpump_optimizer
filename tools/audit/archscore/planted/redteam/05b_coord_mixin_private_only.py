"""Variant of 05: move only the coordinator's _private methods into the _CoordinatorBody base."""
import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0], sys.argv[1], "private"]
runpy.run_path(str(Path(__file__).with_name("05_coord_mixin_relocation.py")), run_name="__main__")
