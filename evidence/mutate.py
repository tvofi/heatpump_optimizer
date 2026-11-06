import sys, pathlib
p = pathlib.Path(sys.argv[1]) / "custom_components/heatpump_optimizer/coordinator.py"
s = p.read_text()
M = {
 # the reply deadline removed: wait forever for readability
 "deadline_none": [("    if not _reply_ready(stdout, timeout):", "    if not _reply_ready(stdout, None):")],
 # the frame size is not measured across reads: each read is bounded alone, the cumulative frame is not
 "measure": [("        left_bytes -= size\n", "")],
 # no-op control: a comment only
 "none": [("def _run_in_process(", "# no-op control mutant\ndef _run_in_process(")],
}
for old, new in M[sys.argv[2]]:
    assert s.count(old) == 1, (sys.argv[2], old)
    s = s.replace(old, new)
p.write_text(s)
print("mutated", sys.argv[2])
