"""Run a harness as __main__ and print its process's thread factor and load1 at exit."""
import atexit, os, runpy, sys, time
atexit.register(lambda: print("RESULT thread_factor=%.3f load1_end=%.2f" % (
    time.process_time() / max(time.thread_time(), 1e-9), os.getloadavg()[0]), flush=True))
path = sys.argv[1]; sys.argv = sys.argv[1:]
runpy.run_path(path, run_name="__main__")
