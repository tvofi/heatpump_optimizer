Fix review: merge 8f30964ffb7e7977ad407268dfaed0c6f43a46bd

Round 2. Code delta 57eeaa6d..7fc5d3fa judged in NOTES.md (the round-1 survivors R2, R3, R6 and R9 now fail the tests; the alt text is fixed). Resolution delta 7fc5d3fa..8f30964f (a merge of main d536fb4d, the v6.7.13 stamp):
- Against git's own merge result, only tests/golden/card_claimed_drift.txt differs (conflict markers removed).
- That claim file is main's file (header, claims-for: 6.7.13) plus the branch's 39 claims and their note, verbatim.
- The only change to the branch's files beyond 7fc5d3fa is CARD_VERSION 6.7.12 -> 6.7.13, main's stamp.
- VERSION is 6.7.13, which is main's.
- At 8f30964f: card.mjs ALL CARD CHECKS PASSED; card_drift vs merge base d536fb4d: 39 moved and claimed, 1 identical (card_drift_head = drift_r3.log).
- merge-tree origin/main(6b04e444) 8f30964f: clean, rc 0.
- Heavy CI: cite the head's run as the Mac reports it; not re-run here.
- Still open outside the code: the roster's R9-UX-5 brief should carry carry-1795.json's text.
