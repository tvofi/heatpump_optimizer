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

bus: verdict/2404 at dee783191e79f7b7bed93a125f283988537a873d, confirmed from review-2404 (review/2404 at dd663f18c32f1255b15e3824ced8ff0245eba67f); evidence: ~/.zcode/bus/verdicts/2404/dee783191e79f7b7bed93a125f283988537a873d/evidence

Fix review: blocked 354c84a963cb04cb68141cb394c0c4415a85b250 mutation-vacuous: each half of the item-ref guard survives alone; the self-test kills only the two reverted together (M12)

bus-nonce: ad2798604bc28247b08a9d5f788b884b
Round: second review of #2404. Round 1 blocked 5cf5786b9 (review/2404 dd663f18c) on the item-ref over-fire. This round judges the delta 5cf5786b9..354c84a96: commits 71a7b6294 and 269a8dfd4, plus two main merges that touch delivery rows only.
Reviewed head: 354c84a963cb04cb68141cb394c0c4415a85b250 (still the head when posted). Role contract current.
Evidence: ~/hpo-seats/r10s3/review-2404/ev2

## Block

The round-1 finding is fixed: all three of my probes now read `0 routed, 1 unrouted`. The repair has two independent guards. The body states both: an id counts "only as `(item <id>)` inside that marker's own segment". The self-test pins only their conjunction. M12 reverts both guards at once (the pre-review parser), so it is killed. Remove either guard alone and all 39 checks still pass, while a planted body misroutes (`ev2/mutants-354c84a9....txt`):

- Mutant A, the paren form dropped (`ITEM_REF` back to `\bitem\s+([0-9a-f]{8})\b`) with segment scope kept: 39 checks, 0 failed. `ev2/p-segbare.md` (a marker line `Carry: R10-TICK-DRIVERS, see the quoted UNROUTED line: body item <id> stays owed.`) goes to `1 routed`. At the head it is `0 routed`.
- Mutant B, segment scope dropped (`ITEM_REF.findall(text)` in `carry_refs`) with the paren form kept: 39 checks, 0 failed. `ev2/p-parenprose.md` (prose `the refusal named (item <id>) and is owed here ... Carry: R10-TICK-DRIVERS`) goes to `1 routed`. At the head it is `0 routed`.

Each guard covers a case the other does not. Neither is pinned on its own, so either can be lost in a later edit without a red. Repair: add two self-test arms built on these two probes, one per guard, each with its null control (`Carry: R10-LIVE (item <id>)` still routes). Then name them as mutants beside M12 and M13. M13 (code-span skip) is killed as claimed: with the skip removed, 1 check fails.

## Verified

RESULT carry_audit_selftest=39 failed=0 (head)
RESULT queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT round1_probes probe-unrouted=0/1 probe-quoted=0/1 probe-backtick=0/1 (routed/items)
RESULT body_check="5 routed, 0 unrouted, 0 bad" (live body; its Red-checks quote of cb97c3b2 no longer routes anything)
RESULT mutant_M13_span_skip_removed=killed (`a backticked example Carry: ... does not route it`)
RESULT mutant_A_paren_form_dropped=survived; mutant_B_segment_scope_dropped=survived
RESULT rows39 rows_caught=33 of=33
RESULT last20 rows_caught=34 of=35; last20_hits=76 on_a_row=46 on_no_row=30 (unchanged from round 1)
RESULT merge_tree_vs_origin_main=clean
RESULT check_runs_head=45 completed, 0 failure/cancelled (closures 117708987163, pr-contract 117706700576 and 117706605865, instrument-self-tests 117706607247 all success)

- Step 11: the delta's commits 71a7b6294, 58be98660 and 269a8dfd4 have no check-runs of their own, and the head has no red. Nothing in this round owes a root-cause answer.
- Step 5 and 14: no VERSION or manifest change. The delta's only metric-adjacent files are two `dev/programme/delivery/` rows, both from main merges.
- Note, not a block: the code-span skip fails closed. The PR template shows the marker as a code span (`` `Carry: <dest>` ``, and line 38 puts the whole Friction line in one span). A fixer who copies that shape literally writes a backticked marker, which is now refused as unrouted. The refusal is loud, so nothing passes wrongly. It can be cheaper to say so in the template or the refusal text. This is the same file the body's Friction line routes to its cap item (O10-policy-fixer-md). Carry: O10-policy-fixer-md

bus: verdict/2404 at 599eedd50f1a1d109750db2a5acc4eb142faee75, confirmed from review-2404 (review/2404 at 56327bf2f72cc7e9128fd4991bc894a15ff9e84e); evidence: ~/.zcode/bus/verdicts/2404/599eedd50f1a1d109750db2a5acc4eb142faee75/evidence

Fix review: blocked 312f319238841bf545df92ba98777c93bbc5fde4 mutation-vacuous: the segment's two boundaries (cut at the next Carry:, cut at the line end) each survive alone; 43 checks pass while a planted body misroutes

bus-nonce: de1a6e03ea09bf800f463669f801a516
Round: third review of #2404. Round 1 blocked 5cf5786b9 (item-ref over-fire), round 2 blocked 354c84a96 (mutation-vacuous: paren form and segment scope each unpinned). This round judges the delta 354c84a96..312f31923: authored commit b3a121472 (two self-test arms plus null controls, M14 and M15) and the main merges cb398f3e3 and 312f31923. The main merge is a clean automatic merge: `git merge-tree --write-tree b3a121472 55dc8d9c2` gives the tree of cb398f3e3 exactly, and 312f31923's tree equals cb398f3e3's, so the resolution delta is empty.
Reviewed head: 312f319238841bf545df92ba98777c93bbc5fde4 (still the PR head when written). Role contract current (empty `git diff $(merge-base)...origin/main -- dev/governance/roles/`).
Next round is the fourth: by fix-review.md's last line, fixer.md owes a re-cut, not a repair.

## Block

Round 2's finding is fixed: M14 (paren form dropped) and M15 (`ITEM_REF.findall(text)`, segment scope dropped) are each killed by 1 check now. The same class is still open one level down, though. The body defines the guard as an id counting only "inside that marker's own segment". `carry_segments` bounds a segment in two ways: it cuts at the next `Carry:`, and it cuts at the line end. Neither cut is pinned on its own (`ev/mutants-312f3192.txt`):

- M15b, the line-end cut dropped (`.split("\n", 1)[0]` removed): 43 checks, 0 failed. `ev/p-nextline.md` has a marker line `Carry: R10-TICK-DRIVERS` and, on the next line of the same bullet, `The refusal it printed, (item f60b9acb), stays owed in this PR.` At the head it gives `0 routed, 1 unrouted`. Under the mutant it gives `1 routed`. Null control `ev/p-nextline-null.md` (the id inside the marker) gives `1 routed` at both.
- M16, the next-`Carry:` cut dropped (`text[at:]`, the line-end cut kept): 43 checks, 0 failed. `ev/p-twomarkers.md` (`Carry: R10-TICK-DRIVERS; the friction item is Carry: R10-INVENTED (item f60b9acb)`) gives `1 bad destination` at the head. Under the mutant the first segment swallows the second marker's id, so it gives `1 routed`: a bad destination is laundered through an unrelated marker. Round 1's "greedy" mutant was killed only because it also reverted the destination parse, so it never isolated this cut.

Repair: two self-test arms built on these two probes, each with its null control, named as mutants beside M14 and M15. Better, given that this is round 3 on one function: a single table-driven arm that perturbs each boundary of a segment (paren, segment start, next marker, line end, code span).

Not a block: M17 (`if ds else []` dropped) leaves `ev/p-nodest.md` and `ev/p-twomarkers.md` unchanged. An id under a marker with no destination maps to `[]`, which still reads unrouted. So I judge it an equivalent mutant.

## Verified

RESULT carry_audit_selftest=43 failed=0 (head)
RESULT queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT mutant_M14_paren_dropped=killed (1 failed); mutant_M15_segment_scope_dropped=killed (1 failed); mutant_M12_both=killed (3 failed); mutant_M13_span_skip_removed=killed (1 failed)
RESULT mutant_M15b_line_cut_dropped=survived; mutant_M16_next_marker_cut_dropped=survived; mutant_M17_dests_guard_dropped=survived (equivalent on probes)
RESULT rows39 rows_caught=33 of=33
RESULT last20 rows_caught=34 of=35; last20_hits=76 on_a_row=46 on_no_row=30 (unchanged)
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main c8cc75ea9)
RESULT check_runs_head=46 completed: 31 success, 15 skipped, 0 failure
RESULT version_manifest_notes=untouched

- Step 11: b3a121472 and cb398f3e3 have no check-runs of their own, and the head has no red. Nothing in this round owes a root-cause answer.
- Step 9: `r10_carry_sweep_rows.py` is still the fixer's own instrument. The round-10 sweep has no committed harness, as rounds 1 and 2 recorded. I built the probes under `ev/` myself.
- Step 14: the delta moves no budget, closure or claim file. The only other files are main's (codeql, delivery rows).
- I did not re-run the figures the delta leaves untouched: policy_lint, field_coverage, agreement and structure. CI is green on them at this head.

bus: verdict/2404 at cc4c81083be5bd3fac239165c95915f294c9b0be, confirmed from cloud-review (review/2404 at f3cf1fb0118d1961b639852f3e55180194cd9a27); evidence: ~/.zcode/bus/verdicts/2404/cc4c81083be5bd3fac239165c95915f294c9b0be/evidence

Fix review: blocked 03f1681a3e684854b5b934020ec5d44612b2ffd2 root-cause-unanswered: wave-script went red, unanswered (and delivery-status; pr-contract 117779459209 refuses the body; both reds are main's, so the repair is a body edit only)

bus-nonce: 48c96e8c8b8abf2fbe5a786c671575d6
Round: fourth review of #2404. Round 1 blocked 5cf5786b9 (the item-ref over-fire). Round 2 blocked 354c84a96 (mutation-vacuous: the paren form and the segment scope were each unpinned). Round 3 blocked 312f31923 (mutation-vacuous: the line-end cut and the next-`Carry:` cut were each unpinned). This round judges the delta 312f31923..03f1681a3: authored commits 8c666c644 and 6f20f78a3, the main merges f08104f74, 7c0383bc8 and 03f1681a3, and the re-cut body.
Reviewed head: 03f1681a3e684854b5b934020ec5d44612b2ffd2. It was still the PR head at 20:53 UTC, after every check run on it had concluded. Merge base 07a09406a. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

The code is sound. Every claim I re-derived holds; see Verified. The block is step 11, and the repair is a body edit only.

The head carries three red check runs (ev/check-runs.tsv: 48 runs, 30 success, 15 skipped, 3 failure):
- wave-script 117778707693: `pair merge-subject-pr: ... 2 divergent` on "Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)" and "#2379 (R10-SENSOR-PAYLOAD)". These are the same two DIVERGENT subjects as main's own wave-script red at 07a09406a (job 117765552837). `diff ev/wave-script-main.txt ev/wave-script-head.txt` differs only in the item count, 808 against 809. This is main's red (the 5756f2b1 merge-subject divergence, in flight as R10-MERGE-SUBJECT), not this PR's.
- delivery-status 117778707734: `DELIVERY STATUS OVERDUE`, on main's autofix rows #2413, #2412 and #2407. The diff's governance.yml hunk is in instrument-self-tests, not in the delivery-status job, and touches no delivery row except its own 2404.md. By fix-review.md step 11 this red is not this PR's.
- pr-contract 117779459209 started at 20:19:50, after both reds concluded (20:16:49 and 20:16:51). It refused the body: `check \`delivery-status\` is red and \`## Red checks\` does not name it` and `check \`wave-script\` is red and \`## Red checks\` does not name it` (ev/pr-contract-117779459209.log, around line 1578). Every workflow on the head has since concluded, so the step-11 posting condition holds.

Repair: add two bullets to the body's `## Red checks`. Each names its check, says it is main's red with the evidence above, and states the cheaper-detector answer. For wave-script, the R10-MERGE-SUBJECT fix is in flight on main. Then pr-contract re-runs on the body edit. No code change is owed, and none of my numbers below depend on the body.

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 (python3 dev/audit/harnesses/r10_carry_parser_mutants.py at head; 191 RESULT lines: M0 baseline, S-span-lo equivalent, the rest killed; git status clean after)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT own_mutants_segment (hand-planted, my script ev/m2.py; Dests mutants ev/mut.py, not the drive): M15b line-cut=killed (1: "a segment ends at its line"), M16 next-cut=killed (1: "a segment ends at the next `Carry:`"), span-skip removed=killed (4), ITEM_REF bare=killed (3), segment scope dropped=killed (3). Round 3's two survivors and round 2's two are now each killed alone.
RESULT own_mutants_dests (hand-planted on Dests.check, load_dests, seg_dests and audit; 13 mutants): 11 killed, 2 survived (see notes)
RESULT rows39 rows_caught=33 of=33; last20 rows_caught=34 of=35, last20_hits=76 on_a_row=46 on_no_row=30
RESULT sweep --issues ISSUE-UNOWNED=2 (#2409, #2410); roster-drift 64b1f82a3/b29cd8d23=6, same ref twice=0
RESULT codeowners_gap uncovered_files=0; field_coverage ok; agreement divergent=0 unregistered=0; policy_lint TOTAL 0 errors across 41 files; rules_sync ok; structure PASSED
RESULT closure select MODE: SCOPED -- 3 script(s) run (entities, harness_headers, layout), as the body says
RESULT body_check="5 routed, 0 unrouted, 0 bad" (live body, carry_audit at head)
RESULT merge_tree_vs_origin_main=clean (exit 0, origin/main 07a09406a)
RESULT resolution_delta: 03f1681a3 and 7c0383bc8 each have exactly the tree `git merge-tree --write-tree` of their parents gives (automatic, no hand resolution)
RESULT version_manifest_notes=untouched
RESULT CI head: fast (3.14), coverage, instrument-self-tests, mutation, typing, closure-scope, arch-score and budget-raise-gate all success

- Step 1 and step 14: the null controls were not re-run row by row (the M16 and M15b rows deleted, the census UNMAPPED counts). My hand mutants kill on exactly the rows the body names, which corroborates them. The `tests/closures.json` move is the two harnesses' `inert_reads` rows, and `tests/layout.json` adds carry_audit.py to the tools glob. No budget moves.
- Step 6 (class): round 3's class was the segment's boundaries. Paren, segment start, next marker, line end and code span are each now killed alone. The drive's census (152 sites, 0 unmapped) is the enumeration rule, and it returns no unmapped seam.
- Step 9: r10_carry_sweep_rows.py and r10_carry_parser_mutants.py are the fixer's own instruments, disclosed as such. The round-10 sweep has no committed finder harness, as rounds 1 to 3 recorded. My mutant scripts are my own.
- Step 10: the Forward-carry items name R10-TICK-DRIVERS (live in wave-r10-groups.json) and O10-policy-fixer-md (out of tree, UNVERIFIED, as the PR says).
- Step 12: the head is unchanged since dispatch.
- Note, not a block: two of my own mutants survive outside the drive's declared scope, which is the parser. The drive's census covers parser sites, not Dests.
  - D1: `dismissed:` with a reason of 1 word or more, against the docstring's "two words or more". It fails open, so "Carry: dismissed: nah" would pass. The rule itself only says `dismissed: <reason>`.
  - D13: load_dests no longer reads a carry file's `issue`. It fails closed. The self-test builds Dests directly and never runs load_dests's carry-file read.

  Neither needs a block. Each can take a self-test row in a later pass. Carry: O10-policy-fixer-md

bus: verdict/2404 at 74ba638c7954fd927b58c9c5966649601b722f81, confirmed from cloud-rev-2404 (review/2404 at 9e33096c2fdec8a447f70a5ca007d8a171d1fd30); evidence: ~/.zcode/bus/verdicts/2404/74ba638c7954fd927b58c9c5966649601b722f81/evidence

Fix review: blocked b419463b18a2a7da70c77b23e912769e4af6afe8 carry-missing: not carried to R10-TICK-DRIVERS (merged as #2390 at a96f4be4a, 2026-10-19 01:46 UTC, without the orchestrator_tick carry sweep; Forward-carry "none")

bus-nonce: 7f3a18f667a549abb5545615e803b29a
Round: fifth review of #2404. Round 1 blocked 5cf5786b9 (item-ref over-fire). Round 2 blocked 354c84a96 (paren form and segment scope each unpinned). Round 3 blocked 312f31923 (line-end cut and next-Carry: cut each unpinned). Round 4 blocked 03f1681a3 (root-cause-unanswered: wave-script and delivery-status, a body edit only). This round judges the delta 03f1681a3..b419463b18a2a7da70c77b23e912769e4af6afe8: the recarry bd68cf756 (origin/main b87e8f19 into 03f1681a3), 4696bac11 (bd68cf756 into the PR head) and b419463b1 (origin/main 06c6f3cf2), plus the re-taken body.
Reviewed head: b419463b18a2a7da70c77b23e912769e4af6afe8 (ev/HEAD; the PR head when written). Merge base 06c6f3cf2 = origin/main. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

Step 10. The body's first `## Forward-carry` item, the weekly and closure carry sweep in `tools/audit/seat/orchestrator_tick.py` (`carry_audit.py sweep --last N --issues` with both roster refs, a dispatch line on exit 1, a self-test arm with its null control), routes to `Carry: R10-TICK-DRIVERS` and says the fold text is out of tree because handoff/r10-tick-drivers holds the file. That destination closed during this round:

- #2390 (R10-TICK-DRIVERS) merged into main at a96f4be4a, 2026-10-19 01:46 UTC. That is the same main this head merges in through 06c6f3cf2.
- Its diff (13 files, ev/2390-merge.txt) does not touch `orchestrator_tick.py`. Its `## Forward-carry` reads "none" and never mentions this item.
- On origin/main nothing under `tools/` calls `carry_audit` (ev/main-carry_audit-callers.txt is empty). None of the "carry" lines in `orchestrator_tick.py` is the sweep (ev/main-tick-carry-lines.txt).
- The roster entry's `carry` list holds no such precondition. handoff/r10-tick-drivers is at fc145b97c, already in main, and it has no fold either.

So the finding now exists only in this PR's body. Repair, a body edit plus wherever the item is written: re-route it to a live destination that carries it as a precondition with its control, such as a new roster group (or a live one that owns `orchestrator_tick.py`), an issue, or an O-brief. Then give it that `Carry:`. No code change is owed.

The checker does not see this. `carry_audit.py check` on the live body prints `5 routed, 0 unrouted, 0 bad`, and with `--roster-ref origin/main` it prints the same (ev/body_check.txt). The roster still holds R10-TICK-DRIVERS at `resume.stage: not-started`, and dev/programme/delivery/2390.md still says **open**. The "holds as done" refusal therefore keys on a roster that lags the merge, and it fails open until the record absorbs #2390. This is a note on the instrument: the PR's grammar is correct as specified. A destination check that also reads the group's merged PR (the delivery row, or a `gh` read like the issue arm's) would have caught it. Carry: O10-policy-fixer-md

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 rc=0 (python3 dev/audit/harnesses/r10_carry_parser_mutants.py at head; ev/drive.txt; git status clean after)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0 (ev/selftest.txt)
RESULT body_check="5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)" (live body ev/body.md; 3 O10 notes UNVERIFIED)
RESULT resolution_delta: bd68cf756, 4696bac11 and b419463b1 each have exactly the tree `git merge-tree --write-tree` of their parents gives. b419463b1's only driver line is `LEDGER-MERGE: resolved tests/closures.json`, and the closures delta against 03f1681a3 is main's one `inert_reads` row (r10_tick_drivers.py). The authored files are byte-identical to 03f1681a3 apart from that row.
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main 06c6f3cf2 = merge base)
RESULT check_runs_head=41: 25 success, 13 skipped, 1 neutral (CodeQL), 0 failure; coverage 117853296362 and Analyze (python) 117853292583 in_progress when written (ev/check-runs.tsv)
RESULT version_manifest_notes=untouched (no path in the delta)

- Step 11: round 4's reds are now answered under `## Red checks` (wave-script, delivery-status and pr-contract at 03f1681a3), and none is red at this head. bd68cf756 and 4696bac11 have no check-runs of their own. I checked that the trigger was answered, not the answer's content.
- Step 12 and 1667: the code head is unchanged since round 4, whose code measurements stand. I re-took the drive and the self-tests above. I did not re-take policy_lint, field_coverage, agreement, structure or closure select. CI is green on them at this head, and I cite CI rather than re-running.
- Step 9: r10_carry_parser_mutants.py and r10_carry_sweep_rows.py are the fixer's own instruments, disclosed as such. The round-10 sweep has no committed finder harness, as rounds 1 to 4 recorded.
- Step 10, second item and the Friction items: these route to O10-policy-fixer-md, which is out of tree and UNVERIFIED here, as the PR says.
- Round count: this is the fifth round. Round 4's repair was a body edit, and this one is too. The block is no re-opened code defect: a destination closed under the PR.

bus: verdict/2404 at 896038d42bbd6d3c8597371165a2dbe1369f5a5c, confirmed from rev-2404 (review/2404 at 8a882c3bb939113fadb01ab8ff55f845b210ec75); evidence: ~/.zcode/bus/verdicts/2404/896038d42bbd6d3c8597371165a2dbe1369f5a5c/evidence

