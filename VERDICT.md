Fix review: merge 8766b840f5582e96d13b7a322da0662433cce9a5

bus-nonce: bbf45a39fc326542b87bc153dcab5714
Seat: review-2072. Round 3, reviewing the delta 91b77d0c..8766b840 (one commit: carry-1922.json and prepr.sh). Merge base bd59a4af1b26, origin/main 47b083b03a9d. Live head re-read before posting: unchanged.

## Round-2 items: both resolved

- RESULT carry: the carry-1922.json entry now names only `finding.schema.json`, the one retired instrument (tests/layout.json retires it to dev/audit/config/). judge_batch.py and fold_ledger.py are gone from both `control` and `brief`. The JSON parses, and brief_lint reports carry-1922.json at 0 errors (TOTAL 0 across 44 files). The control's grep target is real: audit-find.js:224 still cites tools/audit/finding.schema.json.
- RESULT citation hint: I re-ran my round-2 plant, a stale citation line in README.md committed over the head.
  - It now gives `new-reference: README.md cites retired path tools/audit/harnesses/: ... -- re-point the citation to its new path in tests/layout.json`, rc 1.
  - The other arms are unchanged. A moved path gives "move it to the new path", rc 1. A zero-categories file gives "place it where tests/layout.json says", rc 1. Null at the head: rc 0, `GUARD: 0 refusal(s) against bd59a4af1b26`.
  - The new self-test row pins the citation arm.
- RESULT non-blocking items: the 6e comment reads "0.4 to 2.1 s", and the body says "about 860x" (1828 s / 2.1 s = 870).

## Re-taken at this head

- RESULT self-test: 220 passed, 0 failed, on two consecutive runs at 8766b840. A first concurrent run failed 2 rows with rc 141; see the note below. It is not this diff's defect.
- RESULT checks: 40 check-runs, all completed. fast (3.14), instrument-self-tests and policy-docs are success. The only failure is nightly-status, which this diff does not reach.
- RESULT merge simulation with #2067 (09d2061b) and #2073 (now 5bcf9d2b, moved from 3637f1c7), in 9 combinations and orders onto origin/main: all merge with no conflict, all pass `bash -n`, and all have unique step labels (22 headings with all three PRs merged).
- RESULT diff: four files three-dot (CLAUDE.md, fixer.md, carry-1922.json, prepr.sh), +80 -2. VERSION, the manifest and the notes heading are untouched. The policy re-points still owe the owner's approving review under the mandate.

## Note (not this PR's defect; for routing)

prepr.sh's call-site rows run `printf '%s\n' "$flow" | grep -q ...` under `set -o pipefail`. `$flow` is about 21 KB, which is above macOS's 16 KB default pipe buffer. When grep -q exits early, printf can take SIGPIPE, and the row reads rc 141.
- One local run at this head failed the body_line row (on main since 05ae6d239) and the moved_line row this way. Two re-runs passed.
- Linux's 64 KB buffer hides it in CI.
- This PR adds a third row of the same shape. The fix, a here-string (`grep -q ... <<<"$flow"`), covers all three rows and belongs with prepr.sh's owner, not this review.

Evidence: /Users/timmalmstrom/hpo-seats/review-2072/evidence-r3 (HEAD.txt names the head)
