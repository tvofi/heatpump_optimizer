# Reviewer's probe: a 10 s meter blip over the on-threshold, compressor off, on the edge path.
import sys, runpy
ns = runpy.run_path(sys.argv[1], run_name="sce")  # loads the build's harness (prints its own rows)
replay = ns["replay"]
for blip_s in (5, 10, 20, 29, 31, 45):
    rig = replay([(0, 0.0), (600, 2.0), (600 + blip_s, 0.0), (1200, 0.0)])
    print(f"RESULT blip_{blip_s}s={rig.c._start_counter.lifetime}")
