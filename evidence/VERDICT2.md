Fix review: merge 6eafd3a5ef72968f463a1a0818f309ff6c643584

bus-nonce: 34df80510152edbf0c379cda85218127

Delta 9a8255b3..6eafd3a5: probe file ux5_idle_codes_sites.py + inert_reads entry + triage row reason; merge 6eafd3a5 reproduces by merge-tree (tree 883068dd), no main merge. Probe run from tree: A prev-vs-head 0/4000 (control 714); B each mutant fails its own check, restored passes; C n<=0 -> n<0 0 differing of 4000 (1522 at n==0), control 1522. My independent mutation drive (bound <=, guard off) red; old-vs-new idle_codes fuzz 0/60000; n==0 equivalence 0/3310, control 3310. CI venv (3.14): harness_headers ALL 109 PASSED, entities ALL 2214 PASSED. Body cites the in-tree probe, no machine paths; tmp_paths 0 refused. Check-runs at head settled: mutation, closures, fast, mutation-pins green; reds are delivery-status and nightly-status only (not required), named in body. coverage not waited per instruction. Evidence in this dir.
