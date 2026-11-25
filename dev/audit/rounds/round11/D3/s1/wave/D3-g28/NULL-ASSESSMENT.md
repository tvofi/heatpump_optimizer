# Null control, box D3-g28

`fullgate.py null` (comment-only marker; GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh at baseline 92d38ecb):
gate_rc 1, wall 3305.6 s (provisional), load1 0.86 -> 0.92, thread_factor 1.0; summary line `3 TEST SCRIPT(S) FAILED` present.

Red scripts and their failing checks (gates/null.log), each an artefact of this box's tree, not of production:
- `tests/closure.py selftest` (2 of 118): "a refused merge surfaces merge()'s reason ..." and its null control, both status
  'skip-not-under-scoped': the merge-bot selftest reads git state of this detached, stripped worktree.
- `tests/entities.py` (1 of 2723): "and is accepted when it does [the scoped path records only what the diff can reach]",
  a closure re-derive instrument check that reads the worktree's git state.
- `tests/harness_headers.py` (4 of 115): "every inlined walk matches the canonical helper" (it names this box's own
  untracked probes under wave/D3-g28/probes/), `round4/D6/claims.py` claims_true/claims_false vs header (the finder wall
  stripped docs it counts) and "executed harnesses leave their committed output byte-identical" (the same claims.py run).
No machine-caused red (no card.mjs heap, no stress.py budget): the null is usable and is not re-taken. The same three
scripts are red on the D3-top6 and D3-rem nulls. A key whose gate is red only on these scripts at no more FAIL lines
reads RED-AS-NULL (survived), by fullgate.py's own comparison against gates/null.json.
