Fix review: blocked 5cf5786b95dd5a559a43de7eae68d6c12519c667 other: carry_audit's item-ref routing over-fires: a quoted refusal ("item <id>") plus any Carry: in the same item routes the finding

bus-nonce: 59b4fe58a0ba61c1bc0a78033cd0c39a
Round: first review of #2404 (no earlier "Fix review:" comment or review/2404 ref). The fixer's round answering the two reds.
Reviewed head: 5cf5786b95dd5a559a43de7eae68d6c12519c667 (still the head when posted). Merge base f1b21daab. Role contract current (no drift in dev/governance/roles/ between the merge base and origin/main).
Evidence: ~/hpo-seats/r10s3/review-2404/ev

## Block

Both reds are fixed, and both fixes are proved (below). The block is a defect in the mechanism this PR lands, and the PR's own body is an instance of it.

`finding-propagation.md` (lines 44-45 at head) defines the reference form as a `Carry:` that names the id, `Carry: R10-X (item 1a2b3c4d)`. `finding_rows` does something looser. Any `item <8 hex>` anywhere in an item's text (`ITEM_REF = \bitem\s+([0-9a-f]{8})\b`), with any `Carry:` destination anywhere in that same item, routes the named item. The refusal's own output reads `UNROUTED body item <id> ...` (line 342). A fixer answering the pr-contract red under `## Red checks` quotes that line, as the red-check rule tells them to. So a quoted refusal, with any marker in the same paragraph, silences the refusal.

- Planted (`ev/probe-unrouted.md`): one unrouted `## Friction` item gives `0 routed, 1 unrouted`, rc=1.
- The same body plus a `## Red checks` bullet that quotes `UNROUTED body item e7176be8 (## Friction)` and an example `Carry: R10-TICK-DRIVERS` (`ev/probe-quoted.md`) gives `1 routed, 0 unrouted`, rc=0. Nothing routed the finding.
- This PR's body: under the pre-fix parser (`carry_audit.py` at 713182ca1), the current body passes `4 routed`. It passes only because its `## Red checks` paragraph quotes `UNROUTED body item cb97c3b2` next to `Carry: O10-policy-fixer-md`. With that one id removed, the old parser gives `3 of 4` and the new one `4 of 4`. So the head's green `pr-contract` does not show that red #1 is fixed. I showed it separately, below.

Repair (inside this PR, because the grammar is this PR's): bind the reference to the `Carry:` segment. Read `(item <id>)` inside each segment that `carry_dests` already cuts, or at least require the parenthesised form the rule documents. Add a self-test arm built on the probe above (a quoted refusal plus an unrelated marker stays unrouted), with its null control (`Carry: R10-LIVE (item <id>)` still routes).

Folded into the same repair (same parser, same class of a mention counting as a marker): a backticked example marker inside a finding's own prose routes it (`ev/probe-backtick.md`: "its example `Carry: R10-TICK-DRIVERS` names a group..." gives `1 routed`). Either decide the quoted case explicitly in the rule and the self-test, or exclude code spans.

## Verified

RESULT carry_audit_selftest=35 failed=0 (head)
RESULT queue_pre_flight_selftest=37 failed=0 (head)
RESULT body_check="4 routed, 0 unrouted, 0 bad" (head body, new parser); old parser with the item ref removed = 3 of 4 (the red reproduces), new = 4 of 4
RESULT mutant_greedy_carry=killed (CARRY back to `Carry:\s*(.+)` with the finditer loop restored: `FAIL a quoted Carry: ... earlier on a line does not hide the real one after it`, 35 checks 1 failed; restored, git status clean)
RESULT depth_seam_census=clean at head (harness_headers.inline_scan child, run as its parent runs it); null control: with the pre-fix r10_carry_sweep_rows.py put back it prints `FAIL depth seams: ...r10_carry_sweep_rows.py:33: ROOT = Path(__file__).resolve().parents[3]`; restored
RESULT rows39 rows_caught=33 of=33
RESULT last20 rows_caught=34 of=35; last20_hits=76 on_a_row=46 on_no_row=30
RESULT merge_tree_vs_origin_main=clean (exit 0)
RESULT version_manifest_notes=untouched

- Step 6 (class). Red #2: the class rule is the census itself (`inline_scan`), and it returns no other seam at head. Red #1: `carry_dests` is the one `Carry:` parser. Its other callers (`finding_rows`, `ledger_unrouted`) go through it, so the segment fix covers them. The `dismissed:` reason now stops at a following `Carry:`, which is intended. The over-fire above is the class this round left open.
- Step 9: `dev/audit/harnesses/r10_carry_sweep_rows.py` is the fixer's own instrument, and its header says so. The round-10 sweep has no committed harness, only its REPORT rows. The figures I re-derived above come from that fixer harness, not from a finder's harness.
- Step 11: the reds in the range are all at 713182ca1. pr-contract 117682018192, 117682137845 and 117690102107 are one refusal (UNROUTED cb97c3b2, and on the third run also the body not yet naming fast). fast (3.14) 117682154858 is the depth seam. The body's `## Red checks` names and answers both. faf1bf1b1, 71b30848f and 18e26326c have no red. At the head, `closures` (117699455174) and `Analyze (python)` (117697926837) were still in progress when this was written. This block does not depend on them.
- Step 14: the `tests/closures.json` move is one `inert_reads` row for the new harness (ci_predict --apply-inert), earned by the census reading it. `tests/layout.json` and CODEOWNERS add `carry_audit.py` only. No budget rows move.
- Step 10: the two Forward-carry items name R10-TICK-DRIVERS and O10-policy-fixer-md. The O-brief is out of tree, so here it is UNVERIFIED, which the PR itself says. I did not open the out-of-tree fold.
