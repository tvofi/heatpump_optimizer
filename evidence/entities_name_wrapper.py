import atexit, runpy, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import harness
orig = harness.Results.check
fails = []
def check(self, name, condition, detail=""):
    r = orig(self, name, condition, detail)
    if not condition and self.title == "Entities and platforms":
        fails.append(name)
    return r
harness.Results.check = check
atexit.register(lambda: sys.stderr.write("TOPFAIL " + repr(fails) + "\n"))
sys.argv = ["tests/entities.py"]
runpy.run_path("tests/entities.py", run_name="__main__")
