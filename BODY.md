Part 5 of R10-BODY-CONTRACT (carry_audit.py and the bus.sh topic read). Four carries, each checked against main first with a grep for its symbol (`norm_pr`, `marker_shaped`, a `--topic` pass in `carry_landed`, a scoped `deferred`): none was on main at 2ced371c1af5, so none is dismissed.

Carry 0: built. An indented `Carry:` line after a paragraph's blank joins the paragraph, and a double-quoted `Carry:` phrase is no marker.
Carry 1: built. The bare word `deferred` flags a verdict item only in a findings, block or note section; `## Verified` or `## Summary` lines are no longer refused for it. The quoted-phrase half is carry 0's.
Carry 2: built. `norm_pr` maps an all-digit `--pr` to `#<N>` in `landed` and `land_ops`; `main` answers rc 2 naming `#<N>` for any other spelling.
Carry 3: built. In a structural section `Carry:` is a marker only when a group, `#N`, O-brief or `dismissed:` token follows; a findings section keeps today's rule.
Carry 4 (CARRY-LANDED-OWN-TOPIC): built. `bus.sh carry_landed` reads `.head.ref` in the same API call, maps it with `topic_grammar.py pr-topic` and passes `--topic` to `landed` and `land-ops`.

The fixtures of the refused verdicts #3327 and #3330 could not be read from this seat (no gh): the fixtures here are cut from the shapes the carries describe, not copied from those comments.

## Head

a72500c787fb4aa21c218405aa53a074765377e9, merge base 289c9b996832e50da330335deb3432836759ad2c; it descends from the earlier code head 45ae9ae7297ccf9ed2abaf67bb16c7e711f3fef4 and the PR head 8cf976936e013314c513ecf4bb283b7c88f63d8b.

## Re-cut

Past three rounds, so the repair is minimal: the latest verdict at 8cf97693 was blocked mutation-vacuous on three survivors on added `carry_audit.py` lines, and this head adds only the three `check(...)` calls that pin them (plus the `tests/closures.json` re-derivation the self-test change forces). Nothing in production code moved.

- `quoted_lookbehind_alone` (drop `(?<![\w"])` from `QUOTED_PHRASE`): pinned by `carry 3: an opening quote glued to a word (5" before the marker, a later 6" after it) never swallows the marker`; red under the mutant (447 checks, 1 failed), green at the head (447 checks, 0 failed).
- `quoted_lookahead_alone` (drop `(?!\w)`): pinned by `carry 3: a quote closed against a word ("x" too after a lone opening quote) never swallows the marker`; red under the mutant, green at the head.
- `mdlink_url_any` (`[^)\s]*` to `[^)]*` in `MD_LINK`): pinned by `carry 3: a link whose destination holds a space is no link, so Carry: [#100](a b) is no marker`; red under the mutant, green at the head.

Each mutant was applied alone to `tools/audit/carry_audit.py`, the self-test run, then the file restored.

## Earlier rounds

Round 3, answering both blocked verdicts (round 1 on `verdict/3493`, round 2 on `probe/revt-r10-carry-audit-p5-606604be`) in one pass, item by item:

1. Round 1, bus.sh `carry_landed` unreadable body: cured at e0aed259 (`$(gh ... && echo x)` keeps gh's status), pinned by `an unreadable body is still reported by carry_landed ... (CARRY-LANDED-UNREAD)`.
2. Round 1 mutant `kindsec_noNote`: killed by `carry 1: deferred under a blocked verdict's heading holding a note word mid-heading (## Open residuals) is a note`.
3. Round 1 mutant `para_nobullet`: equivalent, so the condition is deleted. A bullet line starts its own item in the line loop (`starts`), so `and not BULLET.match(nxt)` in the blank-line test decided nothing; the one-space-indented-bullet check is the null control, passing before and after.
4. Round 1 mutant `para_nocarry`: killed by `carry 0: an indented line without a marker after the blank is its own item`.
5. Round 1 mutant `quoted_lookbehind`: killed by `carry 0: a quote glued to a word (5") opens no phrase, so the marker after it routes`.
6. Round 1 mutant `marker_brief`: killed by `carry 3: an O-brief destination under ## Evidence is a marker` and by the corpus.
7. Round 1 spelling corpus: the `carry 3 corpus` check drives 13 destination spellings in 8 contexts and 8 mention spellings and asserts both sizes.
8. Round 1 P1: `carry_segments` pairs quotes on the text with its code spans blanked (same length); `carry 3 corpus P1` and `carry 0: blanking a code span keeps its length ...` pin it.
9. Round 1 P2: `marker_shaped` and `seg_dests` read a link-form destination as its text (`MD_LINK`); `carry 3 corpus P2` pins both readers.
10. Round 2, Figures line: restated below from the instrument.
11. Round 2 mutant `m2` (the `&& echo x` sentinel removed): killed by `a body ending in a literal x is read whole, not cut by the sentinel strip (CARRY-LANDED-SENTINEL)`.
12. Round 2 mutant `m3` was already killed by the wider dispatch suite; no change.

## Mutation proof

Each mutant applied alone to `tools/audit/carry_audit.py`, `python3 tools/audit/carry_audit.py --self-test` run, then restored:
- drop the `norm_pr` mapping in `landed`: FAIL carry 2.
- `carry_segments(t, shaped=True)` to `carry_segments(t)`: FAIL carry 3.
- `findings_section or ...` to `True or ...`: FAIL carry 1.
- drop the paragraph-continuation condition: FAIL carry 0.
- drop the quoted-phrase spans: FAIL carries 0/1.
- `bus.sh`, drop the `--topic` pass: `bash tools/audit/seat/bus.sh --self-test` FAIL "a body's own-group status line passes when the head ref is the group's branch".
- the three Re-cut mutants above: each FAIL (1 failed of 447).
- `bus.sh` remove `&& echo x`: FAIL `CARRY-LANDED-SENTINEL`.

## Null control

Each arm has its own: a `Carry: R10-LIVE` after a quoted phrase routes; `## Block` with `deferred` is still owed; `Carry: R10-LIVE`, `#100` and `dismissed: <reason>` under `## Evidence` are markers and `Carry: R10-NO-SUCH` is still a bad destination; a `From #3425` carry reports 0 missing for `3425` and `#3425`; the same own-group line under another group's head ref is still refused CARRY-MISSING. For the Re-cut pins the null control is the head itself: the same three checks pass unmutated.

## Figures

- `python3 tools/audit/carry_audit.py --self-test`: 447 checks, 0 failed at the head above.
- `bash tools/audit/seat/bus.sh --self-test`: 178 checks, 0 failed at the head above.

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

The three survivors named in the verdict (`quoted_lookbehind_alone`, `quoted_lookahead_alone`, `mdlink_url_any`) are pinned, none is equivalent. The remaining diff-mutant survivors on added lines are deletions of a `check(...)` call or a fixture constant (the `vh` id, `refused = True`) inside `_self_test`; a deleted check removes one assertion and the count line moves, which the mutation proof above covers arm by arm.
