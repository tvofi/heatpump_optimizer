import importlib.util, sys
spec = importlib.util.spec_from_file_location("d13_s3", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.res("dora_keys_loads", m.dora_instrument_check())
