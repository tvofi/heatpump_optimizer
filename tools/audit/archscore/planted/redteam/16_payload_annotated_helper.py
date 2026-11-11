"""Game untyped_payload_keys by moving a published dict behind an annotated parameter: the away view
``data.update(self._away_state.as_dict())`` becomes ``data.update(_away_view(self._away_state))``, a module
function whose ``state: away_mode.AwayState`` parameter carries the type. Nothing is typed and the same keys are
published; a census that types a value only through the coordinator's attributes read them as gone (ARCH-s3,
round 10: the ten away keys today's ``_fold_away(state: ...)`` publishes were invisible). Counter C14."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
call = "        data.update(self._away_state.as_dict())\n"
cls = "\nclass HeatPumpOptimizerCoordinator("
assert src.count(call) == 1 and src.count(cls) == 1
helper = ('\ndef _away_view(state: away_mode.AwayState) -> dict[str, Any]:\n'
          '    """The away keys the payload carries."""\n    return state.as_dict()\n\n')
src = src.replace(call, "        data.update(_away_view(self._away_state))\n")
i = src.index(cls)
p.write_text(src[:i] + helper + src[i:])
print("away view behind an annotated parameter")
