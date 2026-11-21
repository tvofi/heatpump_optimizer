# unbacktick.py <body>: in ## Figures only, a scratch probe is named in prose, not as a command.
import re, sys

p = sys.argv[1]
s = open(p).read()
head, rest = s.split("## Figures\n", 1)
figs, tail = rest.split("## Red checks\n", 1)
subs = {
    "`ev/census.py` (scratch; execs": "The seat's scratch probe census.py (not in the tree; it execs",
    "The round-5 reviewer's probe `rev3729-r5/ev/probe_r5.py` (sha1": "The round-5 reviewer's probe probe_r5.py, from that review's evidence directory (not in the tree; sha1",
    "`ev/covtrust.py` runs tests.yml's two steps": "the seat's scratch probe covtrust.py, not in the tree, runs tests.yml's two steps",
    "under `ev/reach.py` (Null control)": "under the scratch reach.py driver (Null control)",
    "`ev/reach.py` `ok` for all three checks": "the scratch reach.py driver prints `ok` for all three checks",
    "`ev/census.py` `modules 96": "the census probe prints `modules 96",
}
for a, b in subs.items():
    assert a in figs, a
    figs = figs.replace(a, b)
assert not re.search(r"`(rev3729-r5/)?ev/", figs), re.findall(r".{30}ev/.{30}", figs)
open(p, "w").write(head + "## Figures\n" + figs + "## Red checks\n" + tail)
