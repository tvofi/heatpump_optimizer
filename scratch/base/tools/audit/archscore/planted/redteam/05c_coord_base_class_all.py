"""Variant of 05: move the whole coordinator body into a _CoordinatorBody(DataUpdateCoordinator) base; the named class becomes an empty subclass."""
import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0], sys.argv[1], "all"]
runpy.run_path(str(Path(__file__).with_name("05_coord_mixin_relocation.py")), run_name="__main__")
