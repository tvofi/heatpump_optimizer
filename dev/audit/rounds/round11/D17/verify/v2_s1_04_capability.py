import sys; sys.path.insert(0,"custom_components")
from heatpump_optimizer import thermal_model as tm, const
for mode in ("on_off","modulating","auto"):
    print("RESULT s1_04_probe_install_on_off[%s]=%s" % (mode, tm.probe_install({const.CONF_COMPRESSOR_MODULATION: mode}).on_off))
