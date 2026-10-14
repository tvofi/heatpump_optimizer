Fix review: blocked ed9989c0b2e3f042c8195936daa110f3e3d6a017 row-format: delivery rows for #2197 #2201 #2203 carry 9-char merge shas, record_row.row_line writes 7 (sha7)

bus-nonce: e8432ebdbadc89eb33be8c36926eff08

RESULT head ed9989c0b2e3f042c8195936daa110f3e3d6a017 measured and still the PR head at post time.
RESULT facts: all merge SHAs, tags, mandate text/expiry, body (non-empty, read via gh pr view 2213 --json body) verified.
RESULT row-format: record_row.py row_line emits "**merged `sha7`**" ([:7]); rows 2197/2201/2203 use 65081374f, 5db55db1e, 686126772. has_row skips existing rows, so the 9-char form is permanent and not the established shape. Re-write with 7 chars: 6508137, 5db55db, 6861267.
RESULT writing-for-agents: HANDOVER.md "D15 ... is in flight as #2209 together with a grader split; its brief is not in dev/governance/dimensions/ until that merges" is volatile PR state that goes stale on merge and belongs on #201 ("Nothing goes in both"); "together with a grader split" is not what #2209's title/body state (cap D15.md, re-record corpus_tokens). The "Merged so far" list restates Delivery-status rows (the file must link, not restate). Cut or move to #201.
RESULT checks: at head nightly-status failure (main's, answered in body); pr-contract, budget-raise-gate, arch-score, delivery-status, mutation, briefs, wave-script, policy-docs, hassfest success; typing, fast, coverage, browser, env-matrix, instrument-self-tests, CodeQL still in progress when read, so green not established.
