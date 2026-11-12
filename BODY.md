Part 5 of R10-BODY-CONTRACT (carry_audit.py and the bus.sh topic read). Four carries, each checked against main first with a grep for its symbol (`norm_pr`, `marker_shaped`, a `--topic` pass in `carry_landed`, a scoped `deferred`): none was on main at 2ced371c1af5, so none is dismissed.

Carry 0: built. An indented `Carry:` line after a paragraph's blank joins the paragraph, and a double-quoted `Carry:` phrase is no marker.
Carry 1: built. The bare word `deferred` flags a verdict item only in a findings, block or note section; `## Verified` or `## Summary` lines are no longer refused for it. The quoted-phrase half is carry 0's.
Carry 2: built. `norm_pr` maps an all-digit `--pr` to `#<N>` in `landed` and `land_ops`; `main` answers rc 2 naming `#<N>` for any other spelling.
Carry 3: built. In a structural section `Carry:` is a marker only when a group, `#N`, O-brief or `dismissed:` token follows; a findings section keeps today's rule.
Carry 4 (CARRY-LANDED-OWN-TOPIC): built. `bus.sh carry_landed` reads `.head.ref` in the same API call, maps it with `topic_grammar.py pr-topic` and passes `--topic` to `landed` and `land-ops`.

The fixtures of the refused verdicts #3327 and #3330 could not be read from this seat (no gh): the fixtures here are cut from the shapes the carries describe, not copied from those comments.

## Head

1ccc74680c3292f147de1268494167fac4121017, merge base 2ced371c1af5581c47dc6163b53c29ee15347a3d.

## Mutation proof

Each mutant applied alone to `tools/audit/carry_audit.py`, `python3 tools/audit/carry_audit.py --self-test` run, then restored:
- drop the `norm_pr` mapping in `landed` (`mut:normpr`): FAIL carry 2 (two checks).
- `carry_segments(t, shaped=True)` to `carry_segments(t)`: FAIL carry 3, the three mention shapes b6e4992b, 2c51d159, 8e3e097e.
- `findings_section or ...` to `True or ...`: FAIL carry 1, `deferred` in `## Verified`.
- drop the paragraph-continuation condition: FAIL carry 0.
- drop the quoted-phrase spans: FAIL carries 0/1, the double-quoted phrase.
- `bus.sh`, drop the `--topic` pass (`mut:landtopic`): `bash tools/audit/seat/bus.sh --self-test` FAIL "a body's own-group status line passes when the head ref is the group's branch".

## Null control

Each arm has its own: a `Carry: R10-LIVE` after a quoted phrase routes; `## Block` with `deferred` is still owed; `Carry: R10-LIVE`, `#100` and `dismissed: <reason>` under `## Evidence` are markers and `Carry: R10-NO-SUCH` is still a bad destination; a `From #3425` carry reports 0 missing for `3425` and `#3425`; the same own-group line under another group's head ref is still refused CARRY-MISSING.

## Figures

- `python3 tools/audit/carry_audit.py --self-test`: 434 checks, 0 failed at the head above.
- `bash tools/audit/seat/bus.sh --self-test`: 176 checks, 0 failed at the head above.

## Red checks

none

## Forward-carry

none

## Friction

none

## Unpinned sites

The `prepr.sh` diff-mutant survivors on added lines in `_self_test` are deletions of a `check(...)` call or the `vh` fixture id; a deleted check removes one assertion and the count line moves, which the mutation proof above covers arm by arm.
