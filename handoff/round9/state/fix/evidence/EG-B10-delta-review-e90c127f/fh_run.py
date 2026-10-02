import faulthandler, runpy, sys
f = open(sys.argv[1], "w")
faulthandler.dump_traceback_later(float(sys.argv[2]), repeat=True, file=f)
sys.argv = ["tests/features.py"]; sys.path.insert(0, "tests")
runpy.run_path("tests/features.py", run_name="__main__")
