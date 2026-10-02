Fix review: blocked ec16668596e03bf86e8b5133b95e7ad86d3e7864 replay: the dedupe keys on the signature's base64 text, and a padding-variant of the same signature verifies and posts again

Head ec166685 (handoff/r9-proc-4); delta from e773c070 is bus.sh only (+19/-1).

WHAT ROUND 3 FIXED
The exact replay from round 2 is refused at this head. replay_probe_exact.txt shows "BUS refused 1829 ...: this signed verdict was already posted on #1829 (a replay)". The new self-test case fails without the fix, and the self-test passes 42 of 42.

BLOCKING: THE SAME REPLAY WITH ONE BYTE CHANGED (replay_malleable_probe.sh/.txt)
post_verdict dedupes on the `bus-signature:` line as text. signed_by_approver decodes that text with `openssl base64 -d -A`, which accepts several spellings of the same bytes: a trailing space, a trailing CR, or an extra "=" all still give "Verified OK" (checked directly). The probe copies round 1's signed merge onto a new commit with one "=" appended to the signature line. It verifies, misses the dedupe, and posts "Fix review: merge H" after round 2's block. That is the round-2 outcome again.
Fix: dedupe on what was signed, not on how it was spelled. Key `posted-signed` on "<pr> <tree>": the tree is what the signature covers, and a fresh nonce per round already makes each round's tree differ. Alternatively, key on a hash of the decoded signature bytes, or refuse a signature line that isn't exactly the canonical `openssl base64 -A` re-encoding of its decoded bytes. Add the padding-variant case to the self-test, red-first.

UNCHANGED FROM ROUND 2, STILL FINE
Authorship needs hpo-approver's key on the Mac. Cross-PR replay and tamper are refused. The bus approves nothing, so code-owned PRs still need tvofi. The three restored passages are present. No budgets changed. policy_lint is unaffected (only bus.sh changed).
The fixer.md line "a list here would be a carried number..." stays cut. That is accepted, since the file is at its cap and the line is a rationale, not a rule.
Not run: entities.py and the full gate. Cite the head's CI.
