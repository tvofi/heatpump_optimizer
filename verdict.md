Fix review: merge 41effd9e0ab41e3b3421e52c70229f809a4df71e

bus-nonce: aa87d534bc4a4134bec658eb074764ee

## Findings

None.

## Evidence

- Head measured: 41effd9e0ab41e3b3421e52c70229f809a4df71e (still the PR head at post time; ls-remote of fix/r10-site-dompurify-2615-pr).
- Lockfile equals #2615's head 09a62bb574: `git diff 09a62bb574 41effd9e0ab41e3b3421e52c70229f809a4df71e -- tools/site/package-lock.json` is empty (ev/lock-vs-2615.diff, 0 bytes).
- Diff vs merge base: only tools/site/package-lock.json (4+, 3-: dompurify 3.4.16 -> 3.4.17, integrity, license field) and the delivery row dev/programme/delivery/2617.md (1 line). Nothing else.
- merge-tree with origin/main: clean, exit 0 (ev/merge-tree.txt).
- CI on this head (check-runs read, ev/check-runs.txt): fast (3.14) success, which runs tests/doc_claims.py and tests/entities.py on Linux, so the 4 entities failures seen on macOS do not occur there; closures, coverage, typing, browser, env-matrix, mutation, closure-scope, pr-contract, delivery-status, policy-docs, arch-score, budget-raise-gate, hassfest, validate-hacs all success. CodeQL is neutral. nightly-status was still in progress; it grades main rather than this diff, and it is not a required check and does not block.
- Body: mutation proof n/a with a valid reason (lockfile-only, no code); Red checks names the macOS entities failures and the #2615 reds (pr-contract author/headings, nightly-status); Supersedes #2615 stated; figures (1 file + row, 4/3 lines) re-derived and match. Author is hpo-author[bot].
- Not re-derived locally: tests/doc_claims.py needs voluptuous, absent in this seat; CI's green run stands in.
