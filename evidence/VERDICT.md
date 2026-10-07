Fix review: merge ae6f9c29780ae674910790969aba67f6831fab37

bus-nonce: 960d5060efd25e71d7fa596eeef41834

Measured head ae6f9c29780ae674910790969aba67f6831fab37 (still the branch tip when posted).

- Three-dot diff: tests/closures.json (+1 line, eg_b7_seam_hubs.py in inert_reads of tests/harness_headers.py, sorted) and dev/programme/delivery/2022.md. Nothing else; no VERSION/manifest/notes, no claim files, no briefs/governance drift vs merge base.
- Precedent: that script's inert_reads now lists 13 tools/audit/harnesses/* files (12 prior); no other harness with an EXPECTED RESULT header is unlisted.
- Own stand-in (one-script recording, inert read eg_b7_seam_hubs.py, closure.py check --partial): origin/main closures.json rc=1 naming tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py; head rc=0. Null control (recording lists dual_path.py): rc=0 on both. No full derive run.
- CI authority: closures job 112847300792 at this head: completed success (check step success).
- Body answers delivery-status and nightly-status as main's, names closures as the defect. Other red at head (delivery-status, nightly-status) are main's per the body; the diff reaches neither.
