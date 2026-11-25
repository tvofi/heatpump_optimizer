# Null control, box D3-g41 (fullgate.py null, comment-only marker), 2026-11-25 00:53-01:40Z
gate_rc 1, wall 2799 s, load1 0.93 (provisional), nproc 4, Intel Xeon @ 2.30GHz.
Red scripts: tests/closure.py selftest (2 of 118 closure shrink pins: merge-reason pins, status skip-not-under-scoped),
tests/entities.py (1 of 2723: "and is accepted when it does" - the scoped path records only what the diff can reach),
tests/harness_headers.py (4 of 115: the inlined-walk check names this box's probes/probe_*.py, which carry their own
repo_root walk; round4/D6/claims.py header drift x2; executed harness output not byte-identical).
Read as host/tree artefacts: a subset of the earlier boxes' null (state/gates-prior/null.json: the same three plus
optimality.py and stress.py); no script red because of the machine (no card.mjs heap failure). Not re-taken.
Consequence: the probe .py files in the wave dir stay byte-frozen while gates run, so every gate sees the same
harness_headers input as the null; later probe edits are kept in probes/out/pending/*.py.txt until the last gate ends.
