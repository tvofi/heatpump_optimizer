Fix review: blocked 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e merge-conflict: head conflicts with origin/main in .github/workflows/governance.yml, tools/audit/seat/INSTRUMENTS.md, tools/audit/seat/beat_jobs.py, tools/audit/seat/instruments/beat_jobs.py.md

bus-nonce: 6e46a569100d5d70114fb4de057e6319

## Block
`git merge-tree --write-tree origin/main 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e` (origin/main d4968fe08ba0b18f9d96f6ca308edf45f35ca469) exits 1 with content conflicts in four paths, none of them claim files: .github/workflows/governance.yml, tools/audit/seat/INSTRUMENTS.md, tools/audit/seat/beat_jobs.py, tools/audit/seat/instruments/beat_jobs.py.md. Main has moved 32 commits past the merge base 56ce2f695bcba5218444f52c04a5ed923a07d563; 6c87325160 (round_metrics self-test step + instrument entry) and b0051ab6df (beat scorecard row) touch the conflicting paths. No MERGE-CLAIM line was printed; the only ledger merge (tests/closures.json) resolved. By fix-review.md step 13 a conflict off the claim files is the author's: merge main, resolve, and re-dispatch review at the new head. The review of the diff itself was not carried further, since any resolution changes the head and voids a verdict here.

## Evidence
- ev/HEAD.txt: the head reviewed.
- ev/merge-tree.txt: the merge-tree output and exit code.
- ev/main-commits-on-conflicting-paths.txt: main commits since the merge base on the conflicting paths.
- ev/review-packet.md: review_packet.py render, REFUSE structure (head does not merge cleanly with origin/main); gate digest pending at render.
- CI was not waited on: the block is independent of CI state at this head.
