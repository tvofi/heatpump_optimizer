"""All pure-evasion games in one change (no feature deleted, no base-class move):
02 hub via object.__setattr__, 03 shared via dunder/helper, 10 setattr in __init__,
06 passthrough properties, 01 all-Any TypedDict, 07 family re-declaration,
08 keep-alive registry, 11 **kw bags, then 04 no-op interleave (sites re-located at each step)."""
import runpy, sys
from pathlib import Path
here = Path(__file__).parent
root = sys.argv[1]
for name in ("02_hub_object_setattr", "03_shared_dunder_spelling", "10_writers_setattr_init",
             "06_private_passthrough_props", "01_typeddict_all_any", "07_family_declare_away",
             "08_keepalive_registry", "11_params_kwargs_bag", "04_dup_noop_interleave"):
    for m in [k for k in sys.modules if k in ("hub_solve_writes", "shared_inplace_writes", "private_reach",
                                              "untyped_payload_keys", "family_splits", "dead_by_reachability",
                                              "public_surface", "_common", "metrics_v1")]:
        del sys.modules[m]
    sys.argv = [str(here / f"{name}.py"), root]
    print("--", name)
    runpy.run_path(str(here / f"{name}.py"), run_name="__main__")
