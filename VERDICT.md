Fix review: blocked 1570415e53f8ca862d146d23b59299771f8218ae citation-wrong: carry numbers 5 and 8 on R10-HANDOFF-PATH do not match the roster

bus-nonce: 310f4a1d81e1a6de9b3ad929406466e0

## Block
Round 1. P385 cites two carries of R10-HANDOFF-PATH by number, at the roster branch it names (`37843c16d`, and the live tip `bb2f7a1d9` numbers them the same; 11 carries at both):
- "carry 8 owns the rest of that key: (topic, handoff sha, body sha)", "carry 8's key", "carry 8's reason kept", "carry 8's 'unrecoverable'". Carry 8 is the P362 `pr_tools_fresh` / STALE CHECKOUT carry. The key text and the "unrecoverable" count (28 entries) are in **carry 9**.
- "R10-HANDOFF-PATH carry 5 names the driver". Carry 5 is the #3052 `max_class_loc` merge carry. The driver (`driver4.py`, seen2.txt) is **carry 6** (also 11).
The "carry 8's key" wording is inside the "Carry text for R10-HANDOFF-PATH" block, which roster_edit.py will paste into the roster, so the wrong number would land in a durable carry that points a fixer at the P362 carry. Fix: carry 9 for the key, carry 6 for the driver (and check 11), then re-push.

Also state, once corrected: carry 9 already says "Only content refusals (prepr REFUSE) stay recorded failed"; the new text should say it narrows that sentence by splitting body-content from retryable steps, so a fixer does not read two rules.

## Evidence
- Head measured: 1570415e53f8ca862d146d23b59299771f8218ae; docs-only diff (triage entry + delivery row), no production code, no mutation proof owed.
- Verified against the tree: train.sh 484 lines, lines 403-406 and 446-451 read only the HPO_STATE_DIR default; shims/seat-python3 line 28 tries $STATE then default; update_pr.sh line 36 venv path; cloud_relay.sh 478-483 key skip, line 480 grep; open_driver.py line 11 quote; R10-HANDOFF-PATH exists, stage not-started, after empty. P375/P376 are taken on main (s6-batch115.md), P383 only on handoff/triage-s12-batch119, P384/P385 free everywhere.
- Verdict grammar, ACCEPT destination and the ACCEPT rule run are present; capped-file --budgets statements are present; roles dir unchanged vs main.
- Not re-derivable here: all session-local figures (transcript refusal counts, driver4/relay logs, the 22-of-45 table, minutes); the host has no ~/.local/state/hpo/venv-ci. The arithmetic inside the tables is consistent (22+23=45; 2+3+1=6; 18+36=54; 5+31=36).
- figure_lint: 1 not verified (a quoted git diff --stat in the checker's own text), 0 refused. carry_audit: 0 findings.
- merge-tree origin/main vs head: clean (rc 0). Delivery row present.
- CI at this head: classify printed WAIT (pending, gate red: none) at review time; the block is on content, not CI.
