R10-FLY-ARCHSCORE-STMT-PACKING, repair round 2. `coord_footprint` (counter C25) now reads a packed statement as the plain statements it spells, for every shape the round 1 review named. The first cut left two shapes open and over-counted a display bound to one target. Each shape has a calibration case planted beside attempt 48.

What changed in `footprint._units`:
- **Nested pairs** are paired recursively: `a, (b, c) = e1, (e2, e3)` and `(a, b), c = (f(), g()), h()` read 3. A pair of plumbing reads 0, as before.
- **A `for` over a literal display** counts the target/element pairs it unpacks: `for a, b, c in [(e1, e2, e3,)]` reads 3. A loop with one target over a literal (`for x in (1, 2, 3)`) stays 1, because its body is written once.
- **Over-count removed.** Only a real unpack is charged per name. A display bound to ONE target is one statement: `x = [1, 2, 3]` and `cur = (self.a, self.b, self.c, self.d)` read 1, as the base read them.
- **Bare displays**: a tuple, list, set or dict statement counts its flattened elements, constants excluded.
- **Walrus**: each walrus in a statement's own expressions counts one, beyond one that is itself the statement or an element of a bare display. `h(a := f(), b := g())` and `c = (a := f()) + (b := g())` read what the plain spelling reads.
- **Conditional-expression chains** of two or more `if`s read as the if/elif/else they spell (3 branches read 5).
- **Disposition**, written in ABOUT.md: a lone `a = x if p else y` reads 1. It is the idiom, and an `if/else` respelled as one is a bounded 3 to 1, not a class.

New red-team cases, planted in `calibration/expected.json` and `tests/closures.json`:
- rt_49: nested tuple pairs.
- rt_50: `for` over a one-element literal.
- rt_51: walrus in a call.
- rt_52: set display.
- rt_53: if/elif/else rewritten as a chain.

The first four are recorded NULL. rt_51 is recorded WORSENS and inadmissible, because its `repr(...)` wrapper is itself a new logic statement. rt_53 (the if/elif/else chain rewrite) is recorded NULL. `tests/arch_score.py` gained one table row per shape plus the display, lone-conditional and one-target-loop controls. The shared site finder is `coordinator_runs` in `redteam/rt_lib.py`.

The stored corpus was re-measured (`calibrate.py --measure-corpus --only-metric footprint`): every case reads ok and no corpus verdict moved. `tests/structure.py` is untouched and passes. Claim files are byte-identical to origin/main. No budget was raised.

## Head

852725752a6c0470322a855f11cd1ed0365cdb7b (merges nothing new: origin/main is still 499162c89d0f, already in the PR head).

## Mutation proof

The mutant that reaches the code is `ARCHSCORE_ABLATE=C25`. The earlier `footprint.PACKING_UNITS = False` source edit is reset by `vector.measure`, so it proves nothing. With C25 ablated, `calibrate.py --only rt_48..rt_53` reads IMPROVES for all six (rt_49 to rt_52 at +0.0034, rt_53 at +0.0023, rt_48 at +0.0092). Forcing `_units` to `return 1` fails the packed/plain table, the control, `a1_G2_dedupe`, rt_48 and "no red-team attempt reads IMPROVES", as the reviewer measured.

The tests were written first: before the fix, rt_50 to rt_53 moved to IMPROVES under `calibrate.py` at the first-cut instrument, and `calibrate.py` printed 'calibration moved'. After the fix, `PYTHONPATH=tests/hastub python3 tests/arch_score.py` passes in full, including rt_49 to rt_53 classifying as recorded.

## Null control

`rt_00_null_rename` still reads NULL. rt_48 to rt_53 read NULL, apart from rt_51 (WORSENS, inadmissible) as recorded above. On #3185 the base instrument (`ARCHSCORE_ABLATE=C25`, cc67aa45 against its merge base d7582ed4) reads packed +0.0042 and plain +0.0030. This head reads packed +0.0069 (footprint 2513 to 2501) and plain +0.0075 (2513 to 2500), the same within one statement. The plain spelling replaces the generator unpack with four `self._x = cur if n[i] is None else n[i]` assignments. The packed spelling read +0.0006 against plain +0.0029 at the reviewed head.

## Figures

- Packed on #3185: `python3 tools/audit/archscore/score.py --diff d7582ed404a87603bd02fefda610d7ebbe4181e1 cc67aa45df1ca9931130c6bdca543d9acc97a748` prints "dS +0.0069", footprint 2513 to 2501.
- Base instrument on the same pair: `ARCHSCORE_ABLATE=C25 python3 tools/audit/archscore/score.py --diff d7582ed404a87603bd02fefda610d7ebbe4181e1 cc67aa45df1ca9931130c6bdca543d9acc97a748` prints "dS +0.0042", footprint 2381 to 2374.
- Plain spelling of #3185: the same `score.py --diff`, against a local commit of cc67aa45 with the generator unpack respelled. It prints +0.0075 (2513 to 2500), and +0.0030 (2381 to 2376) under C25 ablation.

## Architecture score

`arch-score` passes; the diff is under `tools/audit/archscore/` and `tests/`, outside the scored package. Re-measured with `tools/audit/archscore/score.py --diff` on the real diff, no scored metric moves. `python3 tests/arch_score.py` passes: 277 checks, 0 failed.

## Red checks

none concluded for this head: CI has not run on 852725752 yet. At the reviewed head 0a13dd1a9 the only red `gate` was a cancelled superseded run (ci_priority.py's pause, not a red). `governance/delivery-status` was also failing in the live run when the reviewer read it, and I have not re-read it for the final head. `prepr.sh` at this head: rc=0, "CI PREDICT: no closures, fast, governance or instrument red predicted".

## Forward-carry

none

## Friction

none
