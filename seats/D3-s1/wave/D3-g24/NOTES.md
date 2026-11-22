# Box D3-g24 partial notes (written as work proceeds; checkpointed)
Probe classifications (pre-gate; a KILLED gate overrides):
- candidate: ce5b92d704397d85 (optimize lambda>0, sigma None -> IndexError), aab0b73e229ad900 (NaN sigma on unknown step -> failed plan), 56de38e47369b2b7 (refused == 1e-9 tie tightens a cap), df066a5f3f3d3e0f (new_cap == cap-1e-9 tie -> changed True), bbcded8a73c6a2f1 (debug count at 1e-9 tie)
- equivalent-candidate: 1dcb273b03f63a4e, c679a9939ee7b3ee (guess leaves bounds, plan never moves), 41d866cef7ea4115, fa3bb379b762e2a9, dd2b698bc1d5d4b8, 7cb1bac951ddeb9e, 68ee8d20663ac601 (no move), 0f03bb94bcab1682 (return moves, consumers mod per_window), 9bfc2c6d1bfe66bd / f54d3d4c7351ac76 / 0270b5efaac478d2 (move only on inputs production never produces)
- harness_headers.py inline_scan: probes use the canonical repo_root copy; no depth seams (checked rc 0 during the null)
- null control usable: red on worktree/strip artefacts only (gates/null-note.txt)
