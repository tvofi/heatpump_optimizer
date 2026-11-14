Hotfix: the rounded-coordinate redaction check in `tests/entities.py` searched the whole diagnostics blob, which carries clock readings (`exported_at`, `diagnostics.py` `_VIEWS` draw_range timestamp), so a reading such as `...:18.1xxxxx` matches "18.1" by chance. `tests / fast (3.14)` failed 1 of 2711 entity checks on main at 50373173. The chance match is the mechanism by inference (both redaction reads were `**REDACTED**`); which timestamp matched was not measured. Production code is unchanged: no coordinate leak was shown.

The payload is now taken at two pinned clocks (`dt_util.freeze`); every value that differs is dropped (no field named), then the rounded strings are searched. A hit prints the string and its context.

## Head

f38124f19c658d49741232d56cc833f4c7c281ad

## Mutation proof

Mutant: `_clockless` returns `a` unchanged (strips nothing). `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 1 with `FAIL the rounded-coordinate search ignores a clock reading that contains one`; restored, exit 0.

## Null control

Poisoned clock `2026-01-05T03:04:18.100000Z` (isoformat holds "18.1"): the old whole-blob search hits, the new one does not (check `the rounded-coordinate search ignores a clock reading that contains one`, ok). A genuinely coarsened coordinate planted in the payload still fails the new search (check `a genuinely coarsened coordinate in the payload still fails the clock-free search`, ok). Unmodified tree: the poisoned-clock demonstration fails the new search's old form by construction (the whole-blob arm is asserted true in that check).

## Figures

none

## Red checks

`tests / fast (3.14)` at main 50373173. Cheaper detector: none. The whole-blob search was correct for every reading except those holding a rounded string, an event with probability set by the clock; the earliest detector of a clock-dependent match is a run at the matching clock, which is this fix's pinned-clock demonstration, now in the same script. Standing cost of the countermeasure: two extra diagnostics builds per `entities.py` run, not timed here.

## Forward-carry

none

## Friction

none
