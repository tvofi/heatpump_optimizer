# Judge cross-check: run a harness (argv[1]) under D12-s3-01's --perturb explicit_presence (copied verbatim from flow_paths.py:_perturb_explicit_presence).
import runpy, sys
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
from heatpump_optimizer import const, thermal_model
target = sys.argv[1]; perturb = "--perturb" in sys.argv
sys.argv = [target] + [a for a in sys.argv[2:] if a != "--perturb"]
if perturb:
    def dhw(config):
        return bool(config.get(const.CONF_DHW_ENABLED, False))
    thermal_model._dhw_enabled_from_config = dhw
    orig = thermal_model.ThermalParameters.from_config.__func__
    def from_config(cls, config, *a, **k):
        config = dict(config)
        config.setdefault(const.CONF_TWO_ZONE_MODE, const.TWO_ZONE_MODE_OFF)
        return orig(cls, config, *a, **k)
    thermal_model.ThermalParameters.from_config = classmethod(from_config)
runpy.run_path(target, run_name="__main__")
