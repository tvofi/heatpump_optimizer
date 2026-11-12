Fix review: blocked e0aed259368fa56032f493ea9237e477d4231015 prior-block-open: the bus.sh carry_landed regression is cured and pinned, but round 1's other block items (five surviving carry_audit.py mutants and the missing spelling corpus with P1 and P2) are untouched by the delta, and the body's Figures line still states 176 bus.sh checks where the head runs 177

bus-nonce: 606604be2c4a65ec3e795355f3967bab

Round 2 of this handoff review. It is a delta review over 1ccc74680c3292f147de1268494167fac4121017..e0aed259368fa56032f493ea9237e477d4231015, which is one commit touching only `tools/audit/seat/bus.sh` (`ev/delta_stat.txt`). Because it is an instrument delta, it does not widen the scope (fix-review.md step 12).

## Block

- Round 1 block item 2 is still open. The delta does not touch `tools/audit/carry_audit.py`: `git diff 1ccc7468 e0aed259 -- tools/audit/carry_audit.py` is empty. The body's `## Unpinned sites` is also unchanged and still names only `_self_test` deletions. I re-applied each of the five added-production-line mutants alone at this head, and each survives with `carry_audit self-test: 434 checks, 0 failed`, rc 0 (`ev/mutants_carry_audit_head.txt`):
  - `kindsec_noNote`: drops `NOTE_HEADING.search(sec)` from `kind_sec` (carry_audit.py:288).
  - `para_nobullet`: drops `and not BULLET.match(nxt)` (carry_audit.py:240).
  - `para_nocarry`: drops `CARRY.search(nxt)` (carry_audit.py:240).
  - `quoted_lookbehind`: reduces `QUOTED_PHRASE` to `"[^"\n]*"` (carry_audit.py:169).
  - `marker_brief`: drops `BRIEF_TOK` from `marker_shaped` (carry_audit.py:321).

  Each needs a killing check or an `## Unpinned sites` disposition (fixer.md step 2).
- Round 1 block item 3 is still open. The body still names no spelling corpus for the shape guards `marker_shaped`, `QUOTED_PHRASE` and the paragraph-continuation test. Round 1's two spellings are still unsettled, because carry_audit.py is byte-identical to the blocked head:
  - P1: a marker between two code spans that each hold a `"`. `QUOTED_PHRASE` pairs the quotes across the spans and drops the marker.
  - P2: `Carry: [#100](https://x)` under `## Evidence`. This fails open against the base.
- A body figure is false at the head it names. `## Figures` says `bash tools/audit/seat/bus.sh --self-test: 176 checks, 0 failed at the head above`, and the head above is e0aed259. At that head the run prints `bus self-test: 177 checks, 0 failed` (`ev/bus_selftest_head.txt`). The 176 is the blocked head's count (`ev/bus_selftest_base.txt`). The body's own `## Head` paragraph says 177, so the body contradicts itself. Restate the line at the head.
- A surviving mutant on the repaired line, which no disposition covers. Mutant `m2` removes the sentinel entirely: `raw=$(gh ... 2>/dev/null); then` with no `&& echo x` (`ev/mutant_m2.diff`). It survives `bus.sh --self-test` at 177 checks, 0 failed, rc 0 (`ev/bus_selftest_m2.txt`). The new code comment and the body both claim the sentinel keeps "the body's trailing newlines". No check pins that claim. Without the sentinel, `raw=${raw%x}` would also strip a literal trailing `x` from a body. Pin it with a body ending in newlines or in `x`, or disposition it in `## Unpinned sites`.

## Evidence

- Head reviewed: e0aed259368fa56032f493ea9237e477d4231015 (`ev/HEAD.txt`). It equals `refs/heads/handoff/r10-carry-audit-p5` and the body's `## Head` at handoff-body 01644f4c1190. The body's merge base 2ced371c1af5 is unchanged.
- The named regression is cured. `bus.sh` line 236 now reads `$(gh ... 2>/dev/null && echo x)`, so the substitution's status is gh's whenever gh fails. RESULT `bus.sh --self-test` at the head: 177 checks, 0 failed, rc 0 (`ev/bus_selftest_head.txt`). The new check is `an unreadable body is still reported by carry_landed, and the dispatch goes on (CARRY-LANDED-UNREAD)`.
- The repair has a working mutation proof. Restoring `; echo x` (`ev/mutant_mut.diff`) gives `FAIL an unreadable body is still reported by carry_landed ...`, 177 checks, 1 failed, rc 1 (`ev/bus_selftest_mut.txt`). That matches the body's "177 checks, 1 failed" and "restoring `; echo x` makes it fail again".
- Null control for the repair: at the blocked head the suite runs 176 checks, 0 failed, rc 0 (`ev/bus_selftest_base.txt`). The new check is absent there, and the gain of one check is the only count movement.
- Reviewer's extra mutant `m3` turns the UNREAD branch's `return 0` into `return 1`. It is killed, with 71 checks failing (`ev/bus_selftest_m3.txt`), so the "dispatch goes on" half is pinned by the wider dispatch suite, not by the new check. The new check greps only the UNREAD line, not rc.
- Finder's harness: the round-1 reviewer's UNREAD probe (`BUS_GH=false run dispatch 7 ...`, expecting `carry-landing UNREAD #7`) is the check the fixer committed. It fails at the blocked line and passes at the head, as shown above.
- RESULT `carry_audit.py --self-test` at the head: 434 checks, 0 failed (`ev/carry_selftest_head.txt`). This matches the body.
- Merge check: `git merge-tree --write-tree origin/main e0aed259` exits 0 against origin/main 0b276e8c0cd4 (`ev/merge_tree.txt`). There is no conflict.
- No pull request exists for this head, so there is no review packet and no CI run to read. `merge_train.py owed-reds` (`ev/owed_reds.txt`) has no runs to apply to, and the body's `## Red checks: none` cannot be checked against live checks.
- Role drift: `git diff 2ced371c...origin/main -- dev/governance/roles/` touches fix-review.md steps 6, 11 and 12, the same drift round 1 reported. None of it changes this verdict.
- Versions: VERSION, the manifest and RELEASE_NOTES.md are untouched. The PR's whole diff is `tools/audit/carry_audit.py` and `tools/audit/seat/bus.sh`, and it has no golden or claim files.
- This is round 2, so fixer.md does not owe a re-cut yet.
