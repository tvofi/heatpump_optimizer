Fix review: merge e67bc382e7e763e8fa27350f152a5466c79f32cb

Merge-delta judgement for PR #1824 (stage 3): 3e74c871..e67bc382, a merge of main 25e5b9cc (after #1822).
- The tree of e67bc382 equals git merge-tree 25e5b9cc 3e74c871 (ff96665f). It is a clean merge with no hand
  edits.
- main(25e5b9cc)..e67bc382 changes only tests.yml, tests/entities.py and docs/delivery/1824.md. Its +/- lines
  are byte-identical to the original authored diff af2ac763..7a113ee6. The files that changed on both sides
  (closure.py, mutation_table.py, run.sh, coverage_tree.sh and others) carry nothing from this PR beyond what
  #1822 landed.
- On top of #1822 as merged: runner.os is in the key, the covtrust step is present, the reuse reads
  steps.covtrust.outputs.trusted (the raw cache-hit test is gone), and the push staging writes the marker.
- I ran the two steps' own run: scripts (cov_marker_probe.txt). The push marker is trusted and kept. A pull
  request save, a missing marker, and main's marker at another commit are each discarded.
- codeowners_gap --check: uncovered_files=0.
UNRUN: CI on e67bc382 (merge on green only), typing, real-HA.
