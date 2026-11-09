Fix review: merge 4c6d20a9e29d198ba275de70f0641e398b4b04ae

bus-nonce: 8352e84f36b698c57905a0a5078da901

Round 1. Docs-only triage ruling (dev/programme/triage/s6-batch135.md plus this PR's delivery row); no product, VERSION, claim-file or budget change.

## Evidence
- RESULT mutation: P424 reads ACCEPT; flipped to REJECT, triage_refusal refuses "not an ACCEPT ruling (REJECT)"; file absent refuses "not on the roster branch or origin/main"; P425 reads None ("no such entry"). Matches the body (ev/mutation.txt).
- RESULT merge: git merge-tree --write-tree origin/main head exits 0, no conflict.
- RESULT ci: merge_train.py classify exits 0, GREEN, pending none, red none. owed-reds lists only green checks.
- RESULT scope: three-dot diff is 2 files, 103 insertions. VERSION untouched. No Claude footer or Co-Authored-By in the branch commits.
- Figures: the body's "1 file" for dee8b413f...9059cce re-derived. The ruling's own figures (48 h / 7 d dispatch counts, p50/p90, line counts of cloud_relay.sh) read an ls-remote snapshot and out-of-tree scripts; I could not re-derive them, so they are not verified. The body states every figure is printed by the command the ruling names.
- No finder's harness exists for a triage ruling; the fixer's mutation is the roster_edit gate itself, which I re-ran.
- Red checks: none owed. Forward-carry: none claimed; the ruling's own carries (R10-CLOUD-SEAT-CHANNEL, R10-TICK-LEVELS carry 14) are named in the ruling.
