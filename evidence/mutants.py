M = {
 "B1-wire-call": ("    wire_quiet(a, opts)\n    if a.cmd", "    pass\n    if a.cmd"),
 "B2-env-dropped": ('if not (a.verbose or os.environ.get("TRAIN_VERBOSE") == "1"):', 'if not (a.verbose):'),
 "B3-flush-always": ('        if "TRAIN STOPPED" in m:\n            for h in held:', '        if True:\n            for h in held:'),
 "B4-pred-false": ("        if QUIET_CHATTER_RE.match(m):\n            held", "        if False:\n            held"),
 "B5-pred-true": ("        if QUIET_CHATTER_RE.match(m):\n            held", "        if True:\n            held"),
 "B6-drop-member": ('    (r"grade \\S+ \\S+: ok", "grade batch-1 abcd1234: ok (41s)"),\n', ''),
 "B7-tail-unbounded": ("            del held[:-tail]\n", ""),
 "B8-member-SKIP": ('(r"(released|deleted) ",', '(r"(released|deleted|SKIP) ",'),
 "R1-no-full-write": ('        fh.write(m + "\\n")\n', ''),
 "R2-no-clear": ("                out(\"  | \" + h)\n            held.clear()\n", "                out(\"  | \" + h)\n"),
 "R3-no-prefix": ('out("  | " + h)', 'out(h)'),
 "R4-widen-pr": ('(r"#\\d+ recarry: ",', '(r"#\\d+ ",'),
 "R5-flag-ignored": ('if not (a.verbose or os.environ', 'if not (False or os.environ'),
 "R6-search": ("if QUIET_CHATTER_RE.match(m):", "if QUIET_CHATTER_RE.search(m):"),
 "R7-env-truthy": ('os.environ.get("TRAIN_VERBOSE") == "1"', 'os.environ.get("TRAIN_VERBOSE")'),
 "R8-stop-not-printed": ("            held.clear()\n        out(m)\n", "            held.clear()\n            return\n        out(m)\n"),
}
import sys, pathlib
name = sys.argv[1]; p = pathlib.Path(sys.argv[2])
s = p.read_text(); a, b = M[name]
assert s.count(a) == 1, (name, s.count(a)); p.write_text(s.replace(a, b))
