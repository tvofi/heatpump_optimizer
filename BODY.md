Part 5 of R10-BODY-CONTRACT (carry_audit.py and the bus.sh topic read). Four carries, each checked against main first with a grep for its symbol (`norm_pr`, `marker_shaped`, a `--topic` pass in `carry_landed`, a scoped `deferred`): none was on main at 2ced371c1af5, so none is dismissed.

Carry 0: built. An indented `Carry:` line after a paragraph's blank joins the paragraph, and a double-quoted `Carry:` phrase is no marker.
Carry 1: built. The bare word `deferred` flags a verdict item only in a findings, block or note section; `## Verified` or `## Summary` lines are no longer refused for it. The quoted-phrase half is carry 0's.
Carry 2: built. `norm_pr` maps an all-digit `--pr` to `#<N>` in `landed` and `land_ops`; `main` answers rc 2 naming `#<N>` for any other spelling.
Carry 3: built. In a structural section `Carry:` is a marker only when a group, `#N`, O-brief or `dismissed:` token follows; a findings section keeps today's rule.
Carry 4 (CARRY-LANDED-OWN-TOPIC): built. `bus.sh carry_landed` reads `.head.ref` in the same API call, maps it with `topic_grammar.py pr-topic` and passes `--topic` to `landed` and `land-ops`.

The fixtures of the refused verdicts #3327 and #3330 could not be read from this seat (no gh): the fixtures here are cut from the shapes the carries describe, not copied from those comments.

## Head

45ae9ae7297ccf9ed2abaf67bb16c7e711f3fef4, merge base 2ced371c1af5581c47dc6163b53c29ee15347a3d.

Round 3, answering both blocked verdicts (round 1 on `verdict/3493`, round 2 on `probe/revt-r10-carry-audit-p5-606604be`) in one pass. Item by item, what cured each:

1. Round 1, bus.sh `carry_landed` unreadable body: cured at e0aed259 (`$(gh ... && echo x)` keeps gh's status), pinned by `an unreadable body is still reported by carry_landed ... (CARRY-LANDED-UNREAD)`.
2. Round 1 mutant `kindsec_noNote`: killed by `carry 1: deferred under a blocked verdict's heading holding a note word mid-heading (## Open residuals) is a note`. The reviewer's own P4 probe (`## Residuals`) cannot separate it, since `FINDINGS_HEADING` already matches that heading; a heading that only `NOTE_HEADING` matches can.
3. Round 1 mutant `para_nobullet`: equivalent, so the condition is deleted rather than triaged. A bullet line starts its own item in the line loop (`starts`), so `and not BULLET.match(nxt)` in the blank-line test decided nothing. Removing it leaves the one-space-indented-bullet check (`carry 0: a one-space-indented bullet after a paragraph's blank is its own item`) as the null control, passing before and after.
4. Round 1 mutant `para_nocarry`: killed by `carry 0: an indented line without a marker after the blank is its own item`.
5. Round 1 mutant `quoted_lookbehind`: killed by `carry 0: a quote glued to a word (5") opens no phrase, so the marker after it routes`.
6. Round 1 mutant `marker_brief`: killed by `carry 3: an O-brief destination under ## Evidence is a marker` and by the corpus.
7. Round 1 spelling corpus: the `carry 3 corpus` check drives 13 destination spellings in 8 contexts (104 marker spellings, each must flag) and 8 mention spellings (none may route); its name states both sizes and the check asserts them.
8. Round 1 P1 (marker between two code spans each holding a `"`): `carry_segments` pairs quotes on the text with its code spans blanked (same length, so offsets hold); `carry 3 corpus P1` pins it, and `carry 0: blanking a code span keeps its length ...` kills the mutant `m.group(0)` to `m.group(1)` that `mutant_run.py --diff` found on that new line.
9. Round 1 P2 (`Carry: [#100](https://x)` fail-open): `marker_shaped` and `seg_dests` read a link-form destination as its text (`MD_LINK`), so it is a marker and resolves to `#100`; `carry 3 corpus P2` pins both readers and that `[R10-NO-SUCH](https://x)` is still a bad destination.
10. Round 2, Figures line stated 176 bus.sh checks: restated below from the instrument at this head.
11. Round 2 mutant `m2` (the `&& echo x` sentinel removed): killed by `a body ending in a literal x is read whole, not cut by the sentinel strip (CARRY-LANDED-SENTINEL)`: `R10-LIVEx` names no group so the gate passes; with the sentinel gone `${raw%x}` cuts it to `R10-LIVE`, which holds no carry, and the dispatch is refused CARRY-MISSING.
12. Round 2 mutant `m3` (UNREAD branch `return 0` to `return 1`) was already killed by the wider dispatch suite, as the verdict records; no change.

The corpus uses the finder's spellings P1 and P2 and the reviewer's P5; the guards classify by shape, so a spelling a later reviewer finds is added to `dsp`/`ctx`/`neg` in `_self_test`.

## Mutation proof

Each mutant applied alone to `tools/audit/carry_audit.py`, `python3 tools/audit/carry_audit.py --self-test` run, then restored:
- drop the `norm_pr` mapping in `landed` (`mut:normpr`): FAIL carry 2 (two checks).
- `carry_segments(t, shaped=True)` to `carry_segments(t)`: FAIL carry 3, the three mention shapes b6e4992b, 2c51d159, 8e3e097e.
- `findings_section or ...` to `True or ...`: FAIL carry 1, `deferred` in `## Verified`.
- drop the paragraph-continuation condition: FAIL carry 0.
- drop the quoted-phrase spans: FAIL carries 0/1, the double-quoted phrase.
- `bus.sh`, drop the `--topic` pass (`mut:landtopic`): `bash tools/audit/seat/bus.sh --self-test` FAIL "a body's own-group status line passes when the head ref is the group's branch".

Round 3 additions, each applied alone and the self-test run (`python3 tools/audit/carry_audit.py --self-test`; for bus.sh `bash tools/audit/seat/bus.sh --self-test`):
- the reviewer's own spec (`probe/revt-r10-carry-audit-p5-f6551b52` `ev/mutant_driver.py`) re-run at this head: every mutant that still applies is KILLED; `para_nobullet` no longer exists (item 3), and `para_cont`, `para_noindent`, `para_nocarry`, `quoted_spans`, `marker_issue`, `marker_true` were re-expressed against the edited lines and are KILLED.
- `kindsec_noNote`, `para_nocarry`, `quoted_lookbehind`, `marker_brief`: KILLED (items 2, 4, 5, 6).
- drop the `blanked` pairing (`QUOTED_PHRASE.finditer(text)`): KILLED (P1); drop `MD_LINK` in `marker_shaped`, in `seg_dests`: KILLED (P2).
- `bus.sh` remove `&& echo x`: FAIL `CARRY-LANDED-SENTINEL`, 178 checks, 1 failed.

## Null control

Each arm has its own: a `Carry: R10-LIVE` after a quoted phrase routes; `## Block` with `deferred` is still owed; `Carry: R10-LIVE`, `#100` and `dismissed: <reason>` under `## Evidence` are markers and `Carry: R10-NO-SUCH` is still a bad destination; a `From #3425` carry reports 0 missing for `3425` and `#3425`; the same own-group line under another group's head ref is still refused CARRY-MISSING.

## Figures

- `python3 tools/audit/carry_audit.py --self-test`: 444 checks, 0 failed at the head above.
- `bash tools/audit/seat/bus.sh --self-test`: 178 checks, 0 failed at the head above.
- `python3 tools/audit/seat/mutant_run.py --diff 2ced371c1af5581c47dc6163b53c29ee15347a3d...HEAD --cmd 'python3 tools/audit/carry_audit.py --self-test' --report-only --max-mutants 200` at the pre-fix head: 54 mutants drawn; its production-line survivor was the `m.group(1)` mutant (item 8), killed since. The rest are in `_self_test` (see Unpinned sites).

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

The `prepr.sh` diff-mutant survivors on added lines in `_self_test` are deletions of a `check(...)` call or the `vh` fixture id; a deleted check removes one assertion (round 3 adds more of the same shape: `check(...)` calls and fixture constants such as the `vh` id and `refused = True`) and the count line moves, which the mutation proof above covers arm by arm.
