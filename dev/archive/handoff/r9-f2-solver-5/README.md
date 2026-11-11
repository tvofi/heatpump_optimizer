# R9-F2.5 evidence harnesses

Everything this PR's body cites, in the tree (a /private/tmp copy is not a
record; this directory is).

- `share_base.py`, `term_base.py`: the round-9 recompute RCA's cost harnesses
  (`evidence/share.py` sha1 c0f74441..., `evidence/term.py` sha1 db88907d...),
  copied verbatim from the export of origin/handoff/audit-r9-plan's
  `handoff/round9/state/rca/avoidable-interpreter-bound-recomputation/` so
  they run from this worktree root; run at the merge base and at the head.
- `mutation_proof.py`: the in-memory mutation proof (M1-M5), one mutant at a
  time against the production symbol, with the healthy arm and the restore.
  `ev/mutation_proof_arm64.txt` (CPython 3.11.5, arm64) and
  `ev/mutation_proof_x86.txt` (CPython 3.14.7, x86_64, hpo-ci container) are
  its two runs.
- `run_calls.py`: drives the production-call channel -- the
  `CALLS_PROBE_DRIVER` text of `tests/stress.py` at
  handoff/r9-rca-avoidable-interpreter-bound-recomputation@ab04e39b, derived
  from that ref by the script itself (nothing on a seat-local scratch path is
  load-bearing) -- against one tree root. Needs CPython 3.12+
  (`sys.monitoring`); the captures in `ev/calls_base.json` and
  `ev/calls_head.json` ran in the hpo-ci container.
- `dbg_term.py`: the terminal detector measurement -- on the 97-row grid the
  builtin `sum` differs from plain sequential adds on 3 of 87 rows
  (single-sum arm) and 12 of 97 (four-store terms) on CPython 3.14, and on
  none of them on 3.11; run in the container. That measurement is why M4 of
  the mutation proof expects 0 on this box and 4 on the container.
- `ev/`: the runs the body quotes -- share/term at base and head, the
  enumerator at base and head, the full features.py logs at base and head,
  the production-call captures, the typing-ruler and env_drift logs.

The F2.5 test block itself (drafted as f25_block_final.py on a scratch path)
is committed where the suite runs it: the `# -- R9-F2.5` block of
`tests/features.py` (commit 1abac893), five `R.check`s in sorted position
after the F2.3 section.

Files under `tools/audit/` are outside every closure by the INERT prefix, so
this directory classifies itself and adds no gate surface.
