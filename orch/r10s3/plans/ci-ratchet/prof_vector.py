import sys, time, tempfile
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "tools" / "audit")); sys.path.insert(0, str(root / "tools/audit/archscore/planted"))
from archscore import vector
import cases
with tempfile.TemporaryDirectory() as t:
    pin = cases.extract_pin(Path(t))
    print("cases:", len(cases.cases()))
    for only in [None, {"structure"},{"hub_solve_writes"},{"shared_inplace_writes"},{"untyped_payload_keys"},{"family_splits"},{"public_unused"},{"footprint"},{"layering"},{"literal_clone_copies"},{"card"},{"shape_copies"},{"reflective_writes","computed_attr_access","family_orphan_overrides","unread_private_globals"}]:
        a=time.time(); vector.measure(pin, only); print(f"{time.time()-a:7.2f}s", only)
