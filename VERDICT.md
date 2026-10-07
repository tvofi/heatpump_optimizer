Fix review: merge 8a5d98296c62a085bf1311a8cd00b0a0f1468d4f
bus-nonce: bde2f50aaf4dca4d9a086d22deae9b49

RESULT both ends, GIT_AUTHOR_NAME=Tvofi2 GIT_AUTHOR_EMAIL=x@y exported: base f060cb4c 186 passed 7 failed (rc 2); head 8a5d98296c62a085bf1311a8cd00b0a0f1468d4f 193 passed 0 failed (rc 0).
RESULT null control, variables unset: base 193/0, head 193/0 (both green).
RESULT mutation: deleting the added export line at the head with Tvofi2 exported gives 186 passed 7 failed again; restored, worktree clean.
Diff touches only tools/pr/prepr.sh (+4: comment and one export) and dev/programme/delivery/2021.md. No VERSION, manifest, notes or claim file. git merge-tree origin/main head exits 0.
Other fixture repos in prepr.sh (lines 1124, 1278, 1427, 1602) are not SHA-keyed and passed under the env at base, so the class is one seam, as the body says.
Red checks at the head: nightly-status and delivery-status are main's (diff reaches neither reader), body answers them. budget-raise-gate is CANCELLED, not red (no raise in the diff); orchestrator should rerun the cancelled twin before merge. CodeQL neutral.
Code-owned: no. prepr.sh and delivery/2021.md match no CODEOWNERS pattern.
Round 1. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2021-evidence
