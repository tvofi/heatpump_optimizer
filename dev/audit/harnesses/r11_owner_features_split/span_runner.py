"""Run tests/features.py under case_select with a plan, printing @@SPAN <id> at each span start."""
import sys
sys.path.insert(0, "tests")
import case_select as cs


class Marker:
    def begin(self, sid, stmts, ns):
        print(f"@@SPAN {sid}", flush=True)

    def end(self, ns):
        pass


plan = {l.rstrip("\n") for l in open(sys.argv[1]) if l.strip()}
sys.exit(cs.run("tests/features.py", plan=plan, recorder=Marker()))
