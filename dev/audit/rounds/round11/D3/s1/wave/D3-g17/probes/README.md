Box D3-g17 probes. Each probes/<key>/ holds the probe at its repo-relative path with a `.py.txt` suffix,
its shared helper _g17.py.txt, its last output (.out.txt) and INDEX.md. The suffix is deliberate: this wave dir
sits inside the gate's tree, and tests/harness_headers.py rglobs every .py/.mjs/.js/.sh under dev/audit/rounds/,
so a .py written here mid-wave would change what later gates scan relative to the null control. The runnable
.py copies are checkpointed in the seat dir (wave/D3-g17/probes/*.py) and are restored into this dir as .py once
every gate has run. Probes were developed and run in a separate baseline worktree (~/probe-tree), never in the
gate's tree. _box/ holds the generator and the results builder (scratch scripts).
