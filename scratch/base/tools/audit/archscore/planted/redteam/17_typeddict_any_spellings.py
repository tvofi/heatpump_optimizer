"""Game untyped_payload_keys with attempt 01's all-untyped contract, every key spelled so that it states no type
without the word ``Any`` standing alone: ``Any | None``, ``Optional[Any]``, ``"Any"``, a package alias of ``Any``,
``Union[Any, None]``, ``Annotated[Any, ..]``, ``"Optional[Any]"``, ``Any | int`` (a union with ``Any`` accepts every
value). C1 read each as typed (ARCH-s3, round 10: 8 spellings). Counter C1b."""
import ast, sys
from rt_lib import pkg, metric, replace_nodes
root = sys.argv[1]
keys = metric("untyped_payload_keys", root)["details"]["untyped"]
SPELLINGS = ["Any | None", "Optional[Any]", '"Any"', "_Untyped", "Union[Any, None]", 'Annotated[Any, "k"]',
             '"Optional[Any]"', "Any | int", "_UntypedOpt"]
p = pkg(root) / "coordinator.py"
src = p.read_text()
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
fn = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_async_update_data")
replace_nodes(p, [(fn.returns, "CoordinatorPayload")])
assert all(k.isidentifier() for k in keys)
body = "".join(f"    {k}: {SPELLINGS[i % len(SPELLINGS)]}\n" for i, k in enumerate(keys))
decl = ("\n\nfrom typing import Annotated, Optional, TypeAlias, TypedDict, Union  # noqa: E402\n\n"
        "_Untyped = Any\n_UntypedOpt: TypeAlias = Optional[_Untyped]\n\n\n"
        "class CoordinatorPayload(TypedDict, total=False):\n"
        '    """Every key coordinator.data carries."""\n\n' + body + "\n")
src = p.read_text()
i = src.index("\nclass HeatPumpOptimizerCoordinator(")
j = src.rfind("\n\n", 0, i)
p.write_text(src[:j] + decl + src[j:])
print("keys", len(keys))
